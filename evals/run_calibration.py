"""Explicit opt-in live judge calibration; never changes application responses."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from commercelens_ai.config import Settings
from commercelens_ai.providers import OpenAICompatibleModel
from commercelens_ai.eval_contracts import judge_contract


def agreement(fixture, assessment):
    checks = {'gate': assessment.get('gate_status') == fixture['expected_gate_status']}
    if fixture.get('expected_documentation_gap'):
        checks['documentation_gap'] = assessment.get('documentation_gap', {}).get('status') == fixture['expected_documentation_gap']
    if fixture.get('expected_score_order'):
        scores = assessment.get('scores', {})
        a, b = scores.get('application_correctness'), scores.get('documentation_grounding')
        checks['correctness_separate_from_grounding'] = a is not None and b is not None and a > b
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Send fixtures to configured chat provider')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error('--live explicitly authorizes sending evaluation fixtures to the configured provider')
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    settings = Settings.from_env(ROOT)
    cases = {c['id']: c for c in map(json.loads, (ROOT/'evals/golden.jsonl').read_text(encoding='utf-8').splitlines())}
    fixtures = list(map(json.loads, (ROOT/'evals/judge_calibration.jsonl').read_text(encoding='utf-8').splitlines()))

    def grade(fixture):
        model = OpenAICompatibleModel(settings.chat_api_key, settings.chat_base_url, settings.chat_model, max_tokens=8000, timeout=120)
        complete = model.complete
        def capture(messages):
            raw = complete(messages)
            (output/(fixture['id']+'-raw.json')).write_text(raw, encoding='utf-8')
            return raw
        model.complete = capture
        try:
            assessment = judge_contract(model, cases[fixture['case_id']], fixture['result'])
        except Exception as exc:
            assessment = {'status': 'error', 'error': type(exc).__name__}
        checks = agreement(fixture, assessment)
        return {'fixture': fixture, 'assessment': assessment, 'agreement': checks, 'all_match': all(checks.values())}

    rows = []
    with (output/'results.jsonl').open('w', encoding='utf-8') as stream, ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(grade, f) for f in fixtures]):
            row = future.result(); rows.append(row)
            stream.write(json.dumps(row)+'\n'); stream.flush()
            print(row['fixture']['id'], row['assessment']['status'], row['all_match'], flush=True)
    summary = {'count': len(rows), 'agreement_count': sum(r['all_match'] for r in rows),
               'judge_errors': sum(r['assessment']['status'] != 'ok' for r in rows),
               'note': 'Agent-authored fixtures; not independent human calibration. Keep all disagreements.'}
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
