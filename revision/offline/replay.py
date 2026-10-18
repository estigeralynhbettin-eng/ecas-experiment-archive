#!/usr/bin/env python3
"""Whitelisted offline qualification and replay of immutable archived policies.

No historical generator is imported or executed. The only executable artifacts
are the fixed ECAS interpreter and the included OPA binary with no-network caps.
"""
from pathlib import Path, PurePosixPath
import argparse, ast, collections, copy, datetime, hashlib, importlib.metadata
import json, os, platform, shutil, subprocess, sys, traceback
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'runtime/engine/scripts'))
import ec_field_security_engine_v3 as engine

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def path(relative):
    p=PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:raise RuntimeError('Invalid packaged input: '+relative)
    return ROOT/relative
def manifest_check():
    m=read(ROOT/'MANIFEST.json');checked=0
    for e in m['files']:
        p=path(e['path'])
        if sha(p)!=e['sha256']:raise RuntimeError('Input digest mismatch: '+e['path'])
        checked+=1
    return checked
def tool(args,folder,name):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    env={k:v for k,v in os.environ.items() if not any(x in k.lower() for x in ['key','token','secret','password','proxy'])}
    env['NO_PROXY']='*'
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8',timeout=30,env=env)
    (folder/(name+'.stdout.txt')).write_text(p.stdout,encoding='utf-8')
    (folder/(name+'.stderr.txt')).write_text(p.stderr,encoding='utf-8')
    dump(folder/(name+'.exit.json'),{'exit_code':p.returncode,'argv':[str(x) if not str(x).startswith(str(ROOT)) else str(Path(x).relative_to(ROOT)) for x in args]})
    return p
def opa():
    p=path('runtime/bin/opa');p.chmod(p.stat().st_mode|0o111);return p
def capabilities(out):
    p=tool([opa(),'capabilities','--current'],out,'capabilities')
    if p.returncode:raise RuntimeError('OPA capabilities failed')
    cap=json.loads(p.stdout)
    forbidden={'http.send','net.lookup_ip_addr','opa.runtime','rand.intn','time.now_ns','print','internal.print'}
    cap['builtins']=[b for b in cap['builtins'] if b['name'] not in forbidden]
    cap['allow_net']=[];dump(out/'restricted_capabilities.json',cap)
    return out/'restricted_capabilities.json'
def check_rego(policy,cap,out):
    p=tool([opa(),'check','--strict','--capabilities',cap,policy],out,'check')
    return p.returncode
def evaluate_rego(policy,envelope,cap,out,name):
    inp=out/(name+'.input.json');dump(inp,envelope)
    p=tool([opa(),'eval','--capabilities',cap,'--format=json','--data',policy,'--input',inp,'data.external_pilot.allow'],out,name)
    if p.returncode:raise RuntimeError('OPA evaluation failed: '+name)
    rs=json.loads(p.stdout).get('result',[])
    if len(rs)!=1 or len(rs[0].get('expressions',[]))!=1:raise RuntimeError('Undefined/ambiguous OPA output')
    value=rs[0]['expressions'][0]['value']
    if type(value) is not bool:raise RuntimeError('OPA output is not boolean')
    return {'status':'EXECUTED','decision':'allow' if value else 'deny','exit_code':0}
def archive_adapter(t,envelope):
    """Compile only the original data adapter function, with relative ROOT."""
    source=path(t['adapter_source']);tree=ast.parse(source.read_text(encoding='utf-8'))
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='adapt']
    if len(nodes)!=1:raise RuntimeError('Exactly one original adapt function required')
    allowed={'read':read,'ROOT':source.parent,'json':json}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),allowed)
    value=allowed['adapt'](t['task'],copy.deepcopy(envelope))
    if value['request']!=envelope['request'] or value.get('trusted',{})!=envelope.get('trusted',{}):
        raise RuntimeError('Adapter changed business input')
    return value
def contains(v,candidate):
    if canonical(v)==canonical(candidate):return True
    if isinstance(v,dict):return any(contains(x,candidate) for x in v.values())
    if isinstance(v,list):return any(contains(x,candidate) for x in v)
    if isinstance(v,str):
        text=v.strip()
        if text.startswith('```'):text='\n'.join(text.splitlines()[1:-1])
        if text.startswith(('{','[')):
            try:return contains(json.loads(text),candidate)
            except ValueError:return False
    return False
def t0(out):
    if out.exists() and any(out.iterdir()):raise RuntimeError('T0 output must be new/empty')
    out.mkdir(parents=True,exist_ok=True);checks=[]
    count=manifest_check();checks.append({'check':'all_input_digests','pass':count>0,'files':count})
    cap=capabilities(out)
    version=tool([opa(),'version'],out,'opa_version')
    if version.returncode:raise RuntimeError('OPA cannot start')
    frozen=read(ROOT/'REPLAY_INPUT_INDEX.json')
    t=next(x for x in frozen['traces'] if x['method']=='ECAS_MATCHED')
    candidate=read(path(t['candidate']));contract=read(path(t['contract']))
    policy=engine.compile_model_ir(candidate)['policy'];engine.compile_policy(policy,contract)
    # Existing archived fixture: qualification check, not a new scientific case.
    f=t['fixtures'][0];envelope=f['mapped_input'] or archive_adapter(t,f['original_input'])
    actual=engine.evaluate(policy,contract,envelope,admission_mode='semantic')
    checks.append({'check':'frozen_engine_archived_fixture','pass':actual==f['archived_actual']})
    demo=out/'qualification.rego'
    demo.write_text('package external_pilot\nimport rego.v1\ndefault allow := false\nallow if { input.probe >= 0 }\n',encoding='utf-8')
    ck=check_rego(demo,cap,out/'opa_qualification')
    vals=[evaluate_rego(demo,{'probe':n},cap,out/'opa_qualification',str(n))['decision'] for n in [1,-1]]
    checks.append({'check':'opa_synthetic_allow_deny','pass':ck==0 and vals==['allow','deny'],'engineering_only':True})
    routes=Path('/proc/net/route').read_text() if Path('/proc/net/route').exists() else ''
    checks.append({'check':'no_nonloopback_network_route','pass':len(routes.splitlines())<=1,'required':True})
    checks.append({'check':'space_at_least_300MiB','pass':shutil.disk_usage(out).free>=300*1024**2})
    report={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,
       'python':sys.version,'platform':platform.platform(),'jsonschema':importlib.metadata.version('jsonschema'),
       'python_dependencies':{n:importlib.metadata.version(n) for n in ['jsonschema','jsonschema-specifications','referencing','rpds-py','attrs']},
       'network_route_table':routes,'uid':os.getuid(),'cwd':str(Path.cwd()),'artifact_root':str(ROOT),
       'offline_entry_sha256':sha(Path(__file__)),'engine_sha256':sha(path('runtime/engine/scripts/ec_field_security_engine_v3.py')),
       'opa_sha256':sha(opa()),'shared_services_started':[],'gpu_docker_model_api_used':False,'new_model_calls':0,
       'scientific_result':False,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    dump(out/'T0_RECEIPT.json',report)
    if report['status']!='PASS':raise RuntimeError('T0 failed')
    print(json.dumps({'status':'PASS','mode':'T0','input_files':count,'output':str(out)}))
def seven_cases(index,out,cap):
    rows=[]
    for t in index['traces']:
        folder=out/'seven_cases'/(t['batch']+'_'+t['task']+'_'+t['method']);folder.mkdir(parents=True)
        row={k:t[k] for k in ['batch','task','method','final_status','original_pre_format_status','source_result']}
        row['requests']=[]
        if t['final_status']=='OUT_OF_SCOPE':
            if t['policy'] or t['fixtures']:raise RuntimeError('Out-of-scope trace has an executable fixture')
            row.update(replay_status='NOT_EXECUTED_OUT_OF_SCOPE',qualification_match=True)
        elif t['final_status']=='DEVELOPMENT_REJECTED':
            if not t['policy'] or t['fixtures']:raise RuntimeError('Failed trace lacks its failed policy or has execution fixtures')
            exit_code=check_rego(path(t['policy']),cap,folder)
            if exit_code==0:raise RuntimeError('Originally rejected policy now compiles')
            row.update(replay_status='NOT_EXECUTED_COMPILE_REJECTED',qualification_match=True,compile_exit=exit_code)
        else:
            policy=path(t['policy']);contract=read(path(t['contract']))
            if t['method']=='ECAS_MATCHED':
                candidate=read(path(t['candidate']));compiled=engine.compile_model_ir(candidate)['policy']
                if compiled!=read(policy):raise RuntimeError('Compiled candidate differs from archived executable rule')
                engine.compile_policy(compiled,contract)
                if not any(contains(read(path(c['raw'])),candidate) for c in t['calls']):
                    raise RuntimeError('ECAS candidate absent from actual archived raw responses')
            elif check_rego(policy,cap,folder):raise RuntimeError('Eligible Rego no longer compiles')
            for j,f in enumerate(t['fixtures']):
                envelope=f['mapped_input'] if f['mapped_input'] is not None else archive_adapter(t,f['original_input'])
                dump(folder/(str(j)+'.mapped_input.json'),envelope)
                actual=engine.evaluate(compiled,contract,envelope,admission_mode='semantic') if t['method']=='ECAS_MATCHED' else evaluate_rego(policy,envelope,cap,folder,'request_'+str(j))
                match=actual==f['archived_actual']
                if not match:raise RuntimeError('Archived request observation mismatch: '+t['task']+'/'+t['method'])
                row['requests'].append({'channel':f['channel'],'expected':f['expected'],'actual':actual,'archive_match':match,
                  'matches_archived_label':actual['decision']==f['expected'],'synthetic_input':True})
            row.update(replay_status='EXECUTED',qualification_match=True)
        rows.append(row);dump(folder/'REPLAY_RESULT.json',row)
    return rows
def ablation(index,out):
    rows=[]
    for parent in index['ablation_parents']:
        candidate=read(path(parent['candidate']))
        if not contains(read(path(parent['raw_response'])),candidate) or not contains(read(path(parent['parsed_response'])),candidate):
            raise RuntimeError('Ablation parent is absent from original raw/parsed response')
    for v in index['variants']:
        archived=read(path(v['archived_result']));candidate=read(path(v['candidate']));contract=read(path(v['contract']))
        row={k:v[k] for k in ['row_id','parent_id','task','configuration','variant','classification']}
        row.update(full_executed=False,shape_executed=False,full_evaluations=[],shape_evaluations=[])
        try:
            compiled=engine.compile_model_ir(candidate)['policy'];row['ir_status']='COMPILED'
        except engine.PolicyError:
            row.update(ir_status='IR_SCHEMA_OR_TYPE_FAILURE',full_status='NOT_ATTEMPTED',shape_status='NOT_ATTEMPTED',eligible_admission_contrast=False)
        else:
            if compiled!=read(path(v['compiled_policy'])):raise RuntimeError('Variant compiled policy differs from archive')
            errors=engine.core._format_errors(engine.core.CONTRACT_VALIDATOR,contract);row['contract_shape_valid']=not bool(errors)
            try:engine.compile_policy(compiled,contract);row['full_status']='ADMITTED'
            except engine.PolicyError:row['full_status']='CONTRACT_SCHEMA_FAILURE' if errors else 'ADMISSION_REJECTED'
            try:engine.compile_policy_shape_only(compiled);row['shape_status']='COMPILED_NO_INVENTORY'
            except engine.PolicyError:row['shape_status']='POLICY_SCHEMA_OR_TYPE_FAILURE'
            row['eligible_admission_contrast']=row['contract_shape_valid'] and row['shape_status']=='COMPILED_NO_INVENTORY'
            fixtures=read(path(v['fixtures']))
            for arm,status,mode in [('full','ADMITTED','semantic'),('shape','COMPILED_NO_INVENTORY','shape_only')]:
                if row[arm+'_status']==status:
                    row[arm+'_executed']=True
                    for f in fixtures:
                        actual=engine.evaluate(compiled,contract if arm=='full' else None,f['input'],admission_mode=mode)
                        row[arm+'_evaluations'].append({'fixture_id':f['id'],'fixture_class':f['class'],'expected':f['expected'],'actual':actual,
                             'correct':None if f['expected'] is None else actual['decision']==f['expected'] and not actual.get('engine_error')})
        keys=['ir_status','full_status','shape_status','eligible_admission_contrast','full_executed','shape_executed','full_evaluations','shape_evaluations']
        if 'contract_shape_valid' in row:keys.append('contract_shape_valid')
        mismatches=[k for k in keys if row[k]!=archived.get(k,[] if k.endswith('_evaluations') else None)]
        row['archive_match']=not mismatches;row['mismatched_fields']=mismatches
        dump(out/'ablation'/v['row_id']/'REPLAY_RESULT.json',row)
        if mismatches:raise RuntimeError('Ablation archive mismatch '+v['row_id']+': '+','.join(mismatches))
        rows.append(row)
    return rows
def replay(out):
    if read(out/'T0_RECEIPT.json')['status']!='PASS':raise RuntimeError('Use successful T0 first')
    if (out/'REPLAY_SUMMARY.json').exists():raise RuntimeError('Replay output already exists; use a fresh run directory')
    files=manifest_check();index=read(ROOT/'REPLAY_INPUT_INDEX.json');cap=out/'restricted_capabilities.json'
    traces=seven_cases(index,out,cap);variants=ablation(index,out)
    failures={'evidence_refs_absent','evidence_version_mismatch','evidence_insufficient','required_binding_facts_absent','trusted_path_to_unregistered_client_path'}
    invalid=[r for r in variants if r['variant'] in failures]
    counts={'traces':len(traces),'qualified_traces':sum(r['replay_status']=='EXECUTED' for r in traces),
       'unexecuted_traces':sum(r['replay_status']!='EXECUTED' for r in traces),'original_request_decisions':sum(len(r['requests']) for r in traces),
       'ablation_rows':len(variants),'ablation_parents':len({r['parent_id'] for r in variants}),
       'admission_contrast':sum(r['eligible_admission_contrast'] for r in variants),
       'schema_controls':sum(r['classification'].startswith('ENGINEERING') for r in variants),
       'invalid_evidence_or_path_variants':len(invalid)}
    if counts!=index['expected_counts']:raise RuntimeError('Count reconciliation failed')
    if not all(r['full_status']=='ADMISSION_REJECTED' and not r['full_executed'] and r['shape_status']=='COMPILED_NO_INVENTORY' for r in invalid):raise RuntimeError('51-variant mechanism reconciliation failed')
    observations=sum(len(r['full_evaluations'])+len(r['shape_evaluations']) for r in variants)
    report={'status':'PASS','counts':counts,'ablation_engine_observations':observations,'all_archived_qualifications_and_observations_match':True,
        'manifest_files_reverified':files,'new_model_calls':0,'new_candidate_generation':0,'new_independent_cases':0,
        'method_scope':'Archived selected outputs, not native baseline reproduction or fresh LLM evaluation',
        'not_executed_scopes':['E17 model Judge','E18 qualitative semantic reading','E19 full missing-state control','E20-E21 full source-function probe'],
        'traces':traces,'variants':variants,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    dump(out/'REPLAY_SUMMARY.json',report);manifest_check()
    print(json.dumps({'status':'PASS','mode':'ARCHIVED_ENGINE_REPLAY','counts':counts,'ablation_engine_observations':observations,'new_model_calls':0}))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['t0','replay']);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    out=args.output.resolve()
    if out.is_relative_to(ROOT):raise RuntimeError('Outputs must be outside the extracted immutable artifact')
    try:
        if args.mode=='t0':t0(out)
        else:replay(out)
    except Exception:
        out.mkdir(parents=True,exist_ok=True);(out/'FAILURE.log').write_text(traceback.format_exc(),encoding='utf-8');raise
if __name__=='__main__':main()
