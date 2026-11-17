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


def _role_stage_graph(record: dict) -> dict:
    """Show real role graph node completion events, never inferred model turns."""
    report = record.get("report") or {}
    transitions = record["graph_events"]
    attempts = record.get("attempts") or []
    qid = record.get("question_id", report.get("question_id"))
    nodes = [dict(id="input", kind="input", title=f"Question {qid}", detail=dict(
        question_id=qid, db_id=report.get("db_id"),
        question=record.get("question"), evidence=record.get("evidence")))]
    edges, previous, attempt_index = [], "input", -1
    for index, event in enumerate(transitions, 1):
        name = event.get("node")
        if name not in {"prepare_input", "extract_requirements", "generate_sql",
                        "review_sql", "route_decision", "refine_sql", "finalize_sql"}:
            continue
        if name == "generate_sql":
            attempt_index += 1
        attempt = attempts[attempt_index] if 0 <= attempt_index < len(attempts) else {}
        detail = {"node": name, "observed_at_ms": event.get("observed_at_ms")}
        title = name.replace("_", " ").title()
        if name == "generate_sql":
            title += f" · Attempt {attempt_index + 1}"
            detail.update(candidate_sql=attempt.get("candidate_sql"),
                          b0_report=attempt.get("b0_report"),
                          b0_events=attempt.get("b0_events"))
        elif name == "review_sql":
            title += f" · Attempt {attempt_index + 1}"
            detail.update(review_report=attempt.get("review_report"),
                          review=attempt.get("review"))
            detail["status"] = (attempt.get("review") or {}).get("status") or "not reviewed"
        elif name == "route_decision":
            following = transitions[index].get("node") if index < len(transitions) else "END"
            detail.update(next_node=following, retry=following == "generate_sql",
                          feedback=(attempt.get("review") or {}).get("feedback"))
            detail["status"] = "retry" if following == "generate_sql" else "finalize"
        elif name == "extract_requirements":
            detail.update(extraction=record.get("extraction"))
        elif name == "refine_sql":
            detail.update(refinement=record.get("refinement"))
        elif name == "finalize_sql":
            title = "Final SQL"
            detail = {"status": report.get("output_status") or "missing",
                      "final_sql": report.get("final_sql"),
                      "error": report.get("error"),
                      "graph_completed": report.get("graph_completed"),
                      "reason": report.get("stop_reason")}
        node_id = f"stage-{index}"
        nodes.append(dict(id=node_id,
                          kind="final" if name == "finalize_sql" else "stage",
                          title=title, detail=detail))
        edges.append(dict(source=previous, target=node_id, kind="sequence"))
        previous = node_id
    return dict(question_id=qid, db_id=report.get("db_id"), legacy=False,
                report=report, nodes=nodes, edges=edges)


def _metadata_stage_graph(record: dict) -> dict:
    """Visualize observed metadata A1/B1/C1 or V1 transitions, not guessed turns."""
    report = record.get("report") or {}
    events = record.get("structured_events") or []
    steps = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("kind") == "graph_node_complete":
            steps.append({"node": event.get("node"), "observed": event})
        elif report.get("workflow") == "metadata-discovery-v2":
            name = event.get("node")
            if name in {"a1", "b1", "c1", "exhausted"}:
                if not steps or steps[-1]["node"] != name:
                    steps.append({"node": name, "observed": event})
    qid = record.get("question_id", report.get("question_id"))
    nodes = [dict(id="input", kind="input", title=f"Question {qid}", detail={
        "question_id": qid, "db_id": report.get("db_id"),
        "question": record.get("question"), "evidence": record.get("evidence")})]
    edges, previous = [], "input"
    for index, step in enumerate(steps, 1):
        name = step["node"]
        node_id = f"stage-{index}"
        nodes.append(dict(
            id=node_id, kind="stage",
            title=name.replace("_", " ").upper() if len(name) < 10 else name.replace("_", " ").title(),
            detail={"node": name, "observed": step["observed"]},
        ))
        edges.append(dict(source=previous, target=node_id, kind="sequence"))
        previous = node_id
    nodes.append(dict(id="final", kind="final", title="Final SQL", detail={
        "status": report.get("stop_reason") or "unknown",
        "final_sql": report.get("final_sql"),
        "graph_completed": report.get("graph_completed")}))
    edges.append(dict(source=previous, target="final", kind="sequence"))
    return dict(question_id=qid, db_id=report.get("db_id"),
                legacy=False, report=report, nodes=nodes, edges=edges)


def build_graph(record):
    """Build ordered model nodes, child tool nodes and related edges."""
    if (
        (record.get("report") or {}).get("workflow") == "metadata-discovery-v2"
        or any(isinstance(e, dict) and e.get("kind") == "graph_node_complete"
               for e in record.get("structured_events", []))
    ):
        return _metadata_stage_graph(record)
    if any(isinstance(e, dict) and e.get("node") == "generate_sql"
           for e in (record.get("graph_events") or [])):
        return _role_stage_graph(record)
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
                "finish", "content", "input_tokens", "output_tokens",
                "total_tokens", "cached_input_tokens", "reasoning_tokens",
                "reasoning_effort", "thinking_level", "reasoning_mode",
                "observed_at_ms")}
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
