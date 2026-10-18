"""Independent read-only audit. Does not import or execute source/probe/engine/OPA."""
import ast
import copy
import csv
import datetime as dt
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LANE = Path('/root/ecas_source_rule_chain_20261015')
RUN = LANE / 'managed_runs/source-rule-chain-main-v1'
DAY = dt.date(2026, 10, 15)
ARMS = ('raw', 'saved', 'effective_manual')
METHODS = ('ECAS_MATCHED', 'P2P_STYLE', 'AUTOPAC_STYLE')
CHECKS = []


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(name, passed, detail=None):
    CHECKS.append({'check': name, 'pass': bool(passed), 'detail': detail})
    if not passed:
        raise AssertionError(name)


def fn_node(path, cls, name):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    classes = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == cls]
    check(f'one_class_{cls}', len(classes) == 1)
    functions = [x for x in classes[0].body if isinstance(x, ast.FunctionDef) and x.name == name]
    check(f'one_method_{cls}_{name}', len(functions) == 1 and not functions[0].decorator_list)
    return functions[0]


def normalized(v):
    return {
        'on_hold': v['on_hold'],
        'hold_type': (v['hold_type'] or 'All') if v['on_hold'] else '',
        'release_date': v['release_date'] if v['on_hold'] else '',
    }


def hold_check(v):
    s = normalized(v)
    active = not s['release_date'] or dt.date.fromisoformat(s['release_date']) >= DAY
    return 'deny' if s['on_hold'] and s['hold_type'] in ('All', 'Invoices') and active else 'allow'


def expected_envelope(v, arm):
    s = {k: v[k] for k in ('on_hold', 'hold_type', 'release_date')} if arm == 'raw' else normalized(v)
    if arm == 'effective_manual' and s['release_date'] and dt.date.fromisoformat(s['release_date']) < DAY:
        s['on_hold'] = False
    return {'request': {'body': {'action': 'PURCHASE_ORDER', 'supplier': 'SUPPLIER-SYNTH-1'}},
            'trusted': {'supplierOnHold': s['on_hold'], 'holdType': s['hold_type']}}


def policy_formula(method, envelope):
    held, kind = envelope['trusted']['supplierOnHold'], envelope['trusted']['holdType']
    allow = (not held or kind == 'Payments') if method == 'ECAS_MATCHED' else not (held and kind in ('Invoices', 'All'))
    return 'allow' if allow else 'deny'


def main():
    status = read(RUN / 'status.json')
    check('actual_managed_main_succeeded', status['state'] == 'SUCCEEDED' and status['exit_code'] == 0)
    result_path = ROOT / 'RESULTS.json'
    result = read(result_path)
    managed_path = RUN / 'outputs/result.json'
    check('scope_result_matches_managed_bytes', sha(result_path) == sha(managed_path) == status['outputs'][0]['sha256'])
    check('completed_scope_identity', result['status'] == 'COMPLETED' and result['scope_id'] == 'ECAS-SOURCE-RULE-CHAIN-20261015-01')
    check('no_model_new_cases', result['new_model_calls'] == result['new_cases'] == 0)
    for entry in read(ROOT / 'INPUT_MANIFEST.json'):
        check('frozen_input_hash:' + entry['path'], sha(entry['path']) == entry['sha256'])
    for entry in read(ROOT / 'SOURCE_MANIFEST.json'):
        check('source_snapshot_hash:' + entry['snapshot'], sha(entry['source']) == sha(entry['snapshot']) == entry['sha256'])
    before, after = read(RUN / 'inputs.before.json'), read(RUN / 'inputs.after.json')
    check('managed_before_after_input_hashes_identical', before == after)
    for entry in after:
        check('managed_input_current_hash:' + entry['path'], sha(entry['path']) == entry['sha256'])
    t0_status = read(LANE / 'managed_runs/source-rule-chain-t0-v1/status.json')
    check('actual_t0_succeeded', t0_status['state'] == 'SUCCEEDED' and t0_status['exit_code'] == 0)
    t0 = read(ROOT / 'T0_RECEIPT.json')
    check('t0_checks_all_observed_pass', t0['status'] == 'PASS' and len(t0['checks']) == 18 and all(x['pass'] for x in t0['checks']))
    gate = read(ROOT / 'SCOPED_GATE_READY.json')
    check('formal_gate_ready_without_blockers', gate['data']['ready_for_formal_run'] and not gate['data']['blockers'])

    source_refs = {}
    for filename, cls, name in (('supplier.py', 'Supplier', 'before_save'),
                                ('accounts_controller.py', 'AccountsController', 'ensure_supplier_is_not_blocked')):
        snapshot = ROOT / 'inputs' / filename
        node = fn_node(snapshot, cls, name)
        source_refs[name] = {
            'source': str(snapshot), 'class': cls, 'function': name,
            'line_start': node.lineno, 'line_end': node.end_lineno,
            'ast_sha256': hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(),
        }
    source_function = [x for x in ast.parse((ROOT / 'source_chain_probe.py').read_text(encoding='utf-8')).body
                       if isinstance(x, ast.FunctionDef) and x.name == 'source_function'][0]
    check('extraction_static_no_AST_rewrite',
          'fn = copy.deepcopy(functions[0])' in ast.unparse(source_function)
          and "ast.Module(body=[fn], type_ignores=[])" in ast.unparse(source_function)
          and len([x for x in ast.walk(source_function) if isinstance(x, ast.Assign) and
                   any(isinstance(t, ast.Attribute) for t in x.targets)]) == 0)

    frozen = read(ROOT / 'FROZEN_VECTORS.json')
    expected_vectors = [{'id': f'state-{i:02}', 'on_hold': h, 'hold_type': k, 'release_date': d}
                        for i, (h, k, d) in enumerate(itertools.product(
                            (False, True), ('', 'All', 'Invoices', 'Payments'),
                            ('', '2026-10-14', '2026-10-15', '2026-10-16')), 1)]
    check('frozen_complete_32_grid', frozen['fixed_today'] == DAY.isoformat() and frozen['vectors'] == expected_vectors)
    vectors = {v['id']: v for v in frozen['vectors']}
    check('source_rows_exact_32_unique', len(result['source_rows']) == 32 and
          {x['state_id'] for x in result['source_rows']} == set(vectors))
    for row in result['source_rows']:
        v = vectors[row['state_id']]
        check('source_before_identity:' + row['state_id'], row['before'] == v)
        check('source_normalized_state:' + row['state_id'], row['after_before_save'] == normalized(v))
        check('source_and_frozen_oracle:' + row['state_id'], row['source_decision'] == row['frozen_oracle'] == hold_check(v))
        check('complete_source_AST_identity:' + row['state_id'],
              row['source_function_refs'] == [source_refs['before_save'], source_refs['ensure_supplier_is_not_blocked']])
    check('today_inclusive_source_boundary', all(
        x['source_decision'] == ('deny' if x['before']['hold_type'] in ('', 'All', 'Invoices') else 'allow')
        for x in result['source_rows'] if x['before']['on_hold'] and x['before']['release_date'] == DAY.isoformat()))

    rows = result['rows']
    keys = [(x['state_id'], x['arm'], x['method']) for x in rows]
    expected_keys = set(itertools.product(vectors, ARMS, METHODS))
    check('policy_288_identity_unique_complete', len(rows) == len(set(keys)) == 288 and set(keys) == expected_keys)
    packet = read(ROOT / 'inputs/packet.json')
    stats = {arm: {method: Counter() for method in METHODS} for arm in ARMS}
    opa_rows = 0
    for row in rows:
        sid, arm, method = row['state_id'], row['arm'], row['method']
        key = f'{sid}/{arm}/{method}'
        v = vectors[sid]
        envelope = expected_envelope(v, arm)
        check('same_arm_input:' + key, row['envelope'] == envelope)
        check('manual_arm_label:' + key, row['manual_adapter'] is (arm == 'effective_manual'))
        check('source_label_and_agreement:' + key, row['source_decision'] == hold_check(v)
              and row['agrees'] is (row['decision'] == row['source_decision']))
        check('independent_policy_formula:' + key, row['decision'] == policy_formula(method, envelope))
        observation_path = LANE / 'results' / arm / method / (sid + '.observation.json')
        check('observation_file_equals_row:' + key, read(observation_path) == row)
        if method == 'ECAS_MATCHED':
            raw = row['actual_ecas_output']
            check('ecas_actual_output_qualified:' + key, raw['decision'] == row['decision']
                  and not raw.get('engine_error') and raw['fail_closed'] is True)
        else:
            opa_rows += 1
            stem = LANE / 'results' / arm / method / sid
            opa_input = read(str(stem) + '.input.json')
            expected = copy.deepcopy(envelope)
            abi = packet['common_adapter']
            expected.update(subject={'id': abi['subject_id'], 'role': abi['subject_role']},
                            action=packet['target']['operation'],
                            resource={'id': abi['resource_id'], 'system': packet['target']['system'],
                                      'version': packet['target']['version']})
            check('opa_actual_input_equivalence:' + key, opa_input == expected)
            stdout = read(str(stem) + '.stdout.json')
            values = [x['value'] for r in stdout.get('result', []) for x in r.get('expressions', [])]
            check('opa_raw_stdout_reconciled:' + key, len(values) == 1 and isinstance(values[0], bool)
                  and ('allow' if values[0] else 'deny') == row['decision'])
            check('opa_no_stderr:' + key, Path(str(stem) + '.stderr.txt').read_text(encoding='utf-8') == '')
        stat = stats[arm][method]
        stat['total'] += 1
        stat['agrees' if row['agrees'] else 'disagrees'] += 1
        if row['decision'] == 'deny' and row['source_decision'] == 'allow':
            stat['over_reject'] += 1
        if row['decision'] == 'allow' and row['source_decision'] == 'deny':
            stat['miss_reject'] += 1
    check('exact_192_OPA_raw_outputs', opa_rows == 192)
    expected_stats = {
        'raw': {'ECAS_MATCHED': (29, 3, 0), 'P2P_STYLE': (27, 2, 3), 'AUTOPAC_STYLE': (27, 2, 3)},
        'saved': {m: (29, 3, 0) for m in METHODS},
        'effective_manual': {m: (32, 0, 0) for m in METHODS},
    }
    for arm in ARMS:
        for method in METHODS:
            s = stats[arm][method]
            check('summary_reconciled:' + arm + '/' + method,
                  (s['agrees'], s['over_reject'], s['miss_reject']) == expected_stats[arm][method])
    old_policy = ROOT.parents[0] / '20261014_matched_evidence_labor/matched_generation/method_runs/FSV-B19/ECAS_MATCHED/initial/admitted_policy.json'
    check('original_admitted_ECAS_policy_unchanged', read(LANE / 'results/admitted_policy.json') == read(old_policy))
    with (ROOT / 'OBSERVATIONS.csv').open(encoding='utf-8-sig', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    check('CSV_exact_288_rows', len(csv_rows) == len(rows) == 288)
    for a, b in zip(csv_rows, rows):
        check('CSV_row:' + a['state_id'] + '/' + a['arm'] + '/' + a['method'],
              all(a[k] == str(b[k]) for k in a))
    report = {
        'audit_id': 'ECAS-SOURCE-PROBE-INDEPENDENT-AUDIT-20261015-01',
        'status': 'PASS_WITH_EXPLICIT_SCOPE_LIMITS',
        'procedure': 'Independent stdlib file/hash/AST and archived-output audit. No import or execution of source, engine, frozen probe or OPA.',
        'new_model_calls': 0, 'new_policy_executions': 0, 'new_source_function_executions': 0,
        'source_states': 32, 'policy_rows': 288, 'opa_raw_outputs': opa_rows,
        'result_sha256': sha(result_path), 'frozen_probe_sha256': sha(ROOT / 'source_chain_probe.py'),
        'managed_status_sha256': sha(RUN / 'status.json'),
        'source_function_refs': source_refs, 'stats': stats, 'checks': CHECKS,
        'limits': [
            'One B19 case, 32 manual related states and 288 correlated policy observations; no new sample or model accuracy estimate.',
            'Source allow means only this supplier hold check did not block; it is not full Purchase Order acceptance.',
            'AST body copied completely, but class/container and application callback execution were not run. Normal callback order supported only by separate static source audit.',
            'Frappe single-Supplier lookup, date and exception interfaces are stubs; database, cache, hooks, authentication, freshness, API forwarding and production reachability unverified.',
            'raw intentionally includes pre-save and inconsistent states; it cannot represent normal saved Supplier state or prove production vulnerability.',
            'saved retains raw on_hold after normalization and omits release_date from gateway ABI. Effective-state production mapping is unknown.',
            'effective_manual is a manually added expiry projection applied identically to all methods; its gains are engineering integration gains, not model extraction or an existing deployed ECAS adapter.',
            'Local bounded source oracle was specified before this grid run but after historical cases/results were exposed. It is not an independent blind benchmark.',
            'The grid diagnoses adapter and expiry semantics beyond the focused original hold-type task; it must not retroactively change original task labels or count as independent semantic accuracy.',
        ],
    }
    (ROOT / 'PROBE_INDEPENDENT_AUDIT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'checks': len(CHECKS), 'stats': stats,
                      'result_sha256': report['result_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
