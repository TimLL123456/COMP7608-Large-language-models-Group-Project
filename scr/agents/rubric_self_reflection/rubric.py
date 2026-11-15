"""Atomic requirements and evidence-backed verdict validation for RubricSelfReflection."""
from __future__ import annotations

import json

CATEGORIES = frozenset({
    "output", "filter", "metric", "grain", "time", "source_join",
    "value_semantics", "presentation", "execution",
})
STATUSES = frozenset({"PASS", "FAIL", "UNCERTAIN", "N/A"})
MAX_REQUIREMENTS = 30
MAX_INSPECTION_REQUESTS = 2


def model_json(response) -> dict:
    """Parse one complete JSON object; reject trailing content and silent coercion."""
    if isinstance(response, dict):
        result = response
    else:
        value = getattr(response, "content", response)
        if isinstance(value, list):
            value = "".join(part.get("text", "") for part in value
                            if isinstance(part, dict) and part.get("type") in ("text", "output_text"))
        if not isinstance(value, str) or len(value) > 60_000:
            raise ValueError("Invalid model JSON content")
        value = value.strip()
        if value.startswith("```"):
            lines = value.splitlines()
            if len(lines) < 3 or lines[-1].strip() != "```":
                raise ValueError("Unclosed model JSON fence")
            value = "\n".join(lines[1:-1]).strip()
        result = json.loads(value)
    if not isinstance(result, dict):
        raise ValueError("Expected one JSON object")
    return result


def parse_requirements(payload: dict, question: dict) -> list[dict]:
    """Validate stable atomic IDs against authorized question/evidence text."""
    items = payload.get("requirements")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_REQUIREMENTS:
        raise ValueError("Invalid requirement list length")
    source = ((question.get("question") or "") + "\n" + (question.get("evidence") or "")).casefold()
    seen = set()
    result = []
    for i, entry in enumerate(items, 1):
        if not isinstance(entry, dict):
            raise ValueError("Requirement must be an object")
        req_id, category = entry.get("requirement_id"), entry.get("category")
        expected, quote, material = (entry.get("expected"), entry.get("source_quote"),
                                     entry.get("material"))
        if req_id != f"R{i:02d}" or req_id in seen or category not in CATEGORIES:
            raise ValueError("Requirement IDs must be ordered, unique and categorized")
        if not isinstance(expected, str) or not expected.strip() or len(expected) > 1000:
            raise ValueError("Missing expected requirement")
        if not isinstance(quote, str) or not quote.strip() or quote.strip().casefold() not in source:
            raise ValueError("Requirement quote is not grounded in question/evidence")
        if type(material) is not bool:
            raise ValueError("Material flag must be boolean")
        seen.add(req_id)
        result.append({"requirement_id": req_id, "category": category,
                       "expected": expected.strip(), "source_quote": quote.strip(),
                       "material": material})
    return result


def parse_review(payload: dict, requirements: list[dict], *, finalizing: bool) -> dict:
    """Enforce full ID coverage and verdict precedence; model cannot grant itself PASS."""
    assessments = payload.get("assessments")
    coverage = payload.get("coverage")
    issues = payload.get("issues")
    requests = payload.get("inspection_requests")
    if not isinstance(assessments, list) or not isinstance(coverage, dict) or not isinstance(issues, list):
        raise ValueError("Missing review sections")
    if not isinstance(requests, list) or len(requests) > MAX_INSPECTION_REQUESTS:
        raise ValueError("Invalid inspection requests")
    if len(assessments) != len(requirements):
        raise ValueError("All extracted requirements must be assessed")
    by_id = {r["requirement_id"]: r for r in requirements}
    seen = set()
    checked = []
    for row in assessments:
        if not isinstance(row, dict):
            raise ValueError("Invalid assessment")
        rid = row.get("requirement_id")
        if rid not in by_id or rid in seen or row.get("status") not in STATUSES:
            raise ValueError("Unknown/duplicate requirement ID or status")
        seen.add(rid)
        for key in ("observed", "evidence", "reason"):
            if not isinstance(row.get(key), str):
                raise ValueError(f"Missing assessment field: {key}")
        if row["status"] in ("PASS", "FAIL") and not all(
                row[k].strip() for k in ("observed", "evidence", "reason")):
            raise ValueError("PASS/FAIL need observed SQL evidence and reason")
        if row["status"] == "N/A":
            if by_id[rid]["material"] or not row["reason"].strip():
                raise ValueError("Material user requirements cannot be N/A")
        checked.append({**by_id[rid], "status": row["status"],
                        "observed": row["observed"][:2000], "evidence": row["evidence"][:4000],
                        "reason": row["reason"][:1200]})
    if seen != set(by_id):
        raise ValueError("Missing requirement IDs")
    if coverage.get("status") not in ("COMPLETE", "GAP", "UNCERTAIN") or not isinstance(
            coverage.get("details"), str):
        raise ValueError("Invalid question coverage check")
    if len(issues) > 15:
        raise ValueError("Too many issues")
    for issue in issues:
        if not isinstance(issue, dict) or issue.get("requirement_id") not in by_id:
            raise ValueError("Issue references an unknown requirement")
        if checked[next(i for i,r in enumerate(checked) if r["requirement_id"] == issue["requirement_id"])]["status"] != "FAIL":
            raise ValueError("Issue must refer to a failed requirement")
        if not all(isinstance(issue.get(k), str) and issue[k].strip()
                   for k in ("description", "evidence", "suggested_action")):
            raise ValueError("Issue requires grounded diagnostic feedback")
    for req in requests:
        if not isinstance(req, dict) or req.get("kind") not in ("list_tables", "inspect_table", "execute_sql"):
            raise ValueError("Invalid read-only inspection kind")
        if not isinstance(req.get("reason"), str) or not req["reason"].strip():
            raise ValueError("Inspection request needs reason")
        key = "table" if req["kind"] == "inspect_table" else "sql" if req["kind"] == "execute_sql" else None
        if key and (not isinstance(req.get(key), str) or not req[key].strip()):
            raise ValueError("Inspection request missing table/SQL")
    material = [r for r in checked if r["material"]]
    failed = any(r["status"] == "FAIL" for r in checked)
    unresolved = any(r["status"] == "UNCERTAIN" for r in material)
    calculated = ("FAIL" if failed else
                  "UNCERTAIN" if unresolved or coverage["status"] != "COMPLETE" else "PASS")
    if payload.get("overall_status") != calculated:
        raise ValueError("Overall verdict conflicts with detailed findings")
    if failed and not issues:
        raise ValueError("Confirmed FAIL requires diagnostic issues")
    if issues and not failed:
        raise ValueError("Issues require FAIL")
    if calculated == "PASS" and (not material or any(r["status"] != "PASS" for r in material)):
        raise ValueError("PASS requires positive material coverage")
    feedback = payload.get("feedback")
    if not isinstance(feedback, str) or (failed and not feedback.strip()):
        raise ValueError("FAIL must provide feedback")
    needs = payload.get("needs_more_evidence")
    if type(needs) is not bool:
        raise ValueError("Invalid evidence flag")
    if calculated != "UNCERTAIN" and (needs or requests):
        raise ValueError("Only UNCERTAIN may request inspection")
    if finalizing and (needs or requests):
        raise ValueError("No tool requests permitted in review finalization")
    if calculated == "UNCERTAIN" and not needs and requests:
        raise ValueError("Inspection requests require evidence flag")
    return {"status": calculated, "requirements": checked, "coverage": coverage,
            "issues": issues, "feedback": feedback[:5000],
            "needs_more_evidence": needs, "inspection_requests": requests}
