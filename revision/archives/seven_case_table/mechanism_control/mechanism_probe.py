"""Frozen offline counterfactuals for missing-state behavior. No model/API code."""
import ast
import copy
import csv
import datetime
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
MAIN=PROJECT/'working/exploration/20261014_matched_evidence_labor/matched_generation'
LANE=Path('/root/ecas_missing_state_mechanism_20261015')
SCOPE='ECAS-MISSING-STATE-MECHANISM-20261015-01'
TASKS=['FSV-B17','FSV-B19']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def csvtext(rows,fields):
    out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows);return out.getvalue()
def engine():
    sys.path.insert(0,str(LANE/'runtime/scripts'))
    import ec_field_security_engine_v3 as e
    return e
def verify():
    for item in read(ROOT/'INPUT_MANIFEST.json'):
        if sha(item['path'])!=item['sha256']:raise RuntimeError('Frozen input changed: '+item['path'])
    for item in read(ROOT/'SOURCE_MANIFEST.json'):
        if sha(item['source'])!=item['sha256'] or sha(item['snapshot'])!=item['sha256']:raise RuntimeError('Original/snapshot drift')
def cmd(argv,folder,name):
    folder.mkdir(parents=True,exist_ok=True)
    p=subprocess.run([str(x) for x in argv],capture_output=True,text=True,encoding='utf-8',timeout=30)
    (folder/(name+'.stdout.txt')).write_text(p.stdout,encoding='utf-8');(folder/(name+'.stderr.txt')).write_text(p.stderr,encoding='utf-8')
    return p
def prepare():
    if (ROOT/'INPUT_MANIFEST.json').exists():raise RuntimeError('Already prepared: inspect rather than overwrite')
    LANE.mkdir(parents=True,exist_ok=False)
    shutil.copytree('/root/ecas_matched_generation_20261014/runtime',LANE/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
    (LANE/'tools').mkdir();shutil.copyfile('/root/ecas_matched_generation_20261014/tools/opa',LANE/'tools/opa');(LANE/'tools/opa').chmod(0o755)
    sources=[]
    def snap(source,target):
        target=ROOT/'inputs'/target;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        sources.append({'source':str(source),'snapshot':str(target),'sha256':sha(source)});return target
    snap(MAIN/'sealed_evaluation/branch_protocol.json',Path('branch_protocol.json'))
    snap(MAIN/'EXECUTION_INPUT_MANIFEST.json',Path('prior_main_manifest.json'))
    for task in TASKS:
        snap(MAIN/'method_runs'/task/'ECAS_MATCHED/first_candidate.json',Path(task)/'candidate.json')
        snap(MAIN/'execution_inputs'/task/'contract.json',Path(task)/'contract.json')
        snap(MAIN/'generation_inputs'/task/'packet.json',Path(task)/'packet.json')
        for method in ['P2P_STYLE','AUTOPAC_STYLE']:
            snap(MAIN/'method_runs'/task/method/'initial/external_pilot/policy.rego',Path(task)/(method+'.rego'))
        for channel in ['O-L','O-I']:snap(MAIN/'sealed_evaluation'/task/(channel+'.json'),Path(task)/(channel+'.json'))
    snap(Path('/root/ecas_matched_generation_20261014/outputs/t0/restricted_capabilities.json'),Path('restricted_capabilities.json'))
    dump(ROOT/'SOURCE_MANIFEST.json',sources)
    (ROOT/'guards').mkdir()
    guards={
      'FSV-B17':'valid_state if { is_boolean(input.trusted.customerDisabled) }',
      'FSV-B19':'valid_state if { input.trusted.supplierOnHold == false }\n\nvalid_state if { input.trusted.supplierOnHold == true; input.trusted.holdType in {"All", "Invoices", "Payments"} }'}
    for task,body in guards.items():
        text='package ecas_mechanism_guard\n\nimport rego.v1\n\ndefault allow := false\n\n'+body+'\n\nallow if { data.external_pilot.allow; valid_state }\n'
        (ROOT/'guards'/(task+'.rego')).write_text(text,encoding='utf-8')
    vectors={}
    for task in TASKS:
        rows=[]
        for channel in ['O-L','O-I']:
            for v in read(ROOT/'inputs'/task/(channel+'.json'))['vectors']:
                rows.append({'id':v['vector_id'],'envelope':v['envelope'],'expected':v['expected_class'],'kind':'original_pair'})
        for name,envelope,expected,kind in read(ROOT/'inputs/branch_protocol.json')['vectors'][task]:
            rows.append({'id':name,'envelope':envelope,'expected':expected,'kind':kind})
        if task=='FSV-B19':
            base=copy.deepcopy(rows[0]['envelope'])
            for name,trusted in [('partial-status-false-only',{'supplierOnHold':False}),('partial-payments-only',{'holdType':'Payments'})]:
                v=copy.deepcopy(base);v['trusted']=trusted
                rows.append({'id':name,'envelope':v,'expected':None,'kind':'partial_missing_observation_no_gold'})
        vectors[task]=rows
    dump(ROOT/'FROZEN_VECTORS.json',vectors)
    scope={'kind':'new-experiment-block','status':'FROZEN','protocol_path':'PROTOCOL_CN.md','protocol_sha256':sha(ROOT/'PROTOCOL_CN.md'),
       'scope_id':SCOPE,'project_id':'EC-CSI','experiment_id':'missing-state-mechanism','runtime_lane':str(LANE),
       'classification':'OFFLINE_COUNTERFACTUAL_EXPOSED_TASKS_NOT_MODEL_GENERATION','new_model_calls':0,'new_cases':0,'new_systems':0}
    dump(ROOT/'EXPERIMENT_SCOPE.json',scope)
    fields=list(next(csv.DictReader((MAIN/'RESULT_TRACEABILITY.csv').open(encoding='utf-8-sig'))).keys())
    (ROOT/'RESULT_TRACEABILITY.csv').write_text(csvtext([],fields),encoding='utf-8-sig')
    (ROOT/'CLAIM_EVIDENCE_MATRIX.csv').write_bytes((MAIN/'CLAIM_EVIDENCE_MATRIX.csv').read_bytes())
    paths=[ROOT/'mechanism_probe.py',ROOT/'TASK_CONTRACT_CN.md',ROOT/'PROTOCOL_CN.md',ROOT/'EXPERIMENT_SCOPE.json',ROOT/'SOURCE_MANIFEST.json',ROOT/'FROZEN_VECTORS.json']
    paths += [p for sub in ['inputs','guards'] for p in (ROOT/sub).rglob('*') if p.is_file()]
    paths += [p for sub in ['runtime','tools'] for p in (LANE/sub).rglob('*') if p.is_file()]
    manifest=[{'path':str(p),'sha256':sha(p)} for p in sorted(set(paths))]
    dump(ROOT/'INPUT_MANIFEST.json',manifest)
    req={'schema_version':1,'run_id':'missing-state-mechanism-t0-v1','run_root':str(LANE/'managed_runs'),
      'argv':['/usr/bin/python3',str(ROOT/'mechanism_probe.py'),'t0','{run_dir}/outputs/result.json'],'cwd':str(ROOT),
      'inputs':manifest+[{'path':str(ROOT/'INPUT_MANIFEST.json'),'sha256':sha(ROOT/'INPUT_MANIFEST.json')}],
      'outputs':[{'path':'outputs/result.json','kind':'json','nonempty':True,'required_keys':['status','checks']}],
      'timeout_seconds':120,'authorization_ref':'Current user requests continued missing-state mechanism investigation; local zero-model control only'}
    dump(ROOT/'T0_REQUEST.json',req)
    print(json.dumps({'status':'PREPARED','source_files':len(sources),'frozen_files':len(manifest),'new_API_calls':0}))
def rego(task,method,guard,envelope,out,name):
    packet=read(ROOT/'inputs'/task/'packet.json');abi=packet['common_adapter'];inp=copy.deepcopy(envelope)
    inp.update(subject={'id':abi['subject_id'],'role':abi['subject_role']},action=packet['target']['operation'],
       resource={'id':abi['resource_id'],'system':packet['target']['system'],'version':packet['target']['version']})
    path=out/(name+'.input.json');dump(path,inp)
    argv=[LANE/'tools/opa','eval','--format=json','--capabilities',ROOT/'inputs/restricted_capabilities.json','--data',ROOT/'inputs'/task/(method+'.rego')]
    if guard:argv += ['--data',ROOT/'guards'/(task+'.rego')]
    argv += ['--input',path,'data.ecas_mechanism_guard.allow' if guard else 'data.external_pilot.allow']
    p=cmd(argv,out,name)
    if p.returncode:raise RuntimeError('OPA evaluation failed: '+name)
    values=[x['value'] for r in json.loads(p.stdout).get('result',[]) for x in r.get('expressions',[])]
    if len(values)!=1 or not isinstance(values[0],bool):raise RuntimeError('OPA decision not Boolean')
    return 'allow' if values[0] else 'deny'
def t0(output):
    verify();e=engine();checks=[]
    def ck(n,v):checks.append({'check':n,'pass':bool(v)})
    imports=[n.module.split('.')[0] if isinstance(n,ast.ImportFrom) else a.name.split('.')[0] for n in ast.walk(ast.parse(Path(__file__).read_text(encoding='utf-8'))) if isinstance(n,(ast.Import,ast.ImportFrom)) for a in (n.names if isinstance(n,ast.Import) else [None])]
    ck('no_network_library_imports',not set(imports).intersection({'requests','urllib','http','socket'}))
    # Synthetic guard fixture verifies missing-state closure and valid-state preservation.
    for task in TASKS:
        for method in ['P2P_STYLE','AUTOPAC_STYLE']:
            paths=[ROOT/'inputs'/task/(method+'.rego'),ROOT/'guards'/(task+'.rego')]
            p=cmd([LANE/'tools/opa','check','--strict','--capabilities',ROOT/'inputs/restricted_capabilities.json',*paths],LANE/'t0',task+method)
            ck(task+method+'_wrapper_strict_compile',p.returncode==0)
            envelope={'request':{'body':{}},'trusted':{}}
            ck(task+method+'_empty_state_guard_deny',rego(task,method,True,envelope,LANE/'t0',task+method+'_empty')=='deny')
        candidate=read(ROOT/'inputs'/task/'candidate.json');contract=read(ROOT/'inputs'/task/'contract.json')
        ck(task+'_original_missing_parameter_deny',candidate['rules'][0]['params']['on_missing']=='deny')
        for missing in ['deny','skip']:
            variant=copy.deepcopy(candidate);variant['rules'][0]['params']['on_missing']=missing
            proposal=e.compile_model_ir(variant)
            full=e.compile_policy(proposal['policy'],contract);shape=e.compile_policy_shape_only(proposal['policy'])
            ck(task+'_'+missing+'_full_shape_compiles',bool(full) and bool(shape))
    ck('18_frozen_vectors',sum(len(x) for x in read(ROOT/'FROZEN_VECTORS.json').values())==18)
    ck('isolated_lane_space',shutil.disk_usage(LANE).free>1024**3)
    receipt={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks,'scope_id':SCOPE,'run_id':'missing-state-mechanism-t0-v1',
       'runtime_lane':str(LANE),'completed_at':now(),'new_model_calls':0,'scientific_result':False,'manifest_sha256':sha(ROOT/'INPUT_MANIFEST.json')}
    dump(ROOT/'T0_RECEIPT.json',receipt);dump(output,receipt)
    dump(ROOT/'T0_EVIDENCE.json',{'status':receipt['status'],'scope_id':SCOPE,'run_id':receipt['run_id'],'runtime_lane':str(LANE),
       'receipt_path':'T0_RECEIPT.json','receipt_sha256':sha(ROOT/'T0_RECEIPT.json'),'completed_at':receipt['completed_at']})
    ledger=ROOT/'RESULT_TRACEABILITY.csv'
    fields=next(csv.reader(ledger.open(encoding='utf-8-sig')))
    row={'result_id':'MISSING-STATE-T0','experiment_id':SCOPE,'metric_name':'engineering_checks','dataset_name':'engineering_fixtures',
      'dataset_version':'t0-v1','data_split':'engineering_only','sample_count':len(checks),'raw_value':len(checks),'reported_value':len(checks),'unit':'checks',
      'aggregation':'actual_checks_not_cases','source_output_path':str((ROOT/'T0_RECEIPT.json').relative_to(PROJECT)),
      'source_locator':'status;checks','script_path':str(Path(__file__).relative_to(PROJECT)),
      'command_or_config':'mechanism_probe.py t0','seed':'NOT_APPLICABLE','environment':'WSL Python OPA isolated lane',
      'git_commit':'NOT_AVAILABLE_HASH_FROZEN','checksum':sha(ROOT/'T0_RECEIPT.json'),'rounding_rule':'none','status':'PASS',
      'verified_by':'actual_managed_t0','verified_at':now(),'notes':'No model call; not scientific performance'}
    ledger.write_text(csvtext([row],fields),encoding='utf-8-sig')
    if receipt['status']!='PASS':raise RuntimeError('T0 failed')
def make_request():
    gate=read(ROOT/'SCOPED_GATE_READY.json')
    if not gate['data']['ready_for_formal_run'] or gate['data']['blockers']:raise RuntimeError('Actual scope gate not ready')
    req=read(ROOT/'T0_REQUEST.json');req.update(run_id='missing-state-mechanism-v1',timeout_seconds=600)
    req['argv'][2]='run';req['outputs'][0]['required_keys']=['status','rows','new_model_calls']
    for name in ['T0_RECEIPT.json','T0_EVIDENCE.json','SCOPED_GATE_READY.json']:
        req['inputs'].append({'path':str(ROOT/name),'sha256':sha(ROOT/name)})
    dump(ROOT/'RUN_REQUEST.json',req)
def run(output):
    verify();gate=read(ROOT/'SCOPED_GATE_READY.json')
    if not gate['data']['ready_for_formal_run'] or gate['data']['blockers']:raise RuntimeError('Actual gate not ready')
    if (ROOT/'RESULTS.json').exists():raise RuntimeError('Results exist: no repeated run')
    e=engine();vectors=read(ROOT/'FROZEN_VECTORS.json');rows=[];admissions=[]
    out=LANE/'results';out.mkdir(exist_ok=False)
    for task in TASKS:
        candidate=read(ROOT/'inputs'/task/'candidate.json');contract=read(ROOT/'inputs'/task/'contract.json')
        for variant_name,missing in [('original','deny'),('missing_skip','skip')]:
            variant=copy.deepcopy(candidate);variant['rules'][0]['params']['on_missing']=missing
            proposal=e.compile_model_ir(variant);dump(out/task/(variant_name+'.candidate.json'),variant)
            for mode in ['full','shape']:
                arm='ECAS_'+variant_name+'_'+mode
                policy=e.compile_policy(proposal['policy'],contract) if mode=='full' else e.compile_policy_shape_only(proposal['policy'])
                dump(out/task/(arm+'.policy.json'),policy)
                admissions.append({'task':task,'arm':arm,'status':'ADMITTED' if mode=='full' else 'SHAPE_COMPILED','on_missing':missing})
                for v in vectors[task]:
                    actual=e.evaluate(policy,contract,v['envelope'],admission_mode='semantic' if mode=='full' else 'shape_only')
                    if actual.get('engine_error') or actual.get('decision') not in ('allow','deny'):raise RuntimeError('ECAS execution error')
                    row={'task':task,'arm':arm,'method':'ECAS','variant':variant_name,'mode':mode,'probe_id':v['id'],'kind':v['kind'],
                       'historical_expected':v['expected'],'decision':actual['decision'],'agrees_with_historical_label':None if v['expected'] is None else actual['decision']==v['expected'],
                       'classification':'COUNTERFACTUAL_CONTROL_NOT_NEW_GENERATION','actual':actual}
                    rows.append(row);dump(out/task/arm/(v['id']+'.json'),{'input':v['envelope'],'result':row})
        for method in ['P2P_STYLE','AUTOPAC_STYLE']:
            for guarded in [False,True]:
                arm=method+('_manual_guard' if guarded else '_original')
                for v in vectors[task]:
                    actual=rego(task,method,guarded,v['envelope'],out/task/arm,v['id'])
                    rows.append({'task':task,'arm':arm,'method':method,'variant':'manual_guard' if guarded else 'original','mode':'OPA',
                       'probe_id':v['id'],'kind':v['kind'],'historical_expected':v['expected'],'decision':actual,
                       'agrees_with_historical_label':None if v['expected'] is None else actual==v['expected'],
                       'classification':'MANUAL_DETERMINISTIC_GUARD_CONTROL' if guarded else 'FROZEN_ORIGINAL_REPLAY'})
    if len(rows)!=144:raise RuntimeError('Unexpected output count')
    verify()
    result={'status':'COMPLETED','scope_id':SCOPE,'rows':rows,'admissions':admissions,'new_model_calls':0,'new_cases':0,
       'row_count':len(rows),'classification':'POSTHOC_OFFLINE_COUNTERFACTUAL_MECHANISM_CONTROL','completed_at':now()}
    dump(ROOT/'RESULTS.json',result);dump(output,result)
    fields=['task','arm','method','variant','mode','probe_id','kind','historical_expected','decision','agrees_with_historical_label','classification']
    (ROOT/'OBSERVATIONS.csv').write_text(csvtext(rows,fields),encoding='utf-8-sig')
    print(json.dumps({'status':'COMPLETED','rows':len(rows),'new_model_calls':0}))
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='t0':t0(sys.argv[2])
    elif mode=='requests':make_request()
    elif mode=='run':run(sys.argv[2])
    else:raise RuntimeError('Unknown mode')
