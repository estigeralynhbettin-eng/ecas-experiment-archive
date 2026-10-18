"""Mock-call control-flow regression. Isolated synthetic outputs; never calls APIs."""
import copy
import json
import shutil
from pathlib import Path
import run_matched as runner
from pilot_lib import ROOT,LANE,read,dump,sha

original_root=ROOT
base=LANE/'outputs/workflow_t0_v1'
base.mkdir(parents=True,exist_ok=False)
known=read(ROOT/'t0_fixtures/known_s03_candidate.json')
wrong=copy.deepcopy(known);wrong['rules'][0]['params']['expected_type']='string'
checks=[]
calls=[]
correct_rego='package external_pilot\nimport rego.v1\ndefault allow := false\nallow if { is_number(input.request.body.age); input.request.body.age == floor(input.request.body.age) }\n'
bad_rego='package external_pilot\nimport rego.v1\ndefault allow := false\n'

def trial(name,method,responses,expected_status,expected_calls,eligible):
    folder=base/name;folder.mkdir()
    for section in ['generation_inputs','execution_inputs']:
        shutil.copytree(original_root/section,folder/section)
    runner.ROOT=folder
    seen=[]
    def fake_call(task,actual_method,stage,previous=None,smoke=False,smoke_id=None):
        assert task=='FSV-S03' and actual_method==method and stage in responses
        assert not (folder/'sealed_evaluation').exists()
        seen.append(stage)
        return copy.deepcopy(responses[stage]),{'index':len(seen),'status':'SYNTHETIC_NOT_MODEL','scope_id':runner.CONFIG['scope_id']}
    runner.call=fake_call
    result=runner.prepare_candidate('FSV-S03',method)
    passed=result['status']==expected_status and result['execution_eligible']==eligible and seen==expected_calls
    checks.append({'check':name,'pass':passed,'observed_status':result['status'],'execution_eligible':result['execution_eligible'],
                   'seen_stages':seen,'expected_stages':expected_calls,'sealed_evaluation_absent':True,'model_calls':0})

trial('ecas_repair_fail_closed','ECAS_MATCHED',{'ecas_generate':{'candidate':wrong},'ecas_repair':{'candidate':wrong}},
      'DEVELOPMENT_REJECTED',['ecas_generate','ecas_repair'],False)
trial('ecas_repair_valid','ECAS_MATCHED',{'ecas_generate':{'candidate':wrong},'ecas_repair':{'candidate':known}},
      'ELIGIBLE',['ecas_generate','ecas_repair'],True)
trial('ecas_first_valid_no_repair','ECAS_MATCHED',{'ecas_generate':{'candidate':known}},'ELIGIBLE',['ecas_generate'],True)
trial('autopac_one_repair','AUTOPAC_STYLE',{'autopac_generate':{'status':'READY','rego':bad_rego,'reason':'synthetic'},
      'autopac_judge':{'verdict':'REVISE','issues':['synthetic developer defect']},'repair':{'status':'READY','rego':correct_rego,'reason':'synthetic'}},
      'ELIGIBLE',['autopac_generate','autopac_judge','repair'],True)
trial('autopac_judge_abstain','AUTOPAC_STYLE',{'autopac_generate':{'status':'READY','rego':correct_rego,'reason':'synthetic'},
      'autopac_judge':{'verdict':'ABSTAIN','issues':['synthetic abstention']}},'JUDGE_ABSTAIN',['autopac_generate','autopac_judge'],False)
packet=read(ROOT/'generation_inputs/FSV-S03/packet.json')
org=read(ROOT/'generation_inputs/FSV-S03/organization_schema.json')
extract={'status':'READY','components':[{'subject':org['subject'][0],'action':org['action'][0],'resource':org['resource'][0],
          'condition':'synthetic source condition','purpose':'unspecified','decision':'allow','evidence_refs':['VIS-FSV-S03-01']}]}
dev=read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks']['FSV-S03']
tests=[{'id':t['id'],'input':t['input'],'expected':t['expected'],'source_ref':t['source_ref']} for t in dev]
trial('p2p_out_of_scope','P2P_STYLE',{'p2p_detect':{'status':'OUT_OF_SCOPE','reason':'synthetic scope boundary'}},'OUT_OF_SCOPE',['p2p_detect'],False)
trial('p2p_one_repair','P2P_STYLE',{'p2p_detect':{'status':'READY','statements':[{'text':'synthetic','evidence_refs':['VIS-FSV-S03-01']}]},
      'p2p_extract':extract,'p2p_rego':{'status':'READY','rego':bad_rego,'reason':'synthetic'},'p2p_tests':{'tests':tests},
      'repair':{'status':'READY','rego':correct_rego,'reason':'synthetic'}},
      'ELIGIBLE',['p2p_detect','p2p_extract','p2p_rego','p2p_tests','repair'],True)
runner.ROOT=original_root
receipt={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','scope_id':runner.CONFIG['scope_id'],'model_calls':0,
         'classification':'SYNTHETIC_OFFLINE_CONTROL_FLOW_NOT_SCIENTIFIC','production_inputs_unchanged':True,'checks':checks,
         'production_manifest_sha256':sha(original_root/'EXECUTION_INPUT_MANIFEST.json'),'test_script_sha256':sha(__file__),
         'all_deny_common_developer_fail_not_eligible':True,'final_fixtures_not_read_in_generation':True}
dump(original_root/'WORKFLOW_T0_RECEIPT.json',receipt)
print(json.dumps({'status':receipt['status'],'checks':len(checks),'failures':[x['check'] for x in checks if not x['pass']]}))
if receipt['status']!='PASS':raise SystemExit(2)
