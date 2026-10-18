"""Read-only reconciliation of existing raw captures; never evaluates policies."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LANE = Path('/root/ecas_missing_state_mechanism_20261015')
RUN = LANE / 'managed_runs/missing-state-mechanism-v1'
checks = []

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ck(label, condition):
    checks.append({'check': label, 'pass': bool(condition)})

result = read(ROOT / 'RESULTS.json')
status = read(RUN / 'status.json')
gate = read(ROOT / 'SCOPED_GATE_READY.json')
ck('actual_run_succeeded', status['state'] == 'SUCCEEDED' and status['exit_code'] == 0)
ck('actual_gate_ready', gate['data']['ready_for_formal_run'] and not gate['data']['blockers'])
ck('result_matches_runner_bytes', sha(ROOT / 'RESULTS.json') == sha(RUN / 'outputs/result.json') == status['outputs'][0]['sha256'])
ck('result_status_and_scope', result['status'] == 'COMPLETED' and result['scope_id'] == 'ECAS-MISSING-STATE-MECHANISM-20261015-01')
ck('no_new_models_or_cases', result['new_model_calls'] == result['new_cases'] == 0)
for i, item in enumerate(read(ROOT / 'INPUT_MANIFEST.json')):
    ck(f'frozen_input_{i}', sha(item['path']) == item['sha256'])
for i, item in enumerate(read(ROOT / 'SOURCE_MANIFEST.json')):
    ck(f'original_snapshot_{i}', sha(item['source']) == sha(item['snapshot']) == item['sha256'])

vectors = read(ROOT / 'FROZEN_VECTORS.json')
rows = result['rows']
csvrows = list(csv.DictReader((ROOT / 'OBSERVATIONS.csv').open(encoding='utf-8-sig', newline='')))
ck('18_vectors_and_144_observations', sum(map(len, vectors.values())) == 18 and len(rows) == len(csvrows) == 144)
index = {(r['task'], r['arm'], r['probe_id']): r for r in rows}
ck('144_unique_observation_keys', len(index) == 144)
for row, csvrow in zip(rows, csvrows):
    name = '/'.join([row['task'], row['arm'], row['probe_id']])
    for key, value in csvrow.items():
        expected = '' if row.get(key) is None else str(row[key])
        ck(name + '/csv/' + key, value == expected)
    vector = next(v for v in vectors[row['task']] if v['id'] == row['probe_id'])
    ck(name + '/frozen_label', row['historical_expected'] == vector['expected'] and row['kind'] == vector['kind'])
    if row['method'] == 'ECAS':
        actual = read(LANE / 'results' / row['task'] / row['arm'] / (row['probe_id'] + '.json'))
        ck(name + '/raw_result', actual['input'] == vector['envelope'] and actual['result'] == row)
        ck(name + '/executed_without_engine_error', 'engine_error' not in row['actual'] and row['decision'] == row['actual']['decision'])
    else:
        out = LANE / 'results' / row['task'] / row['arm']
        raw = read(out / (row['probe_id'] + '.stdout.txt'))
        values = [e['value'] for r in raw.get('result', []) for e in r.get('expressions', [])]
        ck(name + '/raw_opa_boolean', len(values) == 1 and type(values[0]) is bool and row['decision'] == ('allow' if values[0] else 'deny'))
        packet = read(ROOT / 'inputs' / row['task'] / 'packet.json')
        adapted = dict(vector['envelope'])
        abi = packet['common_adapter']
        adapted.update(subject={'id': abi['subject_id'], 'role': abi['subject_role']}, action=packet['target']['operation'],
            resource={'id': abi['resource_id'], 'system': packet['target']['system'], 'version': packet['target']['version']})
        ck(name + '/raw_opa_input', adapted == read(out / (row['probe_id'] + '.input.json')))
    if vector['expected'] is None:
        ck(name + '/no_invented_gold', row['agrees_with_historical_label'] is None)

admissions = {(a['task'], a['arm']): a for a in result['admissions']}
ck('eight_actual_admission_records', len(admissions) == 8 and all(a['status'] in ('ADMITTED', 'SHAPE_COMPILED') for a in admissions.values()))
for task, task_vectors in vectors.items():
    orig = read(ROOT / 'inputs' / task / 'candidate.json')
    original_output = read(LANE / 'results' / task / 'original.candidate.json')
    skip = read(LANE / 'results' / task / 'missing_skip.candidate.json')
    ck(task + '/original_candidate_unchanged', orig == original_output)
    expected_skip = json.loads(json.dumps(orig))
    expected_skip['rules'][0]['params']['on_missing'] = 'skip'
    ck(task + '/only_on_missing_changed', skip == expected_skip)
    for variant in ('original', 'missing_skip'):
        fp = read(LANE / 'results' / task / ('ECAS_' + variant + '_full.policy.json'))
        sp = read(LANE / 'results' / task / ('ECAS_' + variant + '_shape.policy.json'))
        ck(task + '/' + variant + '/same_policy_full_shape', fp == sp)
        for v in task_vectors:
            f = index[(task, 'ECAS_' + variant + '_full', v['id'])]
            s = index[(task, 'ECAS_' + variant + '_shape', v['id'])]
            ck(task + '/' + variant + '/' + v['id'] + '/same_execution_full_shape', f['actual'] == s['actual'])
    ck(task + '/original_empty_trusted_deny', index[(task, 'ECAS_original_full', 'missing-trusted')]['decision'] == 'deny')
    ck(task + '/skip_full_still_admitted_and_allows_empty_state', admissions[(task, 'ECAS_missing_skip_full')]['status'] == 'ADMITTED' and index[(task, 'ECAS_missing_skip_full', 'missing-trusted')]['decision'] == 'allow')
    for method in ('P2P_STYLE', 'AUTOPAC_STYLE'):
        for v in task_vectors:
            a = index[(task, method + '_original', v['id'])]
            b = index[(task, method + '_manual_guard', v['id'])]
            if v['kind'] in ('original_pair', 'documented_rule', 'engineering_trust_control'):
                ck(task + '/' + method + '/' + v['id'] + '/normal_behavior_preserved', a['decision'] == b['decision'] == v['expected'])
        targets = ['missing-trusted'] + (['held-empty-type', 'held-unknown-type'] if task == 'FSV-B19' else [])
        for probe in targets:
            ck(task + '/' + method + '/' + probe + '/manual_guard_closes_observed_allow', index[(task, method + '_original', probe)]['decision'] == 'allow' and index[(task, method + '_manual_guard', probe)]['decision'] == 'deny')

for probe in ('partial-status-false-only', 'partial-payments-only'):
    for arm in {r['arm'] for r in rows if r['task'] == 'FSV-B19' and r['method'] == 'ECAS'}:
        ck('B19/' + arm + '/' + probe + '/allow_observation_without_gold', index[('FSV-B19', arm, probe)]['decision'] == 'allow' and index[('FSV-B19', arm, probe)]['historical_expected'] is None)
    for method in ('P2P_STYLE', 'AUTOPAC_STYLE'):
        ck('B19/' + method + '/partial_false_only_guard_keeps_allow', index[('FSV-B19', method + '_manual_guard', 'partial-status-false-only')]['decision'] == 'allow')
        ck('B19/' + method + '/partial_payments_only_guard_deny_observation', index[('FSV-B19', method + '_manual_guard', 'partial-payments-only')]['decision'] == 'deny')

failure = [c for c in checks if not c['pass']]
receipt = {'status': 'PASS' if not failure else 'FAIL', 'date': '2026-10-15',
    'classification': 'INDEPENDENT_STATIC_RECONCILIATION_WITH_ALL_RAW_CAPTURES_NO_POLICY_REEXECUTION',
    'check_count': len(checks), 'failures': failure, 'checks': checks,
    'new_model_calls': 0, 'new_policy_executions': 0, 'observed_rows_reconciled': 144,
    'independent_sample_count': 'NOT_144_TWO_EXISTING_TASKS_AND_RELATED_PROBES',
    'findings': [
        'Full and shape have identical policy and output for all 18 frozen inputs, both original and skip variants.',
        'Changing only on_missing to skip still admits through full contract and permits both empty-state probes.',
        'Separate manual typed guards close all observed baseline empty/unknown-state allows while preserving documented normal decisions.',
        'B19 original ECAS allows Payments-only state with supplierOnHold absent; observed without normative gold.',
        'This does not establish source authenticity, runtime-state attestation, real API attacks, native baseline performance, or uniqueness.'
    ],
    'artifacts': [{'path': str(ROOT / name), 'sha256': sha(ROOT / name)} for name in ['RESULTS.json', 'OBSERVATIONS.csv', 'FROZEN_VECTORS.json', 'INPUT_MANIFEST.json', 'SOURCE_MANIFEST.json', 'mechanism_probe.py']]}
(ROOT.parent / 'MECHANISM_INDEPENDENT_AUDIT.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': receipt['status'], 'checks': len(checks), 'failures': failure, 'reconciled_existing_rows': 144, 'new_policy_executions': 0}))
