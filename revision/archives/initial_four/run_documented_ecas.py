"""Uniform ECAS semantic-interface revision. No prior candidate or test feedback in generation."""
import json
import sys
from pathlib import Path
import run_pilot
from pilot_lib import ROOT,CONFIG,read,dump,sha,verify_inputs,compile_model_ir,compile_policy,evaluate_ecas,PolicyError
def verify_documentation():
    verify_inputs()
    for item in read(ROOT/'DOCUMENTED_INPUT_MANIFEST.json'):
        if sha(Path(item['path']))!=item['sha256']:raise RuntimeError('Documented input changed')
def make_prompt(task,stage,previous=None,smoke=False):
    if stage!='ecas_generate' or previous is not None:raise ValueError('Documented ECAS generation accepts no prior feedback')
    packet=read(ROOT/'generation_inputs'/task/'packet.json');packet.pop('common_adapter')
    schema=json.loads(json.dumps(run_pilot.TEMPLATES['ecas_prompt_schema']))
    schema['representation_notice']='Factored schema: choose one rule_variant row and combine with rule_common. Original full schema validates output.'
    payload={'packet':packet,'organization_schema':read(ROOT/'generation_inputs'/task/'organization_schema.json'),'output_schema':schema,'operator_semantics':read(ROOT/'DOCUMENTED_OPERATOR_SEMANTICS.json')}
    key=f'{task}_{stage}_DOCUMENTED_'+('SMOKE' if smoke else 'MAIN');begin='BEGIN_'+key;end='END_'+key
    prompt=run_pilot.TEMPLATES['common']+f'BEGIN={begin}\nEND={end}\nSTAGE={stage}\n'+run_pilot.TEMPLATES['stages'][stage]+'\nVISIBLE_INPUT='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))
    return prompt,begin,end
run_pilot.make_prompt=make_prompt
def main():
    mode=sys.argv[1];target=Path(sys.argv[2]) if len(sys.argv)>2 else None
    if mode=='stats':
        rows=[]
        for task in CONFIG['tasks']:
            p,_,_=make_prompt(task,'ecas_generate');rows.append({'task':task,'bytes':len(p.encode()),'estimated_tokens':(len(p.encode())+1)//2+128})
        dump(ROOT/'DOCUMENTED_PROMPT_SIZES.json',rows);print(json.dumps(rows));return
    verify_documentation()
    if read(ROOT/'EXECUTION_STATE.json')['status']!='COMPLETED':raise RuntimeError('Base generation active')
    if (ROOT/'FORMAT_RECOVERY_STATE.json').exists() and read(ROOT/'FORMAT_RECOVERY_STATE.json')['status']=='RUNNING':raise RuntimeError('Peer generation active; ledger must remain serial')
    if mode=='smoke':
        out,record=run_pilot.call(CONFIG['smoke_task'],'ecas_generate',smoke=True)
        smoke={'case_id':CONFIG['smoke_task']+'_ecas_documented','coverage':'ecas_documented','dataset':'ERPNext_longest_source','max_output_tokens':CONFIG['max_tokens'],'actual_output_tokens':record['usage']['completion_tokens'],'prompt_tokens':record['usage']['prompt_tokens'],'finish_reason':record['finish_reason'],'parse_status':'PASS','content_empty':False,'retry_count':0,'truncated':False,'call_index':record['index']}
        dump(ROOT/'DOCUMENTED_SMOKE_RECORD.json',smoke);dump(target,smoke);return
    if mode!='run':raise ValueError('Unsupported mode')
    if (ROOT/'DOCUMENTED_EXECUTION_STATE.json').exists():raise RuntimeError('Documented generation already dispatched')
    token=read(ROOT/'DOCUMENTED_TOKEN_GATE.json')['data']
    if token['status']=='block':raise RuntimeError('Documented token gate blocked')
    state={'status':'RUNNING','configuration':'DOCUMENTED_PRIMITIVES_V2','rows':[]};dump(ROOT/'DOCUMENTED_EXECUTION_STATE.json',state)
    try:
        for task in CONFIG['tasks']:
            folder=ROOT/'documented_ecas'/task/'ECAS_MATCHED';folder.mkdir(parents=True,exist_ok=False)
            result={'task':task,'method':'ECAS_MATCHED','status':'STARTED','requests':[],'calls':[],'documentation_revision':True,'configuration':'DOCUMENTED_PRIMITIVES_V2'}
            out,record=run_pilot.call(task,'ecas_generate');result['calls'].append(record['index']);candidate=out['candidate'];dump(folder/'candidate.json',candidate)
            proposal=compile_model_ir(candidate);dump(folder/'compiled_proposal.json',proposal)
            if proposal['decision']!='propose':result.update({'status':'ABSTAIN','reason':candidate.get('reason_code')})
            else:
                contract=read(ROOT/'execution_inputs'/task/'contract.json')
                try:
                    admitted=compile_policy(proposal['policy'],contract);dump(folder/'admitted_policy.json',admitted);result['admission']='ADMITTED'
                    dev=[]
                    for vector in read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]:
                        actual=evaluate_ecas(admitted,contract,vector['input'],admission_mode='semantic')
                        dev.append({'id':vector['id'],'expected':vector['expected'],'actual':actual,'pass':actual['decision']==vector['expected'] and not actual.get('engine_error')})
                    result['common_developer_results']={'passed':all(x['pass'] for x in dev),'rows':dev};dump(folder/'COMMON_DEVELOPER_RESULTS.json',result['common_developer_results'])
                    dump(folder/'CANDIDATE_FREEZE.json',{'policy_path':str(folder/'admitted_policy.json'),'policy_sha256':sha(folder/'admitted_policy.json'),'frozen_at':run_pilot.now(),'final_evaluation_not_yet_read':True})
                    for channel in ('O-L','O-I'):
                        for v in read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']:
                            actual=evaluate_ecas(admitted,contract,v['envelope'],admission_mode='semantic');result['requests'].append({'channel':channel,'input':v['envelope'],'expected':v['expected_class'],'actual':actual})
                    result['status']='EVALUATED'
                except PolicyError as exc:result.update({'status':'ADMISSION_REJECTED','reason':str(exc)})
            result['request_pair_correct']=result['status']=='EVALUATED' and len(result['requests'])==2 and all(x['actual']['decision']==x['expected'] for x in result['requests'])
            dump(folder/'RESULT.json',result);state['rows'].append(result);dump(ROOT/'DOCUMENTED_EXECUTION_STATE.json',state)
            print(json.dumps({'task':task,'status':result['status'],'pair_correct':result['request_pair_correct']}),flush=True)
        state['status']='COMPLETED';dump(ROOT/'DOCUMENTED_EXECUTION_STATE.json',state);dump(target,state);verify_documentation()
    except Exception as exc:
        state.update({'status':'STOPPED','error':str(exc),'error_type':type(exc).__name__});dump(ROOT/'DOCUMENTED_EXECUTION_STATE.json',state);raise
if __name__=='__main__':main()
