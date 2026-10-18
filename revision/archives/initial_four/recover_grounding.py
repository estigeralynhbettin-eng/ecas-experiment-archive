"""Complete eligible DSARCP branches via exact object-id normalization, within original call cap."""
import json
import sys
from pathlib import Path
from pilot_lib import ROOT,CONFIG,read,dump,sha,verify_inputs,policy_checks,run_tests
from run_pilot import call,final_rego,now
def verify_recovery():
    verify_inputs()
    for item in read(ROOT/'FORMAT_RECOVERY_INPUT_MANIFEST.json'):
        if sha(Path(item['path']))!=item['sha256']:raise RuntimeError('Recovery input changed')
def normalize(task,extraction):
    result=json.loads(json.dumps(extraction));packet=read(ROOT/'generation_inputs'/task/'packet.json');org=read(ROOT/'generation_inputs'/task/'organization_schema.json')
    envelope=packet['common_adapter']['envelope_representation'];changes=[]
    for i,component in enumerate(result.get('components',[])):
        for field in ('subject','action','resource'):
            value=component.get(field)
            if value in org[field]:continue
            if field in ('subject','resource') and isinstance(value,dict) and value==envelope[field] and value.get('id') in org[field]:
                component[field]=value['id'];changes.append({'component':i,'field':field,'from':value,'to':value['id'],'classification':'EXACT_NEUTRAL_OBJECT_ID_REPRESENTATION'})
            else:raise ValueError('Not eligible for representation-only recovery: '+field)
    if not changes:raise ValueError('No representation recovery needed')
    for a,b in zip(result['components'],extraction['components']):
        assert all(a.get(key)==b.get(key) for key in set(a).union(b)-{'subject','resource'})
    return result,changes
def recover(task,source):
    verify_recovery();folder=ROOT/'format_recovery'/task/'P2P_STYLE';folder.mkdir(parents=True,exist_ok=False)
    original=read(source/'RESULT.json');extraction=read(source/'extraction.json');detection=read(source/'detection.json')
    grounded,changes=normalize(task,extraction)
    dump(folder/'ORIGINAL_RESULT.json',original);dump(folder/'detection.json',detection);dump(folder/'extraction.json',extraction);dump(folder/'extraction_grounded.json',grounded)
    dump(folder/'GROUNDING_REPRESENTATION_RECEIPT.json',{'original_status':original['status'],'original_source':str(source),'changes':changes,'business_fields_changed':False,'source_extraction_sha256':sha(source/'extraction.json'),'derived_extraction_sha256':sha(folder/'extraction_grounded.json'),'no_repeat_detect_extract_calls':True})
    result={'task':task,'method':'P2P_STYLE','classification':CONFIG['classification'],'status':'STARTED','requests':[],'calls':original['calls'].copy(),'original_interface_status':original['status'],'format_recovery':True}
    dump(folder/'RESULT.json',result)
    previous={'detection':detection,'extraction':grounded}
    generation,record=call(task,'p2p_rego',previous);result['calls'].append(record['index']);dump(folder/'generation.json',generation)
    if generation['status']!='READY':
        result.update({'status':'ABSTAIN','reason':generation.get('reason')});dump(folder/'RESULT.json',result);return result
    generated,record=call(task,'p2p_tests',previous);result['calls'].append(record['index'])
    tests=generated['tests']+read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]
    dump(folder/'generated_developer_tests.json',tests)
    checks=policy_checks(generation['rego'],folder/'initial',True)
    dev=run_tests(task,checks['policy_path'],tests,folder/'initial') if checks['accepted'] else {'passed':False,'rows':[]}
    dump(folder/'INITIAL_DEVELOPMENT.json',{'checks':checks,'tests':tests,'developer_results':dev,'judge':None})
    if not checks['accepted'] or not dev['passed']:
        feedback={'prior_generation':generation,'developer_checks':checks,'developer_tests':tests,'developer_results':dev,'judge':None,'prior_extraction':previous}
        repaired,record=call(task,'repair',feedback);result['calls'].append(record['index']);dump(folder/'repair.json',repaired)
        if repaired['status']!='READY':
            result.update({'status':'REPAIR_ABSTAIN','reason':repaired.get('reason')});dump(folder/'RESULT.json',result);return result
        checks=policy_checks(repaired['rego'],folder/'repaired',True)
        dev=run_tests(task,checks['policy_path'],tests,folder/'repaired') if checks['accepted'] else {'passed':False,'rows':[]}
        result['repaired_once']=True
    result.update({'developer_checks':checks,'developer_results':dev})
    if not checks['accepted'] or not dev['passed']:result['status']='DEVELOPMENT_REJECTED'
    else:
        dump(folder/'CANDIDATE_FREEZE.json',{'policy_path':checks['policy_path'],'policy_sha256':sha(checks['policy_path']),'frozen_at':now(),'final_evaluation_not_yet_read':True})
        result['requests']=final_rego(task,'P2P_STYLE',checks['policy_path'],folder);result['status']='EVALUATED'
    result['request_pair_correct']=result['status']=='EVALUATED' and len(result['requests'])==2 and all(x['actual'].get('decision')==x['expected'] and not x['actual'].get('engine_error') for x in result['requests'])
    result['completed_at']=now();dump(folder/'RESULT.json',result);verify_recovery();return result
def main():
    base=read(ROOT/'EXECUTION_STATE.json')
    if base['status']!='COMPLETED':raise RuntimeError('First batch must be completed')
    if (ROOT/'FORMAT_RECOVERY_STATE.json').exists():raise RuntimeError('Recovery already dispatched; inspect original run')
    output={'status':'RUNNING','rows':[],'not_eligible':[]};dump(ROOT/'FORMAT_RECOVERY_STATE.json',output)
    try:
        for task in CONFIG['tasks']:
            source=ROOT/'effect_runs'/task/'P2P_STYLE';result=read(source/'RESULT.json')
            if result['status']!='SCHEMA_GROUNDING_REJECTED':continue
            try:normalize(task,read(source/'extraction.json'))
            except ValueError as exc:
                output['not_eligible'].append({'task':task,'reason':str(exc)});continue
            row=recover(task,source);output['rows'].append(row);dump(ROOT/'FORMAT_RECOVERY_STATE.json',output)
            print(json.dumps({'task':task,'status':row['status'],'pair_correct':row.get('request_pair_correct')},ensure_ascii=False),flush=True)
        output['status']='COMPLETED';dump(ROOT/'FORMAT_RECOVERY_STATE.json',output)
        target=Path(sys.argv[1]);target.parent.mkdir(parents=True,exist_ok=True);dump(target,output)
    except Exception as exc:
        output.update({'status':'STOPPED','error_type':type(exc).__name__,'error':str(exc)});dump(ROOT/'FORMAT_RECOVERY_STATE.json',output);raise
if __name__=='__main__':main()
