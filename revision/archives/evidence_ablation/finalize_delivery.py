#!/usr/bin/env python3
"""Audited, Windows-readable delivery derived from the completed offline run."""
import csv
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LANE=Path('/root/ecas_evidence_ablation_20261014')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def windows_path(p):
    value=str(p)
    if value.startswith('/mnt/') and len(value)>7 and value[6]=='/':
        return value[5].upper()+':/'+value[7:]
    return value

original=read(ROOT/'COMPARISON_SUMMARY.json');rows=original['rows'];checks=[];delivery=[]
for parent in read(ROOT/'PARENT_CANDIDATES.json'):
    checks.append({'check':'raw_and_parsed_exact_candidate_'+parent['parent_id'],'pass':parent['raw_candidate_exact_match']})
for p in sorted(LANE.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:continue
    dest=ROOT/'evidence_files'/p.relative_to(LANE);dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists() or sha(p)!=sha(dest):shutil.copyfile(p,dest)
    delivery.append({'source':str(p),'delivered':str(dest),'windows_delivered':windows_path(dest),'sha256':sha(p),'copy_match':sha(p)==sha(dest)})
for row in rows:
    parent=next(p for p in read(ROOT/'PARENT_CANDIDATES.json') if p['parent_id']==row['parent_id'])
    baseline=next(r for r in rows if r['parent_id']==row['parent_id'] and r['variant']=='original')
    if row['variant']=='original':side='NONE_ARCHIVED_INPUT'
    elif row['variant'].startswith('schema_ir') or row['variant']=='trusted_path_to_unregistered_client_path':side='POLICY_IR'
    else:side='INVENTORY_CONTRACT'
    row['mutation_side']=side
    row['full_dispatch_eligibility']='ELIGIBLE' if row['full_status']=='ADMITTED' else 'INELIGIBLE_NOT_EXECUTED'
    row['full_request_decisions']=None if not row['full_executed'] else [x['actual']['decision'] for x in row['full_evaluations']]
    row['shape_request_decisions']=None if not row['shape_executed'] else [x['actual']['decision'] for x in row.get('shape_evaluations',[])]
    if row['variant'] in ['original','evidence_refs_absent','evidence_version_mismatch','evidence_insufficient','required_binding_facts_absent','source_locator_hash_unresolvable']:
        checks.append({'check':'same_compiled_policy_'+row['row_id'],'pass':sha(Path(row['output_folder'])/'compiled_policy.json')==sha(Path(baseline['output_folder'])/'compiled_policy.json')})
        if row['shape_executed']:
            actual=[x['actual'] for x in row['shape_evaluations']]
            expected=[x['actual'] for x in baseline['shape_evaluations']]
            checks.append({'check':'same_shape_execution_for_contract_only_'+row['row_id'],'pass':actual==expected})
    if row['full_status']!='ADMITTED':
        checks.append({'check':'ineligible_full_never_executes_'+row['row_id'],'pass':row['full_executed'] is False and row.get('full_evaluations',[])==[] and row['full_request_decisions'] is None})
    if row.get('eligible_admission_contrast'):
        checks.append({'check':'valid_schema_for_admission_contrast_'+row['row_id'],'pass':row['contract_shape_valid'] and row['ir_status']=='COMPILED' and row['shape_status']=='COMPILED_NO_INVENTORY'})
    row['windows_output_folder']=windows_path(ROOT/'evidence_files/outputs'/row['row_id'])
    row['original_pair_correct_label']='ARCHIVED_FIXTURE_LABEL_MATCH_ONLY_NOT_INDEPENDENT_SEMANTIC_GOLD'
original['rows']=rows;original['audit_notes']={'new_model_calls':0,'source_inventory_truth_assumed_by_original_guarantee':True,
    'mutated_inventory_source_identity_is_outside_that_assumption':True,'original_pair_labels_not_independent_semantic_gold':True,
    'b06_target_scope_and_s02_closed_fields_authority_not_fully_closed':True,'all_mutation_sides_explicit':True}
dump(ROOT/'COMPARISON_AUDITED.json',original)
fields=['row_id','parent_id','case','configuration','variant','mutation_side','classification','ir_status','contract_shape_valid','full_status','full_dispatch_eligibility','shape_status','eligible_admission_contrast','full_executed','shape_executed','original_pair_correct','full_error','error','windows_output_folder']
with (ROOT/'COMPARISON_AUDITED.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
checks += [{'check':'exact_7_cases_11_parents_95_variant_rows','pass':len(set(r['case'] for r in rows))==7 and len(set(r['parent_id'] for r in rows))==11 and len(rows)==95},
           {'check':'original_reconciliation_pass','pass':read(ROOT/'FINAL_RECONCILIATION.json')['status']=='PASS'},
           {'check':'managed_t0_and_effects_success','pass':all(read(LANE/'managed_runs'/run/'status.json')['state']=='SUCCEEDED' for run in ['evidence-ablation-t0-v1','evidence-ablation-effects-v1'])},
           {'check':'copied_evidence_byte_equal','pass':all(x['copy_match'] for x in delivery)},
           {'check':'zero_runtime_errors','pass':original['summary']['execution_errors']==0},
           {'check':'no_schema_control_enters_contrast_denominator','pass':all(not r.get('eligible_admission_contrast') for r in rows if r['classification'].startswith('ENGINEERING'))}]
spoof=[]
for r in rows:
    if r['variant']=='trusted_path_to_unregistered_client_path':
        x=next(t for t in r['shape_evaluations'] if t['fixture_id']=='SYNTH-CLIENT-SPOOF')
        spoof.append({'parent_id':r['parent_id'],'full':'NOT_EXECUTED','shape':x['actual']['decision'],
                      'classification':'SYNTHETIC_PATH_TRUST_CHALLENGE_NOT_REAL_ATTACK','engine_error':x['actual'].get('engine_error')})
dump(ROOT/'CLIENT_PATH_PROBE_SUMMARY.json',spoof)
dump(ROOT/'DELIVERY_MANIFEST.json',delivery)
dump(ROOT/'DELIVERY_QA.json',{'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','completed_at':now(),'check_count':len(checks),'checks':checks,
                            'delivered_files':len(delivery),'effect_rows':len(rows),'model_calls':0,'scientific_generalization_validated':False})

report=ROOT/'RESULTS_CN.md';text=report.read_text(encoding='utf-8').split('\n## 扰动对象与执行资格')[0]
text=text.replace('| 两条均正确 |','| 两条归档标签均命中 |')
if '不能将归档标签作为独立语义gold' not in text:
    text=text.replace('B17 v1错误原语、','表中“标签命中”只对归档请求对负责。B06的通用undo target与Re-Age条款范围、S02封闭字段约定的原出处仍未完全闭合，不能将归档标签作为独立语义gold。\n\nB17 v1错误原语、')
text=text.replace('因此仍可能通过。这是当前实现边界，不能写为完整来源真实性验证。','11个父候选全部通过。原稿相对Inventory的保证假定清单已经结构化且可信；直接篡改清单来源真实性位于这一假设之外，因此这项结果不直接推翻该限定保证，也不能称为真实攻击或漏洞。它说明当前执行入口不负责源文件解析与清单真实性核验。')
text=text.replace('后续同预算同行实验需要另比较生成时有/无证据、首次生成与等预算修复，及真实手工计时。','后续同预算同行实验需要另比较生成时有/无证据、首次生成与等预算修复。用户已取消人工计时；本轮只登记生成方式与可观察工程工作量，不将代理量写成真实人时节省。')
text += '\n## 扰动对象与执行资格\n\n'
text += '- 原候选未改变任何输入；可信路径替换和未知操作控制改变policy IR。其余证据缺失、版本、关系、绑定事实、locator/hash和visibility变体改变Inventory contract。\n'
text += '- 完整组被拒时是`INELIGIBLE_NOT_EXECUTED`，请求决策为`None`；没有造出deny，也不把这种拒绝算成业务全对。\n'
text += '- 仅contract变化的变体保留同一份compiled policy；独立QA核对无契约组执行观察与原候选逐项相同。\n'
text += '- schema控制不进入准入机制分母。元数据/路径构造挑战反映机制边界，不代表真实攻击发生率，也不用于声称优于AutoPAC。\n\n'
text += '## 客户端声明挑战观察\n\n| 父候选 | 完整组 | 无契约组在合成伪造声明下 |\n|---|---|---|\n'
for r in spoof:text += f"| {r['parent_id']} | 无执行资格 | {r['shape']} |\n"
text += '\n执行器对已有错误规则仍可能拒绝合法输入；合成声明被无契约组允许只说明该路径绑定挑战的风险，不表示所有规则或真实网关均有此漏洞。\n\n'
text += '## Windows交付与局部记录\n\n'
text += '- `COMPARISON_AUDITED.json/csv`增加扰动对象、执行资格、未执行的None和Windows证据路径。原始`COMPARISON_SUMMARY.json`保留。\n'
text += '- 本文档的后续建议按用户最新范围修订，取消人工计时；实际运行脚本与managed runner输入hash保持不变。\n'
text += '- `evidence_files/`交付只读输入、实际编译/请求/结果和两次managed run回执；`DELIVERY_MANIFEST.json`逐文件hash对账。\n'
text += '- `DELIVERY_QA.json`是局部交付核验；`RESULT_TRACEABILITY.csv`仅本实验局部账本，不写根科学ledger。\n'
report.write_text(text,encoding='utf-8')

trace_fields=['result_id','experiment_id','metric_name','dataset_name','dataset_version','data_split','sample_count','raw_value','reported_value','unit','aggregation','source_output_path','source_locator','script_path','command_or_config','seed','environment','git_commit','checksum','rounding_rule','status','verified_by','verified_at','notes']
trace=[]
for i,row in enumerate(rows):
    if not row.get('eligible_admission_contrast'):continue
    source=ROOT/'COMPARISON_AUDITED.json';value=int(row['full_status']=='ADMITTED')
    trace.append({'result_id':f'EV-ADMIT-{i+1:03d}','experiment_id':SCOPE_ID if 'SCOPE_ID' in globals() else original['scope_id'],'metric_name':'full_inventory_admitted',
                  'dataset_name':row['case'],'dataset_version':row['configuration'],'data_split':'historical_exposed_output_or_constructed_paired_perturbation','sample_count':1,
                  'raw_value':value,'reported_value':value,'unit':'boolean','aggregation':'one_variant_of_parent_not_independent_case',
                  'source_output_path':'COMPARISON_AUDITED.json','source_locator':'rows['+str(i)+'].full_status','script_path':'evidence_ablation.py',
                  'command_or_config':'RUN_REQUEST.json','seed':'NOT_APPLICABLE','environment':'WSL Ubuntu Python restricted original V3 engine offline CPU',
                  'git_commit':'NOT_AVAILABLE_HASH_FROZEN','checksum':sha(source),'rounding_rule':'none','status':'PASS','verified_by':'deterministic_independent_delivery_checks',
                  'verified_at':now(),'notes':row['classification']+'; '+row['mutation_side']+'; no-gate control is not AutoPAC; rejected full never executes'})
with (ROOT/'RESULT_TRACEABILITY.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=trace_fields);writer.writeheader();writer.writerows(trace)
(ROOT/'README.md').write_text('# Same-candidate Inventory admission ablation\n\nRead RESULTS_CN.md, COMPARISON_AUDITED.json, DELIVERY_QA.json.\n\nOffline historical candidates only; no model calls, human timing, API forwarding, AutoPAC Judge execution, or source authenticity guarantee. Seven historical cases and eleven configurations, not ninety-five independent cases.\n',encoding='utf-8')
(ROOT/'REPRODUCE.md').write_text('# Reproduce\n\nThe historical runtime and inputs are delivered under evidence_files/runtime and evidence_files/inputs. SOURCE_MANIFEST.json maps every snapshot to the original hash. The completed runs are under evidence_files/managed_runs with request bindings, raw logs and status.\n\n1. Verify SOURCE_MANIFEST.json / DELIVERY_MANIFEST.json.\n2. Use an isolated WSL lane and the original Python 3.10+ interpreter with jsonschema.\n3. For the original lane, validate and start T0_REQUEST.json once with the D:/lunwen/tools/wsl-experiment-runner/Invoke-WslExperiment.ps1 managed runner; inspect terminal status.\n4. After T0 PASS, validate/start RUN_REQUEST.json once and inspect the final state.\n5. Running a fresh reproduction requires new lane/run IDs and corresponding path binding; never overwrite the original lane or infer submission readiness from SUCCEEDED.\n\nSchema failures are engineering controls. Inventory rejection makes a policy ineligible for execution; it is not a deny decision or business correctness.\n',encoding='utf-8')
dump(ROOT/'PROTOCOL_EXECUTED.json',{'document_class':'POST_RUN_DURABLE_DESIGN_RECORD_NOT_FORMAL_PREREGISTRATION','scope_id':original['scope_id'],
    'objective':'Isolate Inventory admission from candidate generation and runtime behavior','deliverables':['RESULTS_CN.md','COMPARISON_AUDITED.json','COMPARISON_AUDITED.csv','SOURCE_MANIFEST.json','DELIVERY_MANIFEST.json','DELIVERY_QA.json'],
    'budget':{'external_model_calls':0,'gpu':0,'services':0},'authorization_ref':'Current user asks matched experiments, generation labor and evidence-driven option; parent delegated zero external admission ablation',
    'done':'actual T0; frozen source hashes;11 raw candidates exact match;full vs shape control;rejections never execute;95 mutation rows;original request pair replay;Windows hash-reconciled delivery',
    'stop_conditions':['T0 fail','input hash drift','dependency failure','unexpected original raw mismatch','unexplained execution error'],
    'scientific_scope':'retrospective admission-mechanism observations only','inventory_assumption':'prestructured trusted declarations','script_frozen_before_run':True,
    'no_human_labor_measured':True,'no_new_generation_evidence_ablation':True})
print(json.dumps({'status':read(ROOT/'DELIVERY_QA.json')['status'],'qa_checks':len(checks),'delivered_files':len(delivery),'local_trace_rows':len(trace),'client_path_probes':spoof},ensure_ascii=False))
if not all(x['pass'] for x in checks):raise SystemExit(1)
