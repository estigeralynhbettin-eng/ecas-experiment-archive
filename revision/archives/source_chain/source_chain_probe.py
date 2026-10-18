"""Frozen source-function/adapter experiment. No model, network, service or production API."""
import ast
import copy
import csv
import datetime as dt
import hashlib
import io
import itertools
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
MAIN = PROJECT / 'working/exploration/20261014_matched_evidence_labor/matched_generation'
LANE = Path('/root/ecas_source_rule_chain_20261015')
ERP = Path('/mnt/d/lunwen/ec/runtime/erpnext_qualification/erpnext-v16.0.0/erpnext-16.0.0/erpnext')
SCOPE = 'ECAS-SOURCE-RULE-CHAIN-20261015-01'
DAY = dt.date(2026, 10, 15)
ARMS = ('raw', 'saved', 'effective_manual')
METHODS = ('ECAS_MATCHED', 'P2P_STYLE', 'AUTOPAC_STYLE')


def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def dump(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def csvtext(rows, fields):
    f = io.StringIO(newline=''); w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    w.writeheader(); w.writerows(rows); return f.getvalue()


def verify():
    for entry in read(ROOT / 'INPUT_MANIFEST.json'):
        if sha(entry['path']) != entry['sha256']: raise RuntimeError('Input drift: ' + entry['path'])
    for entry in read(ROOT / 'SOURCE_MANIFEST.json'):
        if sha(entry['source']) != entry['sha256'] or sha(entry['snapshot']) != entry['sha256']:
            raise RuntimeError('Source/snapshot drift: ' + entry['source'])


def engine():
    sys.path.insert(0, str(LANE / 'runtime/scripts'))
    import ec_field_security_engine_v3 as e
    return e


def source_function(file, cls, name, namespace):
    text = file.read_text(encoding='utf-8')
    tree = ast.parse(text)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls]
    assert len(classes) == 1
    functions = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(functions) == 1 and not functions[0].decorator_list
    fn = copy.deepcopy(functions[0])
    # The original complete function body is compiled unchanged; only its class container is omitted.
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(file), 'exec'), namespace)
    return namespace[name], {'source': str(file), 'class': cls, 'function': name,
                            'line_start': fn.lineno, 'line_end': fn.end_lineno,
                            'ast_sha256': hashlib.sha256(ast.dump(fn, include_attributes=False).encode()).hexdigest()}


class SourceBlocked(Exception): pass


def supplier(v):
    return SimpleNamespace(on_hold=v['on_hold'], hold_type=v['hold_type'],
                           release_date=dt.date.fromisoformat(v['release_date']) if v['release_date'] else '')


def state(obj):
    return {'on_hold': obj.on_hold, 'hold_type': obj.hold_type,
            'release_date': obj.release_date.isoformat() if isinstance(obj.release_date, dt.date) else obj.release_date}


def saved_source(v):
    obj = supplier(v)
    save, save_ref = source_function(ROOT / 'inputs/supplier.py', 'Supplier', 'before_save', {})
    save(obj)
    def msgprint(message, raise_exception=0):
        if raise_exception: raise SourceBlocked(message)
        raise RuntimeError('Unexpected nonblocking msgprint')
    namespace = {'frappe': SimpleNamespace(get_lazy_doc=lambda doctype, name: obj, msgprint=msgprint),
                 '_': lambda s: s, 'getdate': lambda x: dt.date.fromisoformat(x) if isinstance(x, str) else x,
                 'nowdate': lambda: DAY.isoformat()}
    check, check_ref = source_function(ROOT / 'inputs/accounts_controller.py', 'AccountsController',
                                        'ensure_supplier_is_not_blocked', namespace)
    target = SimpleNamespace(doctype='Purchase Order', supplier='SUPPLIER-SYNTH-1', party_type='', party='')
    try:
        check(target); decision = 'allow'
    except SourceBlocked:
        decision = 'deny'
    return state(obj), decision, [save_ref, check_ref]


def source_oracle(v):
    # Independently specified in PROTOCOL_CN.md before running the state grid.
    held = v['on_hold']; kind = (v['hold_type'] or 'All') if held else ''
    active = not v['release_date'] or DAY <= dt.date.fromisoformat(v['release_date'])
    return 'deny' if held and kind in ('All', 'Invoices') and active else 'allow'


def envelope(raw, saved, arm):
    s = copy.deepcopy(raw if arm == 'raw' else saved)
    if arm == 'effective_manual' and s['release_date'] and dt.date.fromisoformat(s['release_date']) < DAY:
        s['on_hold'] = False
    return {'request': {'body': {'action': 'PURCHASE_ORDER', 'supplier': 'SUPPLIER-SYNTH-1'}},
            'trusted': {'supplierOnHold': s['on_hold'], 'holdType': s['hold_type']}}


def rego(method, inp, folder, key):
    packet = read(ROOT / 'inputs/packet.json'); abi = packet['common_adapter']; inp = copy.deepcopy(inp)
    inp.update(subject={'id': abi['subject_id'], 'role': abi['subject_role']}, action=packet['target']['operation'],
               resource={'id': abi['resource_id'], 'system': packet['target']['system'], 'version': packet['target']['version']})
    folder.mkdir(parents=True, exist_ok=True); ipath = folder / (key + '.input.json'); dump(ipath, inp)
    cmd = [str(LANE / 'tools/opa'), 'eval', '--format=json', '--capabilities', str(ROOT / 'inputs/restricted_capabilities.json'),
           '--data', str(ROOT / 'inputs' / (method + '.rego')), '--input', str(ipath), 'data.external_pilot.allow']
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=30)
    (folder / (key + '.stdout.json')).write_text(p.stdout, encoding='utf-8')
    (folder / (key + '.stderr.txt')).write_text(p.stderr, encoding='utf-8')
    if p.returncode: raise RuntimeError('OPA failed: ' + key)
    values = [x['value'] for r in json.loads(p.stdout).get('result', []) for x in r.get('expressions', [])]
    if len(values) != 1 or not isinstance(values[0], bool): raise RuntimeError('Invalid Boolean output')
    return 'allow' if values[0] else 'deny'


def prepare():
    if (ROOT / 'INPUT_MANIFEST.json').exists(): raise RuntimeError('Already frozen; no overwrite')
    LANE.mkdir(parents=True, exist_ok=False)
    shutil.copytree('/root/ecas_matched_generation_20261014/runtime', LANE / 'runtime', ignore=shutil.ignore_patterns('__pycache__'))
    (LANE / 'tools').mkdir(); shutil.copyfile('/root/ecas_matched_generation_20261014/tools/opa', LANE / 'tools/opa')
    (LANE / 'tools/opa').chmod(0o755)
    sources = []
    def snap(source, target):
        source = Path(source); target = ROOT / 'inputs' / target; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target); sources.append({'source': str(source), 'snapshot': str(target), 'sha256': sha(source)})
    snap(ERP / 'buying/doctype/supplier/supplier.py', 'supplier.py')
    snap(ERP / 'controllers/accounts_controller.py', 'accounts_controller.py')
    snap(MAIN / 'generation_inputs/FSV-B19/packet.json', 'packet.json')
    snap(MAIN / 'execution_inputs/FSV-B19/contract.json', 'contract.json')
    snap(MAIN / 'method_runs/FSV-B19/ECAS_MATCHED/first_candidate.json', 'candidate.json')
    for m in ('P2P_STYLE', 'AUTOPAC_STYLE'):
        snap(MAIN / 'method_runs/FSV-B19' / m / 'initial/external_pilot/policy.rego', m + '.rego')
    snap('/root/ecas_matched_generation_20261014/outputs/t0/restricted_capabilities.json', 'restricted_capabilities.json')
    for f in ('RESULT_TRACEABILITY.csv', 'CLAIM_EVIDENCE_MATRIX.csv'):
        header = (PROJECT / f).read_text(encoding='utf-8-sig').splitlines()[0]
        (ROOT / f).write_text(header + '\n', encoding='utf-8-sig')
    vectors = [{'id': f'state-{i:02}', 'on_hold': held, 'hold_type': kind, 'release_date': date}
               for i, (held, kind, date) in enumerate(itertools.product((False, True), ('', 'All', 'Invoices', 'Payments'),
                    ('', '2026-10-14', '2026-10-15', '2026-10-16')), 1)]
    dump(ROOT / 'FROZEN_VECTORS.json', {'fixed_today': DAY.isoformat(), 'vectors': vectors, 'classification': 'MANUAL_RELATED_SOURCE_STATE_GRID'})
    dump(ROOT / 'SOURCE_MANIFEST.json', sources)
    dump(ROOT / 'EXPERIMENT_SCOPE.json', {'kind': 'new-experiment-block', 'status': 'FROZEN',
         'protocol_path': 'PROTOCOL_CN.md', 'protocol_sha256': sha(ROOT / 'PROTOCOL_CN.md'), 'scope_id': SCOPE,
         'project_id': 'EC-CSI', 'experiment_id': 'source-rule-chain', 'runtime_lane': str(LANE),
         'classification': 'SOURCE_FUNCTION_WITH_STUBS_AND_MANUAL_ADAPTER_NOT_PRODUCTION', 'new_model_calls': 0,
         'new_cases': 0, 'new_systems': 0})
    paths = [ROOT / f for f in ('source_chain_probe.py', 'TASK_CONTRACT_CN.md', 'PROTOCOL_CN.md', 'FROZEN_VECTORS.json', 'SOURCE_MANIFEST.json', 'EXPERIMENT_SCOPE.json')]
    paths += [p for p in (ROOT / 'inputs').rglob('*') if p.is_file()]
    paths += [p for sub in ('runtime', 'tools') for p in (LANE / sub).rglob('*') if p.is_file()]
    dump(ROOT / 'INPUT_MANIFEST.json', [{'path': str(p), 'sha256': sha(p)} for p in sorted(set(paths))])
    request('t0'); print(json.dumps({'status': 'FROZEN', 'states': len(vectors), 'new_model_calls': 0}))


def request(mode):
    if mode == 'run':
        gate = read(ROOT / 'SCOPED_GATE_READY.json')
        if not gate['data']['ready_for_formal_run'] or gate['data']['blockers']: raise RuntimeError('Scope gate blocked')
    inputs = read(ROOT / 'INPUT_MANIFEST.json') + [{'path': str(ROOT / 'INPUT_MANIFEST.json'), 'sha256': sha(ROOT / 'INPUT_MANIFEST.json')}]
    if mode == 'run': inputs += [{'path': str(ROOT / f), 'sha256': sha(ROOT / f)} for f in ('T0_RECEIPT.json', 'T0_EVIDENCE.json', 'SCOPED_GATE_READY.json')]
    dump(ROOT / ('T0_REQUEST.json' if mode == 't0' else 'RUN_REQUEST.json'), {
        'schema_version': 1, 'run_id': 'source-rule-chain-' + ('t0-v1' if mode == 't0' else 'main-v1'),
        'run_root': str(LANE / 'managed_runs'), 'argv': ['/usr/bin/python3', str(ROOT / 'source_chain_probe.py'), mode, '{run_dir}/outputs/result.json'],
        'cwd': str(ROOT), 'inputs': inputs, 'outputs': [{'path': 'outputs/result.json', 'kind': 'json', 'nonempty': True,
        'required_keys': ['status', 'checks'] if mode == 't0' else ['status', 'rows', 'source_rows', 'new_model_calls']}],
        'timeout_seconds': 600, 'authorization_ref': 'Current user: advance the two selected source-to-rule-chain statements; TASK_CONTRACT_CN.md; zero model calls'})


def ledger_row(result_id, metric, count, file, locator, kind):
    ledger = ROOT / 'RESULT_TRACEABILITY.csv'
    with ledger.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; rows = list(reader)
    if any(r['result_id'] == result_id for r in rows): raise RuntimeError('Duplicate result registration')
    rows.append({'result_id': result_id, 'experiment_id': SCOPE, 'metric_name': metric, 'dataset_name': 'FSV-B19_source_state_grid',
         'dataset_version': 'frozen-v1', 'data_split': kind, 'sample_count': count, 'raw_value': count, 'reported_value': count,
         'unit': 'related_observations_or_engineering_checks', 'aggregation': 'not_independent_cases_or_model_accuracy',
         'source_output_path': str(file.relative_to(PROJECT)), 'source_locator': locator,
         'script_path': str(Path(__file__).relative_to(PROJECT)), 'command_or_config': 'PROTOCOL_CN.md;RUN_REQUEST.json',
         'seed': 'NOT_APPLICABLE', 'environment': 'WSL Python OPA; source functions with stubs; isolated lane',
         'git_commit': 'NOT_AVAILABLE_HASH_FROZEN', 'checksum': sha(file), 'rounding_rule': 'none', 'status': 'PASS',
         'verified_by': 'actual_source_function_and_policy_execution', 'verified_at': now(), 'notes': 'No model or production execution; manual effective adapter explicitly separate'})
    ledger.write_text(csvtext(rows, fields), encoding='utf-8-sig')


def t0(output):
    verify(); checks = []
    def ck(n, b): checks.append({'check': n, 'pass': bool(b)})
    for date, expected in (('', 'deny'), ('2026-10-14', 'allow'), ('2026-10-15', 'deny'), ('2026-10-16', 'deny')):
        s, decision, refs = saved_source({'on_hold': True, 'hold_type': '', 'release_date': date})
        ck('source_empty_defaults_all_' + date, s['hold_type'] == 'All')
        ck('source_date_boundary_' + date, decision == expected)
    s, d, refs = saved_source({'on_hold': False, 'hold_type': 'Invoices', 'release_date': '2026-10-16'})
    ck('source_unheld_clears_type_and_date', s['hold_type'] == s['release_date'] == '' and d == 'allow')
    e = engine(); c = read(ROOT / 'inputs/contract.json'); cand = read(ROOT / 'inputs/candidate.json')
    proposal = e.compile_model_ir(cand); policy = e.compile_policy(proposal['policy'], c)
    ck('original_ir_full_admitted', bool(policy))
    bad = copy.deepcopy(c); bad['evidence'] = []
    rejected = False
    try: e.compile_policy(proposal['policy'], bad)
    except Exception: rejected = True
    ck('missing_evidence_rejected', rejected)
    inp = envelope({'on_hold': False, 'hold_type': '', 'release_date': ''}, {}, 'raw')
    ck('ecas_execution_allow', e.evaluate(policy, c, inp, admission_mode='semantic')['decision'] == 'allow')
    for method in ('P2P_STYLE', 'AUTOPAC_STYLE'):
        ck(method + '_OPA_allow', rego(method, inp, LANE / 't0', method) == 'allow')
    ck('frozen_32_states', len(read(ROOT / 'FROZEN_VECTORS.json')['vectors']) == 32)
    ck('space_at_least_1GiB', shutil.disk_usage(LANE).free >= 1024**3)
    ck('no_network_library_imports', not any(isinstance(n, (ast.Import, ast.ImportFrom)) and
       any(a.name.split('.')[0] in ('requests', 'urllib', 'http', 'socket') for a in n.names) for n in ast.walk(ast.parse(Path(__file__).read_text(encoding='utf-8')))))
    audit = subprocess.run(['ps', '-eo', 'pid,ppid,comm,args'], capture_output=True, text=True, timeout=20)
    (LANE / 't0/process_inventory.txt').write_text(audit.stdout, encoding='utf-8')
    ck('process_inventory_collected', audit.returncode == 0)
    receipt = {'status': 'PASS' if all(x['pass'] for x in checks) else 'FAIL', 'scope_id': SCOPE,
       'run_id': 'source-rule-chain-t0-v1', 'checks': checks, 'runtime_lane': str(LANE), 'source_functions': refs,
       'completed_at': now(), 'uid': os.getuid(), 'scientific_result': False, 'new_model_calls': 0}
    dump(ROOT / 'T0_RECEIPT.json', receipt); dump(output, receipt)
    dump(ROOT / 'T0_EVIDENCE.json', {'status': receipt['status'], 'scope_id': SCOPE, 'run_id': receipt['run_id'],
         'runtime_lane': str(LANE), 'receipt_path': 'T0_RECEIPT.json', 'receipt_sha256': sha(ROOT / 'T0_RECEIPT.json'), 'completed_at': receipt['completed_at']})
    if receipt['status'] != 'PASS': raise RuntimeError('T0 failed')
    ledger_row('SOURCE-CHAIN-T0', 'engineering_checks', len(checks), ROOT / 'T0_RECEIPT.json', 'checks', 'engineering_only')


def run(output):
    verify()
    if (ROOT / 'RESULTS.json').exists(): raise RuntimeError('Existing result; never rerun automatically')
    gate = read(ROOT / 'SCOPED_GATE_READY.json')
    if not gate['data']['ready_for_formal_run'] or gate['data']['blockers']: raise RuntimeError('Scope gate blocked')
    e = engine(); contract = read(ROOT / 'inputs/contract.json'); candidate = read(ROOT / 'inputs/candidate.json')
    policy = e.compile_policy(e.compile_model_ir(candidate)['policy'], contract)
    folder = LANE / 'results'; folder.mkdir(exist_ok=False)
    dump(folder / 'admitted_policy.json', policy)
    source_rows, rows = [], []
    for v in read(ROOT / 'FROZEN_VECTORS.json')['vectors']:
        saved, source_decision, refs = saved_source(v)
        expected = source_oracle(v)
        if source_decision != expected: raise RuntimeError('Frozen source oracle disagreement: ' + v['id'])
        source_rows.append({'state_id': v['id'], 'before': v, 'after_before_save': saved, 'source_decision': source_decision,
                            'frozen_oracle': expected, 'source_function_refs': refs})
        for arm in ARMS:
            inp = envelope(v, saved, arm)
            for method in METHODS:
                raw = None
                if method == 'ECAS_MATCHED':
                    raw = e.evaluate(policy, contract, inp, admission_mode='semantic'); decision = raw.get('decision')
                    if raw.get('engine_error') or decision not in ('allow', 'deny'): raise RuntimeError('ECAS runtime error')
                else: decision = rego(method, inp, folder / arm / method, v['id'])
                row = {'state_id': v['id'], 'arm': arm, 'method': method, 'source_decision': source_decision,
                       'decision': decision, 'agrees': decision == source_decision, 'envelope': inp,
                       'manual_adapter': arm == 'effective_manual', 'actual_ecas_output': raw}
                rows.append(row); dump(folder / arm / method / (v['id'] + '.observation.json'), row)
    assert len(rows) == 288 and len(source_rows) == 32
    verify()
    result = {'status': 'COMPLETED', 'scope_id': SCOPE, 'classification': 'POSTHOC_SOURCE_FUNCTION_ADAPTER_PROBE_NOT_PRODUCTION',
              'source_rows': source_rows, 'rows': rows, 'new_model_calls': 0, 'new_cases': 0,
              'policy_observations': len(rows), 'related_source_states': len(source_rows), 'completed_at': now()}
    dump(ROOT / 'RESULTS.json', result); dump(output, result)
    fields = ['state_id', 'arm', 'method', 'source_decision', 'decision', 'agrees', 'manual_adapter']
    (ROOT / 'OBSERVATIONS.csv').write_text(csvtext(rows, fields), encoding='utf-8-sig')
    ledger_row('SOURCE-CHAIN-SOURCE-STATES', 'source_function_states', 32, ROOT / 'RESULTS.json', 'source_rows', 'posthoc_related_states')
    ledger_row('SOURCE-CHAIN-POLICY-OBSERVATIONS', 'policy_observations', 288, ROOT / 'RESULTS.json', 'rows', 'posthoc_related_states')
    print(json.dumps({'status': 'COMPLETED', 'source_states': 32, 'policy_observations': 288, 'new_model_calls': 0}))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'prepare': prepare()
    elif mode == 'make-request': request('run')
    elif mode == 't0': t0(Path(sys.argv[2]))
    elif mode == 'run': run(Path(sys.argv[2]))
    else: raise ValueError(mode)
