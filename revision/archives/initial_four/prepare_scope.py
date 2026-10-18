"""Prepare a new frozen scope; no external model calls."""
import csv
import hashlib
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'20261014_external_baseline_pilot'
SCREEN=ROOT.parent/'20261014_multi_case_extension_screen'
LANE=Path('/root/ecas_four_case_peer_20261014')
TASKS=['FSV-S03','FSV-B13','FSV-B17','FSV-B19']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
if (ROOT/'EXECUTION_CONFIG.json').exists():raise RuntimeError('Scope already prepared')
LANE.mkdir(exist_ok=False);(LANE/'tools').mkdir();(LANE/'outputs').mkdir()
old_manifest=read(OLD/'EXECUTION_INPUT_MANIFEST.json')
for name in ('opa','regal'):
    original=Path('/root/ecas_external_pilot_20261014/tools')/name
    expected=next(x['sha256'] for x in old_manifest if x['path']==str(original))
    assert sha(original)==expected
    dest=LANE/'tools'/name;shutil.copyfile(original,dest);dest.chmod(0o555)
shutil.copytree(SCREEN/'runtime',LANE/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
screen_manifest=read(SCREEN/'INPUT_MANIFEST.json')
for item in screen_manifest:
    assert sha(SCREEN/item['path']).upper()==item['sha256']
schema=read(LANE/'runtime/EC_FIELD_SECURITY_MODEL_IR_SCHEMA_V3.json')
dump(ROOT/'execution_inputs/ecas_output_schema.json',schema)
prompt_schema=read(OLD/'execution_inputs/ecas_prompt_schema.json')
assert prompt_schema['$defs']['propose']['properties']['rules'].get('maxItems')==schema['$defs']['propose']['properties']['rules'].get('maxItems')
dump(ROOT/'execution_inputs/ecas_prompt_schema.json',prompt_schema)
originals=[]
field_keys={'fieldname','fieldtype','options','default','reqd','read_only','mandatory_depends_on','depends_on','fetch_from','allow_on_submit','unique','length','non_negative','precision'}
def compact_fields(value):
    if isinstance(value,dict):
        if 'fieldname' in value:return {k:v for k,v in value.items() if k in field_keys}
        return {k:compact_fields(v) for k,v in value.items()}
    if isinstance(value,list):return [compact_fields(v) for v in value]
    return value
for task in TASKS:
    src=SCREEN/'cases'/task/'visible_input.json';original=read(src)
    sources=[];available=[]
    for raw in original['visible_sources']:
        item=json.loads(json.dumps(raw))
        if item['source_id']=='EC-V2-RUNTIME-INTERFACE-CATALOG-V1':
            available=item['content']['available_values']
            item['content']={k:item['content'][k] for k in ('available_values','target_operation','notice')}
        elif isinstance(item['content'],dict):item['content']=compact_fields(item['content'])
        sources.append(item)
    rid=original['target']['system']+':'+original['target']['version']
    packet={'task_window_id':task,'target':original['target'],'visible_sources':sources,'common_adapter':{
        'subject_role':'authenticated_api_caller','subject_id':'authenticated_api_caller','action':original['target']['operation'],
        'resource_id':rid,'resource_system':original['target']['system'],'resource_version':original['target']['version'],
        'request_and_trusted_paths':available,
        'envelope_representation':{'subject':{'id':'authenticated_api_caller','role':'authenticated_api_caller'},'action':original['target']['operation'],'resource':{'id':rid,**original['target']},'request':'original request unchanged','trusted':'original trusted unchanged'},
        'notice':'resource is an object; compare resource.id to organization schema resource strings. Subject id/role are neutral aliases, not an added permission rule. Source evidence and runtime path declarations contain no evaluation label.'}}
    # resource has only the declared id/system/version fields, never a second action binding.
    packet['common_adapter']['envelope_representation']['resource'].pop('operation')
    dest=ROOT/'generation_inputs'/task/'packet.json';dump(dest,packet)
    originals.append({'path':str(dest),'source_path':str(src),'source_sha256':sha(src),'derived_sha256':sha(dest),'derivation':'remove primitive focus; compact all field metadata by fixed allowlist; complete resource object ABI'})
    org={'subject':['authenticated_api_caller'],'action':[original['target']['operation']],'resource':[rid],'condition_paths':[v['path'] for v in available]}
    dump(ROOT/'generation_inputs'/task/'organization_schema.json',org)
    for channel in ('O-L','O-I'):
        src=SCREEN/'cases'/task/(channel+'.json');dest=ROOT/'sealed_evaluation'/task/(channel+'.json');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
        originals.append({'path':str(dest),'source_path':str(src),'source_sha256':sha(src),'derived_sha256':sha(dest),'derivation':'byte-identical archived request; no model access'})
    dest=ROOT/'execution_inputs'/task/'contract.json';dest.parent.mkdir(parents=True);shutil.copyfile(SCREEN/'cases'/task/'contract.json',dest)
    sourcecopy=ROOT/'source_snapshots'/task/'visible_input.json';sourcecopy.parent.mkdir(parents=True);shutil.copyfile(SCREEN/'cases'/task/'visible_input.json',sourcecopy)
dump(ROOT/'INPUT_DERIVATIONS.json',originals)
dev={
 'FSV-S03':[
 {'id':'dev_integer','input':{'request':{'body':{'age':42}},'trusted':{}},'expected':'allow','source_ref':'VIS-FSV-S03-01'},
 {'id':'dev_integer_string','input':{'request':{'body':{'age':'42'}},'trusted':{}},'expected':'deny','source_ref':'VIS-FSV-S03-01'}],
 'FSV-B13':[
 {'id':'dev_limit','input':{'request':{'body':{'qty':54}},'trusted':{'derivedMaximumQty':54,'authorizedRole':False}},'expected':'allow','source_ref':'VIS-FSV-B13-01'},
 {'id':'dev_over','input':{'request':{'body':{'qty':55}},'trusted':{'derivedMaximumQty':54,'authorizedRole':False}},'expected':'deny','source_ref':'VIS-FSV-B13-01'},
 {'id':'dev_role_exception','input':{'request':{'body':{'qty':55}},'trusted':{'derivedMaximumQty':54,'authorizedRole':True}},'expected':'allow','source_ref':'VIS-FSV-B13-01'}],
 'FSV-B17':[
 {'id':'dev_enabled','input':{'request':{'body':{'customer':'DEV-CUSTOMER-842'}},'trusted':{'customerDisabled':False}},'expected':'allow','source_ref':'VIS-FSV-B17-01'},
 {'id':'dev_disabled','input':{'request':{'body':{'customer':'DEV-CUSTOMER-843'}},'trusted':{'customerDisabled':True}},'expected':'deny','source_ref':'VIS-FSV-B17-01'}],
 'FSV-B19':[
 {'id':'dev_not_held','input':{'request':{'body':{'supplier':'DEV-SUPPLIER-852','action':'PURCHASE_ORDER'}},'trusted':{'supplierOnHold':False,'holdType':''}},'expected':'allow','source_ref':'VIS-FSV-B19-01'},
 {'id':'dev_invoices','input':{'request':{'body':{'supplier':'DEV-SUPPLIER-853','action':'PURCHASE_ORDER'}},'trusted':{'supplierOnHold':True,'holdType':'Invoices'}},'expected':'deny','source_ref':'VIS-FSV-B19-01'},
 {'id':'dev_payments','input':{'request':{'body':{'supplier':'DEV-SUPPLIER-854','action':'PURCHASE_ORDER'}},'trusted':{'supplierOnHold':True,'holdType':'Payments'}},'expected':'allow','source_ref':'VIS-FSV-B19-01'}]}
dump(ROOT/'execution_inputs/operator_developer_tests.json',{'classification':'COMMON_PUBLIC_SOURCE_DEVELOPER_TESTS_ALL_METHODS','tasks':dev})
probes=read(SCREEN/'BRANCH_PROBE_PROTOCOL.json')
dump(ROOT/'sealed_evaluation/branch_protocol.json',probes)
templates=read(OLD/'PROMPT_TEMPLATES.json');templates['ecas_prompt_schema']=prompt_schema
templates['common']+=' Complete common ABI: subject is {id,role}; both identity values are authenticated_api_caller. action is the exact target operation string. resource is an object {id,system,version}; resource.id is system:version and matches the organization-schema resource string. request/trusted are unchanged. Do not compare resource object directly to a string. Policy only checks the supported focused target constraint; authentication and other domain validation are upstream.\n'
templates['stages']['p2p_extract']='Extract DSARCP for each detected policy. Return {status:READY|OUT_OF_SCOPE|ABSTAIN,components:[{decision,subject,action,resource,condition,purpose,evidence_refs}],reason}. Subject/action/resource must be literal strings from organization_schema. Conditions come only from sources and runtime paths; purpose may be unspecified.'
templates['stages']['p2p_tests']+=' The input envelope you return contains original request/trusted only; the adapter adds the declared identity/action/resource constants. Do not fabricate undeclared trusted paths.'
dump(ROOT/'PROMPT_TEMPLATES.json',templates)
sizes={t:len(compact(read(ROOT/'generation_inputs'/t/'packet.json')).encode()) for t in TASKS}
config=read(OLD/'EXECUTION_CONFIG.json');config.update({'scope_id':'ECAS-FOUR-PEER-BASELINES-20261014-01','runtime_lane':str(LANE),'tasks':TASKS,'max_calls':40,'max_smoke_calls':4,'max_total_external_repair_calls':8,'contracts':{t:str(ROOT/'execution_inputs'/t/'contract.json') for t in TASKS},'smoke_task':max(sizes,key=sizes.get),'classification':'RETROSPECTIVE_FOUR_CASE_ADAPTED_PEER_BASELINES_NOT_NATIVE_OR_BLIND'})
dump(ROOT/'EXECUTION_CONFIG.json',config)
# Adapt copied orchestration before its immutable execution freeze.
p=ROOT/'run_pilot.py';text=p.read_text(encoding='utf-8-sig')
text=text.replace("'FSV-S04'", "CONFIG['smoke_task']").replace("'FSV-S02'", "'FSV-S03'")
text=text.replace("tests=generated_tests['tests'];dump", "tests=generated_tests['tests']+read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task];dump")
text=text.replace("if smoke and sum(x['smoke']", "if stage=='repair' and sum(x['stage']=='repair' for x in ledger)>=CONFIG['max_total_external_repair_calls']:raise RuntimeError('Repair budget exhausted')\n    if smoke and sum(x['smoke']")
# Keep the first-generation compile/developer results before any repair.
text=text.replace("needs_repair=not checks", "dump(folder/'INITIAL_DEVELOPMENT.json',{'checks':checks,'tests':tests,'developer_results':dev_result,'judge':judge})\n        needs_repair=not checks")
p.write_text(text,encoding='utf-8')
p=ROOT/'pilot_lib.py';text=p.read_text(encoding='utf-8-sig')
old="'subject':{'role':p['common_adapter']['subject_role']},'action':p['target']['operation'],\n                  'resource':p['target']['system']+':'+p['target']['version']"
new="'subject':{'role':p['common_adapter']['subject_role'],'id':p['common_adapter']['subject_id']},'action':p['target']['operation'],\n                  'resource':{'id':p['common_adapter']['resource_id'],'system':p['target']['system'],'version':p['target']['version']}"
assert old in text;text=text.replace(old,new);p.write_text(text,encoding='utf-8')
rh=next(csv.reader((OLD/'RESULT_TRACEABILITY.csv').open(encoding='utf-8-sig')))
ch=next(csv.reader((OLD/'CLAIM_EVIDENCE_MATRIX.csv').open(encoding='utf-8-sig')))
for name,headers in [('RESULT_TRACEABILITY.csv',rh),('CLAIM_EVIDENCE_MATRIX.csv',ch)]:
    with (ROOT/name).open('w',encoding='utf-8',newline='') as f:csv.writer(f).writerow(headers)
dump(ROOT/'EXPERIMENT_SCOPE.json',{'kind':'new-experiment-block','status':'FROZEN','scope_id':config['scope_id'],'protocol_path':'FROZEN_PROTOCOL_CN.md','protocol_sha256':sha(ROOT/'FROZEN_PROTOCOL_CN.md')})
dump(ROOT/'PREPARATION_SUMMARY.json',{'status':'PREPARED_NO_MODEL_CALL','scope':config['scope_id'],'packet_bytes':sizes,'schema_prompt_bytes':len(compact(prompt_schema).encode()),'smoke_task':config['smoke_task'],'model_calls':0,'windows_exception':'Mandated approved Windows model wrapper/key loader; orchestration and all policy evaluation in WSL'})
print(json.dumps(read(ROOT/'PREPARATION_SUMMARY.json'),ensure_ascii=False))
