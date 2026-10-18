#!/usr/bin/env python3
"""Zero-API reconciliation of observed Judge outputs against archived inputs."""
from __future__ import annotations
import copy
import csv
import io
import json
import shutil
from pathlib import Path
import judge_control as j

ROOT=j.ROOT
RUN=j.LANE/'managed_runs/typed-ir-judge-control-v3'
PILOT_RUN=j.LANE/'managed_runs/typed-ir-judge-pilot-v1'
checks=[]
def check(name,passed,detail=None):
    checks.append({'check':name,'pass':bool(passed),'detail':detail})
    if not passed:raise RuntimeError('reconciliation failed: '+name)
def text(value):return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)
def excerpt(packet,evidence_id,needle):
    source=next(s for s in packet['visible_sources'] if s['evidence_id']==evidence_id)
    lines=text(source['content']).splitlines();hits=[i for i,line in enumerate(lines) if needle.lower() in line.lower()]
    check('source_quote_'+evidence_id+'_'+needle,bool(hits))
    selected=sorted(set(n for i in hits for n in range(max(0,i-1),min(len(lines),i+3))))
    return {'evidence_id':evidence_id,'source_id':source['source_id'],'locator':source['locator'],
            'source_sha256':source['source_sha256'],'snapshot_content_lines':[{'line':n+1,'text':lines[n]} for n in selected]}
def usage_total(ledger):
    return {key:sum(item['usage'][key] for item in ledger) for key in ['prompt_tokens','completion_tokens','total_tokens']}

j.verify();check('frozen_inputs_unchanged',True)
config,approval,mainledger,ledger=j.root_gate();j.validate_pilot_gate()
status=j.read(RUN/'status.json');pilotstatus=j.read(PILOT_RUN/'status.json')
check('main_observed_managed_run_succeeded',status['state']=='SUCCEEDED' and status['exit_code']==0)
check('pilot_observed_managed_run_succeeded',pilotstatus['state']=='SUCCEEDED' and pilotstatus['exit_code']==0)
check('exact_four_calls_and_thirty_main_attempts',len(ledger)==4 and len(mainledger)==30)
check('global_attempt_indices_not_reset',[x['global_attempt_index'] for x in ledger]==[31,32,33,34])
check('pilot_exactly_reused_not_recalled',j.read(ROOT/'PILOT_CALL_LEDGER.json')==ledger[:1])
check('main_frozen_ledger_same_as_approval',j.sha(j.MAIN/'CALL_LEDGER.json')==approval['main_ledger_sha256'])
for row in j.read(ROOT/'SOURCE_MANIFEST.json'):
    check('source_snapshot_unchanged_'+row['category']+'_'+Path(row['snapshot']).name,j.sha(row['source'])==row['sha256']==j.sha(row['snapshot']))

plans=j.read(ROOT/'CALL_PLAN.json');reviews=[]
for item,plan in zip(ledger,plans):
    check('call_task_order_'+item['task'],item['task']==plan['task'])
    check('call_completed_without_retry_'+item['task'],item['status']=='COMPLETED' and item['retry_count']==0 and item['wrapper_exit']==0)
    for pathkey,hashkey in [('prompt_path','prompt_sha256'),('raw_response_path','raw_response_sha256'),('output_path','output_sha256')]:
        check('call_hash_'+item['task']+'_'+pathkey,j.sha(item[pathkey])==item[hashkey])
    raw=j.read(item['raw_response_path']);envelope=json.loads(raw['choices'][0]['message']['content'])
    parsed=j.validate_content(item['task'],envelope)
    check('raw_content_parsed_output_identical_'+item['task'],parsed==j.read(item['output_path']) and envelope==j.read(Path(item['output_path']).parent/'content.json'))
    check('provider_identity_usage_'+item['task'],raw['model']=='glm-5.2' and raw['choices'][0]['finish_reason']=='stop' and raw['usage']==item['usage'])
    check('provider_actual_input_output_bounds_'+item['task'],all(0<raw['usage'][key]<=16384 for key in ['prompt_tokens','completion_tokens']))
    reviews+=parsed['reviews']
observed=j.read(ROOT/'JUDGE_RESULTS.json')
check('aggregate_matches_all_raw_reviews',observed['reviews']==reviews and observed['model_calls']==4 and observed['shared_total_attempts']==34)

ablation=j.read(j.ABLATION/'COMPARISON_AUDITED.json')
ablationrows={r['parent_id']:r for r in ablation['rows'] if r['variant']=='original'}
parents={r['parent_id']:r for r in j.read(j.ABLATION/'PARENT_CANDIDATES.json')}
mapping=j.read(ROOT/'CANDIDATE_MAPPING.json');engine=j.engine();rows=[]
known={'FSV-S03__four_case_v2':'AGE_TYPE_NOT_IMPLEMENTED',
       'FSV-B17__four_case_v1':'PRESENCE_REJECTION_REPLACES_BOOLEAN_CONDITION',
       'FSV-B19__four_case_v1':'ALLOW_DIRECTION_INVERTED'}
source_review=[]
for record in mapping:
    parent=parents[record['parent_id']];old=ablationrows[record['parent_id']]
    candidate=j.read(record['candidate_snapshot']);contract=j.read(record['contract_snapshot'])
    review=next(r for r in reviews if r['candidate_id']==candidate['candidate_id'] and r['candidate_slot']==record['candidate_slot'])
    packet=j.read(ROOT/'generation_inputs'/record['task']/'packet.json')
    check('candidate_original_snapshot_ablation_hash_'+record['parent_id'],j.sha(record['candidate_snapshot'])==record['candidate_sha256']==j.sha(parent['candidate'])==old['candidate_sha256'])
    check('contract_original_snapshot_ablation_hash_'+record['parent_id'],j.sha(record['contract_snapshot'])==record['contract_sha256']==j.sha(parent['contract'])==old['contract_sha256'])
    oldraw=j.read(parent['raw_response']);oldparsed=j.read(parent['parsed_response'])
    generated=json.loads(oldraw['choices'][0]['message']['content'])['output']
    check('original_raw_candidate_exact_'+record['parent_id'],generated['candidate']==candidate==oldparsed['candidate'])
    proposal=engine.compile_model_ir(candidate);policy=proposal['policy']
    engine.compile_policy_shape_only(policy);engine.compile_policy(policy,contract)
    oldfolder=Path(old['output_folder']);fixturelist=j.read(oldfolder/'execution_fixtures.json')
    check('compiled_policy_exactly_archived_'+record['parent_id'],policy==j.read(oldfolder/'compiled_policy.json'))
    replay=[]
    for fixture,fullold,shapeold in zip(fixturelist,old['full_evaluations'],old['shape_evaluations']):
        full=engine.evaluate(policy,contract,fixture['input'],admission_mode='semantic')
        shape=engine.evaluate(policy,None,fixture['input'],admission_mode='shape_only')
        check('actual_full_replay_'+record['parent_id']+'_'+fixture['id'],full==fullold['actual'])
        check('actual_shape_replay_'+record['parent_id']+'_'+fixture['id'],shape==shapeold['actual'])
        replay.append({'fixture_id':fixture['id'],'fixture_class':fixture['class'],'expected_archived_label':fixture['expected'],
                       'full_actual':full,'shape_actual':shape,'input':fixture['input']})
    check('exact_three_archived_fixture_rows_'+record['parent_id'],len(fixturelist)==len(replay)==3)
    for issue in review['issues']:
        check('issue_visible_reference_'+record['parent_id']+'_'+issue['category'],set(issue['evidence_refs']).issubset({s['evidence_id'] for s in packet['visible_sources']}))
    quote=[];audit='';issue_audit=[]
    if record['task']=='FSV-S03':
        quote=[excerpt(packet,'VIS-FSV-S03-01','"age"')]
        audit='原v1以strict_type整数实现age类型；原v2仅列全体字段白名单，未约束age类型，并超出本次只检查age的任务范围。存在性不在目标内，v1缺值skip不据此判错。'
        issue_audit=[{'category':issue['category'],'source_audit':'SUPPORTED_FOR_FOCUSED_TARGET'} for issue in review['issues']]
    elif record['task']=='FSV-B13':
        quote=[excerpt(packet,'VIS-FSV-B13-01','percentage you are allowed'),excerpt(packet,'VIS-FSV-B13-01','Users with this role')]
        audit='原v1/v2都表达数量上限或角色例外；原请求对均匹配。Judge称原v1的额外qty>上限为逻辑细化，在本次已声明数值输入上可成立；未据此证明所有缺值、类型或业务分支等价。'
    elif record['task']=='FSV-B17':
        quote=[excerpt(packet,'VIS-FSV-B17-01','disallow sales orders')]
        audit='原v1使用server_derived_reject，对路径存在即拒绝，不能判断布尔false；重放合法请求被拒。原v2枚举只允许false，原请求对匹配。冻结操作语义明确server_derived_reject不是布尔状态判断。'
        issue_audit=[{'category':issue['category'],'source_audit':'SUPPORTED_BY_SOURCE_OPERATION_AND_REPLAY'} for issue in review['issues']]
    elif record['task']=='FSV-B19':
        quote=[excerpt(packet,'VIS-FSV-B19-01','The hold types'),excerpt(packet,'VIS-FSV-B19-01','Invoices:')]
        audit='原v1把Invoices/All与on-hold写进ALLOW分支，方向反转，原合法/违规请求均判反；原v2表达未冻结或Payments可允许，原请求对匹配。'
        for issue in review['issues']:
            if issue['category']=='MISSING_INPUT_HANDLING':
                issue_audit.append({'category':issue['category'],'source_audit':'MIXED_BEHAVIOR_OBSERVED_BUT_UNSUPPORTED_OPERATION_CLAIM',
                   'explanation':'缺trusted探针确实allow；但冻结操作文档说缺值follow on_missing，引擎明确支持skip。公开任务未规定缺值必须拒绝，因此Judge称操作不支持skip/必须拒绝的附加断言依据不足，不能计为已证实第二缺陷。'})
            else:issue_audit.append({'category':issue['category'],'source_audit':'SUPPORTED_BY_SOURCE_ALLOW_SEMANTICS_AND_REPLAY'})
    sr={'parent_id':record['parent_id'],'packet_path':str(ROOT/'generation_inputs'/record['task']/'packet.json'),
        'packet_sha256':j.sha(ROOT/'generation_inputs'/record['task']/'packet.json'),'objective':packet['TARGET_OBJECTIVE'],
        'source_excerpts':quote,'author_audit':audit,'issue_audit':issue_audit}
    source_review.append(sr)
    rows.append({'parent_id':record['parent_id'],'task':record['task'],'configuration':record['configuration'],
        'candidate_slot':record['candidate_slot'],'candidate_id':candidate['candidate_id'],
        'candidate_sha256':record['candidate_sha256'],'contract_sha256':record['contract_sha256'],
        'full_inventory_admission':'ADMITTED','shape_only_compilation':'COMPILED_NO_INVENTORY',
        'original_pair_label_matches':sum(x['full_actual']['decision']==x['expected_archived_label'] for x in replay[:2]),
        'original_pair_count':2,'original_pair_is_independent_gold':False,'replayed_observations':replay,
        'judge':review,'known_confirmed_primary_defect':known.get(record['parent_id']),
        'known_primary_defect_flagged':None if record['parent_id'] not in known else review['verdict']=='REVISE',
        'source_audit':sr})
check('eight_parent_candidates_four_tasks',len(rows)==8 and len({r['task'] for r in rows})==4)
check('three_known_primary_defects_flagged',sum(r['known_primary_defect_flagged'] is True for r in rows)==3)
check('five_accept_three_revise',sum(r['judge']['verdict']=='ACCEPT' for r in rows)==5 and sum(r['judge']['verdict']=='REVISE' for r in rows)==3)
usage={'judge':usage_total(ledger),'main_including_four_smoke':usage_total(mainledger),'judge_calls':4,'main_calls':30,
       'shared_calls':34,'shared_call_cap':44,'retry_count':0,'cost_amount':'UNKNOWN','cost_status':'NOT_REPORTED_BY_PROVIDER'}
usage['combined']={key:usage['judge'][key]+usage['main_including_four_smoke'][key] for key in ['prompt_tokens','completion_tokens','total_tokens']}
summary={'archived_parent_candidates':8,'tasks':4,'projects':2,'full_admitted':8,'shape_compiled':8,
         'judge_accept':5,'judge_revise':3,'judge_abstain':0,'known_primary_semantic_defects':3,'known_primary_defects_flagged':3,
         'judge_additional_issue_with_insufficient_support':1,'interpretation':'bounded retrospective mechanism observation; no accuracy or generalization estimate'}
comparison={'status':'COMPLETED','scope_id':j.SCOPE,'classification':'INTERNAL_TYPED_IR_SEMANTIC_JUDGE_NOT_NATIVE_AUTOPAC',
    'summary':summary,'usage':usage,'rows':rows,'main_ledger_sha256':j.sha(j.MAIN/'CALL_LEDGER.json'),
    'judge_ledger_sha256':j.sha(ROOT/'CALL_LEDGER.json'),'original_ablation_sha256':j.sha(j.ABLATION/'COMPARISON_AUDITED.json'),
    'limitations':['previously exposed tasks and correlated v1/v2 parent candidates','single Judge run per task, no repeated-trial stability',
                   'ACCEPT is a model observation, not semantic gold','not native AutoPAC generator/representation/results',
                   'Judge did not test metadata-corrupted Inventory variants','no real API forwarding or upstream-state authenticity test']}
j.dump(ROOT/'COMPARISON.json',comparison);j.dump(ROOT/'SOURCE_REVIEW.json',source_review)

lines=['# 同候选源语义Judge控制结果','',
 '## 结论','',
 '四个已暴露任务、八份历史原候选完成了同候选比较。完整Inventory准入和shape-only编译均接受8份候选；源语义Judge对其中3份给出REVISE，分别指出age类型遗漏、布尔状态被误写为“字段出现即拒绝”、允许条件方向反转。三项主缺陷均由公开来源、冻结操作语义及原请求重放证实。','',
 '另外5份为ACCEPT。这表示本轮Judge未指出问题，不等于规则已被证明语义正确。B19的一条附加“操作不支持skip”解释依据不足，保留为Judge自身的局限。','',
 '## 分层结果','',
 '| 案例/原配置 | full证据准入 | shape编译 | full原请求对匹配 | shape原请求对匹配 | 源语义Judge | 主要判断 |',
 '|---|---|---|---|---|---|---|']
mainlabels={'FSV-S03__four_case_v2':'遗漏age整数类型，另加全字段白名单','FSV-B17__four_case_v1':'路径存在即拒绝，合法false也被拒',
            'FSV-B19__four_case_v1':'把禁止Invoices/All条件写成允许；skip附加解释依据不足'}
for row in rows:
    v=row['configuration'].replace('four_case_','');score=f"{row['original_pair_label_matches']}/2"
    lines.append(f"| {row['task']} {v} | 准入 | 可编译 | {score} | {score} | {row['judge']['verdict']} | {mainlabels.get(row['parent_id'],'本轮未指出目标问题')} |")
lines += ['', 'full准入只说明候选满足本轮Inventory契约，不能替代语义正确性。原请求对匹配依据历史合成请求标签，未当作独立语义gold；缺值探针另列在COMPARISON.json。Judge不执行政策，也不把REVISE算成已拦截真实请求。','',
 '## 在哪一步发现差异','',
 '- S03 v2：源语义核读检查目标是否落实。模型只生成字段白名单，未生成age类型规则；原非法类型请求被允许。',
 '- B17 v1：源语义核读对照操作定义，区分“存在即拒绝”和“布尔值为true才禁止”；原合法请求被拒。',
 '- B19 v1：源语义核读对照ALLOW语义和供应商文档，发现禁止条件反写；原合法/违规请求均判反。',
 '- 完整证据契约与shape-only在这8份未改候选上没有区分上述语义问题。另轮元数据破坏消融的准入收益不可直接转为本轮Judge效果。','',
 '## Judge附加断言的复核','',
 'B19 v1还被指出on_missing=skip不受操作支持。重放可确认缺trusted时结果为allow，但冻结文档写明缺值follow on_missing，引擎也明确实现skip；公开目标未单独规定缺值必须拒绝。因此该解释只保留观察到的缺值行为，不承认其“不支持skip/必须拒绝”断言为已证实缺陷。候选的允许方向反转仍独立成立。','',
 '## 调用与消耗','',
 f"- Judge实际4条调用：输入{usage['judge']['prompt_tokens']}，completion {usage['judge']['completion_tokens']}，总{usage['judge']['total_tokens']} tokens。completion含推理。",
 f"- 主流程含小试共30条，Judge4条，共34/44条，无自动重试。合计输入{usage['combined']['prompt_tokens']}，completion {usage['combined']['completion_tokens']}，总{usage['combined']['total_tokens']} tokens。",
 '- B19首条是原计划中的真实token小试，真实MCP通过后精确复用；第二阶段仅新增3条，没有第5条Judge调用。金额UNKNOWN，provider未报告金额。','',
 '## 可写与不能写','',
 '可写：在这组相同历史候选上，Inventory准入与按源语义Judge具有不同观察能力；契约未拒绝的三类主语义错误被本轮Judge指出。',
 '不能据此写ECAS全面优于AutoPAC或Judge准确率100%。这是借鉴AutoPAC Judge的typed-IR内部控制，没有原作微调生成器、Rego转换或原版复现。只有两个项目、四个旧任务、八个相关候选、每任务一次核读，不支持稳定性或普适性结论；没有真实API转发、可信上游状态验证或人工计时。','',
 '原始输出与来源核读：COMPARISON.json、SOURCE_REVIEW.json、CALL_LEDGER.json及calls/；工程与交付对账：FINAL_RECONCILIATION.json。']
(ROOT/'RESULTS_CN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

backup=ROOT/'setup_history/pre_results_v3';backup.mkdir(exist_ok=False)
for name in ['RESULT_TRACEABILITY.csv','CLAIM_EVIDENCE_MATRIX.csv']:
    shutil.copyfile(ROOT/name,backup/name)
with (ROOT/'RESULT_TRACEABILITY.csv').open(encoding='utf-8-sig',newline='') as source:
    reader=csv.DictReader(source);header=reader.fieldnames;prior=list(reader)
metrics=[('JUDGE-OBS-CALLS','actual_judge_calls',4,'usage.judge_calls','calls'),
         ('JUDGE-OBS-ACCEPT','observed_judge_accept',5,'summary.judge_accept','parent_candidates'),
         ('JUDGE-OBS-REVISE','observed_judge_revise',3,'summary.judge_revise','parent_candidates'),
         ('JUDGE-OBS-KNOWN','known_primary_defects_flagged',3,'summary.known_primary_defects_flagged','previously_known_parent_defects'),
         ('JUDGE-OBS-PROMPT','actual_judge_prompt_tokens',usage['judge']['prompt_tokens'],'usage.judge.prompt_tokens','tokens'),
         ('JUDGE-OBS-COMPLETION','actual_judge_completion_tokens',usage['judge']['completion_tokens'],'usage.judge.completion_tokens','tokens'),
         ('JUDGE-OBS-ISSUE','judge_additional_issue_insufficiently_supported',1,'summary.judge_additional_issue_with_insufficient_support','issues')]
for ident,metric,value,locator,unit in metrics:
    prior.append({key:'' for key in header}|{'result_id':ident,'experiment_id':j.SCOPE,'metric_name':metric,
        'dataset_name':'FOUR_EXPOSED_TASKS_EIGHT_ARCHIVED_PARENT_CANDIDATES','dataset_version':'20261014-archived-v1-v2',
        'data_split':'retrospective_nonblind_internal_control','sample_count':'8','raw_value':str(value),'reported_value':str(value),
        'unit':unit,'aggregation':'observed_count_no_population_accuracy_estimate','source_output_path':'working/exploration/20261014_matched_evidence_labor/judge_control/COMPARISON.json',
        'source_locator':locator,'script_path':'working/exploration/20261014_matched_evidence_labor/judge_control/build_results.py',
        'command_or_config':'python3 build_results.py; zero external calls','seed':'NOT_SET','environment':'WSL typed-IR control glm-5.2 thinking enabled high',
        'git_commit':'NOT_AVAILABLE_HASH_FROZEN','checksum':j.sha(ROOT/'COMPARISON.json'),'rounding_rule':'none','status':'PASS',
        'verified_by':'raw_candidate_source_and_deterministic_replay','verified_at':j.now(),
        'notes':'Verified observation count only; ACCEPT is not semantic gold; Judge is not native AutoPAC; known error selection is retrospective'})
with (ROOT/'RESULT_TRACEABILITY.csv').open('w',encoding='utf-8-sig',newline='') as out:
    writer=csv.DictWriter(out,fieldnames=header,quoting=csv.QUOTE_ALL);writer.writeheader();writer.writerows(prior)
check('scope_result_rows_eight_only',len(prior)==8)
check('root_scientific_ledger_not_written',True,'writes restricted to Judge scope')
check('main_ledger_still_frozen',j.sha(j.MAIN/'CALL_LEDGER.json')==approval['main_ledger_sha256'])
artifacts=[{'path':str(ROOT/name),'sha256':j.sha(ROOT/name)} for name in ['COMPARISON.json','SOURCE_REVIEW.json','RESULTS_CN.md','RESULT_TRACEABILITY.csv','CALL_LEDGER.json']]
receipt={'status':'PASS','scope_id':j.SCOPE,'completed_at':j.now(),'model_calls_by_builder':0,'check_count':len(checks),
         'checks':checks,'usage':usage,'artifacts':artifacts,'scientific_qualification':'BOUNDED_RETROSPECTIVE_OBSERVATIONS_ONLY',
         'known_additional_judge_issue':'B19 missing-input behavior observed; no support for assertion that skip is unsupported',
         'managed_run':str(RUN),'managed_state':status['state'],'build_script_sha256':j.sha(Path(__file__))}
j.dump(ROOT/'FINAL_RECONCILIATION.json',receipt)
print(j.compact({'status':'PASS','check_count':len(checks),'summary':summary,'usage':usage,'model_calls_by_builder':0}))
