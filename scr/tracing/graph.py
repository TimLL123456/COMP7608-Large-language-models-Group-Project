"""Convert structured B0 traces and historical text logs into a read-only graph."""
import ast
import json
import re


def legacy_events(lines):
    """Best-effort reconstruction; never invent timing or hidden reasoning."""
    events, pending = [], []
    for index, line in enumerate(lines or [], 1):
        m = re.match(r"MODEL #(\d+) usage=(\{.*?\}|unavailable) finish=(\S+)", line)
        if m:
            try:
                usage = ast.literal_eval(m.group(2)) if m.group(2).startswith("{") else {}
            except (SyntaxError, ValueError):
                usage = {}
            events.append(dict(kind="model", seq=index, model_call=int(m.group(1)),
                               finish=m.group(3), input_tokens=usage.get("input_tokens"),
                               output_tokens=usage.get("output_tokens")))
        elif line.startswith("TOOL CALL "):
            m = re.match(r"TOOL CALL (\w+): (.*)", line, re.S)
            if m:
                try:
                    args = json.loads(m.group(2))
                except ValueError:
                    args = m.group(2)
                key = f"legacy-{index}"
                pending.append((m.group(1), key))
                events.append(dict(kind="tool_call", seq=index, name=m.group(1),
                                   tool_call_id=key, args=args))
        elif line.startswith("TOOL RESULT "):
            m = re.match(r"TOOL RESULT (\w+) \(([^)]+)\): (.*)", line, re.S)
            if m:
                name, status, raw = m.groups()
                found = next((j for j, p in enumerate(pending) if p[0] == name), None)
                key = pending.pop(found)[1] if found is not None else f"unmatched-{index}"
                try:
                    payload = json.loads(raw)
                    duration = payload.get("execution_ms") if isinstance(payload, dict) else None
                except ValueError:
                    duration = None
                events.append(dict(kind="tool_result", seq=index, name=name,
                                   tool_call_id=key, status=status, output=raw,
                                   execution_ms=duration))
        elif line.startswith("MODEL RESPONSE: "):
            events.append(dict(kind="response", seq=index, text=line[len("MODEL RESPONSE: "):]))
        elif line.startswith("FINAL SQL OBSERVED:\n"):
            events.append(dict(kind="response", seq=index, text=line))
    return events


def build_graph(record):
    """Build ordered model nodes, child tool nodes and related edges."""
    report = record.get("report") or {}
    events = record.get("structured_events")
    legacy = not isinstance(events, list)
    if legacy:
        events = legacy_events(record.get("events") or [])
    qid = record.get("question_id", report.get("question_id"))
    nodes = [dict(id="input", kind="input", title=f"Question {qid}", detail=dict(
        question_id=qid, db_id=report.get("db_id"),
        question=record.get("question"), evidence=record.get("evidence")))]
    edges = []
    tools = {}
    current = None
    previous = "input"
    last_answer = None
    for event in events:
        kind = event.get("kind")
        if kind == "model":
            number = event.get("model_call") or 1
            node_id = f"model-{number}"
            if any(n["id"] == node_id for n in nodes):
                continue
            detail = {key: event.get(key) for key in (
                "finish", "content", "input_tokens", "output_tokens", "observed_at_ms")}
            nodes.append(dict(id=node_id, kind="model", title=f"Model #{number}", detail=detail))
            edges.append(dict(source=previous, target=node_id, kind="sequence"))
            current = previous = node_id
        elif kind == "tool_call":
            key = str(event.get("tool_call_id") or f"missing-{event.get('seq')}")
            node_id = f"tool-{len(tools)+1}"
            tools[key] = node_id
            nodes.append(dict(id=node_id, kind="tool", title=event.get("name") or "Unknown tool",
                              parent=current, detail=dict(tool_call_id=key, args=event.get("args"),
                              status="No result observed", output=None, execution_ms=None)))
            edges.append(dict(source=current or "input", target=node_id, kind="tool"))
        elif kind == "tool_result":
            key = str(event.get("tool_call_id"))
            node_id = tools.get(key)
            if node_id:
                node = next(n for n in nodes if n["id"] == node_id)
                node["detail"].update(status=event.get("status"), output=event.get("output"),
                                      execution_ms=event.get("execution_ms"))
            else:
                node_id = f"tool-{len(tools)+1}"
                tools[key] = node_id
                nodes.append(dict(id=node_id, kind="tool", title=event.get("name") or "Unknown tool",
                                  parent=current, detail=dict(tool_call_id=key, args=None,
                                  status=event.get("status"), output=event.get("output"),
                                  execution_ms=event.get("execution_ms"))))
                edges.append(dict(source=current or "input", target=node_id, kind="tool"))
        elif kind in ("response", "final_validation"):
            last_answer = event
    good = report.get("stop_reason") == "final_sql_ready" and bool(report.get("final_sql"))
    detail = dict(status="success" if good else report.get("stop_reason") or "unknown",
                  final_sql=report.get("final_sql"), error=report.get("error"),
                  graph_completed=report.get("graph_completed"))
    if last_answer:
        detail["raw_answer"] = last_answer.get("raw") or last_answer.get("text")
        detail["reason"] = last_answer.get("reason")
    nodes.append(dict(id="final", kind="final", title="Final answer", detail=detail))
    edges.append(dict(source=previous, target="final", kind="sequence"))
    return dict(question_id=qid, db_id=report.get("db_id"), legacy=legacy,
                report=report, nodes=nodes, edges=edges)
