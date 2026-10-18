"""Serial matched-target generation via approved GLM wrapper; no API retries."""
import argparse
import datetime
import hashlib
import json
import subprocess
import time
from pathlib import Path
from jsonschema import Draft202012Validator
from pilot_lib import ROOT, LANE, CONFIG, read, dump, sha, verify_inputs, adapt, policy_checks, rego_decision, run_tests, ground_extraction
from pilot_lib import compile_model_ir, compile_policy, evaluate_ecas, PolicyError

TEMPLATES = read(ROOT / 'PROMPT_TEMPLATES.json')
SCHEMA = read(ROOT / 'execution_inputs/ecas_output_schema.json')
CALLS = ROOT / 'CALL_LEDGER.json'
STATE = ROOT / 'EXECUTION_STATE.json'
METHOD_STAGE = {'P2P_STYLE': 'p2p_rego', 'AUTOPAC_STYLE': 'autopac_generate', 'ECAS_MATCHED': 'ecas_generate'}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def compact(value): return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
def winpath(path): return subprocess.run(['wslpath', '-w', str(path)], capture_output=True, text=True, check=True).stdout.strip()

def make_prompt(task, stage, previous=None, smoke=False, smoke_id=None):
    payload = {'packet': read(ROOT / 'generation_inputs' / task / 'packet.json'),
               'organization_schema': read(ROOT / 'generation_inputs' / task / 'organization_schema.json')}
    # Uniform representation only: common already declares this exact neutral envelope.
    # Original packet and runtime path/authority/type declarations remain frozen.
    payload['packet']['common_adapter'].pop('envelope_representation')
    payload['packet']['common_adapter'].pop('notice')
    instruction = TEMPLATES['stages'][stage]
    if stage in ('ecas_generate','ecas_repair'):
        payload['output_schema'] = TEMPLATES['ecas_prompt_schema']
        payload['operator_semantics'] = read(ROOT / 'DOCUMENTED_OPERATOR_SEMANTICS.json')
    if previous is not None:
        payload['prior_stage_data'] = previous
    if smoke:
        if stage in ('p2p_rego','autopac_generate'):
            payload['additional_public_case'] = read(ROOT / 'generation_inputs/FSV-S03/packet.json')
        if stage == 'p2p_rego':
            instruction = ('Developer interface/token smoke only. Return {detection:{status,statements:[{text,evidence_refs}]},'
                'extraction:{status,components:[{decision,subject,action,resource,condition,purpose,evidence_refs}]},'
                'policy:{status:READY|ABSTAIN,rego,reason},tests:[{id,input:{request:{body:{}},trusted:{}},expected:allow|deny,source_ref}]}. '
                'Exercise P2P-style stages on TARGET_OBJECTIVE, with declared literal organization IDs. If outside scope explicitly abstain, '
                'but still demonstrate a separate synthetic policy allowing input.request.body.probe > 0 with positive/negative tests. '
                'Synthetic output cannot enter case results. Rego package external_pilot, import rego.v1, default allow := false.')
        elif stage == 'autopac_generate':
            instruction = ('Developer interface/token smoke only. Return {generation:{status:READY|ABSTAIN,rego,reason},'
                'judge:{verdict:ACCEPT|REVISE|ABSTAIN,issues:[string]}} for the AutoPAC-style generate/Judge interface. '
                'Policy implements TARGET_OBJECTIVE. Rego package external_pilot, import rego.v1, default allow := false. No final fixtures.')
    identity = task + '_' + stage + '_' + (('SMOKE_' + str(smoke_id)) if smoke else 'MAIN')
    begin, end = 'BEGIN_' + identity, 'END_' + identity
    prompt = TEMPLATES['common'] + f'BEGIN={begin}\nEND={end}\nSTAGE={stage}\n' + instruction + '\nVISIBLE_INPUT=' + compact(payload)
    return prompt, begin, end

def validate_stage(stage, output, smoke=False):
    if not isinstance(output, dict): raise ValueError('Output is not an object')
    if smoke and stage == 'p2p_rego':
        if not {'detection','extraction','policy','tests'}.issubset(output) or not isinstance(output['tests'], list) or not output['tests']:
            raise ValueError('Incomplete P2P smoke interface')
    elif smoke and stage == 'autopac_generate':
        if not {'generation','judge'}.issubset(output): raise ValueError('Incomplete AutoPAC smoke interface')
    elif stage in ('ecas_generate','ecas_repair'):
        Draft202012Validator(SCHEMA).validate(output['candidate'])
    elif stage in ('p2p_detect','p2p_extract'):
        if output.get('status') not in ('READY','OUT_OF_SCOPE','ABSTAIN'): raise ValueError('Invalid extraction status')
        field = 'statements' if stage == 'p2p_detect' else 'components'
        if output['status'] == 'READY' and (not isinstance(output.get(field), list) or not output[field]): raise ValueError('Missing nonempty ' + field)
    elif stage == 'p2p_tests':
        if not isinstance(output.get('tests'), list) or not output['tests']: raise ValueError('Missing developer tests')
        for test in output['tests']:
            if not isinstance(test, dict) or not {'id','input','expected','source_ref'}.issubset(test): raise ValueError('Incomplete developer test')
            if test['expected'] not in ('allow','deny') or not isinstance(test['input'], dict): raise ValueError('Invalid developer test')
    elif stage == 'autopac_judge':
        if output.get('verdict') not in ('ACCEPT','REVISE','ABSTAIN') or not isinstance(output.get('issues'), list): raise ValueError('Invalid Judge response')
    else:
        if output.get('status') not in ('READY','ABSTAIN'): raise ValueError('Invalid policy status')
        if output['status'] == 'READY' and (not isinstance(output.get('rego'), str) or not output['rego']): raise ValueError('Missing policy')

def call(task, method, stage, previous=None, smoke=False, smoke_id=None):
    verify_inputs()
    if not (ROOT / 'DISPATCH_AUTHORIZATION.json').exists(): raise RuntimeError('Root dispatch authorization missing')
    dispatch = read(ROOT / 'DISPATCH_AUTHORIZATION.json')
    if dispatch.get('scope_id') != CONFIG['scope_id'] or dispatch.get('model') != 'glm-5.2' or dispatch.get('max_calls') != 44 or dispatch.get('authorized') is not True:
        raise RuntimeError('Root dispatch authorization identity mismatch')
    prompt, begin, end = make_prompt(task, stage, previous, smoke, smoke_id)
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    ledger = read(CALLS) if CALLS.exists() else []
    # Resume only immutable completed exact prompts. Failed/started identity stops.
    for existing in ledger:
        if existing['prompt_sha256'] == prompt_hash:
            if existing['status'] != 'COMPLETED': raise RuntimeError('Prior attempt unresolved/failed; automatic API retry prohibited')
            if sha(existing['raw_response_path']) != existing['raw_response_sha256'] or sha(existing['output_path']) != existing['output_sha256']:
                raise RuntimeError('Cached evidence changed')
            output = read(existing['output_path']); validate_stage(stage, output, smoke)
            return output, existing
    if len(ledger) >= CONFIG['max_calls']: raise RuntimeError('Total authorized call cap exhausted')
    if smoke and sum(x['smoke'] for x in ledger) >= CONFIG['max_smoke_calls']: raise RuntimeError('Smoke cap exhausted')
    if not smoke:
        prior = [x for x in ledger if not x['smoke'] and x['task'] == task and x['method'] == method]
        if len(prior) >= CONFIG['max_method_case_calls'][method]: raise RuntimeError('Method/case call cap exhausted')
        if stage in ('repair','ecas_repair') and any(x['stage'] in ('repair','ecas_repair') for x in prior): raise RuntimeError('One repair already used')
    estimate = (len(prompt.encode('utf-8')) + 2) // 3 + 128
    if estimate > CONFIG['max_prompt_tokens']: raise RuntimeError('Conservative prompt estimate exceeds input cap')
    index = len(ledger) + 1
    folder = ROOT / 'calls' / f'{index:02d}_{task}_{stage}'
    folder.mkdir(parents=True, exist_ok=False)
    prompt_path = folder / 'prompt.txt'; prompt_path.write_text(prompt, encoding='utf-8')
    item = {'index': index, 'scope_id': CONFIG['scope_id'], 'task': task, 'method': method, 'stage': stage, 'smoke': smoke,
            'started_at': now(), 'status': 'STARTED', 'prompt_path': str(prompt_path), 'prompt_sha256': sha(prompt_path),
            'prompt_bytes': len(prompt.encode('utf-8')), 'estimated_prompt_tokens': estimate,
            'token_count_kind':'UTF8_BYTES_DIV_3_PLUS_128_HISTORICALLY_CALIBRATED_ESTIMATE_NOT_HARD_BOUND',
            'legacy_bytes_div_2_estimate':(len(prompt.encode('utf-8'))+1)//2+128,'raw_response_path': str(folder/'response.raw.json'),
            'max_tokens': CONFIG['max_tokens'], 'thinking':'enabled', 'reasoning_effort':'high', 'retry_count':0}
    ledger.append(item); dump(CALLS, ledger)
    arguments = [CONFIG['pwsh'],'-NoProfile','-File',winpath(CONFIG['model_wrapper']),'-PromptFile',winpath(prompt_path),
                 '-Model','glm-5.2','-Thinking','enabled','-ReasoningEffort','high','-MaxTokens',str(CONFIG['max_tokens']),
                 '-ResponseFormat','json_object','-TimeoutSec',str(CONFIG['timeout_seconds']),'-RawResponsePath',winpath(folder/'response.raw.json'),
                 '-ContentOutputPath',winpath(folder/'content.json'),'-SummaryOutputPath',winpath(folder/'wrapper_summary.json'),
                 '-SummaryOnly','-AsJson','-BeginSentinel',begin,'-EndSentinel',end]
    started = time.monotonic()
    try:
        with (folder/'wrapper.stdout.txt').open('w', encoding='utf-8') as stdout, (folder/'wrapper.stderr.txt').open('w', encoding='utf-8') as stderr:
            process = subprocess.run(arguments, stdout=stdout, stderr=stderr, timeout=CONFIG['timeout_seconds']+30)
        item.update(wrapper_exit=process.returncode, latency_seconds=round(time.monotonic()-started,3))
        if process.returncode: raise RuntimeError('Approved wrapper failed; consult captured evidence')
        raw = read(folder/'response.raw.json'); summary = read(folder/'wrapper_summary.json'); content = read(folder/'content.json')
        item.update(raw_response_sha256=sha(folder/'response.raw.json'), raw_response_bytes=(folder/'response.raw.json').stat().st_size,
                    returned_model=raw.get('model'), finish_reason=raw['choices'][0]['finish_reason'], usage=raw.get('usage'),
                    cost_status=summary.get('cost_status','UNKNOWN'), capture_mode=summary.get('capture_mode'), content_chars=summary.get('normalized_content_chars'))
        if item['returned_model'] != 'glm-5.2' or item['finish_reason'] != 'stop': raise RuntimeError('Model/finish gate failed')
        if content.get('begin') != begin or content.get('end') != end or content.get('stage') != stage: raise ValueError('Sentinel/stage mismatch')
        usage = item['usage'] or {}
        if not isinstance(usage.get('prompt_tokens'),int) or usage['prompt_tokens'] > CONFIG['max_prompt_tokens']: raise RuntimeError('Observed input token gate failed')
        if not isinstance(usage.get('completion_tokens'),int) or usage['completion_tokens'] > CONFIG['max_tokens']: raise RuntimeError('Observed output token gate failed')
        validate_stage(stage, content['output'], smoke)
        output_path = folder/'parsed_output.json'; dump(output_path, content['output'])
        item.update(status='COMPLETED', parse_status='PASS', completeness_gate='PASS', completed_at=now(), output_path=str(output_path), output_sha256=sha(output_path))
        dump(CALLS, ledger); verify_inputs()
        print(compact({'index':index,'task':task,'method':method,'stage':stage,'status':'COMPLETED','prompt_tokens':usage['prompt_tokens'],'completion_tokens':usage['completion_tokens']}), flush=True)
        return content['output'], item
    except Exception as error:
        item.update(status='STOPPED_PROTOCOL_OR_TRANSPORT', error_type=type(error).__name__, error=str(error).split('\n')[0][:1200], completed_at=now())
        raw_path = folder/'response.raw.json'
        if raw_path.exists():
            item.update(raw_response_sha256=sha(raw_path),raw_response_bytes=raw_path.stat().st_size)
            try:
                raw=read(raw_path); item.update(usage=raw.get('usage'),returned_model=raw.get('model'),finish_reason=raw['choices'][0]['finish_reason'])
            except Exception: pass
        dump(CALLS, ledger)
        raise

def freeze(folder, path, label):
    receipt = {'scope_id':CONFIG['scope_id'],'label':label,'path':str(path),'sha256':sha(path),'frozen_at':now(),
               'final_evaluation_not_yet_read':True,'final_labels_in_feedback':False}
    dump(folder/(label+'_FREEZE.json'),receipt)
    return receipt

def check_ecas(task, candidate, folder):
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/'candidate.json';dump(path,candidate)
    value={'accepted':False,'compile_status':None,'admission_status':None,'developer_results':{'passed':False,'rows':[]},'policy_path':None}
    try:
        proposal=compile_model_ir(candidate);dump(folder/'compiled_proposal.json',proposal)
        value['compile_status']='COMPILED'
        if proposal.get('decision')!='propose':
            value.update(abstain=True,reason=candidate.get('reason_code'));dump(folder/'CHECKS.json',value);return value
        contract=read(ROOT/'execution_inputs'/task/'contract.json')
        admitted=compile_policy(proposal['policy'],contract)
        policy=folder/'admitted_policy.json';dump(policy,admitted)
        value.update(admission_status='ADMITTED',policy_path=str(policy))
        rows=[]
        for test in read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]:
            actual=evaluate_ecas(admitted,contract,test['input'],admission_mode='semantic')
            rows.append({'id':test['id'],'expected':test['expected'],'actual':actual,'pass':actual.get('decision')==test['expected'] and not actual.get('engine_error')})
        value['developer_results']={'passed':bool(rows) and all(x['pass'] for x in rows),'rows':rows}
        value['accepted']=value['developer_results']['passed']
    except PolicyError as error:
        value.update(error_type=type(error).__name__,reason=str(error),admission_status='REJECTED' if value['compile_status'] else None)
    dump(folder/'CHECKS.json',value)
    return value

def prepare_candidate(task,method):
    folder=ROOT/'method_runs'/task/method
    if (folder/'RESULT.json').exists():
        existing=read(folder/'RESULT.json')
        if existing.get('status')!='STARTED': return existing
    folder.mkdir(parents=True,exist_ok=True)
    result={'task':task,'method':method,'scope_id':CONFIG['scope_id'],'status':'STARTED','calls':[],'repaired_once':False,'execution_eligible':False}
    dump(folder/'RESULT.json',result)
    def invoke(stage,previous=None):
        output,record=call(task,method,stage,previous);result['calls'].append(record['index']);dump(folder/(stage+'.json'),output);return output
    if method=='ECAS_MATCHED':
        generated=invoke('ecas_generate')
        first_path=folder/'first_candidate.json';dump(first_path,generated['candidate']);freeze(folder,first_path,'FIRST_CANDIDATE')
        first=check_ecas(task,generated['candidate'],folder/'initial');result['first_checks']=first
        final=first
        if first.get('abstain'):
            result['status']='ABSTAIN'
        elif not first['accepted']:
            feedback={'prior_candidate':generated['candidate'],'developer_checks':first,
                      'common_developer_tests':read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]}
            repaired=invoke('ecas_repair',feedback);result['repaired_once']=True
            final=check_ecas(task,repaired['candidate'],folder/'repaired')
            result['status']='REPAIR_ABSTAIN' if final.get('abstain') else ('ELIGIBLE' if final['accepted'] else 'DEVELOPMENT_REJECTED')
        else:result['status']='ELIGIBLE'
        result['final_checks']=final
        result['execution_eligible']=final['accepted']
    else:
        p2p=method=='P2P_STYLE';previous={}
        if p2p:
            detection=invoke('p2p_detect')
            if detection['status']!='READY':
                result.update(status=detection['status'],reason=detection.get('reason'));return terminal(folder,result)
            extraction=invoke('p2p_extract',detection)
            if extraction['status']!='READY':
                result.update(status=extraction['status'],reason=extraction.get('reason'));return terminal(folder,result)
            grounded,receipt=ground_extraction(task,extraction)
            dump(folder/'GROUNDED_EXTRACTION.json',grounded);dump(folder/'GROUNDING_RECEIPT.json',receipt)
            if not receipt['accepted']:
                result.update(status='SCHEMA_GROUNDING_REJECTED',reason=receipt['reason']);return terminal(folder,result)
            previous={'detection':detection,'extraction':grounded}
        generated=invoke(METHOD_STAGE[method],previous or None)
        path=folder/'first_generation.json';dump(path,generated);freeze(folder,path,'FIRST_CANDIDATE')
        if generated['status']!='READY':
            result.update(status='ABSTAIN',reason=generated.get('reason'));return terminal(folder,result)
        common=read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]
        if p2p:
            auto_tests=invoke('p2p_tests',previous)
            packet=read(ROOT/'generation_inputs'/task/'packet.json')
            declared={x['path'] for x in packet['common_adapter']['request_and_trusted_paths']}
            sources={x['evidence_id'] for x in packet['visible_sources']}
            for test in auto_tests['tests']:
                if test['source_ref'] not in sources:raise ValueError('P2P developer source_ref not visible')
                if set(test['input'])-{'request','trusted'}:raise ValueError('P2P developer envelope contains undeclared top-level inputs')
                for field in test['input'].get('trusted',{}):
                    if '/trusted/'+field not in declared:raise ValueError('P2P developer trusted path not declared')
            tests=auto_tests['tests']+common;judge=None
        else:
            tests=common;judge=invoke('autopac_judge',generated)
        dump(folder/'DEVELOPER_TESTS.json',tests)
        first=policy_checks(generated['rego'],folder/'initial',p2p)
        first['developer_results']=run_tests(task,first['policy_path'],tests,folder/'initial') if first['accepted'] else {'passed':False,'rows':[]}
        first['judge']=judge;first['accepted']=first['accepted'] and first['developer_results']['passed'] and (not judge or judge['verdict']=='ACCEPT')
        dump(folder/'INITIAL_DEVELOPMENT.json',first);result['first_checks']=first;final=first
        if judge and judge['verdict']=='ABSTAIN':
            result['status']='JUDGE_ABSTAIN'
        elif not first['accepted']:
            feedback={'prior_generation':generated,'prior_extraction':previous,'developer_checks':first,'developer_tests':tests,'judge':judge}
            repaired=invoke('repair',feedback);result['repaired_once']=True
            if repaired['status']!='READY':
                result.update(status='REPAIR_ABSTAIN',reason=repaired.get('reason'));final={'accepted':False,'policy_path':None}
            else:
                final=policy_checks(repaired['rego'],folder/'repaired',p2p)
                final['developer_results']=run_tests(task,final['policy_path'],tests,folder/'repaired') if final['accepted'] else {'passed':False,'rows':[]}
                final['accepted']=final['accepted'] and final['developer_results']['passed']
                final['judge_after_repair']='NOT_RUN_ONE_REPAIR_BUDGET'
                result['status']='ELIGIBLE' if final['accepted'] else 'DEVELOPMENT_REJECTED'
        else:result['status']='ELIGIBLE'
        result['final_checks']=final
        result['execution_eligible']=final['accepted'] and result['status']=='ELIGIBLE'
    if result['final_checks'].get('policy_path'):
        freeze(folder,Path(result['final_checks']['policy_path']),'FINAL_POLICY')
    return terminal(folder,result)

def terminal(folder,result):
    result['generation_frozen_at']=now();result['final_evaluation_not_yet_read']=True
    dump(folder/'GENERATION_TERMINAL_FREEZE.json',{'task':result['task'],'method':result['method'],'status':result['status'],
          'execution_eligible':result['execution_eligible'],'first_freeze_sha256':sha(folder/'FIRST_CANDIDATE_FREEZE.json') if (folder/'FIRST_CANDIDATE_FREEZE.json').exists() else None,
          'frozen_at':result['generation_frozen_at'],'final_evaluation_not_yet_read':True})
    dump(folder/'RESULT.json',result);return result

def evaluate_policy(task,method,checks,folder,first=False):
    rows=[];branches=[]
    if not checks or not checks.get('policy_path'): return {'execution_status':'NO_COMPILED_POLICY','requests':rows,'branches':branches}
    path=Path(checks['policy_path'])
    if method=='ECAS_MATCHED':
        contract=read(ROOT/'execution_inputs'/task/'contract.json');policy=read(path)
        def decide(env,name): return evaluate_ecas(policy,contract,env,admission_mode='semantic')
    else:
        if checks.get('compile_exit') != 0 or not checks.get('format_receipt',{}).get('ast_semantics_equal_without_location'):
            return {'execution_status':'NO_COMPILED_POLICY','requests':rows,'branches':branches}
        def decide(env,name):return rego_decision(path,adapt(task,env),folder,name)
    for channel in ('O-L','O-I'):
        for index,vector in enumerate(read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']):
            actual=decide(vector['envelope'],'pair_'+channel+'_'+str(index))
            rows.append({'channel':channel,'input':vector['envelope'],'expected':vector['expected_class'],'actual':actual,
                         'pass':actual.get('decision')==vector['expected_class'] and not actual.get('engine_error') and actual.get('status','EXECUTED')=='EXECUTED'})
    for index,(label,envelope,expected,kind) in enumerate(read(ROOT/'sealed_evaluation/branch_protocol.json')['vectors'][task]):
        actual=decide(envelope,'branch_'+str(index))
        branches.append({'label':label,'input':envelope,'expected':expected,'kind':kind,'actual':actual,
                         'pass':actual.get('decision')==expected and not actual.get('engine_error') and actual.get('status','EXECUTED')=='EXECUTED'})
    return {'execution_status':'DIAGNOSTIC_ONLY' if first else 'ELIGIBLE_POLICY_EXECUTED','requests':rows,'branches':branches,
            'request_pair_correct':len(rows)==2 and all(x['pass'] for x in rows),'policy_sha256':sha(path),
            'eligibility_at_generation':checks['accepted'],'branch_classification':'HISTORICAL_POSTHOC_ENGINEERING_NOT_ACCURACY_DENOMINATOR'}

def require_gate(filename,token=False):
    value=read(ROOT/filename);data=value.get('data',value)
    if data.get('scope_id',CONFIG['scope_id'])!=CONFIG['scope_id']:raise RuntimeError('Gate scope mismatch')
    if token:
        if data.get('status') in ('block','FAIL','BLOCKED') or data.get('allow_formal_run',data.get('ready_for_formal_run')) is not True:
            raise RuntimeError('Token gate not ready')
    elif data.get('blockers') or data.get('ready_for_formal_run') is not True:
        raise RuntimeError('Scope gate not ready')

def smoke():
    require_gate('SCOPED_GATE_READY.json')
    if read(ROOT/'T0_RECEIPT.json')['status']!='PASS':raise RuntimeError('T0 not passed')
    results=[]
    plan=[('FSV-B19','P2P_STYLE','p2p_rego','p2p_all'),('FSV-B19','AUTOPAC_STYLE','autopac_generate','autopac_all'),
          ('FSV-B19','ECAS_MATCHED','ecas_generate','ecas_long'),('FSV-S03','ECAS_MATCHED','ecas_generate','ecas_type')]
    for task,method,stage,identity in plan:
        output,record=call(task,method,stage,smoke=True,smoke_id=identity)
        results.append({'case_id':task+'_'+identity,'coverage':identity,'dataset':'Fineract' if task=='FSV-S03' else 'ERPNext',
            'max_output_tokens':CONFIG['max_tokens'],'actual_output_tokens':record['usage']['completion_tokens'],'prompt_tokens':record['usage']['prompt_tokens'],
            'finish_reason':record['finish_reason'],'parse_status':'PASS','content_empty':False,'retry_count':0,'truncated':False,'call_index':record['index']})
        dump(ROOT/'SMOKE_RECORDS.json',results)
    print(compact({'status':'SMOKE_COMPLETE','smoke_calls':len(results)}),flush=True)

def run():
    require_gate('SCOPED_GATE_READY.json');require_gate('TOKEN_GATE_READY.json',True);verify_inputs()
    if STATE.exists():
        prior=read(STATE)
        if prior['status']=='COMPLETED':return
        raise RuntimeError('Prior run unresolved/stopped; diagnosis required before explicit resume')
    state={'status':'RUNNING','scope_id':CONFIG['scope_id'],'started_at':now(),'rows':[],'final_evaluation_read':False};dump(STATE,state)
    try:
        for task in CONFIG['tasks']:
            for method in CONFIG['methods']:
                result=prepare_candidate(task,method);state['rows'].append(result);dump(STATE,state)
                print(compact({'task':task,'method':method,'generation_status':result['status'],'execution_eligible':result['execution_eligible']}),flush=True)
        dump(ROOT/'ALL_GENERATION_FROZEN.json',{'scope_id':CONFIG['scope_id'],'frozen_at':now(),'count':len(state['rows']),
             'rows':[{'task':r['task'],'method':r['method'],'terminal_sha256':sha(ROOT/'method_runs'/r['task']/r['method']/'GENERATION_TERMINAL_FREEZE.json')} for r in state['rows']],
             'final_evaluation_not_yet_read':True})
        state['final_evaluation_read']=True
        for result in state['rows']:
            folder=ROOT/'method_runs'/result['task']/result['method']
            result['first_diagnostic']=evaluate_policy(result['task'],result['method'],result.get('first_checks'),folder/'first_diagnostic',True)
            result['final_evaluation']=evaluate_policy(result['task'],result['method'],result.get('final_checks'),folder/'final_evaluation') if result['execution_eligible'] else {'execution_status':'NOT_ELIGIBLE_NOT_EXECUTED','requests':[],'branches':[],'request_pair_correct':None}
            result['request_pair_correct']=result['final_evaluation'].get('request_pair_correct')
            result['evaluated_at']=now();dump(folder/'RESULT.json',result);dump(STATE,state)
        state.update(status='COMPLETED',completed_at=now());dump(STATE,state);verify_inputs()
    except Exception as error:
        state.update(status='STOPPED_PROTOCOL_OR_TRANSPORT',error_type=type(error).__name__,error=str(error).split('\n')[0][:1200],stopped_at=now());dump(STATE,state);raise

def stats():
    rows=[]
    for task in CONFIG['tasks']:
        for stage in TEMPLATES['stages']:
            prompt,_,_=make_prompt(task,stage)
            rows.append({'task':task,'stage':stage,'bytes':len(prompt.encode()),'estimated_prompt_tokens':(len(prompt.encode())+2)//3+128,'legacy_bytes_div_2_estimate':(len(prompt.encode())+1)//2+128})
    for task,stage,identity in [('FSV-B19','p2p_rego','p2p_all'),('FSV-B19','autopac_generate','autopac_all'),('FSV-B19','ecas_generate','ecas_long'),('FSV-S03','ecas_generate','ecas_type')]:
        prompt,_,_=make_prompt(task,stage,smoke=True,smoke_id=identity)
        rows.append({'task':task,'stage':stage,'smoke':True,'coverage':identity,'bytes':len(prompt.encode()),'estimated_prompt_tokens':(len(prompt.encode())+2)//3+128,'legacy_bytes_div_2_estimate':(len(prompt.encode())+1)//2+128})
    lengths=sorted(x['estimated_prompt_tokens'] for x in rows)
    quantiles={f'p{q}':lengths[round((len(lengths)-1)*q/100)] for q in (50,90,95,99)}
    value={'scope_id':CONFIG['scope_id'],'rows':rows,'quantiles':quantiles,'estimated_max':max(lengths),
           'estimate_kind':'UTF8_BYTES_DIV_3_HISTORICALLY_CALIBRATED_NOT_EXACT_OR_HARD_BOUND','cap':CONFIG['max_prompt_tokens'],'repair_feedback_checked_dynamically_before_call':True,
           'smoke_plan_covers':['longest ERPNext packet','Fineract type packet','P2P aggregate output','AutoPAC aggregate output','ECAS original schema']}
    dump(ROOT/'PROMPT_SIZE_PLAN.json',value)
    print(compact({k:v for k,v in value.items() if k!='rows'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['stats','smoke','run']);arguments=parser.parse_args()
    try:{'stats':stats,'smoke':smoke,'run':run}[arguments.mode]()
    except Exception as error:
        print(compact({'status':'STOPPED','error_type':type(error).__name__,'error':str(error).split('\n')[0][:1000]}),flush=True)
        raise SystemExit(2)
