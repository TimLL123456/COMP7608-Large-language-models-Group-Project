"""Build static or live, local-only trace views from saved B0 inference runs."""
import base64
import json
import re
from pathlib import Path

from .graph import build_graph

TEMPLATE = Path(__file__).with_name("templates") / "trace_viewer.html"
MAX_TRACE_BYTES = 50 * 1024 * 1024
MAX_SOURCES_PER_RUN = 40
SAFE_RUN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
SKIP_FILES = {"inference_manifest.json", "selection_manifest.json", "predictions.jsonl",
              "dev.jsonl", "test.jsonl", "summary.json", "run_manifest.json"}


def trace_sources(run_dir: Path) -> list[Path]:
    """Discover trace JSON/JSONL sources in this run only (not scoring artifacts)."""
    candidates = []
    for path in sorted(run_dir.iterdir()):
        if (path.is_symlink() or not path.is_file() or path.name in SKIP_FILES
                or path.suffix.lower() not in {".json", ".jsonl"}
                or not path.resolve().is_relative_to(run_dir.resolve())):
            continue
        # Validate record structure after reading, not the source filename.
        candidates.append(path)
    if len(candidates) > MAX_SOURCES_PER_RUN:
        raise ValueError(f"Too many trace sources in {run_dir}")
    return candidates


def _records(source: Path, *, live: bool):
    if source.stat().st_size > MAX_TRACE_BYTES:
        raise ValueError(f"Trace file exceeds {MAX_TRACE_BYTES} bytes: {source}")
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except (ValueError, TypeError) as exc:
            if live:
                return [], [f"{source.name}: JSON incomplete or invalid ({exc})"]
            raise ValueError(f"Invalid JSON trace: {source}: {exc}") from exc
        records = payload if isinstance(payload, list) else payload.get("traces", [payload]) if isinstance(payload, dict) else None
        if not isinstance(records, list):
            raise ValueError(f"Trace JSON must be a record or list: {source}")
        return records, []
    result, warnings = [], []
    lines = text.splitlines(keepends=True)
    for i, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            result.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            if live and i == len(lines) and not raw.endswith(("\n", "\r")):
                warnings.append(f"{source.name}: waiting for incomplete last JSONL record")
                break
            raise ValueError(f"Invalid trace record at {source}:{i}: {exc}") from exc
    return result, warnings


def load_run(run_dir: Path, *, live: bool = False) -> dict:
    """Load saved trace records; no model or SQL execution."""
    run_dir = Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise ValueError(f"Invalid run directory: {run_dir}")
    manifest = run_dir / "inference_manifest.json"
    if manifest.is_symlink():
        raise ValueError("Symlinked manifest is not allowed")
    metadata = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    graphs, warnings = [], []
    sources = trace_sources(run_dir)
    if not sources and not live:
        raise ValueError(f"No trace files in: {run_dir}")
    seen = set()
    for source in sources:
        try:
            records, notes = _records(source, live=live)
            warnings.extend(notes)
            for item in records:
                if not isinstance(item, dict):
                    raise ValueError(f"Expected trace JSON object in: {source}")
                # The runner's primary traces.jsonl may be supplemented by trace exports.
                if "question_id" not in item and not isinstance(item.get("report"), dict):
                    raise ValueError(f"Missing question_id/report in: {source}")
                graph = build_graph(item)
                identity = (graph["question_id"], source.name)
                if identity in seen:
                    continue
                seen.add(identity)
                graph["source_file"] = source.name
                graphs.append(graph)
        except (ValueError, OSError, UnicodeError) as exc:
            if not live:
                raise
            warnings.append(str(exc))
    if not graphs and not live:
        raise ValueError(f"Empty trace files: {run_dir}")
    return dict(run_id=metadata.get("run_id", run_dir.name),
                split=metadata.get("split", run_dir.parent.name),
                model=metadata.get("model"), graphs=graphs, warnings=warnings)


def discover_runs(base_dir: Path, *, run_ids=None) -> tuple[list[dict], list[str]]:
    """Find run directories without traversal, symlink following or recursive scans."""
    base_dir = Path(base_dir)
    if base_dir.is_symlink() or not base_dir.is_dir():
        return [], [f"Run directory not found: {base_dir}"]
    chosen = run_ids or [p.name for p in sorted(base_dir.iterdir()) if p.is_dir()
                         and not p.is_symlink() and SAFE_RUN.fullmatch(p.name)]
    runs, warnings = [], []
    for run_id in chosen:
        if not SAFE_RUN.fullmatch(run_id):
            warnings.append(f"Invalid run ID: {run_id}")
            continue
        target = base_dir / run_id
        try:
            info = load_run(target, live=True)
            warnings.extend(f"{run_id}: {note}" for note in info.pop("warnings", []))
            if info["graphs"]:
                runs.append(info)
        except (ValueError, OSError, UnicodeError) as exc:
            warnings.append(str(exc))
    return runs, warnings


def render_html(runs: list[dict], *, live: bool = False) -> str:
    if not runs and not live:
        raise ValueError("Select at least one saved run")
    # Base64 ensures trace text is not interpreted as HTML/script instructions.
    raw = json.dumps(runs, ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")
    data = base64.b64encode(raw).decode("ascii")
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count("__TRACE_PAYLOAD__") != 1 or template.count("__TRACE_ENDPOINT__") != 1:
        raise ValueError("Invalid viewer template")
    return (template.replace("__TRACE_PAYLOAD__", data)
            .replace("__TRACE_ENDPOINT__", '"/api/traces"' if live else "null"))


def write_html(run_dirs: list[Path], output_path: Path) -> Path:
    runs = [load_run(path) for path in run_dirs]
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_html(runs), encoding="utf-8")
    return target
