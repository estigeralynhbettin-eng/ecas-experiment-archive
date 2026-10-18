"""Zero-API preparation for source locator validation and exact-cache resume."""
from pathlib import Path
from pilot_lib import ROOT,CONFIG,read,dump,sha,source_reference_check

snapshot=ROOT/'setup_history/as_run_main_v1'
snapshot_receipt=read(snapshot/'SNAPSHOT_RECEIPT.json')
if not all(sha(x['snapshot_path'])==x['sha256'] for x in snapshot_receipt['files']):raise RuntimeError('As-run main-v1 snapshot changed')
state=read(ROOT/'EXECUTION_STATE.json');ledger=read(ROOT/'CALL_LEDGER.json')
if state!=read(snapshot/'EXECUTION_STATE.json') or ledger!=read(snapshot/'CALL_LEDGER.json'):
    raise RuntimeError('Current unresolved state or ledger differs from as-run snapshot')
if state['status']!='STOPPED_PROTOCOL_OR_TRANSPORT' or state['final_evaluation_read'] is not False or state['error']!='P2P developer source_ref not visible':
    raise RuntimeError('This preparation handles only the known source locator interface failure')
if len(ledger)!=13 or any(x['status']!='COMPLETED' for x in ledger):raise RuntimeError('Expected 13 completed actual attempts')
for item in ledger:
    if sha(item['raw_response_path'])!=item['raw_response_sha256'] or sha(item['prompt_path'])!=item['prompt_sha256'] or sha(item['output_path'])!=item['output_sha256']:
        raise RuntimeError('Cached prompt/raw/derived evidence changed')
folder=ROOT/'method_runs/FSV-B13/P2P_STYLE'
tests=read(folder/'p2p_tests.json')
if tests!=read(snapshot/'method_runs/FSV-B13/P2P_STYLE/p2p_tests.json'):
    raise RuntimeError('Developer tests changed before source locator validation')
packet=read(ROOT/'generation_inputs/FSV-B13/packet.json')
references=[dict(source_reference_check(packet,t['source_ref']),developer_test_id=t['id']) for t in tests['tests']]
if not all(x['accepted'] and x['binding_kind']=='EXACT_NORMALIZED_VISIBLE_HEADING' for x in references):
    raise RuntimeError('Actual historical source fragments cannot be independently located as visible headings')
dump(ROOT/'SOURCE_REFERENCE_ACCEPTANCE_V2.json',{'classification':'LOCATOR_INTERFACE_VALIDATION_ONLY','scope_id':CONFIG['scope_id'],
      'tests_path':str(folder/'p2p_tests.json'),'tests_sha256':sha(folder/'p2p_tests.json'),'references':references,
      'original_tests_inputs_expected_references_unchanged':True,'policy_path':str(folder/'p2p_rego.json'),
      'policy_sha256':sha(folder/'p2p_rego.json'),'policy_unchanged_from_as_run':sha(folder/'p2p_rego.json')==sha(snapshot/'method_runs/FSV-B13/P2P_STYLE/p2p_rego.json'),
      'new_API_calls':0,'final_evaluation_read':False})
dump(ROOT/'MAIN_RESUME_AUTHORIZATION_V2.json',{'kind':'DETERMINISTIC_SOURCE_LOCATOR_INTERFACE_CONTINUATION','status':'PREPARED_ROOT_DISPATCH_REQUIRED',
      'scope_id':CONFIG['scope_id'],'as_run_snapshot_path':str(snapshot),'as_run_snapshot_receipt_sha256':sha(snapshot/'SNAPSHOT_RECEIPT.json'),
      'as_run_state_sha256':sha(ROOT/'EXECUTION_STATE.json'),'as_run_ledger_sha256':sha(ROOT/'CALL_LEDGER.json'),
      'actual_paid_attempts':13,'complete_cached_call_indices':[x['index'] for x in ledger],
      'source_reference_acceptance_sha256':sha(ROOT/'SOURCE_REFERENCE_ACCEPTANCE_V2.json'),
      'new_API_calls_in_preparation':0,'automatic_API_retries':0,'root_paid_dispatch_required':True,'final_evaluation_not_yet_read':True,
      'source_test_input_expected_reference_and_policy_business_fields_changed':False})
print({'status':'SOURCE_LOCATORS_VALID_EXPLICIT_RESUME_PREPARED','new_API_calls':0,'actual_paid_attempts':13,'source_checks':len(references)})
