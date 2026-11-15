from pathlib import Path
from datetime import datetime, timezone
import subprocess, sys, json, traceback
ROOT = Path(__file__).resolve().parent
PROJECT = Path('/home/devuser/HKU/2026-2027/Sem1/COMP7608 - Large language models/Group Project')
COMMON = ['--dataset-root', str(PROJECT / 'data/bird/mini-dev-2026'), '--selection-id', 'sr-full-20261113', '--result-root', str(ROOT), '--run-id', 'sr-luna-none-sqlfirst-001']
def status(state, **kwargs):
    record = dict(state=state, updated_utc=datetime.now(timezone.utc).isoformat(), **kwargs)
    temp = ROOT / 'status.tmp'
    temp.write_text(json.dumps(record, indent=2) + '\n')
    temp.replace(ROOT / 'status.json')
try:
    for split in ('dev', 'test'):
        for action in ('infer', 'score', 'visualize'):
            status('running', split=split, action=action)
            cmd = [sys.executable, '-u', '-m', 'scr.cli.run_bird_self_reflection_eval', action, *COMMON, '--split', split]
            if action == 'infer':
                cmd += ['--provider', 'chatgpt-siwc', '--model', 'gpt-6-luna', '--reasoning-effort', 'none', '--prompt-variant', 'generalized-v1']
            with (ROOT / f'{split}-{action}.log').open('x') as log:
                subprocess.run(cmd, cwd=PROJECT, stdout=log, stderr=subprocess.STDOUT, check=True)
    summaries = {}
    for split in ('dev', 'test'):
        run = ROOT / 'sr-full-20261113' / 'SelfReflection' / split / 'sr-luna-none-sqlfirst-001'
        scores = json.loads((run / 'scores' / 'summary.json').read_text())
        rows = [json.loads(line) for line in (run / 'predictions.jsonl').read_text().splitlines()]
        decisions = [json.loads(line) for line in (run / 'reviews' / 'reflection_decisions.jsonl').read_text().splitlines()]
        from collections import Counter
        summaries[split] = dict(scores=scores, review_statuses=dict(Counter(d['review_status'] for d in decisions)), stop_reasons=dict(Counter(d['stop_reason'] for d in decisions)), usage_totals={key:sum(r.get(key) or 0 for r in rows) for key in ('model_calls','tool_calls','sql_calls','input_tokens','output_tokens','total_tokens','latency_ms')})
    (ROOT / 'performance-summary.json').write_text(json.dumps(summaries, indent=2) + '\n')
    total = sum(s['scores']['total'] for s in summaries.values())
    correct = sum(s['scores']['correct'] for s in summaries.values())
    lines = ['# Self Reflection full-dataset performance review', '', f'Execution accuracy: {correct}/{total} ({correct/total:.2%}).', '', 'Source: cbb8ea4. Model: gpt-6-luna; reasoning: none; prompt: generalized-v1.', '', 'Local BIRD Mini-Dev: 400 dev and 100 held-out questions. Reviewer PASS is separate from execution accuracy.', '', 'Preflight: 195 tests passed, one forced-finalization test failed, two skipped. Source was evaluated unchanged.', '', 'See performance-summary.json for split accuracy, usage totals, review statuses and stop reasons. No matched-compute improvement claim is made.']
    (ROOT / 'review.md').write_text('\n'.join(lines) + '\n')
    status('completed', questions=total, correct=correct, execution_accuracy=correct/total)
except BaseException as exc:
    status('failed', error=str(exc))
    traceback.print_exc()
    raise
