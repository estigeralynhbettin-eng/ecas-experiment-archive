"""Scope-specific deterministic engineering checks; no credentials or model calls."""
import copy
import datetime
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from pilot_lib import ROOT, LANE, CONFIG, read, dump, sha, tool, verify_inputs, capabilities, policy_checks, rego_decision, adapt, ground_extraction, source_reference_check
from pilot_lib import compile_model_ir, compile_policy, evaluate_ecas, PolicyError
from run_matched import validate_stage, normalize_stage, validate_resume_inputs, SCHEMA

verify_inputs()
version=sys.argv[1] if len(sys.argv)>1 else 'v1'
out=LANE/('outputs/t0' if version=='v1' else 'outputs/t0_'+version)
out.mkdir(parents=True,exist_ok=False)
capabilities(out)
if version!='v1' and sha(out/'restricted_capabilities.json')!=sha(LANE/'outputs/t0/restricted_capabilities.json'):
    raise RuntimeError('Restrictive capabilities changed between engineering preparations')
checks=[]
def record(name,passed,detail=None):checks.append({'check':name,'pass':bool(passed),'detail':detail})
for name in ('opa','regal'):
    r=tool([LANE/'tools'/name,'version'],out,name+'_version')
    record(name+'_startup',r.returncode==0,r.stdout[:2000])
policy='package external_pilot\nimport rego.v1\ndefault allow := false\nallow if { input.request.body.probe > 0 }\n'
good=policy_checks(policy,out/'good',True)
record('format_ast_compile_full_regal',good['accepted'],good)
record('format_preserves_original',Path(good['original_path']).read_text()==policy and good['format_receipt']['ast_semantics_equal_without_location'])
for name,value,expected in [('allow',1,'allow'),('deny',-1,'deny')]:
    observed=rego_decision(good['policy_path'],adapt('FSV-S03',{'request':{'body':{'probe':value}},'trusted':{}}),out,name)
    record('opa_'+name,observed['decision']==expected,observed)
for name,source,expected in [('syntax','package external_pilot\nallow :=\n','COMPILE_REJECTED'),
                            ('network','package external_pilot\nimport rego.v1\nallow if { http.send({"method":"GET","url":"https://example.invalid"}) }\n','COMPILE_REJECTED'),
                            ('undefined','package external_pilot\nimport rego.v1\nallow if { false }\n','UNDEFINED_OR_AMBIGUOUS'),
                            ('non_boolean','package external_pilot\nallow := "deny"\n','NON_BOOLEAN')]:
    checked=policy_checks(source,out/name,False)
    status='COMPILE_REJECTED' if checked['compile_exit'] else rego_decision(checked['policy_path'],{'request':{'body':{}}},out/name,'evaluate')['status']
    record(name,status==expected,{'expected':expected,'observed':status})
candidate=read(ROOT/'t0_fixtures/known_s03_candidate.json')
validate_stage('ecas_generate',{'candidate':candidate})
proposal=compile_model_ir(candidate)
contract=read(ROOT/'execution_inputs/FSV-S03/contract.json')
admitted=compile_policy(proposal['policy'],contract)
for value,expected in [(43,'allow'),('43','deny'),(True,'deny'),(43.5,'deny')]:
    result=evaluate_ecas(admitted,contract,{'request':{'body':{'age':value}},'trusted':{}},admission_mode='semantic')
    record('known_ecas_'+repr(value),result['decision']==expected,result)
missing=copy.deepcopy(contract);missing['evidence']=[]
try:compile_policy(proposal['policy'],missing);failed=False
except PolicyError:failed=True
record('ecas_missing_evidence_rejected',failed)
bad=copy.deepcopy(candidate);bad['evidence_refs']=['NONEXISTENT-T0-ID'];bad['rules'][0]['evidence_refs']=['NONEXISTENT-T0-ID']
try:compile_policy(compile_model_ir(bad)['policy'],contract);failed=False
except PolicyError:failed=True
record('ecas_wrong_evidence_id_rejected',failed)
normalized,changes=normalize_stage('ecas_generate',copy.deepcopy(candidate))
record('valid_direct_ir_outer_wrapper_only',normalized=={'candidate':candidate} and len(changes)==1 and not changes[0]['business_fields_changed'])
wrapped,changes=normalize_stage('ecas_repair',{'candidate':copy.deepcopy(candidate)})
record('valid_existing_wrapper_unchanged',wrapped=={'candidate':candidate} and not changes)
for name,payload in [('partial_ir',{'ir_version':'EC-FIELD-MODEL-IR-V3'}),('wrong_version',dict(candidate,ir_version='WRONG')),
                     ('ambiguous_wrapper',dict(candidate,candidate=candidate)),('extra_ir_field',dict(candidate,unsupported='extra')),
                     ('list_shape',[candidate]),('candidate_string',{'candidate':'not-an-object'})]:
    try:normalize_stage('ecas_generate',payload);failed=False
    except (ValidationError,ValueError,KeyError):failed=True
    record('wrapper_normalization_'+name+'_rejected',failed)
for name,change in [('missing_field',lambda x:x.pop('target')),('wrong_schema_version',lambda x:x.update(ir_version='WRONG')),
                    ('duplicate_rules',lambda x:x['rules'].append(copy.deepcopy(x['rules'][0])))]:
    bad=copy.deepcopy(candidate);change(bad)
    try:validate_stage('ecas_generate',{'candidate':bad});failed=False
    except (ValidationError,KeyError,ValueError):failed=True
    record('schema_'+name+'_rejected',failed)
for name,payload in [('truncated','{"candidate":'),('empty','')]:
    try:json.loads(payload);failed=False
    except ValueError:failed=True
    record('json_'+name+'_rejected',failed)
for stage,payload in [('p2p_extract',{'status':'READY','components':[]}),('autopac_judge',{'verdict':'ACCEPT'}),('repair',{'status':'READY'})]:
    try:validate_stage(stage,payload);failed=False
    except (ValueError,KeyError):failed=True
    record('stage_'+stage+'_missing_fields_rejected',failed)
for task in CONFIG['tasks']:
    env={'request':{'body':{'probe':'T0'}},'trusted':{'probe':'UNCHANGED'}}
    mapped=adapt(task,env);packet=read(ROOT/'generation_inputs'/task/'packet.json')
    record('neutral_adapter_'+task,mapped['request']==env['request'] and mapped['trusted']==env['trusted'] and mapped['subject']==packet['common_adapter']['envelope_representation']['subject'] and mapped['resource']==packet['common_adapter']['envelope_representation']['resource'])
    extraction={'status':'READY','components':[{'subject':mapped['subject'],'action':mapped['action'],'resource':mapped['resource'],'condition':'T0-condition-unchanged'}]}
    fixed,receipt=ground_extraction(task,extraction)
    record('exact_object_mapping_'+task,receipt['accepted'] and len(receipt['mappings'])==2 and fixed['components'][0]['condition']==extraction['components'][0]['condition'])
    extraction['components'][0]['resource']['id']='WRONG'
    fixed,receipt=ground_extraction(task,extraction)
    record('wrong_object_mapping_rejected_'+task,not receipt['accepted'])
record('max_call_accounting',CONFIG['max_smoke_calls']+len(CONFIG['tasks'])*sum(CONFIG['max_method_case_calls'].values())==44)
record('new_scope_identity',CONFIG['scope_id']=='ECAS-MATCHED-EVIDENCE-LABOR-20261014-01' and str(LANE)=='/root/ecas_matched_generation_20261014')
schema_qa=read(ROOT/'SCHEMA_FACTORIZATION_QA.json')
record('lossless_complete_schema_factorization',schema_qa['status']=='PASS' and schema_qa['reconstructed_full_schema_equal'] and schema_qa['variant_count']==15 and schema_qa['original_schema_sha256']==sha(ROOT/'execution_inputs/ecas_output_schema.json') and schema_qa['factored_schema_sha256']==sha(ROOT/'execution_inputs/ecas_prompt_schema.json'))
record('as_run_smoke_snapshot_preserved',all(sha(x['snapshot_path'])==x['sha256'] for x in read(ROOT/'setup_history/as_run_smoke_v1/SNAPSHOT_RECEIPT.json')['files']))
record('as_run_main_snapshot_preserved',all(sha(x['snapshot_path'])==x['sha256'] for x in read(ROOT/'setup_history/as_run_main_v1/SNAPSHOT_RECEIPT.json')['files']))
packet=read(ROOT/'generation_inputs/FSV-B13/packet.json')
for name,reference,expected in [('base','VIS-FSV-B13-01',True),('limit_anchor','VIS-FSV-B13-01#Limit Percent',True),
                              ('role_anchor','VIS-FSV-B13-01#Role Allowed to Over Deliver/Receive',True),
                              ('case_whitespace','VIS-FSV-B13-01#  LIMIT   percent ',True),
                              ('unknown_base','VIS-NOT-IN-PACKET#Limit Percent',False),
                              ('unknown_fragment','VIS-FSV-B13-01#T0_SECTION_DOES_NOT_EXIST',False),
                              ('empty_fragment','VIS-FSV-B13-01#   ',False),('invalid_type',13,False)]:
    ref=source_reference_check(packet,reference)
    record('source_reference_'+name,ref['accepted']==expected and ref['original_reference']==reference,ref)
authorization=read(ROOT/'MAIN_RESUME_AUTHORIZATION_V3.json');prior=read(ROOT/'EXECUTION_STATE.json');ledger=read(ROOT/'CALL_LEDGER.json')
record('explicit_resume_gate_valid_complete_cache',validate_resume_inputs(prior,authorization,ledger,sha(ROOT/'EXECUTION_STATE.json'),sha(ROOT/'CALL_LEDGER.json')))
for name,state_edit,ledger_edit,state_hash in [('running',{'status':'RUNNING'},False,sha(ROOT/'EXECUTION_STATE.json')),
                                            ('sealed_read',{'final_evaluation_read':True},False,sha(ROOT/'EXECUTION_STATE.json')),
                                            ('state_hash_mismatch',{},False,'0'*64),
                                            ('unresolved_call',{},True,sha(ROOT/'EXECUTION_STATE.json'))]:
    bad_state=copy.deepcopy(prior);bad_state.update(state_edit);bad_ledger=copy.deepcopy(ledger)
    if ledger_edit:bad_ledger[-1]['status']='STARTED'
    try:validate_resume_inputs(bad_state,authorization,bad_ledger,state_hash,sha(ROOT/'CALL_LEDGER.json'));failed=False
    except RuntimeError:failed=True
    record('explicit_resume_gate_'+name+'_rejected',failed)
# Real OPA comment metadata fixture; semantic changes must remain visible.
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
scope=read(ROOT/'EXPERIMENT_SCOPE.json')
record('mcp_scope_record_schema',scope['kind']=='new-experiment-block' and scope['status']=='FROZEN' and scope['scope_id']==CONFIG['scope_id'] and scope['protocol_path']=='FROZEN_PROTOCOL_CN.md' and scope['protocol_sha256']==sha(ROOT/'FROZEN_PROTOCOL_CN.md'))
record('old_runtime_hash_copies_match',all(x['equal'] and sha(x['original_path'])==x['original_sha256'] and sha(x['new_path'])==x['new_sha256'] for x in read(ROOT/'SOURCE_COPY_RECEIPT.json')['runtime_tools']))
tool(['ps','-eo','pid,ppid,comm'],out,'process_inventory')
free=shutil.disk_usage(LANE).free
record('free_space_min_2gb',free>2*1024**3,free)
verify_inputs()
receipt={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','scope_id':CONFIG['scope_id'],'run_id':'matched-generation-t0-'+version,
         'runtime_lane':str(LANE),'setup_version':version,'frozen_manifest_sha256':sha(ROOT/'EXECUTION_INPUT_MANIFEST.json'),
         'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':checks,
         'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'free_bytes':free,
         'uses_docker_gpu_or_services':False,'shared_resources_used':[],'outputs_isolated':True,'raw_model_calls':0,'api_key_loaded':False,
         'scope_paid_model_attempts_at_T0':len(read(ROOT/'CALL_LEDGER.json')) if (ROOT/'CALL_LEDGER.json').exists() else 0,
         'scientific_result':False,'fixture_classification':'ARCHIVED_S03_CANDIDATE_ENGINEERING_FIXTURE_EXCLUDED_FROM_GENERATION'}
for old_name in ['T0_RECEIPT.json','T0_EVIDENCE.json']:
    if (ROOT/old_name).exists():
        old=read(ROOT/old_name);saved=ROOT/'setup_history'/(old_name.replace('.json','_')+old.get('setup_version','v1')+'.json')
        if not saved.exists():dump(saved,old)
dump(ROOT/'T0_RECEIPT.json',receipt);dump(out/'RECEIPT.json',receipt)
dump(ROOT/'T0_EVIDENCE.json',{'status':receipt['status'],'scope_id':CONFIG['scope_id'],'run_id':receipt['run_id'],'runtime_lane':str(LANE),'receipt_path':'T0_RECEIPT.json','receipt_sha256':sha(ROOT/'T0_RECEIPT.json'),'completed_at':receipt['completed_at']})
print(json.dumps({'status':receipt['status'],'checks':len(checks),'failures':[x['check'] for x in checks if not x['pass']]}))
if receipt['status']!='PASS':raise SystemExit(2)
