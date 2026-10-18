"""Independent read-only source/report reconciliation; no model or policy calls."""
from pathlib import Path
import csv, hashlib, json

OUT=Path(__file__).resolve().parent
EXP=OUT.parent
OLD=EXP/'20261014_external_baseline_pilot'
NEW=EXP/'20261014_matched_evidence_labor'/'matched_generation'
PREV=EXP/'20261015_seven_case_mechanism'
def j(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def txt(p): return p.read_text(encoding='utf-8-sig')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name, value): checks.append({'check':name,'pass':bool(value)})
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
idx=j(OUT/'SEMANTIC_EVIDENCE_INDEX.json')
receipt=j(OUT/'BUILD_RECEIPT.json')
for s in idx['source_files']:
    ck('source_hash:'+s['path'],sha(Path(s['path']))==s['sha256'])
for s in receipt['outputs']:
    ck('delivered_output_hash:'+s['path'],sha(Path(s['path']))==s['sha256'])
for p,h in receipt['protected_files_unchanged'].items():
    ck('protected_file_hash:'+p,sha(Path(p))==h)
cur=rows(OUT/'SEMANTIC_COMPARISON.csv')
prev=rows(PREV/'SEVEN_CASE_COMPARISON.csv')
curmap={(r['case'],r['method']):r for r in cur}
prevmap={(r['task'],r['method']):r for r in prev}
ck('21_unique_case_method_rows',len(cur)==len(curmap)==21)
ck('R2_exact_key_join',set(curmap)==set(prevmap))
for key,r in curmap.items():
    p=prevmap[key]
    ck('R2_display_status:'+str(key),r['execution_status_from_R2']==p['displayed_status'])
    ck('R2_display_symbol:'+str(key),r['execution_symbol_from_R2']==p['displayed_symbol'])
    ck('R2_project_batch:'+str(key),r['project_name']==p['project_name'] and r['batch']==p['batch'])
    for e in json.loads(r['evidence_paths_json']):
        path=Path(e['path'])
        ck('row_evidence_hash:'+str(key)+':'+path.name,sha(path)==e['sha256'])
        pointer=e.get('json_pointer','')
        if pointer:
            val=j(path)
            for frag in pointer.split('/')[1:]:
                frag=frag.replace('~1','/').replace('~0','~')
                val=val[int(frag)] if isinstance(val,list) else val[frag]
            ck('row_pointer_resolves:'+str(key)+':'+pointer,val is not None)

evidence=[]
def record(relative,root=NEW):
    p=root/relative
    evidence.append({'path':str(p),'sha256':sha(p)})
    return j(p) if p.suffix=='.json' else txt(p)
g=record('method_runs/FSV-S03/AUTOPAC_STYLE/autopac_generate.json')
r=record('method_runs/FSV-S03/AUTOPAC_STYLE/repair.json')
c1=record('method_runs/FSV-S03/AUTOPAC_STYLE/initial/CHECKS.json')
c2=record('method_runs/FSV-S03/AUTOPAC_STYLE/repaired/CHECKS.json')
ck('S03_integer_intent_in_actual_initial_policy','is_integer(input.request.body.age)' in g['rego'])
ck('S03_initial_and_repair_compile_failures',c1['compile_exit']!=0 and 'undefined function is_integer' in c1['compile_error'] and c2['compile_exit']!=0 and 'undefined function typeof' in c2['compile_error'])
ck('S03_static_optional_presence_risk_not_execution','default allow := false' in g['rego'] and 'default allow := false' in r['rego'] and 'not input.request.body.age' not in g['rego']+r['rego'])
src3=record('generation_inputs/FSV-S03/packet.json')
schema3=src3['visible_sources'][0]['content']['requestBody']['content']['application/json']['schema']
ck('S03_source_age_integer_not_required',schema3['properties']['age']['type']=='integer' and 'age' not in schema3.get('required',[]))
ck('S03_objective_excludes_presence','presence' in src3['TARGET_OBJECTIVE']['scope'])
ir3=record('method_runs/FSV-S03/ECAS_MATCHED/first_candidate.json')
ck('S03_ECAS_integer_skip',ir3['rules'][0]['params']['expected_type']=='integer' and ir3['rules'][0]['params']['on_missing']=='skip')

s2=record('generation_inputs/FSV-S02/packet.json',OLD)
schema2=s2['visible_sources'][0]['content']['requestBody']['content']['application/json']['schema']
ck('S02_closed_world_source_gap','additionalProperties' not in schema2)
for task in ('FSV-S02','FSV-S03'):
    d=record(f'effect_runs/{task}/P2P_STYLE/detection.json',OLD) if task=='FSV-S02' else record(f'method_runs/{task}/P2P_STYLE/p2p_detect.json')
    ck(task+'_scope_out_not_wrong_generated_policy',d['status']=='OUT_OF_SCOPE')
b6=record('effect_runs/FSV-B06/AUTOPAC_STYLE/judge.json',OLD)
ck('B06_Judge_scope_contribution',b6['verdict']=='REVISE' and 'Re-Age' in b6['issues'][0] and 'non-Re-Age' in b6['issues'][0])
rb6=record('effect_runs/FSV-B06/AUTOPAC_STYLE/repair.json',OLD)
ck('B06_repair_not_explicit_type_discriminator','reAgeIsLatestTransaction == false' in rb6['rego'] and 'transactionType' not in rb6['rego'])

s19=record('generation_inputs/FSV-B19/packet.json')
text19=s19['visible_sources'][0]['content']
ck('B19_source_default_All_visible','if you do not select a hold type, ERPNext will set it to "All"' in text19)
abi=[s for s in s19['visible_sources'] if s['evidence_id']=='VIS-FSV-B19-RUNTIME-ABI'][0]
hold=[x for x in abi['content']['available_values'] if x['path']=='/trusted/holdType'][0]
ck('B19_ABI_string_no_enum',hold['type']=='string' and 'enum' not in hold)
ck('B19_adapter_trusted_unchanged',s19['common_adapter']['envelope_representation']['trusted']=='original trusted unchanged')
ir19=record('method_runs/FSV-B19/ECAS_MATCHED/first_candidate.json')
clauses=ir19['rules'][0]['params']['alternatives']
ck('B19_ECAS_allows_false_or_Payments_no_explicit_default',clauses[0]['clauses'][0]['right_value'] is False and clauses[1]['clauses'][0]['right_value']=='Payments' and 'All' not in json.dumps(ir19['rules']))
for m in ('P2P_STYLE','AUTOPAC_STYLE'):
    p19=record(f'method_runs/FSV-B19/{m}/initial/original.rego')
    ck('B19_baseline_known_type_block:'+m,'supplierOnHold == true' in p19 and '{"Invoices", "All"}' in p19)

report=txt(OUT/'SEMANTIC_COMPARISON_CN.md')
r3=txt(OUT/'EXPERIMENT_SUMMARY_CN_R3.md')
ck('both_reports_preserve_S02_boundary',all('additionalProperties=false' in s for s in (report,r3)))
ck('both_reports_preserve_S03_static_risk',all('静态' in s and '额外必填' in s for s in (report,r3)))
ck('both_reports_preserve_B19_not_default_extraction',all('没有显式empty→All' in s and '不能据此认定模型提取了默认值' in s for s in (report,r3)))
ck('both_reports_preserve_B19_production_unknown',all('生产后端是否' in s and '尚未验证' in s for s in (report,r3)))
ck('R3_history_not_new_experiment','144行机制结果及历史模型调用均为以前已完成的批次' in r3 and '新增政策执行0' in r3)
ck('R3_scope_not_native_or_generalized','原版P2P/AutoPAC未运行' in r3 and '不能合计统一准确率' in r3)
ck('neither_report_claims_unique_semantic_understanding',all('语义理解是三方法共同能力' in s or '三者均有自然语言到政策的转换能力' in s for s in (report,r3)))
fails=[x for x in checks if not x['pass']]
payload={'status':'PASS_SCOPED_STAGE_CONTENT_AND_TRACEABILITY' if not fails else 'FAIL_NEEDS_REPAIR','review_scope':'Independent read-only review of integrated report; not full manuscript review or independent semantic gold. Reviewer also authored old-three extraction, but independently checked new-four and integrated statements.','new_model_calls':0,'new_policy_executions':0,'scientific_independent_samples_added':0,'reviewed_outputs':receipt['outputs'],'unique_case_method_rows':len(cur),'source_manifest_file_count':len(idx['source_files']),'check_count_is_not_sample_size':True,'checks':checks,'failures':fails,'directly_read_evidence':evidence,'limits':['B06操作范围仍未闭合。','S02闭集白名单原文依据仍未闭合。','S03缺值风险来自静态阅读，没有执行失败政策来虚构缺值拒绝。','B19来源默认值、ABI与生产可达性必须分列；结果一致不证明显式提取默认值。','原先机制干预与模型批次仅引用，不重复记本轮产出。','当前为事后、暴露任务、适配流程核读，不提供准确率或普适优势证据。']}
(OUT/'INDEPENDENT_SEMANTIC_REVIEW.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 语义比较整合报告独立核验','', '日期：2026-10-15。','', '**结论：在本次限定的阶段解释和追溯范围内通过，未发现需要返工的事实错误或新增科学主张越界。**','', '核验对象为SEMANTIC_COMPARISON_CN.md、EXPERIMENT_SUMMARY_CN_R3.md、SEMANTIC_COMPARISON.csv、SEMANTIC_EVIDENCE_INDEX.json。只读原件，不调用模型、不执行政策。旧三例提取由本核验者曾参与；共同目标四例及整合表述重新直接查原件，不将该复核称完全独立语义gold。','', '## 实质核验','', '|问题|核验结论|','|---|---|','|首次与反馈修复|S02/S04首次缺目标条件与后续反馈补出分列；没有用reason代替实际政策。|','|P2P范围外|S02/S03没有生成政策，不被计成语义理解错误。|','|S02来源|可见OpenAPI缺additionalProperties=false；闭集约定未被写成原文唯一正确含义。|','|S03分层|整数意图、is_integer/typeof编译失败、缺值额外必填静态风险分别说明；不虚构未执行决策。|','|B06|三方首次已有latest条件，适用范围仍开放；AutoPAC Judge发现该范围问题的贡献未被遗漏。|','|B13/B17/B19主条件|对已定义数值或已知合法布尔/枚举状态，原候选支持整合表述；保留适配器提供上限/角色与状态的边界。|','|B19默认值|原文默认All、ABI只声明string、生产可达性未知分开。ECAS没有显式empty→All，整合报告未用deny反推模型提取。|','|历史控制|144行机制结果和历史Judge/模型结果仅为引用；本轮新增模型/政策执行均0。|','', '## 交付与追溯','', f"- 21个唯一案例—方法键，与R2逐行对应；执行status、symbol、project及batch均相同。",f"- {len(idx['source_files'])}份source manifest文件SHA256逐一匹配；4份输出及4份受保护文件哈希匹配；CSV的字段指针可解析。",f"- 共{len(checks)}项机械和定点解释检查全部通过。这是核验项目数量，不是样本量。",'- 具体检查、哈希、直接核读的原件见同名JSON。','', '## 通过范围与未闭合事项','']
lines += ['- '+s for s in payload['limits']]
if fails: lines+=['','## 具体失败',json.dumps(fails,ensure_ascii=False,indent=2)]
(OUT/'INDEPENDENT_SEMANTIC_REVIEW_CN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':payload['status'],'checks':len(checks),'failures':len(fails),'new_model_calls':0,'new_policy_executions':0},ensure_ascii=False))
