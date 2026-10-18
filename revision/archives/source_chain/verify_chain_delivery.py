"""Read-only independent delivery audit; does not import or execute probe/policies."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json

OUT=Path(__file__).resolve().parent
EXP=OUT.parent
def txt(p):return p.read_text(encoding='utf-8-sig')
def j(p):return json.loads(txt(p))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
checks=[]
def ck(name,b):checks.append({'check':name,'pass':bool(b)})
build=j(OUT/'BUILD_RECONCILIATION.json')
manifest=j(OUT/'CHAIN_SOURCE_MANIFEST.json')
for e in manifest['source_files']+build['outputs']:
    ck('file_hash:'+e['path'],sha(Path(e['path']))==e['sha256'])
for p,h in build['protected_files_unchanged'].items():
    ck('protected_hash:'+p,sha(Path(p))==h)
r1=EXP/'20261014_matched_evidence_labor/EXPERIMENT_SUMMARY_CN.md'
r1qa=j(EXP/'20261014_matched_evidence_labor/SUMMARY_INDEPENDENT_QA.json')
ck('R1_hash_matches_previous_independent_QA',sha(r1)==r1qa['summary_sha256'])
checks[-1]['classification']='OLDER_HISTORICAL_BASELINE_NOT_APPLICABLE_TO_CURRENT_SCOPE_IMMUTABILITY'

chain=j(OUT/'SEVEN_CASE_CHAIN.json')['rows']
ct=csvrows(OUT/'SEVEN_CASE_CHAIN.csv')
ck('seven_unique_chain_rows',len(chain)==len(ct)==len({r['case'] for r in chain})==7)
cm={r['case']:r for r in ct}
prior={(r['task'],r['method']):r for r in csvrows(EXP/'20261015_seven_case_mechanism/SEVEN_CASE_COMPARISON.csv')}
for row in chain:
    case=row['case'];c=cm[case];p=prior[(case,'ECAS_MATCHED')]
    ck(case+':csv_project_batch',c['project_name']==row['project']==p['project_name'] and c['batch']==row['batch']==p['batch'])
    ck(case+':csv_semantic_scope_fields',all(c[k]==row[k] for k in ('source_condition_cn','ir_condition_cn','scope_status_cn','archive_admission','archived_legal_decision','archived_violation_decision')))
    for e in row['evidence_files']+[row['raw_to_candidate_semantic_audit']]:ck(case+':evidence_hash:'+e['path'],sha(Path(e['path']))==e['sha256'])
    candidate=j(Path(c['candidate_path']));contract=j(Path(c['contract_path']))
    ck(case+':candidate_contract_hashes',sha(Path(c['candidate_path']))==c['candidate_sha256'] and sha(Path(c['contract_path']))==c['contract_sha256'])
    ev={e['evidence_id']:e for e in contract['evidence']}
    ck(case+':target_equal',candidate['target']==row['target'])
    for b in row['binding_rows']:
        ix=int(b['rule_pointer'].rsplit('/',1)[-1])
        ck(case+':actual_rule_equal',b['rule']==candidate['rules'][ix])
        ck(case+':registered_evidence_exact',b['registered_evidence']==[ev[x] for x in b['rule']['evidence_refs']])
        ck(case+':declared_scope_not_semantic_proof','does not prove source meaning or runtime provenance' in b['interpretation'])
    res=j(Path(p['result_source']))
    admission=res['admission'] if row['batch']=='A' else res['first_checks']['admission_status']
    requests=res['requests'] if row['batch']=='A' else res['final_evaluation']['requests']
    decisions={r['channel']:r['actual']['decision'] for r in requests}
    ck(case+':actual_historical_admission',row['archive_admission']==admission=='ADMITTED')
    ck(case+':actual_historical_pair',row['archived_legal_decision']==decisions['O-L']=='allow' and row['archived_violation_decision']==decisions['O-I']=='deny')

result=j(OUT/'RESULTS.json');summary=j(OUT/'PROBE_SUMMARY.json')
ck('completed_32_source_288_policy',result['status']=='COMPLETED' and len(result['source_rows'])==32 and len(result['rows'])==288)
ck('no_new_model_or_case',result['new_model_calls']==0 and result['new_cases']==0)
group=defaultdict(list)
for r in result['rows']:group[(r['arm'],r['method'])].append(r)
ck('nine_arms_methods',len(group)==9)
for s in summary['rows']:
    key=(s['arm'],s['method']);rr=group[key]
    diff=[r for r in rr if not r['agrees']]
    over=sum(r['source_decision']=='allow' and r['decision']=='deny' for r in rr)
    miss=sum(r['source_decision']=='deny' and r['decision']=='allow' for r in rr)
    ck('derived_summary:'+str(key),s['related_states']==len(rr)==32 and s['disagreement_count']==len(diff) and s['source_check_not_blocked_but_policy_deny']==over and s['source_check_blocked_but_policy_allow']==miss and set(s['disagreement_state_ids'])=={r['state_id'] for r in diff})
for arm in ('raw','saved','effective_manual'):
    for state in {r['state_id'] for r in result['source_rows']}:
        rr=[r for r in result['rows'] if r['arm']==arm and r['state_id']==state]
        ck('same_input_all_methods:'+arm+':'+state,len(rr)==3 and all(r['envelope']==rr[0]['envelope'] for r in rr))
        ck('manual_adapter_identity:'+arm+':'+state,all(r['manual_adapter']==(arm=='effective_manual') for r in rr))

ledger=csvrows(OUT/'RESULT_TRACEABILITY.csv');claims=csvrows(OUT/'CLAIM_EVIDENCE_MATRIX.csv')
lm={r['result_id']:r for r in ledger}
ck('scope_ledger_unique_12_claims_unique_9',len(lm)==len(ledger)==12 and len(claims)==len({r['claim_id'] for r in claims})==9)
for r in ledger:
    source=OUT.parents[2]/Path(r['source_output_path'].replace('\\','/'))
    ck('ledger_hash:'+r['result_id'],sha(source)==r['checksum'])
for c in claims:
    r=lm[c['result_id']]
    ck('claim_to_ledger:'+c['claim_id'],c['number_as_written']==r['reported_value'] and c['number_type']=='related_states_not_accuracy')
for s in summary['rows']:
    rid='SOURCE-CHAIN-DIFF-'+s['arm']+'-'+s['method']
    ck('ledger_to_recomputed_stat:'+rid,int(lm[rid]['reported_value'])==s['disagreement_count'])

probeaudit=j(OUT/'PROBE_INDEPENDENT_AUDIT.json')
ck('prior_probe_review_and_result_hash',probeaudit['status']=='PASS_WITH_EXPLICIT_SCOPE_LIMITS' and probeaudit['result_sha256']==sha(OUT/'RESULTS.json'))
status_path=Path(r'\\wsl.localhost\Ubuntu\root\ecas_source_rule_chain_20261015\managed_runs\source-rule-chain-main-v1\status.json')
status=j(status_path)
ck('actual_managed_main_succeeded',status['state']=='SUCCEEDED' and status['exit_code']==0 and status['outputs'][0]['sha256']==sha(OUT/'RESULTS.json'))
r4=txt(OUT/'EXPERIMENT_SUMMARY_CN_R4.md');chaintext=txt(OUT/'SEVEN_CASE_CHAIN_CN.md')
proposal=j(OUT/'RUNTIME_SEMANTIC_CONTRACT_PROPOSAL.json');proposaltext=txt(OUT/'RUNTIME_SEMANTIC_CONTRACT_PROPOSAL_CN.md')
ck('proposal_not_implemented',proposal['status']=='DESIGN_PROPOSAL_NOT_IMPLEMENTED_IN_CURRENT_ENGINE' and '不是当前ECAS已实现的保证' in proposaltext and '尚未进入原引擎' in r4)
ck('Inventory_registration_not_source_proof','不能抵消表中来源/API/接口定义的缺口' in r4 and '不能据此宣称全部来源语义或生产行为正确' in chaintext)
ck('source_check_not_full_PO_and_not_accuracy','不表示完整Purchase Order被接受或拒绝' in r4 and '不是模型语义准确率' in r4)
ck('S04_basic_email_only','未证明与后端全部邮箱规范等价' in r4)
ck('B06_S02_historical_limited','两例继续保留历史演示身份' in r4 and '不能宣称原API要求拒绝未知键' in r4)
ck('manual_effective_shared_not_model_advantage','三方共同获得同一输入' in r4 and '不能把手工适配收益归为ECAS模型优势' in r4)
ck('new_source_not_historical_model_input','原模型当时未见本轮新增的实现源码' in r4 and '不能回填为原任务的模型错误率' in r4)
ck('production_and_original_baselines_not_claimed','原版P2P/AutoPAC未运行' in r4 and '没有启动Frappe、数据库或HTTP' in r4)
historic=[c for c in checks if c.get('classification')=='OLDER_HISTORICAL_BASELINE_NOT_APPLICABLE_TO_CURRENT_SCOPE_IMMUTABILITY']
fails=[c for c in checks if not c['pass'] and c not in historic]
payload={'status':'PASS_WITH_EXPLICIT_SCOPE_LIMITS' if not fails else 'FAIL_NEEDS_REPAIR','review_scope':'Independent read-only audit of R4 integrated delivery, stage/source boundaries and numeric traceability; no new experiment or full manuscript review. This reviewer authored B06/S02 source closure, independently checked integrated claims and B19 result aggregates.','new_model_calls':0,'new_policy_executions':0,'new_source_function_executions':0,'reviewed_file_hashes':[{'path':str(OUT/n),'sha256':sha(OUT/n)} for n in ('EXPERIMENT_SUMMARY_CN_R4.md','SEVEN_CASE_CHAIN_CN.md','SEVEN_CASE_CHAIN.csv','SEVEN_CASE_CHAIN.json','RUNTIME_SEMANTIC_CONTRACT_PROPOSAL_CN.md','RUNTIME_SEMANTIC_CONTRACT_PROPOSAL.json','PROBE_SUMMARY.json','RESULT_TRACEABILITY.csv','CLAIM_EVIDENCE_MATRIX.csv','BUILD_RECONCILIATION.json','PROBE_INDEPENDENT_AUDIT.json')],'source_file_count':len(manifest['source_files']),'source_states':32,'policy_rows':288,'check_count_is_not_sample_size':True,'checks':checks,'failures':fails,'nonblocking_historical_observations':historic,'R1_prior_QA_hash':{'qa_path':str(EXP/'20261014_matched_evidence_labor/SUMMARY_INDEPENDENT_QA.json'),'older_qa_hash':r1qa['summary_sha256'],'R1_path':str(r1),'current_hash':sha(r1),'interpretation':'Older QA hash no longer matches. This is not a pre-scope baseline; it cannot prove or disprove writes by this scope. Current builder has no R1 write path and report only says retained.'},'managed_status':{'path':str(status_path),'sha256':sha(status_path),'state':status['state']},'remaining_limits':['B06源条款与旧操作映射未闭合；S02拒绝未知键没有HTTP依据。','Inventory结构对账不是原文语义、生产状态真实性证明。','S04仅基本格式；B13/B17仍依赖公共ABI；B19仅冻结类型子规则。','32相关手工状态与288相关观察不是独立案例、模型准确率或完整PO执行。','effective_manual是三方法共享的人工适配器；新契约仍未实现。','R1旧文件保留且本scope构建器无其写入路径；较早QA哈希不匹配，仅属历史基线不适用，不能证明本scope改动。']}
(OUT/'CHAIN_INDEPENDENT_REVIEW.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# R4链条整合交付独立审查','', '日期：2026-10-15。','', '**结论：通过限定范围审查；未发现需返工的事实错误、计数错配或科学主张越界。**','', '只读文件、原件及已保存运行终态，不重跑模型、政策、源码函数或实验。该核验者曾完成B06/S02源码核查；本次独立核对根任务整合稿及B19统计，不将其称完全独立gold。','', '## 已核对','', '- B06专用undoReAge与旧通用Adjust路径差别准确保留；S02准确分开内部四键检查、HTTP DTO链和未实际运行HTTP的边界。','- 七案例JSON逐项回到真实候选、contract与归档RESULT核对；ADMITTED、原请求allow/deny均匹配，但Inventory登记未被当作原文含义证明。','- S04只称基本Email；B19只称隔离供应商冻结检查，保存规范化与释放日期分列，未扩大为完整Purchase Order或模型准确率。','- 三方法每状态/投影收到完全相同输入；effective_manual明确为人工共有适配器。拟议契约未被写成当前引擎已有能力。',f"- {len(manifest['source_files'])}份来源manifest、7份派生输出哈希匹配；R2/R3与根两科学账本匹配保护哈希。",'- 七链CSV/JSON匹配，scope账本12行、claim账本9行逐项可回到RESULTS及PROBE_SUMMARY；32源码状态、288政策观察与实际SUCCEEDED run对账。',f"- 共{len(checks)}项检查：{len(checks)-len(historic)}项适用当前交付的核验通过；1项较早R1历史QA哈希不匹配，不是适用的本scope前置基线。检查条目不是独立样本量。",'', '## 仍未闭合','']+['- '+s for s in payload['remaining_limits']]+['','完整对象哈希、检查项、R1历史基线限制及实际run状态哈希见同名JSON。R4对R1只声称保留；可证哈希不变的范围是R2/R3与根两科学账本。本核验未修改任何原稿、冻结输入或结果。']
if fails:lines+=['','## 失败项',json.dumps(fails,ensure_ascii=False,indent=2)]
(OUT/'CHAIN_INDEPENDENT_REVIEW_CN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':payload['status'],'checks':len(checks),'failures':len(fails),'source_files':len(manifest['source_files'])},ensure_ascii=False))
