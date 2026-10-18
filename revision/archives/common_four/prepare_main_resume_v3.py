"""Zero-network continuation preparation for OPA comment-location metadata."""
import copy
import json
import shutil
from pathlib import Path
from pilot_lib import ROOT, CONFIG, read, dump, sha

snapshot = ROOT / 'setup_history/as_run_main_resume_v2'
if snapshot.exists():
    raise RuntimeError('Existing recovery snapshot: inspect instead of repeating preparation')
state = read(ROOT / 'EXECUTION_STATE.json')
ledger = read(ROOT / 'CALL_LEDGER.json')
if state['status'] != 'STOPPED_PROTOCOL_OR_TRANSPORT' or state['final_evaluation_read'] is not False:
    raise RuntimeError('Only the explicit pre-evaluation stop can be continued')
if state['error'] != 'OPA fmt changed AST semantics; stop instead of model repair' or len(ledger) != 15:
    raise RuntimeError('Unexpected error or actual attempt count')
for item in ledger:
    if item['status'] != 'COMPLETED' or any(sha(item[p]) != item[h] for p, h in [
        ('raw_response_path', 'raw_response_sha256'), ('prompt_path', 'prompt_sha256'), ('output_path', 'output_sha256')]):
        raise RuntimeError('All fifteen immutable responses must be complete')
paths = [p for p in ROOT.glob('*') if p.is_file()]
paths += [p for p in (ROOT / 'method_runs').rglob('*') if p.is_file()]
rows = []
for path in paths:
    target = snapshot / path.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    rows.append({'original_path': str(path), 'snapshot_path': str(target), 'sha256': sha(target)})
dump(snapshot / 'SNAPSHOT_RECEIPT.json', {'status': 'AS_RUN_FAILURE_PRESERVED', 'files': rows,
     'main_run_id': 'matched-generation-main-resume-v2', 'actual_paid_attempts': 15, 'final_evaluation_read': False})

folder = ROOT / 'method_runs/FSV-B13/AUTOPAC_STYLE/initial'
before, after = read(folder / 'ast_before.stdout.txt'), read(folder / 'ast_after.stdout.txt')
def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items() if k not in ('location', 'Location')}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value
if normalized(before) != normalized(after):
    raise RuntimeError('Formatting has a non-location AST difference')
dump(ROOT / 'OPA_COMMENT_LOCATION_ACCEPTANCE_V3.json', {'classification': 'OPA_AST_LOCATION_METADATA_ONLY',
     'scope_id': CONFIG['scope_id'], 'original_ast_sha256': sha(folder / 'ast_before.stdout.txt'),
     'formatted_ast_sha256': sha(folder / 'ast_after.stdout.txt'),
     'normalized_ast_equal': True, 'ignored_metadata_fields': ['location', 'Location'],
     'business_fields_changed': False, 'new_API_calls': 0, 'final_evaluation_read': False})

def replace_exact(name, old, new, count):
    path = ROOT / name
    value = path.read_text(encoding='utf-8')
    if value.count(old) != count:
        raise RuntimeError('Unexpected source shape: ' + name)
    path.write_text(value.replace(old, new), encoding='utf-8')

replace_exact('pilot_lib.py', "if k != 'location'", "if k not in ('location', 'Location')", 1)
replace_exact('run_matched.py', 'MAIN_RESUME_AUTHORIZATION_V2.json', 'MAIN_RESUME_AUTHORIZATION_V3.json', 2)
replace_exact('run_t0.py', 'MAIN_RESUME_AUTHORIZATION_V2.json', 'MAIN_RESUME_AUTHORIZATION_V3.json', 1)
replace_exact('freeze.py', "'prepare_main_resume_v2.py','MAIN_RESUME_AUTHORIZATION_V2.json','SOURCE_REFERENCE_ACCEPTANCE_V2.json'",
              "'prepare_main_resume_v2.py','MAIN_RESUME_AUTHORIZATION_V2.json','SOURCE_REFERENCE_ACCEPTANCE_V2.json',\n                 'prepare_main_resume_v3.py','MAIN_RESUME_AUTHORIZATION_V3.json','OPA_COMMENT_LOCATION_ACCEPTANCE_V3.json'", 1)
replace_exact('freeze.py', "run_id='matched-generation-main-resume-v2'", "run_id='matched-generation-main-resume-v3'", 1)
test = '''# Real OPA comment metadata fixture; semantic changes must remain visible.
from pilot_lib import strip_location
comment_folder=ROOT/'method_runs/FSV-B13/AUTOPAC_STYLE/initial'
before_ast=read(comment_folder/'ast_before.stdout.txt');after_ast=read(comment_folder/'ast_after.stdout.txt')
record('opa_comment_location_metadata_equal',strip_location(before_ast)==strip_location(after_ast))
changed_ast=copy.deepcopy(after_ast)
changed_ast['rules'][0]['head']['name']='changed_semantic_rule'
record('opa_comment_normalization_preserves_rule_semantics',strip_location(before_ast)!=strip_location(changed_ast))
changed_comments=copy.deepcopy(after_ast)
changed_comments['comments'][0]['Text']='changed_comment_content'
record('opa_comment_normalization_preserves_comment_text',strip_location(before_ast)!=strip_location(changed_comments))
'''
replace_exact('run_t0.py', "scope=read(ROOT/'EXPERIMENT_SCOPE.json')", test + "scope=read(ROOT/'EXPERIMENT_SCOPE.json')", 1)
dump(ROOT / 'MAIN_RESUME_AUTHORIZATION_V3.json', {
    'kind': 'DETERMINISTIC_OPA_COMMENT_LOCATION_CONTINUATION', 'status': 'PREPARED_ROOT_DISPATCH_REQUIRED',
    'scope_id': CONFIG['scope_id'], 'as_run_snapshot_path': str(snapshot),
    'as_run_snapshot_receipt_sha256': sha(snapshot / 'SNAPSHOT_RECEIPT.json'),
    'as_run_state_sha256': sha(ROOT / 'EXECUTION_STATE.json'), 'as_run_ledger_sha256': sha(ROOT / 'CALL_LEDGER.json'),
    'actual_paid_attempts': 15, 'complete_cached_call_indices': [x['index'] for x in ledger],
    'opa_location_acceptance_sha256': sha(ROOT / 'OPA_COMMENT_LOCATION_ACCEPTANCE_V3.json'),
    'new_API_calls_in_preparation': 0, 'automatic_API_retries': 0, 'root_paid_dispatch_required': True,
    'final_evaluation_not_yet_read': True, 'policy_or_test_business_fields_changed': False})
print(json.dumps({'status': 'OPA_COMMENT_LOCATION_RECOVERY_PREPARED', 'cached_complete_calls': 15, 'new_API_calls': 0}))
