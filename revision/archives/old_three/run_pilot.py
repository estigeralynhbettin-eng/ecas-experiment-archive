"""Serial adapted policy pilot via approved GLM wrapper with immutable raw evidence."""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from jsonschema import Draft202012Validator
from pilot_lib import ROOT,LANE,CONFIG,read,dump,sha,verify_inputs,adapt,policy_checks,rego_decision,run_tests,compile_model_ir,compile_policy,evaluate_ecas,PolicyError

TEMPLATES=read(ROOT/'PROMPT_TEMPLATES.json')
CALLS=ROOT/'CALL_LEDGER.json'
SCHEMA=read(ROOT/'execution_inputs/ecas_output_schema.json')
STATE=ROOT/'EXECUTION_STATE.json'

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def c(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def winpath(p):
    out=subprocess.run(['wslpath','-w',str(p)],capture_output=True,text=True,check=True)
    return out.stdout.strip()
def make_prompt(task,stage,previous=None,smoke=False):
    packet=read(ROOT/'generation_inputs'/task/'packet.json')
    org=read(ROOT/'generation_inputs'/task/'organization_schema.json')
    payload={'packet':packet,'organization_schema':org}
    if previous is not None:payload['prior_stage_data']=previous
    if stage=='ecas_generate':payload['output_schema']=TEMPLATES['ecas_prompt_schema']
    instruction=TEMPLATES['stages'][stage]
    if smoke:
        # Superset developer interface exercises both case datasets, full longest
        # document, and the method's output modes; outputs never enter effect results.
        if stage!='ecas_generate':payload['additional_public_case']=read(ROOT/'generation_inputs/FSV-S02/packet.json')
        if stage=='p2p_rego':
            instruction='Developer token/interface smoke. Return {detection:{status,statements:[{text,evidence_refs}]},extraction:{status,components:[{decision,subject,action,resource,condition,purpose,evidence_refs}]},policy:{status,rego,reason},tests:[{id,input:{request:{body:{}},trusted:{}},expected:allow|deny,source_ref}]}. Use all stages of a P2P-style pipeline. If OUT_OF_SCOPE use an abstention and report it; still demonstrate a synthetic Rego allow decision for input.request.body.probe > 0 and two synthetic tests. Never treat the synthetic probe as this case policy. Include source references. Rego must use package external_pilot, import rego.v1 and default allow := false.'
        elif stage=='autopac_generate':
            instruction='Developer token/interface smoke. Return {generation:{status,rego,reason},judge:{verdict:ACCEPT|REVISE|ABSTAIN,issues:[string]}} for an AutoPAC-style generation+Judge interface. Use package external_pilot, import rego.v1 and default allow := false. Do not use hidden tests.'
    key=f'{task}_{stage}_{"SMOKE" if smoke else "MAIN"}'
    begin='BEGIN_'+key;end='END_'+key
    prompt=TEMPLATES['common']+f'BEGIN={begin}\nEND={end}\nSTAGE={stage}\n'+instruction+'\nVISIBLE_INPUT='+c(payload)
    return prompt,begin,end

def validate_stage(stage,out,smoke=False):
    if not isinstance(out,dict):raise ValueError('Stage output must be an object')
    if smoke:
        if stage=='p2p_rego':
            for k in ('detection','extraction','policy','tests'):
                if k not in out:raise ValueError('Missing smoke field '+k)
            if not isinstance(out['tests'],list) or not out['tests']:raise ValueError('Empty smoke tests')
        elif stage=='autopac_generate':
            if not {'generation','judge'}.issubset(out):raise ValueError('Incomplete AutoPAC smoke')
        else:Draft202012Validator(SCHEMA).validate(out['candidate'])
    elif stage=='ecas_generate':Draft202012Validator(SCHEMA).validate(out['candidate'])
    elif stage in ('p2p_detect','p2p_extract'):
        if out.get('status') not in ('READY','OUT_OF_SCOPE','ABSTAIN'):raise ValueError('Invalid extraction status')
        field='statements' if stage=='p2p_detect' else 'components'
        if out['status']=='READY' and not isinstance(out.get(field),list):raise ValueError('Missing '+field)
    elif stage=='p2p_tests':
        if not isinstance(out.get('tests'),list):raise ValueError('Missing tests')
    elif stage=='autopac_judge':
        if out.get('verdict') not in ('ACCEPT','REVISE','ABSTAIN'):raise ValueError('Invalid judge verdict')
    else:
        if out.get('status') not in ('READY','ABSTAIN'):raise ValueError('Invalid policy status')
        if out.get('status')=='READY' and not isinstance(out.get('rego'),str):raise ValueError('Missing Rego')

def normalize_stage(stage,out):
    result=json.loads(json.dumps(out))
    changes=[]
    if stage=='p2p_extract' and result.get('status')=='EXTRACTED' and isinstance(result.get('components'),list) and result['components']:
        result['status']='READY';changes.append({'field':'status','from':'EXTRACTED','to':'READY','classification':'EQUIVALENT_COMPLETED_EXTRACTION_STATUS_ALIAS'})
    return result,changes

def call(task,stage,previous=None,smoke=False):
    verify_inputs()
    ledger=read(CALLS) if CALLS.exists() else []
    prompt,begin,end=make_prompt(task,stage,previous,smoke)
    prompt_hash=hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    # Exact prompt identity and raw integrity provide idempotent local resume.
    # No API is called again for completed or locally recoverable existing output.
    for existing in reversed(ledger):
        if existing.get('prompt_sha256')!=prompt_hash:continue
        raw_path=Path(existing['raw_response_path'])
        if existing['status']=='COMPLETED':
            if sha(raw_path)!=existing['raw_response_sha256']:raise RuntimeError('Cached raw hash changed')
            output=read(existing['output_path']);validate_stage(stage,output,smoke)
            print(c({'reused_call':existing['index'],'stage':stage,'no_new_api_call':True}),flush=True)
            return output,existing
        if existing['status']=='STOPPED_PROTOCOL_OR_TRANSPORT' and stage=='p2p_extract' and existing.get('finish_reason')=='stop' and raw_path.exists():
            if sha(raw_path)!=existing['raw_response_sha256']:raise RuntimeError('Recovery raw hash changed')
            raw=read(raw_path);content=json.loads(raw['choices'][0]['message']['content'])
            if raw.get('model')!='glm-5.2' or content.get('begin')!=begin or content.get('end')!=end or content.get('stage')!=stage:raise RuntimeError('Recovery identity mismatch')
            recovered,changes=normalize_stage(stage,content['output'])
            if not changes:raise RuntimeError('Prior failed output is not eligible for local alias recovery')
            validate_stage(stage,recovered,smoke)
            rp=raw_path.parent/'recovered_output.json';dump(rp,recovered)
            dump(raw_path.parent/'LOCAL_RECOVERY_RECEIPT.json',{'original_status':existing['status'],'changes':changes,'raw_sha256':sha(raw_path),'recovered_output_sha256':sha(rp),'business_rules_changed':False,'new_model_calls':0,'checked_at':now()})
            existing.update({'local_recovery_status':'RECOVERED_LOCAL_STATUS_ALIAS','recovered_output_path':str(rp),'recovered_output_sha256':sha(rp)})
            dump(CALLS,ledger)
            print(c({'recovered_call':existing['index'],'stage':stage,'no_new_api_call':True}),flush=True)
            return recovered,existing
        raise RuntimeError('Exact prior failed prompt requires diagnosis, not automatic API retry')
    if len(ledger)>=CONFIG['max_calls']:raise RuntimeError('Authorized call budget exhausted')
    if smoke and sum(x['smoke'] for x in ledger)>=CONFIG['max_smoke_calls']:raise RuntimeError('Smoke budget exhausted')
    idx=len(ledger)+1;name=f'{idx:02d}_{task}_{stage}'
    folder=ROOT/'calls'/name;folder.mkdir(parents=True,exist_ok=False)
    pp=folder/'prompt.txt';pp.write_text(prompt,encoding='utf-8')
    # GLM's public exact tokenizer for this closed model is not available here.
    # Conservative lexical estimate is disclosed; actual provider usage is the
    # mandatory observed count, never labelled as locally exact.
    estimate=(len(prompt.encode('utf-8'))+1)//2+128
    if estimate>CONFIG['max_prompt_tokens']:raise RuntimeError('Conservative prompt estimate exceeds authorization')
    item={'index':idx,'task':task,'stage':stage,'smoke':smoke,'started_at':now(),'status':'STARTED','prompt_path':str(pp),'prompt_sha256':sha(pp),'prompt_bytes':len(prompt.encode()),'estimated_prompt_tokens':estimate,'token_count_kind':'UTF8_BYTES_DIV_2_ESTIMATE_NOT_EXACT_GLM_TOKENIZER','raw_response_path':str(folder/'response.raw.json'),'max_tokens':CONFIG['max_tokens'],'retry_count':0}
    ledger.append(item);dump(CALLS,ledger)
    args=[CONFIG['pwsh'],'-NoProfile','-File',winpath(CONFIG['model_wrapper']),'-PromptFile',winpath(pp),'-Model','glm-5.2','-Thinking','enabled','-ReasoningEffort','high','-MaxTokens',str(CONFIG['max_tokens']),'-ResponseFormat','json_object','-TimeoutSec',str(CONFIG['timeout_seconds']),'-RawResponsePath',winpath(folder/'response.raw.json'),'-ContentOutputPath',winpath(folder/'content.json'),'-SummaryOutputPath',winpath(folder/'wrapper_summary.json'),'-SummaryOnly','-AsJson','-BeginSentinel',begin,'-EndSentinel',end]
    start=time.monotonic()
    try:
        with (folder/'wrapper.stdout.txt').open('w',encoding='utf-8') as stdout,(folder/'wrapper.stderr.txt').open('w',encoding='utf-8') as stderr:
            proc=subprocess.run(args,stdout=stdout,stderr=stderr,timeout=CONFIG['timeout_seconds']+30)
        item['wrapper_exit']=proc.returncode;item['latency_seconds']=round(time.monotonic()-start,3)
        if proc.returncode:raise RuntimeError('Approved wrapper failed; consult local evidence')
        summary=read(folder/'wrapper_summary.json');raw=read(folder/'response.raw.json');content=read(folder/'content.json')
        item.update({'raw_response_sha256':sha(folder/'response.raw.json'),'raw_response_bytes':(folder/'response.raw.json').stat().st_size,'returned_model':raw.get('model'),'finish_reason':raw['choices'][0]['finish_reason'],'usage':raw.get('usage'),'cost_status':summary.get('cost_status'),'capture_mode':summary.get('capture_mode'),'content_chars':summary.get('normalized_content_chars')})
        if item['returned_model']!='glm-5.2' or item['finish_reason']!='stop':raise RuntimeError('Model/finish identity gate failed')
        if content.get('begin')!=begin or content.get('end')!=end or content.get('stage')!=stage:raise ValueError('Sentinel/stage mismatch')
        usage=item['usage'] or {}
        if not isinstance(usage.get('prompt_tokens'),int) or usage['prompt_tokens']>CONFIG['max_prompt_tokens']:raise RuntimeError('Observed prompt token gate failed')
        if not isinstance(usage.get('completion_tokens'),int) or usage['completion_tokens']>CONFIG['max_tokens']:raise RuntimeError('Observed completion token gate failed')
        normalized_output,changes=normalize_stage(stage,content['output'])
        validate_stage(stage,normalized_output,smoke)
        item.update({'status':'COMPLETED','parse_status':'PASS','completeness_gate':'PASS','completed_at':now(),'output_path':str(folder/'parsed_output.json')})
        dump(folder/'parsed_output.json',normalized_output)
        if changes:
            item['format_normalizations']=changes
            dump(folder/'FORMAT_NORMALIZATION.json',{'changes':changes,'business_rules_changed':False,'raw_sha256':item['raw_response_sha256']})
        dump(CALLS,ledger)
        print(c({'call':idx,'task':task,'stage':stage,'smoke':smoke,'status':'COMPLETED','prompt_tokens':usage.get('prompt_tokens'),'completion_tokens':usage.get('completion_tokens')}),flush=True)
        verify_inputs();return normalized_output,item
    except Exception as exc:
        error_message=str(exc).split('\n')[0][:2000]
        item.update({'status':'STOPPED_PROTOCOL_OR_TRANSPORT','error_type':type(exc).__name__,'error':error_message,'completed_at':now()})
        rawp=folder/'response.raw.json'
        if rawp.exists():
            item['raw_response_sha256']=sha(rawp)
            try:
                raw=read(rawp);item['usage']=raw.get('usage');item['returned_model']=raw.get('model');item['finish_reason']=raw['choices'][0]['finish_reason']
            except Exception:pass
        dump(CALLS,ledger);raise

def recover_ecas_smoke():
    out,rec=call('FSV-S04','ecas_generate',smoke=True)
    results=[]
    ledger=read(CALLS)
    for record in ledger:
        if record.get('smoke') and record['status']=='COMPLETED':
            results.append({'case_id':'FSV-S04_'+record['stage'],'coverage':record['stage'],'dataset':'ERPNext+Fineract_public_smoke' if record['stage']!='ecas_generate' else 'ERPNext','max_output_tokens':CONFIG['max_tokens'],'actual_output_tokens':record['usage']['completion_tokens'],'prompt_tokens':record['usage']['prompt_tokens'],'finish_reason':record['finish_reason'],'parse_status':'PASS','content_empty':False,'retry_count':0,'truncated':False})
    dump(ROOT/'SMOKE_RECORDS.json',results)
    print(c({'status':'SMOKE_RECOVERED_NEW_PROMPT','total_smoke_calls':sum(x['smoke'] for x in ledger),'valid_smoke_records':len(results)}),flush=True)

def final_rego(task,method,policy,folder):
    rows=[]
    for channel in ('O-L','O-I'):
        vectors=read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']
        for i,v in enumerate(vectors):
            observed=rego_decision(policy,adapt(task,v['envelope']),folder,f'final_{channel}_{i}')
            rows.append({'channel':channel,'input':v['envelope'],'expected':v['expected_class'],'actual':observed})
    return rows

def pipeline(task,method):
    folder=ROOT/'effect_runs'/task/method
    if (folder/'RESULT.json').exists():
        existing=read(folder/'RESULT.json')
        if existing['status']!='STARTED':return existing
    folder.mkdir(parents=True,exist_ok=True)
    output={'task':task,'method':method,'classification':CONFIG['classification'],'status':'STARTED','requests':[],'calls':[]}
    dump(folder/'RESULT.json',output)
    if method=='ECAS_MATCHED':
        candidate,rec=call(task,'ecas_generate');output['calls'].append(rec['index']);dump(folder/'candidate.json',candidate['candidate'])
        compiled=compile_model_ir(candidate['candidate']);dump(folder/'compiled_proposal.json',compiled)
        if compiled.get('decision')=='abstain' or not compiled.get('policy'):
            output.update({'status':'ABSTAIN','proposal':compiled})
        else:
            contract=read(ROOT/'execution_inputs'/task/'contract.json')
            try:
                admitted=compile_policy(compiled['policy'],contract);output['admission']='ADMITTED';dump(folder/'admitted_policy.json',admitted)
                for channel in ('O-L','O-I'):
                    for v in read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']:
                        observed=evaluate_ecas(admitted,contract,v['envelope'],admission_mode='semantic')
                        output['requests'].append({'channel':channel,'input':v['envelope'],'expected':v['expected_class'],'actual':observed})
                output['status']='EVALUATED'
            except PolicyError as exc:output.update({'status':'ADMISSION_REJECTED','admission':'REJECTED','reason':str(exc)})
    else:
        is_p2p=method=='P2P_STYLE'
        previous={}
        if is_p2p:
            detection,rec=call(task,'p2p_detect');output['calls'].append(rec['index']);dump(folder/'detection.json',detection)
            if detection['status']!='READY':
                output.update({'status':detection['status'],'reason':detection.get('reason')});dump(folder/'RESULT.json',output);return output
            extraction,rec=call(task,'p2p_extract',detection);output['calls'].append(rec['index']);dump(folder/'extraction.json',extraction)
            if extraction['status']!='READY':
                output.update({'status':extraction['status'],'reason':extraction.get('reason')});dump(folder/'RESULT.json',output);return output
            # Deterministic organization grounding check, apart from semantics.
            org=read(ROOT/'generation_inputs'/task/'organization_schema.json')
            for component in extraction.get('components',[]):
                for field in ('subject','action','resource'):
                    val=component.get(field)
                    if val not in org[field]:
                        output.update({'status':'SCHEMA_GROUNDING_REJECTED','reason':field+' not in organization schema'});dump(folder/'RESULT.json',output);return output
            previous={'detection':detection,'extraction':extraction}
        stage='p2p_rego' if is_p2p else 'autopac_generate'
        generation,rec=call(task,stage,previous or None);output['calls'].append(rec['index']);dump(folder/'generation.json',generation)
        if generation['status']!='READY':
            output.update({'status':'ABSTAIN','reason':generation.get('reason')});dump(folder/'RESULT.json',output);return output
        if is_p2p:
            generated_tests,rec=call(task,'p2p_tests',previous);output['calls'].append(rec['index']);tests=generated_tests['tests'];dump(folder/'generated_developer_tests.json',tests)
            judge=None
        else:
            judge,rec=call(task,'autopac_judge',generation);output['calls'].append(rec['index']);dump(folder/'judge.json',judge)
            tests=read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]
            if judge['verdict']=='ABSTAIN':
                output.update({'status':'JUDGE_ABSTAIN','reason':judge.get('issues')});dump(folder/'RESULT.json',output);return output
        checks=policy_checks(generation['rego'],folder/'initial',is_p2p)
        dev_result=run_tests(task,checks['policy_path'],tests,folder/'initial') if checks['accepted'] else {'passed':False,'rows':[]}
        needs_repair=not checks['accepted'] or not dev_result['passed'] or (judge and judge['verdict']=='REVISE')
        if needs_repair:
            feedback={'prior_generation':generation,'developer_checks':checks,'developer_tests':tests,'developer_results':dev_result,'judge':judge,'prior_extraction':previous}
            repaired,rec=call(task,'repair',feedback);output['calls'].append(rec['index']);dump(folder/'repair.json',repaired)
            if repaired['status']!='READY':
                output.update({'status':'REPAIR_ABSTAIN','reason':repaired.get('reason')});dump(folder/'RESULT.json',output);return output
            checks=policy_checks(repaired['rego'],folder/'repaired',is_p2p)
            dev_result=run_tests(task,checks['policy_path'],tests,folder/'repaired') if checks['accepted'] else {'passed':False,'rows':[]}
            output['repaired_once']=True
        output['developer_checks']=checks;output['developer_results']=dev_result
        if not checks['accepted'] or not dev_result['passed']:
            output['status']='DEVELOPMENT_REJECTED'
        else:
            # Frozen candidate is recorded before any final request/label is read.
            dump(folder/'CANDIDATE_FREEZE.json',{'policy_path':checks['policy_path'],'policy_sha256':sha(checks['policy_path']),'frozen_at':now(),'final_evaluation_not_yet_read':True})
            output['requests']=final_rego(task,method,checks['policy_path'],folder)
            output['status']='EVALUATED'
    output['request_pair_correct']=output['status']=='EVALUATED' and len(output['requests'])==2 and all(x['actual'].get('decision')==x['expected'] and not x['actual'].get('engine_error') for x in output['requests'])
    output['completed_at']=now();dump(folder/'RESULT.json',output);return output

def smoke():
    gate=read(ROOT/'SCOPED_GATE_READY.json')['data']
    if gate.get('blockers') or not gate.get('ready_for_formal_run'):raise RuntimeError('Scope gate not ready')
    results=[]
    for stage in ('p2p_rego','autopac_generate','ecas_generate'):
        out,rec=call('FSV-S04',stage,smoke=True)
        results.append({'case_id':'FSV-S04_'+stage,'coverage':stage,'dataset':'ERPNext+Fineract_public_smoke','max_output_tokens':CONFIG['max_tokens'],'actual_output_tokens':rec['usage']['completion_tokens'],'prompt_tokens':rec['usage']['prompt_tokens'],'finish_reason':rec['finish_reason'],'parse_status':'PASS','content_empty':False,'retry_count':0,'truncated':False})
    dump(ROOT/'SMOKE_RECORDS.json',results)
    print(c({'status':'SMOKE_COMPLETE','calls':len(results)}),flush=True)

def run():
    gate=read(ROOT/'TOKEN_GATE_READY.json')['data']
    if gate.get('status')=='block' or not gate.get('allow_formal_run',gate.get('ready_for_formal_run',True)):raise RuntimeError('Token gate blocked')
    if STATE.exists() and read(STATE).get('status')=='RUNNING':raise RuntimeError('Run already active/unknown')
    rows=[];dump(STATE,{'status':'RUNNING','started_at':now(),'rows':rows})
    try:
        for task in CONFIG['tasks']:
            for method in ('P2P_STYLE','AUTOPAC_STYLE','ECAS_MATCHED'):
                result=pipeline(task,method);rows.append(result);dump(STATE,{'status':'RUNNING','rows':rows})
                print(c({'task':task,'method':method,'status':result['status'],'pair_correct':result.get('request_pair_correct')}),flush=True)
        dump(STATE,{'status':'COMPLETED','completed_at':now(),'rows':rows});verify_inputs()
    except Exception as exc:
        dump(STATE,{'status':'STOPPED_PROTOCOL_OR_TRANSPORT','completed_at':now(),'rows':rows,'error_type':type(exc).__name__,'error':str(exc)})
        raise

def prompt_stats():
    rows=[]
    for task in CONFIG['tasks']:
        for stage in TEMPLATES['stages']:
            p,_,_=make_prompt(task,stage);rows.append({'task':task,'stage':stage,'bytes':len(p.encode()),'estimated_prompt_tokens':(len(p.encode())+1)//2+128})
    for stage in ('p2p_rego','autopac_generate','ecas_generate'):
        p,_,_=make_prompt('FSV-S04',stage,smoke=True);rows.append({'task':'FSV-S04','stage':stage,'smoke':True,'bytes':len(p.encode()),'estimated_prompt_tokens':(len(p.encode())+1)//2+128})
    dump(ROOT/'PROMPT_SIZE_PLAN.json',{'count_kind':'UTF8_BYTES_DIV_2_ESTIMATE','rows':rows,'note':'Exact prompt token counts come only from provider smoke usage; no exact local closed-model tokenizer is available. Repair/intermediate prompts additionally checked before every call.'})
    print(c({'rows':len(rows),'estimated_max':max(r['estimated_prompt_tokens'] for r in rows),'smoke':[r for r in rows if r.get('smoke')]}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['stats','smoke','recover_ecas_smoke','run']);args=parser.parse_args()
    try:{'stats':prompt_stats,'smoke':smoke,'recover_ecas_smoke':recover_ecas_smoke,'run':run}[args.mode]()
    except Exception as exc:
        print(c({'status':'STOPPED','error_type':type(exc).__name__,'error':str(exc).split('\n')[0][:1000]}),flush=True)
        raise SystemExit(2)
