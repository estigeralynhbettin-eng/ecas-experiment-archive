#!/usr/bin/env python3
"""Local, same-candidate Inventory admission ablation. Never calls a model."""
from __future__ import annotations
import copy
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[1]
LANE = Path('/root/ecas_evidence_ablation_20261014')
OLD_RUNTIME = Path('/root/ecas_four_case_peer_20261014/runtime')
SCOPE_ID = 'ECAS-SAME-CANDIDATE-EVIDENCE-ABLATION-20261014-01'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def engine():
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(LANE/'runtime/scripts'))
    import ec_field_security_engine_v3 as e
    return e
def copy_source(p, dest, manifest, category):
    p, dest = Path(p), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p, dest)
    if sha(p) != sha(dest): raise RuntimeError('snapshot hash mismatch')
    dest.chmod(0o444)
    manifest.append({'original':str(p), 'snapshot':str(dest), 'sha256':sha(p), 'category':category})
    return dest
def contains_candidate(value, candidate):
    if isinstance(value, dict):
        if canonical(value) == canonical(candidate): return True
        return any(contains_candidate(v, candidate) for v in value.values())
    if isinstance(value, list): return any(contains_candidate(v,candidate) for v in value)
    if isinstance(value,str):
        t = value.strip()
        if t.startswith('```'):
            t = '\n'.join(t.splitlines()[1:-1])
        if t.startswith(('{','[')):
            try: return contains_candidate(json.loads(t),candidate)
            except ValueError: pass
    return False

def prepare():
    if LANE.exists() or (ROOT/'INPUT_MANIFEST.json').exists():
        raise RuntimeError('lane/scope already prepared; do not overwrite')
    LANE.mkdir(parents=True)
    manifest=[]
    for p in sorted(OLD_RUNTIME.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            copy_source(p, LANE/'runtime'/p.relative_to(OLD_RUNTIME), manifest, 'unchanged_engine')
    parents=[]
    specs=[('FSV-B06','three_case_v1','20261014_external_baseline_pilot','effect_runs'),
           ('FSV-S02','three_case_v1','20261014_external_baseline_pilot','effect_runs'),
           ('FSV-S04','three_case_v1','20261014_external_baseline_pilot','effect_runs')]
    for task in ['FSV-S03','FSV-B13','FSV-B17','FSV-B19']:
        specs += [(task,'four_case_v1','20261014_four_case_peer_baselines','effect_runs'),
                  (task,'four_case_v2','20261014_four_case_peer_baselines','documented_ecas')]
    for task,config,scope,batch in specs:
        source=BASE/scope; folder=source/batch/task/'ECAS_MATCHED'
        parent_id=task+'__'+config; snap=LANE/'inputs'/parent_id
        cp=copy_source(folder/'candidate.json', snap/'candidate.json', manifest, 'archived_model_candidate')
        ct=copy_source(source/'execution_inputs'/task/'contract.json', snap/'contract.json',manifest,'archived_inventory')
        rr=copy_source(folder/'RESULT.json',snap/'original_result.json',manifest,'archived_observed_result')
        fixtures=[]
        for channel in ['O-L','O-I']:
            f=copy_source(source/'sealed_evaluation'/task/(channel+'.json'),snap/(channel+'.json'),manifest,'archived_synthetic_request_fixture')
            fixtures.append(str(f))
        result=read(rr); calls=result.get('calls',[])
        if len(calls)!=1: raise RuntimeError('unexpected archived ECAS generation call count')
        call_num=calls[0]
        match=list((source/'calls').glob(f'{call_num:02d}_{task}_ecas_generate'))
        if len(match)!=1: raise RuntimeError('cannot resolve archived raw generation call')
        raw=copy_source(match[0]/'response.raw.json',snap/'response.raw.json',manifest,'archived_provider_raw')
        parsed=copy_source(match[0]/'parsed_output.json',snap/'parsed_output.json',manifest,'archived_parsed_response')
        if not contains_candidate(read(raw),read(cp)) or not contains_candidate(read(parsed),read(cp)):
            raise RuntimeError('candidate not exactly found in archived raw and parsed responses')
        parents.append({'parent_id':parent_id,'case':task,'configuration':config,'candidate':str(cp),'contract':str(ct),
                        'original_result':str(rr),'fixtures':fixtures,'raw_response':str(raw),'parsed_response':str(parsed),
                        'original_source_folder':str(folder),'raw_candidate_exact_match':True})
    dump(ROOT/'PARENT_CANDIDATES.json',parents)
    dump(ROOT/'SOURCE_MANIFEST.json',manifest)
    dump(ROOT/'EXECUTION_CONFIG.json',{'scope_id':SCOPE_ID,'lane':str(LANE),'model_calls':0,'case_count':7,
         'parent_candidate_count':11,'variants_are_not_independent_cases':True,'classification':'RETROSPECTIVE_LOCAL_ADMISSION_MECHANISM_ABLATION',
         'generation_evidence_ablated':False,'source_truth_validated_by_admission':False,'external_state':False})
    items=[]
    for p in [ROOT/'evidence_ablation.py',ROOT/'PARENT_CANDIDATES.json',ROOT/'SOURCE_MANIFEST.json',ROOT/'EXECUTION_CONFIG.json'] + [Path(t['snapshot']) for t in manifest]:
        items.append({'path':str(p),'sha256':sha(p)})
    dump(ROOT/'INPUT_MANIFEST.json',items)
    request={'schema_version':1,'run_id':'evidence-ablation-t0-v1','run_root':str(LANE/'managed_runs'),
             'argv':['/usr/bin/python3',str(ROOT/'evidence_ablation.py'),'t0','{run_dir}/outputs/result.json'],
             'cwd':str(ROOT),'inputs':items+[{'path':str(ROOT/'INPUT_MANIFEST.json'),'sha256':sha(ROOT/'INPUT_MANIFEST.json')}],
             'outputs':[{'path':'outputs/result.json','kind':'json','nonempty':True,'required_keys':['status','checks']}],
             'timeout_seconds':120,'authorization_ref':'Current user authorizes matched experiments and evidence-driven comparison; local offline only'}
    dump(ROOT/'T0_REQUEST.json',request)
    print(json.dumps({'status':'PREPARED','parents':len(parents),'source_files':len(manifest),'t0_request':str(ROOT/'T0_REQUEST.json')}))

def verify_inputs():
    rows=[]
    for item in read(ROOT/'INPUT_MANIFEST.json'):
        actual=sha(item['path'])
        rows.append({'path':item['path'],'expected':item['sha256'],'actual':actual,'pass':actual==item['sha256']})
    if not all(r['pass'] for r in rows): raise RuntimeError('frozen input changed')
    return rows

def t0(output):
    checks=[]; verify_inputs(); e=engine()
    ir={'ir_version':'EC-FIELD-MODEL-IR-V3','candidate_id':'SYNTH-T0-C','decision':'propose',
        'target':{'system':'SYNTHETIC-T0','version':'test-1','operation':'POST /synthetic'},'policy_id':'SYNTH-T0-P',
        'evidence_refs':['SYNTH-T0-E'],'rules':[{'rule_id':'SYNTH-T0-R','primitive_id':'SP-STRICT-TYPE',
        'op':'strict_type','evidence_refs':['SYNTH-T0-E'],'params':{'path':'/request/body/age','expected_type':'integer','on_missing':'deny'}}],
        'reason_code':'none','missing_evidence':[]}
    contract={'contract_version':'EC-EVIDENCE-CONTRACT-V3','contract_id':'SYNTH-T0-K','catalog_id':e.core.CATALOG['catalog_id'],
              'target':copy.deepcopy(ir['target']),'evidence':[{'evidence_id':'SYNTH-T0-E','visibility':'visible',
              'source_kind':'api_documentation','sha256':'0'*64,'locator':'synthetic engineering fixture only',
              'system':'SYNTHETIC-T0','versions':['test-1'],'operations':['POST /synthetic'],'relation':'supports',
              'supports_primitives':['SP-STRICT-TYPE'],'bound_paths':['/request/body/age'],
              'binding_facts':{k:True for k in e.core.CATALOG_REQUIREMENTS['SP-STRICT-TYPE']}}]}
    policy=e.compile_model_ir(ir)['policy']
    e.compile_policy(policy,contract); e.compile_policy_shape_only(policy)
    vectors=[({'request':{'body':{'age':43}}},'allow'),({'request':{'body':{'age':'43'}}},'deny')]
    for mode in ['semantic','shape_only']:
        values=[e.evaluate(policy,contract if mode=='semantic' else None,v,admission_mode=mode) for v,_ in vectors]
        checks.append({'check':mode+'_synthetic_allow_deny','pass':all(v['decision']==expected and 'engine_error' not in v for v,(_,expected) in zip(values,vectors)), 'observed':values})
    no_evidence=copy.deepcopy(contract); no_evidence['evidence'][0]['evidence_id']='SYNTH-MISSING'
    rejected=False
    try: e.compile_policy(policy,no_evidence)
    except e.PolicyError: rejected=True
    checks.append({'check':'synthetic_missing_inventory_full_reject_shape_accept','pass':rejected and e.compile_policy_shape_only(policy)==policy})
    wrong=copy.deepcopy(ir);wrong['rules'][0]['op']='not_registered'
    bad=False
    try: e.compile_model_ir(wrong)
    except e.PolicyError: bad=True
    checks.append({'check':'synthetic_ir_shape_failure','pass':bad})
    checks.append({'check':'isolated_lane_and_free_space','pass':LANE.exists() and shutil.disk_usage(LANE).free>100_000_000})
    ps=subprocess.run(['ps','-eo','pid,ppid,comm,args'],capture_output=True,text=True,check=True)
    (ROOT/'T0_PROCESS_INVENTORY.txt').write_text(ps.stdout,encoding='utf-8')
    receipt={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','scope_id':SCOPE_ID,'checks':checks,'completed_at':now(),
             'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'lane':str(LANE),'free_bytes':shutil.disk_usage(LANE).free,
             'shared_resources_used':[],'docker_gpu_ports_database':'NOT_APPLICABLE_no_services_started','model_calls':0,'scientific_result':False}
    dump(ROOT/'T0_RECEIPT.json',receipt);dump(output,receipt)
    if receipt['status']!='PASS': raise RuntimeError('T0 failed')
    request=read(ROOT/'T0_REQUEST.json');request['run_id']='evidence-ablation-effects-v1'
    request['argv'][2]='run';request['timeout_seconds']=300
    request['inputs'] += [{'path':str(ROOT/'T0_RECEIPT.json'),'sha256':sha(ROOT/'T0_RECEIPT.json')}]
    request['outputs'][0]['required_keys']=['status','rows','summary']
    dump(ROOT/'RUN_REQUEST.json',request)

def replace_trusted_paths(value, mapping):
    if isinstance(value,dict): return {k:replace_trusted_paths(v,mapping) for k,v in value.items()}
    if isinstance(value,list): return [replace_trusted_paths(v,mapping) for v in value]
    if isinstance(value,str) and value.startswith('/trusted/'):
        new='/request/body/ecasClientClaim'+value[len('/trusted'):]
        mapping[value]=new;return new
    return value
def set_pointer(envelope,pointer,value):
    tokens=pointer.strip('/').split('/'); current=envelope
    for token in tokens[:-1]: current=current.setdefault(token,{})
    current[tokens[-1]]=value
def get_pointer(envelope,pointer):
    current=envelope
    for token in pointer.strip('/').split('/'):
        if not isinstance(current,dict) or token not in current:return False,None
        current=current[token]
    return True,current

def variants(candidate,contract):
    out=[]
    def add(name,c,k,classification,expected_full,notes,mapping=None):
        out.append({'variant':name,'candidate':c,'contract':k,'classification':classification,'expected_full':expected_full,
                    'notes':notes,'path_mapping':mapping or {}})
    add('original',copy.deepcopy(candidate),copy.deepcopy(contract),'ARCHIVED_MODEL_OUTPUT','admit','Unmodified archived candidate and inventory')
    k=copy.deepcopy(contract)
    for item in k['evidence']: item['evidence_id']='ABSENT-'+item['evidence_id']
    add('evidence_refs_absent',copy.deepcopy(candidate),k,'CONSTRUCTED_INVENTORY_PERTURBATION','reject','All referenced records absent; schema remains valid')
    k=copy.deepcopy(contract)
    for item in k['evidence']: item['versions']=['ECAS-TEST-NONMATCHING-VERSION']
    add('evidence_version_mismatch',copy.deepcopy(candidate),k,'CONSTRUCTED_INVENTORY_PERTURBATION','reject','Referenced record versions exclude policy target')
    k=copy.deepcopy(contract)
    for item in k['evidence']: item['relation']='insufficient'
    add('evidence_insufficient',copy.deepcopy(candidate),k,'CONSTRUCTED_INVENTORY_PERTURBATION','reject','Valid inventory marks all bindings insufficient')
    k=copy.deepcopy(contract)
    for item in k['evidence']: item['binding_facts']={'unrelated_test_fact':True}
    add('required_binding_facts_absent',copy.deepcopy(candidate),k,'CONSTRUCTED_INVENTORY_PERTURBATION','reject','Valid inventory drops required primitive binding facts')
    k=copy.deepcopy(contract)
    for item in k['evidence']: item['sha256']='0'*64;item['locator']='nonexistent/synthetic-source-only.txt:1'
    add('source_locator_hash_unresolvable',copy.deepcopy(candidate),k,'CONSTRUCTED_SOURCE_AUTHENTICITY_CHALLENGE','admit','Inventory fields have valid shape but source identity is intentionally unresolvable; source-file resolution is not performed by the gate')
    mapping={};c=replace_trusted_paths(copy.deepcopy(candidate),mapping)
    if mapping:
        add('trusted_path_to_unregistered_client_path',c,copy.deepcopy(contract),'CONSTRUCTED_POLICY_PATH_PERTURBATION','reject','All trusted paths changed to client-body paths without changing inventory declarations',mapping)
    k=copy.deepcopy(contract);k['evidence'][0]['visibility']='hidden'
    add('schema_visibility_hidden',copy.deepcopy(candidate),k,'ENGINEERING_CONTRACT_SCHEMA_CONTROL','schema_fail','Visibility is const visible; excluded from admission-mechanism denominator')
    c=copy.deepcopy(candidate);c['rules'][0]['op']='not_registered'
    add('schema_ir_unknown_op',c,copy.deepcopy(contract),'ENGINEERING_MODEL_IR_SCHEMA_CONTROL','schema_fail','Unknown operation; excluded from scientific denominator')
    return out

def run(output):
    if read(ROOT/'T0_RECEIPT.json')['status']!='PASS': raise RuntimeError('T0 not passed')
    before=verify_inputs();e=engine();rows=[]
    for parent in read(ROOT/'PARENT_CANDIDATES.json'):
        candidate=read(parent['candidate']);contract=read(parent['contract'])
        original_fixtures=[]
        for file in parent['fixtures']:
            for v in read(file)['vectors']:
                original_fixtures.append({'id':v['vector_id'],'input':v['envelope'],'expected':v['expected_class'],'source':file,'class':'ARCHIVED_SYNTHETIC_REQUEST'})
        for variant in variants(candidate,contract):
            rid=parent['parent_id']+'__'+variant['variant'];folder=LANE/'outputs'/rid
            dump(folder/'candidate.json',variant['candidate']);dump(folder/'contract.json',variant['contract'])
            row={k:parent[k] for k in ['parent_id','case','configuration']}
            row.update({'row_id':rid,'variant':variant['variant'],'classification':variant['classification'],'expected_full':variant['expected_full'],
                        'notes':variant['notes'],'source_parent_candidate':parent['candidate'],'source_parent_contract':parent['contract'],
                        'candidate_sha256':sha(folder/'candidate.json'),'contract_sha256':sha(folder/'contract.json'),
                        'output_folder':str(folder),'full_executed':False,'shape_executed':False})
            try:
                proposal=e.compile_model_ir(variant['candidate'])
                if proposal['decision']!='propose': raise RuntimeError('unexpected abstention in archived parents')
                policy=proposal['policy'];dump(folder/'compiled_policy.json',policy)
                row['ir_status']='COMPILED'
            except e.PolicyError as exc:
                row.update({'ir_status':'IR_SCHEMA_OR_TYPE_FAILURE','full_status':'NOT_ATTEMPTED','shape_status':'NOT_ATTEMPTED','error':str(exc),'eligible_admission_contrast':False})
                rows.append(row);dump(folder/'RESULT.json',row);continue
            contract_errors=e.core._format_errors(e.core.CONTRACT_VALIDATOR,variant['contract'])
            row['contract_shape_valid']=not bool(contract_errors)
            try:
                e.compile_policy(policy,variant['contract']);row['full_status']='ADMITTED'
            except e.PolicyError as exc:
                row['full_status']='CONTRACT_SCHEMA_FAILURE' if contract_errors else 'ADMISSION_REJECTED';row['full_error']=str(exc)
            try:
                e.compile_policy_shape_only(policy);row['shape_status']='COMPILED_NO_INVENTORY'
            except e.PolicyError as exc:
                row['shape_status']='POLICY_SCHEMA_OR_TYPE_FAILURE';row['shape_error']=str(exc)
            row['eligible_admission_contrast']=row['contract_shape_valid'] and row['shape_status']=='COMPILED_NO_INVENTORY'
            fixtures=copy.deepcopy(original_fixtures)
            if variant['path_mapping']:
                for item in fixtures:
                    for source,target in variant['path_mapping'].items():
                        found,value=get_pointer(item['input'],source)
                        if found:set_pointer(item['input'],target,value)
                    item['class']='CONSTRUCTED_CLIENT_PATH_REPLAY';item['expected']=None
                # The attacker submits the archived legal-state values while real trusted context is invalid.
                spoof=copy.deepcopy(original_fixtures[1]['input'])
                for source,target in variant['path_mapping'].items():
                    found,value=get_pointer(original_fixtures[0]['input'],source)
                    if found:set_pointer(spoof,target,value)
                fixtures.append({'id':'SYNTH-CLIENT-SPOOF','input':spoof,'expected':None,'source':'paired archived request values copied into client body',
                                 'class':'CONSTRUCTED_CLIENT_SPOOF_PROBE'})
            fixtures.append({'id':'SYNTH-MISSING-TRUSTED','input':{'request':copy.deepcopy(original_fixtures[0]['input'].get('request',{})),'trusted':{}},
                             'expected':None,'source':'archived legal request with trusted object emptied','class':'CONSTRUCTED_MISSING_CONTEXT_CONTROL'})
            dump(folder/'execution_fixtures.json',fixtures)
            for arm,status,mode in [('full','ADMITTED','semantic'),('shape','COMPILED_NO_INVENTORY','shape_only')]:
                evaluations=[]
                if row[arm+'_status']==status:
                    for item in fixtures:
                        actual=e.evaluate(policy,variant['contract'] if arm=='full' else None,item['input'],admission_mode=mode)
                        evaluations.append({'fixture_id':item['id'],'fixture_class':item['class'],'expected':item['expected'],'actual':actual,
                                            'correct':None if item['expected'] is None else actual['decision']==item['expected'] and not actual.get('engine_error')})
                    row[arm+'_executed']=True
                row[arm+'_evaluations']=evaluations
            archived=row.get('full_evaluations',[])[:2]
            row['original_pair_correct']=all(x['correct'] is True for x in archived) if len(archived)==2 and variant['variant']=='original' else None
            row['full_execution_errors']=sum(bool(x['actual'].get('engine_error')) for x in row.get('full_evaluations',[]))
            row['shape_execution_errors']=sum(bool(x['actual'].get('engine_error')) for x in row.get('shape_evaluations',[]))
            dump(folder/'RESULT.json',row);rows.append(row)
    summary=summarize(rows)
    dump(ROOT/'COMPARISON_SUMMARY.json',{'status':'COMPLETED','scope_id':SCOPE_ID,'classification':'RETROSPECTIVE_SAME_CANDIDATE_LOCAL_ADMISSION_ABLATION','rows':rows,'summary':summary})
    fields=['row_id','parent_id','case','configuration','variant','classification','ir_status','contract_shape_valid','full_status','shape_status','eligible_admission_contrast','full_executed','shape_executed','original_pair_correct','full_error','error','output_folder']
    with (ROOT/'COMPARISON.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    after=verify_inputs();reconcile=[]
    for item in read(ROOT/'SOURCE_MANIFEST.json'):
        reconcile.append({'original':item['original'],'snapshot':item['snapshot'],'expected':item['sha256'],
                          'original_unchanged':sha(item['original'])==item['sha256'],'snapshot_unchanged':sha(item['snapshot'])==item['sha256']})
    original_rows=[r for r in rows if r['variant']=='original']
    for row in original_rows:
        parent=next(p for p in read(ROOT/'PARENT_CANDIDATES.json') if p['parent_id']==row['parent_id'])
        old=read(parent['original_result'])['requests']
        previous=[{'decision':x['actual']['decision'],'engine_error':bool(x['actual'].get('engine_error'))} for x in old]
        replay=[{'decision':x['actual']['decision'],'engine_error':bool(x['actual'].get('engine_error'))} for x in row['full_evaluations'][:2]]
        reconcile.append({'parent_id':row['parent_id'],'check':'original_request_pair_replayed_exactly','pass':previous==replay,'previous':previous,'replayed':replay})
    passed=all(r.get('pass',r.get('original_unchanged',False) and r.get('snapshot_unchanged',False)) for r in reconcile)
    dump(ROOT/'FINAL_RECONCILIATION.json',{'status':'PASS' if passed else 'FAIL','input_hash_checks':len(before),'source_and_replay_checks':len(reconcile),'checks':reconcile,'after_input_checks':after})
    report(rows,summary)
    dump(output,{'status':'COMPLETED' if passed else 'RECONCILIATION_FAILED','rows':len(rows),'summary':summary})
    if not passed: raise RuntimeError('source/replay reconciliation failed')

def summarize(rows):
    originals=[r for r in rows if r['variant']=='original']
    per_variant={}
    for variant in sorted(set(r['variant'] for r in rows)):
        selected=[r for r in rows if r['variant']==variant]
        per_variant[variant]={'parents':len(selected),'eligible_contrasts':sum(r.get('eligible_admission_contrast',False) for r in selected),
                             'full_admitted':sum(r['full_status']=='ADMITTED' for r in selected),
                             'full_admission_rejected':sum(r['full_status']=='ADMISSION_REJECTED' for r in selected),
                             'contract_schema_failures':sum(r['full_status']=='CONTRACT_SCHEMA_FAILURE' for r in selected),
                             'ir_schema_or_type_failures':sum(r['ir_status']=='IR_SCHEMA_OR_TYPE_FAILURE' for r in selected),
                             'shape_compiled':sum(r['shape_status']=='COMPILED_NO_INVENTORY' for r in selected)}
    return {'unique_cases':7,'parent_candidates':len(originals),'variant_rows':len(rows),'model_calls':0,
            'original_full_admitted':sum(r['full_status']=='ADMITTED' for r in originals),
            'original_request_pair_correct':sum(r['original_pair_correct'] is True for r in originals),
            'original_request_pair_wrong_or_partial':sum(r['original_pair_correct'] is False for r in originals),
            'per_variant':per_variant,'full_rejected_rows_executed':sum(r['full_status']!='ADMITTED' and r['full_executed'] for r in rows),
            'execution_errors':sum(r.get('full_execution_errors',0)+r.get('shape_execution_errors',0) for r in rows),
            'variants_are_independent_cases':False,'generation_without_evidence_tested':False,'autopac_judge_tested_here':False}

def report(rows,summary):
    lines=['# 同候选证据准入消融：本地离线结果','',
           '**结论：证据契约能够阻止未绑定、版本错配及不充分证据的规则进入执行；它没有自动证明规则方向或目标覆盖正确，也未核验清单中的来源文件真实性。**','',
           '## 范围与公平控制','',
           '- 7个旧案例、11个父候选：前三例各1个，后四例v1/v2各保留1个；未逐例择优。全部来自已暴露的历史输出。',
           '- 同一份候选先用原`compile_model_ir`编译；完整组用`compile_policy`及semantic执行，无契约组用引擎已有`compile_policy_shape_only`及shape_only执行。两组共用原语、schema和执行器。',
           '- 无契约组不调用完整Inventory准入。完整组准入拒绝时不执行；无契约风险执行仅使用离线合成请求。',
           '- 这是准入阶段的机制消融。两组候选生成时都看过证据，本轮没有检验“模型生成时不提供证据”，没有新模型调用，也没有AutoPAC Judge的新增对照。',
           '- 配对扰动是人工构造的元数据/路径挑战；一个父候选的多个变体不是多个独立案例。未执行、schema失败、弃权均不算业务请求正确或错误。','',
           '## 完整准入与无契约编译','',
           '| 输入类别 | 父候选数 | 完整准入通过 | 完整准入拒绝 | schema/类型失败 | 无契约编译通过 |','|---|---:|---:|---:|---:|---:|']
    names={'original':'历史原候选','evidence_refs_absent':'引用的证据记录缺失','evidence_version_mismatch':'证据版本错配','evidence_insufficient':'证据标记为不充分','required_binding_facts_absent':'必需绑定事实缺失',
           'source_locator_hash_unresolvable':'来源locator/hash不可解析','trusted_path_to_unregistered_client_path':'可信路径换成未绑定客户端路径','schema_visibility_hidden':'schema控制：hidden visibility','schema_ir_unknown_op':'schema控制：未知操作'}
    for v,s in summary['per_variant'].items():
        lines.append(f"| {names[v]} | {s['parents']} | {s['full_admitted']} | {s['full_admission_rejected']} | {s['contract_schema_failures']+s['ir_schema_or_type_failures']} | {s['shape_compiled']} |")
    lines += ['','完整准入拒绝表示规则不部署；合法业务覆盖同时降为未部署，不可把未执行算成合法允许或违规拒绝。由于元数据扰动不改变原规则，两组在原始清单上通过的合法覆盖相同；坏元数据下完整组宁可拒绝部署，无契约组仍执行。','',
              '## 原候选业务结果与语义漏检','',
              '| 案例 | 配置 | 完整准入 | 原合法请求 | 原违规请求 | 两条均正确 |','|---|---|---|---|---|---|']
    for r in rows:
        if r['variant']=='original':
            values=[x['actual']['decision'] for x in r['full_evaluations'][:2]]
            lines.append(f"| {r['case']} | {r['configuration']} | {r['full_status']} | {values[0] if values else '未执行'} | {values[1] if len(values)>1 else '未执行'} | {'是' if r['original_pair_correct'] else '否'} |")
    lines += ['','B17 v1错误原语、B19 v1禁止条件反写为允许条件、S03 v2只生成字段白名单等历史错误仍保留在表中。完整准入没有自动把这些语义错误拒绝掉。不得用准入通过替代业务语义正确。','',
              '## 可信路径挑战的解释','',
              '将规则引用的`/trusted/...`改为未登记的`/request/body/ecasClientClaim/...`，完整组检查规则路径未绑定而拒绝，无契约组仍编译。另用历史合法状态值写入客户端字段，在真实trusted保持违规状态下离线重放。',
              '该挑战检验注册路径绑定，不证明trusted字段在真实网关中真实性、来源认证、新鲜度或防伪；若操作者在清单中主动声明客户端路径可信，当前准入本身不验证声明真伪。','',
              '## 来源真实性挑战','',
              '所有证据记录的locator改为不存在的合成路径、sha256改为格式合法的全零值，其他绑定保持不变。引擎检查schema与清单声明，没有解析文件或比对源文件hash，因此仍可能通过。这是当前实现边界，不能写为完整来源真实性验证。','',
              '## 可下与不可下的结论','',
              '- 可下：在这7例的11个历史候选及配对构造挑战上，Inventory准入对已实现的证据绑定条件提供可观察的部署阻断。',
              '- 不可下：ECAS整体优于AutoPAC；证据驱动提高生成语义正确率；证明普适性；极大降低人工劳动；证明源文档真实性或trusted值真实性。',
              '- 后续同预算同行实验需要另比较生成时有/无证据、首次生成与等预算修复，及真实手工计时。','',
              '## 核验与复现','',
              '- 独立WSL lane，原引擎字节不改，T0工程正负夹具PASS，无Docker/GPU/服务/API。',
              '- `SOURCE_MANIFEST.json`逐份绑定原件与只读快照；`FINAL_RECONCILIATION.json`核对原件未变、快照未变和11条原请求对重演。',
              '- `COMPARISON_SUMMARY.json`保留逐行准入理由、离线执行观察及变体构造类别；`COMPARISON.csv`为索引。',
              '- 运行入口：`T0_REQUEST.json`与`RUN_REQUEST.json`，用通用WSL managed runner validate/start。','']
    (ROOT/'RESULTS_CN.md').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='t0':t0(sys.argv[2])
    elif mode=='run':run(sys.argv[2])
    else:raise ValueError('unknown mode')
