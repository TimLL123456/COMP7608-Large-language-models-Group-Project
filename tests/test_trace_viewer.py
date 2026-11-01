"""Offline checks for trace graph building and browser HTML generation."""
import json
import tempfile
import unittest
from pathlib import Path

from scr.tracing.graph import build_graph
from scr.tracing.viewer import load_run, render_html, write_html


class TraceViewerTests(unittest.TestCase):
    @staticmethod
    def fixture():
        return {
            "question_id":45,
            "report":{"question_id":45,"db_id":"california_schools",
                      "model_calls":1,"tool_calls":2,"stop_reason":"invalid_final_answer",
                      "final_sql":None,"graph_completed":True,"seconds":0.2},
            "structured_events":[
                {"seq":1,"kind":"model","model_call":1,"finish":"tool_calls","input_tokens":25},
                {"seq":2,"kind":"tool_call","tool_call_id":"a","name":"inspect_table","args":{"table_name":"schools"}},
                {"seq":3,"kind":"tool_call","tool_call_id":"b","name":"execute_sql","args":{"sql":"SELECT 1"}},
                {"seq":4,"kind":"tool_result","tool_call_id":"b","status":"success","output":{"rows":[[1]]},"execution_ms":4.2},
                {"seq":5,"kind":"tool_result","tool_call_id":"a","status":"success","output":"CREATE TABLE schools"},
                {"seq":6,"kind":"final_validation","status":"invalid","raw":"Final SQL Query: ...","reason":"format"}
            ]
        }

    def test_correlates_parallel_tool_results(self):
        graph = build_graph(self.fixture())
        tools = [node for node in graph["nodes"] if node["kind"] == "tool"]
        self.assertEqual([x["detail"]["tool_call_id"] for x in tools], ["a", "b"])
        self.assertEqual([x["detail"]["status"] for x in tools], ["success", "success"])
        self.assertEqual(tools[1]["detail"]["execution_ms"], 4.2)
        self.assertEqual(graph["nodes"][-1]["detail"]["status"], "invalid_final_answer")
        self.assertEqual(sum(e["kind"] == "tool" for e in graph["edges"]), 2)

    def test_legacy_trace_has_observed_data_only(self):
        graph = build_graph({"question_id":45,"report":{"stop_reason":"invalid_final_answer"},
            "events":["MODEL #1 usage={'input_tokens': 9, 'output_tokens': 3} finish=tool_calls",
            'TOOL CALL execute_sql: {"sql": "SELECT 1"}',
            'TOOL RESULT execute_sql (success): {"rows": [[1]], "execution_ms": 1.2}',
            'MODEL RESPONSE: Final SQL Query: """\nSELECT 1\n"""']})
        self.assertTrue(graph["legacy"])
        tool = next(node for node in graph["nodes"] if node["kind"] == "tool")
        self.assertEqual(tool["detail"]["execution_ms"], 1.2)

    def test_html_never_embeds_untrusted_script_text(self):
        data = self.fixture()
        data["structured_events"][-1]["raw"] = "</script><script>alert(1)</script>"
        html = render_html([{"run_id":"demo","graphs":[build_graph(data)]}])
        self.assertNotIn("</script><script>alert(1)</script>", html)
        self.assertIn("Expand all", html)

    def test_multi_run_and_no_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = []
            for name in ("first","second"):
                path = root / name
                path.mkdir()
                paths.append(path)
                (path / "traces.jsonl").write_text(json.dumps(self.fixture()) + "\n")
                (path / "inference_manifest.json").write_text(json.dumps({"run_id":name,"split":"dev"}))
            original = (paths[0] / "traces.jsonl").read_bytes()
            target = write_html(paths, root / "viewer.html")
            self.assertTrue(target.exists())
            self.assertEqual(original, (paths[0] / "traces.jsonl").read_bytes())
            self.assertEqual(load_run(paths[1])["run_id"], "second")

    def test_invalid_trace_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "traces.jsonl").write_text("not json\n")
            with self.assertRaisesRegex(ValueError, "Invalid trace record"):
                load_run(path)
        with self.assertRaises(ValueError):
            render_html([])


class LiveViewerTests(unittest.TestCase):
    def test_discovers_new_runs_and_json_files(self):
        from scr.tracing.viewer import discover_runs
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            one = base / "run-001"
            one.mkdir()
            record = TraceViewerTests.fixture()
            (one / "traces.jsonl").write_text(json.dumps(record) + "\n")
            result, warnings = discover_runs(base)
            self.assertEqual(len(result), 1)
            two = base / "run-002"
            two.mkdir()
            (two / "question-45.json").write_text(json.dumps(record))
            result, warnings = discover_runs(base)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[1]["graphs"][0]["source_file"], "question-45.json")

    def test_jsonl_append_and_unfinished_last_record(self):
        from scr.tracing.viewer import discover_runs
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            run = base / "run"
            run.mkdir()
            first = TraceViewerTests.fixture()
            second = TraceViewerTests.fixture()
            second["question_id"] = 46
            path = run / "traces.jsonl"
            path.write_text(json.dumps(first) + "\n" + '{"question_id":46')
            runs, warnings = discover_runs(base)
            self.assertEqual(len(runs[0]["graphs"]), 1)
            self.assertTrue(any("incomplete" in w for w in warnings))
            path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n")
            runs, warnings = discover_runs(base)
            self.assertEqual(len(runs[0]["graphs"]), 2)
            self.assertEqual(warnings, [])

    def test_malformed_supplemental_file_is_nonfatal(self):
        from scr.tracing.viewer import discover_runs
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            run = base / "run"
            run.mkdir()
            (run / "traces.jsonl").write_text(json.dumps(TraceViewerTests.fixture()) + "\n")
            (run / "trace-extra.json").write_text("{unfinished")
            runs, warnings = discover_runs(base)
            self.assertEqual(len(runs[0]["graphs"]), 1)
            self.assertTrue(warnings)

    def test_live_and_static_html_controls(self):
        from scr.tracing.viewer import render_html
        static = render_html([{"run_id": "demo", "graphs": [build_graph(TraceViewerTests.fixture())]}])
        live = render_html([], live=True)
        self.assertIn("const liveEndpoint=null", static)
        self.assertIn('const liveEndpoint="/api/traces"', live)
        for expected in ('id="go-end"', 'id="refresh"', 'id="auto-refresh"',
                         "resize-grip", "contextmenu", "pointerdown",
                         "View Readable", "data-table", "readable-pre"):
            self.assertIn(expected, live)

    def test_readonly_local_server_endpoints(self):
        from http.server import ThreadingHTTPServer
        from threading import Thread
        from urllib.request import urlopen, Request
        from urllib.error import HTTPError
        from scr.tracing.server import create_handler
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            run = base / "run-001"
            run.mkdir()
            (run / "traces.jsonl").write_text(json.dumps(TraceViewerTests.fixture()) + "\n")
            server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(base))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = "http://127.0.0.1:" + str(server.server_port)
                with urlopen(url + "/api/traces", timeout=5) as resp:
                    self.assertEqual(resp.status, 200)
                    self.assertEqual(len(json.load(resp)["runs"]), 1)
                with self.assertRaises(HTTPError) as err:
                    urlopen(Request(url + "/api/traces", data=b"x", method="POST"), timeout=5)
                self.assertEqual(err.exception.code, 405)
                with self.assertRaises(HTTPError) as missing:
                    urlopen(url + "/secret", timeout=5)
                self.assertEqual(missing.exception.code, 404)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_symlink_trace_is_ignored(self):
        from scr.tracing.viewer import discover_runs
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            run = base / "run"
            run.mkdir()
            external = base / "trace-secret.json"
            external.write_text(json.dumps(TraceViewerTests.fixture()))
            try:
                (run / "trace-external.json").symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks not supported")
            runs, _ = discover_runs(base)
            self.assertEqual(runs, [])


class WidthControlTests(unittest.TestCase):
    def test_width_controls_in_static_and_live_html(self):
        from scr.tracing.viewer import render_html
        versions = (render_html([{"run_id": "test", "graphs": [build_graph(TraceViewerTests.fixture())]}]),
                    render_html([], live=True))
        for html in versions:
            self.assertIn('id="top-level-width"', html)
            self.assertIn('value="1000"', html)
            self.assertIn('min="380" max="1400" step="1"', html)
            self.assertIn('id="reset-top-level-width"', html)
            self.assertIn('topLevelWidth:1000', html)
            self.assertIn("function applyTopLevelWidth(value)", html)
            self.assertIn("isTool&&!customWidth?'100%'", html)
            self.assertIn('.toolgroup{min-width:0;overflow-x:auto}', html)
            self.assertIn('.tools{display:flex;flex-direction:column;', html)
            self.assertIn('.field-content{min-width:0;max-width:100%;overflow:auto}', html)
            self.assertNotIn("card.style.minWidth=", html)

    def test_shared_width_and_individual_overrides_with_node_if_available(self):
        """Execute the real JavaScript width functions in Node when available."""
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable for JavaScript behavior tests")
        from scr.tracing.viewer import render_html
        html = render_html([], live=True)
        source = html.split("function defaultWidth(kind)", 1)[1].split("function asObject(value)", 1)[0]
        javascript = (
            "const assert = require('node:assert/strict');\n"
            "const store={topLevelWidth:1000,widths:new Map()};\n"
            "const field={value:''};const $=()=>field;let renders=0;\n"
            "const render=()=>{renders++};const nodeKey=n=>n.key;\n"
            "function defaultWidth(kind)" + source +
            "assert.equal(defaultWidth('model'),1000);\n"
            "assert.equal(defaultWidth('tool'),300);\n"
            "store.widths.set('run/model-1',640);\n"
            "store.widths.set('run/tool-1',720);\n"
            "applyTopLevelWidth('1200');\n"
            "assert.equal(store.topLevelWidth,1200);\n"
            "assert.equal(defaultWidth('final'),1200);\n"
            "assert.equal(nodeWidth({kind:'model',key:'run/model-1'}),1200);\n"
            "assert.equal(store.widths.has('run/model-1'),false);\n"
            "assert.equal(store.widths.get('run/tool-1'),720);\n"
            "applyTopLevelWidth('1401');\n"
            "assert.equal(field.value,'1200');\n"
            "assert.equal(store.topLevelWidth,1200);\n"
            "applyTopLevelWidth('1000');\n"
            "assert.equal(store.topLevelWidth,1000);\n"
            "assert.equal(renders,2);\n"
        )
        completed = subprocess.run([node, "-e", javascript], capture_output=True,
                                   text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_browser_script_syntax_when_node_available(self):
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable for JavaScript syntax checks")
        from scr.tracing.viewer import render_html
        script = render_html([], live=True).split("<script>", 1)[1].split("</script>", 1)[0]
        result = subprocess.run([node, "--check", "-"], input=script, text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
