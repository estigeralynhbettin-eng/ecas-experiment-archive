"""Reconcile local raw observations and publish a Chinese pilot report; no model calls."""
import csv
import datetime
import json
from pathlib import Path
from pilot_lib import ROOT,LANE,CONFIG,read,dump,sha,verify_inputs

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    verify_inputs();state=read(ROOT/'EXECUTION_STATE.json');calls=read(ROOT/'CALL_LEDGER.json')
    audit=[]
    for call in calls:
        p=Path(call['raw_response_path'])
        if call['status']=='COMPLETED' or call.get('local_recovery_status')=='RECOVERED_LOCAL_STATUS_ALIAS':
            raw=read(p);content=json.loads(raw['choices'][0]['message']['content'])
            audit.append({'check':'call_raw_'+str(call['index']),'pass':sha(p)==call['raw_response_sha256'] and raw['model']=='glm-5.2' and raw['choices'][0]['finish_reason']=='stop' and bool(content.get('output')),'path':str(p)})
            if call.get('local_recovery_status'):
                recovery=read(p.parent/'LOCAL_RECOVERY_RECEIPT.json')
                audit.append({'check':'call_recovery_'+str(call['index']),'pass':sha(call['recovered_output_path'])==recovery['recovered_output_sha256'] and recovery['business_rules_changed'] is False})
    rows=state['rows'];table=[]
    for row in rows:
        task=row['task'];method=row['method'];observed=[]
        for req in row.get('requests',[]):
            fixtures=read(ROOT/'sealed_evaluation'/task/(req['channel']+'.json'))['vectors']
            same=any(v['envelope']==req['input'] and v['expected_class']==req['expected'] for v in fixtures)
            audit.append({'check':task+'_'+method+'_'+req['channel']+'_fixture','pass':same})
            observed.append(req['actual'].get('decision'))
        if method!='ECAS_MATCHED' and row['status']=='EVALUATED':
            base=ROOT/'effect_runs'/task/method
            freeze=read(base/'CANDIDATE_FREEZE.json')
            audit.append({'check':task+'_'+method+'_frozen_policy','pass':sha(freeze['policy_path'])==freeze['policy_sha256']})
            # Verify decisions against raw OPA output, independent from summary booleans.
            for req in row['requests']:
                raw=read(base/(f"final_{req['channel']}_0.stdout.txt"))
                expressions=raw.get('result',[])
                value=expressions[0]['expressions'][0]['value'] if len(expressions)==1 else None
                actual='allow' if value is True else 'deny' if value is False else None
                audit.append({'check':task+'_'+method+'_'+req['channel']+'_raw_opa','pass':actual==req['actual'].get('decision')})
        status=row['status']
        pair=row.get('request_pair_correct',False)
        table.append({'task':task,'method':method,'status':status,'legal':observed[0] if observed else None,'invalid':observed[1] if len(observed)>1 else None,'pair_correct':pair,'model_calls':len(row.get('calls',[])),'repaired_once':row.get('repaired_once',False),'reason':row.get('reason')})
    calls_ok=len(calls)<=30 and sum(c['smoke'] for c in calls)<=CONFIG['max_smoke_calls'] and all(c.get('retry_count',0)==0 for c in calls)
    audit.append({'check':'authorized_call_limit_and_no_retry','pass':calls_ok})
    prompt_tokens=sum((c.get('usage') or {}).get('prompt_tokens',0) for c in calls)
    completion_tokens=sum((c.get('usage') or {}).get('completion_tokens',0) for c in calls)
    receipt={'status':'PASS' if all(x['pass'] for x in audit) else 'FAIL','checked_at':now(),'checks':audit,'frozen_input_files':len(read(ROOT/'EXECUTION_INPUT_MANIFEST.json')),'execution_state':state['status'],'scientific_clearance':False,'scope':CONFIG['scope_id']}
    dump(ROOT/'RESULT_RECONCILIATION.json',receipt)
    summary={'status':state['status'],'classification':CONFIG['classification'],'rows':table,'calls':len(calls),'smoke_calls':sum(c['smoke'] for c in calls),'method_calls':sum(not c['smoke'] for c in calls),'repair_calls':sum(c['stage']=='repair' for c in calls),'total_prompt_tokens':prompt_tokens,'total_completion_tokens':completion_tokens,'actual_cost_status':'NOT_PROVIDER_REPORTED' if all(c.get('cost_status')!='reported_by_provider' for c in calls) else 'SEE_CALL_LEDGER','native_baseline_effect_results':0,'reconciliation_status':receipt['status']}
    dump(ROOT/'FINAL_SUMMARY.json',summary)
    # Preserve native rows unexecuted, replace only corresponding proposed adaptation states.
    original=read(ROOT/'RUN_STATUS.json');mapping={'P2P_STYLE_PROPOSED':'P2P_STYLE','AUTOPAC_STYLE_PROPOSED':'AUTOPAC_STYLE','ECAS_MATCHED_PROPOSED':'ECAS_MATCHED'}
    for original_row in original['rows']:
        match=next((r for r in table if r['task']==original_row['task'] and r['method']==mapping.get(original_row['method'])),None)
        if match:
            original_row.update({'execution_status':match['status'],'observed_legal_decision':match['legal'],'observed_invalid_decision':match['invalid']})
    original.update({'status':state['status'],'model_calls':len(calls),'native_methods_not_run':True,'summary':'FINAL_SUMMARY.json'})
    dump(ROOT/'RUN_STATUS.json',original)
    with (ROOT/'ADAPTED_COMPARISON.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]) if table else ['task','method','status']);w.writeheader();w.writerows(table)
    result_headers=next(csv.reader((ROOT/'RESULT_TRACEABILITY.csv').open(encoding='utf-8')))
    with (ROOT/'RESULT_TRACEABILITY.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=result_headers);w.writeheader()
        for i,row in enumerate(table):
            result_id=f'LOCAL-PILOT-{i+1:02d}'
            p=ROOT/'effect_runs'/row['task']/row['method']/'RESULT.json'
            v=int(row['pair_correct']) if row['status']=='EVALUATED' else ''
            w.writerow({'result_id':result_id,'experiment_id':CONFIG['scope_id'],'metric_name':'archived_request_pair_correct','dataset_name':row['task'],'dataset_version':'archived_FSV_visible_v4_oracle_v1','data_split':'retrospective_selected_already_exposed','sample_count':2 if row['status']=='EVALUATED' else 0,'raw_value':v,'reported_value':v,'unit':'boolean','aggregation':'per_case_per_adapted_method','source_output_path':str(p.relative_to(ROOT.parents[2])),'source_locator':'requests;status','script_path':str((ROOT/'run_pilot.py').relative_to(ROOT.parents[2])),'command_or_config':'EXECUTION_CONFIG.json;FROZEN_PROTOCOL_CN.md','seed':'not_set','environment':'WSL Python3.10/jsonschema;OPA1.19.0;Regal0.43.0;Windows approved GLM wrapper','git_commit':'NOT_AVAILABLE_HASH_FROZEN','checksum':sha(p),'rounding_rule':'none','status':'PASS' if row['status']=='EVALUATED' else 'NOT_APPLICABLE','verified_by':'local_raw_reconciliation','verified_at':now(),'notes':'Adapted pipeline local demonstration; source verified, not whole-manuscript scientific PASS. '+row['status']})
    names={'P2P_STYLE':'P2P适配版','AUTOPAC_STYLE':'AutoPAC适配版','ECAS_MATCHED':'ECAS同模型'}
    lines=['# 三例外部基线适配实测结果','',f'日期：2026-10-14；执行状态：{state["status"]}；原始证据对账：{receipt["status"]}。','',
      '## 结果','', '|案例|方法|合法请求|违规请求|执行状态|请求对正确|', '|---|---|---|---|---|---|']
    for row in table:
        lines.append(f'|{row["task"]}|{names[row["method"]]}|{row["legal"] or "未执行"}|{row["invalid"] or "未执行"}|{row["status"]}|{"是" if row["pair_correct"] else "否" if row["status"]=="EVALUATED" else "不适用"}|')
    lines+=['','合法allow与违规deny同时成立才是本请求对识别正确。全拒绝、范围外、弃权、开发检查拒绝与协议故障单列；未执行不冒充违规deny。','', '## 过程与预算','',
      f'- GLM/Z.AI glm-5.2，thinking enabled/high，共{len(calls)}次：开发smoke {summary["smoke_calls"]}次，方法调用{summary["method_calls"]}次，其中修复{summary["repair_calls"]}次；无自动重试。',
      f'- 提供方实际input tokens合计{prompt_tokens}，完成tokens合计{completion_tokens}。每次原响应、返回模型、finish_reason及usage见CALL_LEDGER.json与calls/。完成预算包含推理；未收到人民币费用字段，实际金额未知。',
      '- 本机没有精确GLM5.2 tokenizer。调用前采用已披露长度估计，smoke及每次调用以提供方prompt_tokens核验实际16384上限；不把估算数称精确token数。',
      '- 第3次开发smoke输出3条规则，因我精简提示schema遗漏原maxItems=1而失败；原响应与失败状态保留。恢复原结构限制，挪用一次预留调用作新提示smoke（共4次），条件修复总预算降为5次，总调用上限仍30次。没有删除候选规则来制造PASS。',
      '- 第6次P2P抽取的原status=EXTRACTED与解析器READY不一致，发生阶段暂停；只统一已完成抽取的等价状态词，保留原失败与原响应，DSARCP和业务条件未改。精确prompt/raw哈希复用第5/6次响应，本地恢复没有追加API调用。',
      '- Linux OPA/Regal与本范围11项T0检查通过，模型输出小试独立计入调用预算且不进入效果结果。编排、lint、编译、评价在WSL；Windows只承担全局批准wrapper的凭据加载与API调用。',
      '- P2P使用完整Regal规则集，唯目录与包名匹配规则因逐例保存目录关闭；记录完整lint输出。AutoPAC开发测试由操作者按公开来源预先冻结，并非原作者测试。',
      '- 最终归档请求对仅在候选冻结后用于评价，未作为Judge或修复反馈。Boolean状态只有两个真值，开发与最终测试不可避免共享条件值；本轮不能称新盲测。','', '## 原版与适配的边界','',
      '- P2P原代码尚未找到；AutoPAC原微调CodeT5权重尚缺，两个原版均未运行。本文报告按论文流程构建的适配实现。AutoPAC生成器替换是重大偏离，不能据此报告原版AutoPAC性能。',
      '- B06/S02来自原Apache Fineract，S04来自原ERPNext，仍只有两个项目。三例已暴露且事后选取，每例一对归档请求；不是总体准确率，也不能证明ECAS整体优越。',
      '- 业务请求上的共同正确与证据准入机制分开解释；P2P/AutoPAC的Rego执行不具有ECAS原契约准入接口，不把“没有这个接口”计作它们识别失败。',
      '- 参数和提示见FROZEN_PROTOCOL_CN.md、PROMPT_TEMPLATES.json、calls/*/prompt.txt；实际政策与开发/最终轨迹见effect_runs/。原版资格证据见NATIVE_QUALIFICATION.json。','', '## 未执行或被拒绝的分支','']
    blocked=[r for r in table if r['status']!='EVALUATED']
    if blocked:
        for row in blocked:lines.append(f'- {row["task"]} / {names[row["method"]]}：{row["status"]}；{row.get("reason") or "详见逐例RESULT.json及开发检查"}。')
    else:lines.append('本轮所有适配方法三例均完成最终请求评价。')
    if state['status']!='COMPLETED':lines+=['',f'运行停止原因：{state.get("error_type")} / {state.get("error")}。未完成项仍待处理，不能把已完成局部结果当全批完成。']
    lines+=['','## 文件入口','', '- FINAL_SUMMARY.json、ADAPTED_COMPARISON.csv：逐例结果与实际调用/usage。','- RESULT_RECONCILIATION.json：原响应、政策冻结与OPA实际输出的确定性对账。','- RESULT_TRACEABILITY.csv：本范围结果追溯；不修改根历史账本。','- EXECUTION_INPUT_MANIFEST.json：冻结输入、代码、工具及wrapper的哈希绑定。','', '本轮未改论文、旧实验或投稿状态；该结果供作者选择案例及设计进一步比较。']
    (ROOT/'RESULTS_CN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'state':state['status'],'reconciliation':receipt['status'],'rows':len(table),'calls':len(calls),'summary':table},ensure_ascii=False))

if __name__=='__main__':main()
