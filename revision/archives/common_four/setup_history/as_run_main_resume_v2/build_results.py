"""Read completed primary outputs, reconcile originals, and build Chinese tables.

This post-run script is outside the 64-file generation freeze. It never calls a
model. No report or scientific result is created when generation is incomplete.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from pilot_lib import ROOT, LANE, CONFIG, read, dump, sha, verify_inputs, adapt, rego_decision, strip_location
from pilot_lib import compile_model_ir, compile_policy, evaluate_ecas, PolicyError
from run_matched import normalize_stage, validate_stage

METHOD_NAMES={'P2P_STYLE':'P2P适配版','AUTOPAC_STYLE':'AutoPAC适配版','ECAS_MATCHED':'ECAS'}
CASE_NAMES={'FSV-S03':'S03：age类型','FSV-B13':'B13：收货数量及授权例外','FSV-B17':'B17：禁用客户','FSV-B19':'B19：供应商冻结类型'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def csv_text(rows,fields):
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows);return out.getvalue()
def mark(evaluation):
    rows=evaluation.get('requests',[])
    if len(rows)!=2:return '—'
    correct=sum(bool(x['pass']) for x in rows)
    return ['○','◐','●'][correct]
def success(actual):return not actual.get('engine_error') and actual.get('status','EXECUTED')=='EXECUTED'
def failure_class(result):
    status=result['status'];checks=result.get('final_checks',{})
    if status=='ELIGIBLE':return 'QUALIFIED_EXECUTION'
    if status=='OUT_OF_SCOPE':return 'METHOD_SCOPE'
    if status=='SCHEMA_GROUNDING_REJECTED':return 'ORGANIZATION_BINDING_REJECTION'
    if 'ABSTAIN' in status:return 'MODEL_OR_INTERNAL_JUDGE_ABSTENTION'
    if result['method']=='ECAS_MATCHED' and checks.get('admission_status')=='REJECTED':return 'EVIDENCE_CONTRACT_REJECTION'
    if result['method']=='ECAS_MATCHED' and not checks.get('compile_status'):return 'MODEL_IR_COMPILATION_REJECTION'
    if checks.get('compile_exit') not in (None,0):return 'REGO_COMPILATION_REJECTION'
    if checks.get('lint_exit') not in (None,0):return 'METHOD_LINT_REJECTION'
    if checks.get('developer_results',{}).get('passed') is False:return 'DEVELOPER_TEST_REJECTION'
    return 'OTHER_RECORDED_METHOD_TERMINAL'

def build(output,write_scope=False):
    state_path=ROOT/'EXECUTION_STATE.json'
    if not state_path.exists() or read(state_path).get('status')!='COMPLETED':
        raise RuntimeError('NOT_READY: no completed main result; do not fabricate or publish results')
    state=read(state_path)
    identity={(t,m) for t in CONFIG['tasks'] for m in CONFIG['methods']}
    rows=state.get('rows',[])
    if len(rows)!=12 or {(r['task'],r['method']) for r in rows}!=identity:
        raise RuntimeError('Completed status lacks exact 12 method/case identities')
    if state.get('scope_id')!=CONFIG['scope_id']:raise RuntimeError('Completed state scope mismatch')
    if output.exists():raise RuntimeError('Review output exists; choose a fresh version rather than overwrite')
    verify_inputs()
    output.mkdir(parents=True,exist_ok=False)
    audit=[]
    def check(name,passed,object_path=None,detail=None):
        audit.append({'check':name,'pass':bool(passed),'object_path':str(object_path) if object_path else None,'detail':detail})
    manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
    for item in manifest:check('frozen_source_script_tool_sha256',sha(item['path'])==item['sha256'],item['path'])
    t0=read(ROOT/'T0_RECEIPT.json')
    check('t0_binds_current_manifest',t0['status']=='PASS' and t0['frozen_manifest_sha256']==sha(ROOT/'EXECUTION_INPUT_MANIFEST.json'),ROOT/'T0_RECEIPT.json')
    ledger=read(ROOT/'CALL_LEDGER.json')
    check('call_indices_contiguous_and_total_cap',[x['index'] for x in ledger]==list(range(1,len(ledger)+1)) and len(ledger)<=44,ROOT/'CALL_LEDGER.json')
    check('smoke_actual_attempts_cap',sum(x['smoke'] for x in ledger)<=4,ROOT/'CALL_LEDGER.json')
    by_call={x['index']:x for x in ledger}
    usage_rows=[]
    for item in ledger:
        folder=Path(item['raw_response_path']).parent
        raw=read(item['raw_response_path']);outer=json.loads(raw['choices'][0]['message']['content'])
        original_content=read(folder/'content.json')
        normalized,changes=normalize_stage(item['stage'],outer['output'])
        validate_stage(item['stage'],normalized,item['smoke'])
        prompt=Path(item['prompt_path']).read_text(encoding='utf-8')
        expected={k:next(line.split('=',1)[1] for line in prompt.splitlines() if line.startswith(k+'=')) for k in ['BEGIN','END','STAGE']}
        usage=raw.get('usage',{})
        check('call_raw_prompt_identity',item['status']=='COMPLETED' and sha(item['raw_response_path'])==item['raw_response_sha256'] and
              Path(item['raw_response_path']).stat().st_size==item['raw_response_bytes'] and sha(item['prompt_path'])==item['prompt_sha256'] and
              Path(item['prompt_path']).stat().st_size==item['prompt_bytes'],item['raw_response_path'],{'index':item['index']})
        check('call_model_finish_settings_usage',raw.get('model')=='glm-5.2' and raw['choices'][0]['finish_reason']=='stop' and
              item['thinking']=='enabled' and item['reasoning_effort']=='high' and usage==item['usage'] and
              isinstance(usage.get('prompt_tokens'),int) and isinstance(usage.get('completion_tokens'),int) and
              usage['prompt_tokens']<=16384 and usage['completion_tokens']<=16384 and item['retry_count']==0,
              item['raw_response_path'],{'index':item['index']})
        check('call_sentinel_and_raw_content_correspondence',outer==original_content and outer['begin']==expected['BEGIN'] and
              outer['end']==expected['END'] and outer['stage']==expected['STAGE']==item['stage'],folder/'content.json')
        check('call_derived_output_equal',normalized==read(item['output_path']) and sha(item['output_path'])==item['output_sha256'],item['output_path'])
        summary=read(folder/'wrapper_summary.json')
        check('wrapper_capture_and_completeness',summary['capture_mode']=='direct_before_parse' and summary['completeness_gate']=='PASS' and
              summary['returned_model']==raw['model'] and summary['usage']==usage,folder/'wrapper_summary.json')
        usage_rows.append({'index':item['index'],'task':item['task'],'method':item['method'],'stage':item['stage'],'smoke':item['smoke'],
              'prompt_tokens':usage['prompt_tokens'],'completion_tokens':usage['completion_tokens'],
              'reasoning_tokens':usage.get('completion_tokens_details',{}).get('reasoning_tokens','UNKNOWN'),
              'latency_seconds':item.get('latency_seconds','UNKNOWN'),'actual_cost':summary.get('cost') if summary.get('cost') is not None else 'UNKNOWN',
              'cost_status':summary.get('cost_status','UNKNOWN'),'format_normalization':bool(changes),
              'as_run_failed_then_locally_recovered':bool(item.get('as_run_failure')),'new_API_for_local_recovery':item.get('local_recovery_new_API_calls',0),
              'raw_path':item['raw_response_path'],'raw_sha256':sha(item['raw_response_path'])})
    raw_files=list((ROOT/'calls').glob('*/response.raw.json'))
    check('raw_file_count_equals_actual_attempts',len(raw_files)==len(ledger),ROOT/'calls')
    all_freeze=read(ROOT/'ALL_GENERATION_FROZEN.json')
    check('all_generation_frozen_before_evaluation',all_freeze['count']==12 and all_freeze['final_evaluation_not_yet_read'] is True,ROOT/'ALL_GENERATION_FROZEN.json')
    freeze_by_id={(r['task'],r['method']):r for r in all_freeze['rows']}
    schema=read(ROOT/'execution_inputs/ecas_output_schema.json')
    compact_rows=[]
    for result in rows:
        task,method=result['task'],result['method'];folder=ROOT/'method_runs'/task/method
        actual_result=read(folder/'RESULT.json')
        check('state_equals_case_primary_result',actual_result==result,folder/'RESULT.json')
        terminal=folder/'GENERATION_TERMINAL_FREEZE.json'
        check('case_terminal_bound_by_all_freeze',sha(terminal)==freeze_by_id[(task,method)]['terminal_sha256'],terminal)
        if (folder/'FIRST_CANDIDATE_FREEZE.json').exists():
            frozen_first=read(folder/'FIRST_CANDIDATE_FREEZE.json')
            check('first_candidate_frozen_hash',sha(frozen_first['path'])==frozen_first['sha256'],folder/'FIRST_CANDIDATE_FREEZE.json')
        check('method_case_calls_and_repair_cap',len(result['calls'])<=CONFIG['max_method_case_calls'][method] and
              sum(by_call[x]['stage'] in ['repair','ecas_repair'] for x in result['calls'])<=1 and
              all(not by_call[x]['smoke'] and by_call[x]['task']==task and by_call[x]['method']==method for x in result['calls']),folder/'RESULT.json')
        packet=read(ROOT/'generation_inputs'/task/'packet.json');contract=read(ROOT/'execution_inputs'/task/'contract.json')
        stages=[('initial','first_checks'),('repaired','final_checks')] if result['repaired_once'] else [('initial','first_checks')]
        for phase,key in stages:
            checks=result.get(key,{})
            if not checks:continue
            phase_folder=folder/phase
            if method=='ECAS_MATCHED':
                candidate=read(phase_folder/'candidate.json');Draft202012Validator(schema).validate(candidate)
                stage_output=read(folder/('ecas_generate.json' if phase=='initial' else 'ecas_repair.json'))['candidate']
                check('ecas_candidate_raw_stage_and_target',candidate==stage_output and candidate['target']==packet['target'],phase_folder/'candidate.json')
                try:proposal=compile_model_ir(candidate)
                except PolicyError as error:
                    check('ecas_compile_rejection_reproduced',not checks.get('compile_status') and checks.get('reason')==str(error),phase_folder/'candidate.json')
                    continue
                check('ecas_compiled_proposal_reproduced',proposal==read(phase_folder/'compiled_proposal.json'),phase_folder/'compiled_proposal.json')
                if checks.get('policy_path'):
                    recomputed=compile_policy(proposal['policy'],contract)
                    check('ecas_admitted_policy_reproduced',recomputed==read(checks['policy_path']),checks['policy_path'])
            else:
                if not phase_folder.exists():continue
                generated=read(folder/('repair.json' if phase=='repaired' else ('p2p_rego.json' if method=='P2P_STYLE' else 'autopac_generate.json')))
                receipt=read(phase_folder/'FORMAT_RECEIPT.json')
                check('rego_original_equals_model_output',Path(checks['original_path']).read_text(encoding='utf-8')==generated['rego'],checks['original_path'])
                check('rego_original_formatted_checksums',sha(checks['original_path'])==receipt['original_sha256'] and
                      sha(checks['policy_path'])==receipt['formatted_sha256'],phase_folder/'FORMAT_RECEIPT.json')
                if receipt['parse_before_exit']==receipt['parse_after_exit']==receipt['format_exit']==0:
                    before=json.loads((phase_folder/'ast_before.stdout.txt').read_text());after=json.loads((phase_folder/'ast_after.stdout.txt').read_text())
                    check('independent_opa_ast_semantics_equal',strip_location(before)==strip_location(after) and receipt['ast_semantics_equal_without_location'],phase_folder/'FORMAT_RECEIPT.json')
                if method=='P2P_STYLE' and checks.get('policy_path'):
                    persisted=read(phase_folder/'CHECKS.json')
                    check('p2p_full_lint_record_retained',persisted.get('lint_exit')==checks.get('lint_exit') and persisted.get('lint_report')==checks.get('lint_report'),phase_folder/'CHECKS.json')
        if method=='P2P_STYLE' and (folder/'GROUNDING_RECEIPT.json').exists():
            old=read(folder/'p2p_extract.json');new=read(folder/'GROUNDED_EXTRACTION.json');receipt=read(folder/'GROUNDING_RECEIPT.json')
            for i,(a,b) in enumerate(zip(old.get('components',[]),new.get('components',[]))):
                check('p2p_grounding_conditions_unchanged',all(a.get(k)==b.get(k) for k in set(a)|set(b) if k not in ['subject','resource']),folder/'GROUNDING_RECEIPT.json',{'component':i})
            check('p2p_grounding_status_matches_result',(receipt['accepted'] and receipt.get('conditions_changed') is False) or
                  (not receipt['accepted'] and result['status']=='SCHEMA_GROUNDING_REJECTED'),folder/'GROUNDING_RECEIPT.json')
        final=result.get('final_evaluation',{})
        if not result['execution_eligible']:
            check('ineligible_not_executed_or_counted_as_success',final.get('execution_status')=='NOT_ELIGIBLE_NOT_EXECUTED' and not final.get('requests') and
                  not final.get('branches') and result.get('request_pair_correct') is None,folder/'RESULT.json')
        else:
            final_checks=result['final_checks']
            check('eligible_developer_gate_pass',final_checks['accepted'] is True and final_checks['developer_results']['passed'] is True and
                  final['execution_status']=='ELIGIBLE_POLICY_EXECUTED',folder/'RESULT.json')
            final_freeze=read(folder/'FINAL_POLICY_FREEZE.json')
            check('final_policy_frozen_hash',sha(final_checks['policy_path'])==final_freeze['sha256'],folder/'FINAL_POLICY_FREEZE.json')
        original=[]
        for channel in ['O-L','O-I']:
            for v in read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']:
                original.append((channel,v['envelope'],v['expected_class']))
        branch_source=read(ROOT/'sealed_evaluation/branch_protocol.json')['vectors'][task]
        for label,key,check_key in [('first_diagnostic','first_diagnostic','first_checks'),('final_evaluation','final_evaluation','final_checks')]:
            evaluation=result.get(key,{})
            if not evaluation.get('requests'):continue
            check('pair_source_identity_'+label,[(r['channel'],r['input'],r['expected']) for r in evaluation['requests']]==original,folder/'RESULT.json')
            check('branch_source_identity_'+label,[(r['label'],r['input'],r['expected'],r['kind']) for r in evaluation['branches']]==[(a,b,c,d) for a,b,c,d in branch_source],folder/'RESULT.json')
            policy_path=result[check_key]['policy_path'];policy=read(policy_path) if method=='ECAS_MATCHED' else None
            replay_dir=output/'replay'/task/method/label
            for n,row in enumerate(evaluation['requests']+evaluation['branches']):
                observed=evaluate_ecas(policy,contract,row['input'],admission_mode='semantic') if method=='ECAS_MATCHED' else rego_decision(policy_path,adapt(task,row['input']),replay_dir,str(n))
                check('actual_request_replay_'+label,observed.get('decision')==row['actual'].get('decision') and
                      success(observed)==success(row['actual']) and row['pass']==(success(observed) and observed.get('decision')==row['expected']),folder/'RESULT.json',{'request_index':n})
            check('pair_symbol_computed_not_handfilled_'+label,evaluation['request_pair_correct']==(len(evaluation['requests'])==2 and all(r['pass'] for r in evaluation['requests'])),folder/'RESULT.json')
        compact_rows.append({'task':task,'case':CASE_NAMES[task],'method':method,'method_name':METHOD_NAMES[method],
              'initial_diagnostic_symbol':mark(result['first_diagnostic']),'initial_eligible':bool(result.get('first_checks',{}).get('accepted')),
              'repaired_once':result['repaired_once'],'final_symbol':mark(final),'final_execution_eligible':result['execution_eligible'],
              'status':result['status'],'failure_class':failure_class(result),'calls':len(result['calls']),'call_indices':result['calls'],
              'final_original_pair':final.get('requests',[]),'final_branches':final.get('branches',[]),'source_result':str(folder/'RESULT.json')})
    verify_inputs()
    failed=[x for x in audit if not x['pass']]
    receipt={'status':'PASS' if not failed else 'FAIL','scope_id':CONFIG['scope_id'],'checked_at':now(),'checks':len(audit),'observations':audit,
             'failures':failed,'actual_paid_attempts':len(ledger),'new_model_calls_for_this_build':0,'builder_sha256':sha(__file__),
             'generation_manifest_sha256':sha(ROOT/'EXECUTION_INPUT_MANIFEST.json'),'primary_state_sha256':sha(state_path),
             'qa_scope':'RAW_SCHEMA_INPUT_IDENTITY_CODE_TOOL_POLICY_REQUEST_REPLAY_NOT_GENERAL_SCIENTIFIC_VALIDITY'}
    dump(output/'PRIMARY_RECONCILIATION.json',receipt)
    if failed:raise RuntimeError('Primary reconciliation failed; report/ledger not released')
    method_stats=[]
    for method in CONFIG['methods']:
        subset=[r for r in compact_rows if r['method']==method];paid=[r for r in usage_rows if not r['smoke'] and r['method']==method]
        requests=[x for r in subset for x in r['final_original_pair']]
        legal=[x for x in requests if x['expected']=='allow'];illegal=[x for x in requests if x['expected']=='deny']
        method_stats.append({'method':method,'method_name':METHOD_NAMES[method],'case_count':4,'eligible_cases':sum(r['final_execution_eligible'] for r in subset),
             'pair_all_correct':sum(r['final_symbol']=='●' for r in subset),'legal_allowed':sum(x['actual'].get('decision')=='allow' and success(x['actual']) for x in legal),
             'legal_total_target_cases':4,'illegal_misallowed':sum(x['actual'].get('decision')=='allow' and success(x['actual']) for x in illegal),
             'illegal_executed':len(illegal),'repair_calls':sum(r['stage'] in ['repair','ecas_repair'] for r in paid),'method_model_calls':len(paid),
             'input_tokens':sum(r['prompt_tokens'] for r in paid),'completion_tokens':sum(r['completion_tokens'] for r in paid),
             'latency_seconds':round(sum(r['latency_seconds'] for r in paid if isinstance(r['latency_seconds'],(int,float))),3),'actual_cost':'UNKNOWN' if any(r['actual_cost']=='UNKNOWN' for r in paid) else sum(r['actual_cost'] for r in paid)})
    summary={'scope_id':CONFIG['scope_id'],'classification':CONFIG['classification'],'rows':compact_rows,'methods':method_stats,
             'actual_total_paid_attempts':len(ledger),'smoke_attempts':sum(x['smoke'] for x in ledger),'method_attempts':sum(not x['smoke'] for x in ledger),
             'local_recovered_as_run_failures':sum(bool(x.get('as_run_failure')) for x in ledger),
             'input_tokens':sum(x['prompt_tokens'] for x in usage_rows),'completion_tokens':sum(x['completion_tokens'] for x in usage_rows),
             'actual_cost':'UNKNOWN' if any(x['actual_cost']=='UNKNOWN' for x in usage_rows) else sum(x['actual_cost'] for x in usage_rows),
             'primary_reconciliation_sha256':sha(output/'PRIMARY_RECONCILIATION.json'),'new_model_calls_for_build':0}
    dump(output/'COMPARISON_SUMMARY.json',summary)
    (output/'COMPARISON.csv').write_text(csv_text(compact_rows,['task','method','initial_diagnostic_symbol','initial_eligible','repaired_once','final_symbol','final_execution_eligible','status','failure_class','calls','call_indices','source_result']),encoding='utf-8-sig')
    (output/'CALL_USAGE.csv').write_text(csv_text(usage_rows,list(usage_rows[0])),encoding='utf-8-sig')
    parts=['# 四例共同目标、一次修复机会的同行适配比较','',f'范围：{CONFIG["scope_id"]}。单轮历史暴露诊断，来源仍为Fineract、ERPNext两个项目。','',
       '## 首次生成与修复后','',
       '● 原合法/违规两条请求均判对；◐ 一条判对；○ 两条均判错；— 未获得执行资格或无可执行政策。首次列是候选冻结后的离线诊断，不等于部署资格。','',
       '| 案例 | 方法 | 首次诊断 | 首次开发/准入合格 | 开发修复 | 修复后实际执行 | 最终资格/状态 | 方法调用 |',
       '|---|---|---|---|---|---|---|---|']
    for r in compact_rows:parts.append(f'| {r["case"]} | {r["method_name"]} | {r["initial_diagnostic_symbol"]} | {"是" if r["initial_eligible"] else "否"} | {"1次" if r["repaired_once"] else "0次"} | {r["final_symbol"]} | {r["status"]} | {r["calls"]} |')
    parts+=['','## 实际资源与覆盖','',
       '| 方法 | 合格案例/4 | 原请求对全对/4 | 合法允许/4 | 违规误放/已执行违规 | 修复调用 | 方法调用 | 输入token | completion token | 金额 |',
       '|---|---|---|---|---|---|---|---|---|---|']
    for r in method_stats:parts.append(f'| {r["method_name"]} | {r["eligible_cases"]}/4 | {r["pair_all_correct"]}/4 | {r["legal_allowed"]}/4 | {r["illegal_misallowed"]}/{r["illegal_executed"]} | {r["repair_calls"]} | {r["method_model_calls"]} | {r["input_tokens"]} | {r["completion_tokens"]} | {r["actual_cost"]} |')
    parts+=['',f'累计真实付费尝试{summary["actual_total_paid_attempts"]}，其中小试{summary["smoke_attempts"]}、方法调用{summary["method_attempts"]}。本结果生成与政策复演新增模型调用0。原格式失败及本地外封装恢复保留，不重复计费或计作业务修复。','',
       '## 分支与工程控制','',
       '| 案例 | 方法 | 业务/类型分支符合/已执行 | 工程及保守控制符合/已执行 |',
       '|---|---|---|---|']
    for r in compact_rows:
        business=[x for x in r['final_branches'] if x['kind'] in ['documented_rule','documented_type','focused_rule_only']]
        engineering=[x for x in r['final_branches'] if x['kind'] not in ['documented_rule','documented_type','focused_rule_only']]
        parts.append(f'| {r["case"]} | {r["method_name"]} | {sum(x["pass"] for x in business)}/{len(business)} | {sum(x["pass"] for x in engineering)}/{len(engineering)} |')
    parts+=['','## 解释边界','',
      '- 三方法共同处理相同目标，单次token上限和至多一次开发修复机会相同；P2P自动测试、AutoPAC Judge属于各自流程，方法调用数和总资源并不相同。',
      '- P2P、AutoPAC为文献流程适配实现，不能当作原作原版性能。三种方法均含模型生成，本轮没有真实人工劳动计时，不能给出人工节省比例。',
      '- 未执行不会计作成功拒绝，全部拒绝无法通过包含合法允许的共同开发测试。schema、通信或工具环境阻断不会伪装成科学错误率。',
      '- 原请求对、业务分支与工程/保守控制分列；额外探针为历史事后工程测试，不能汇成总体准确率。',
      '- 这是四个暴露过的任务的一次诊断，不能证明稳定优势或独立系统泛化；真实API转发、trusted真实性/新鲜度、数量计算与交易提交时点仍未验证。',
      '- 证据驱动的独立效果由另一范围的相同候选有/无契约比较提供，不能从本轮方法差异直接归因于证据契约。','',
      '机器汇总：COMPARISON_SUMMARY.json；原件对账：PRIMARY_RECONCILIATION.json；调用明细：CALL_USAGE.csv。']
    (output/'RESULTS_CN.md').write_text('\n'.join(parts)+'\n',encoding='utf-8')
    existing_path=ROOT/'RESULT_TRACEABILITY.csv'
    with existing_path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream);fields=reader.fieldnames;old=list(reader)
    additions=[]
    for r in compact_rows:
        source=Path(r['source_result'])
        additions.append({'result_id':'MATCHED-'+r['task']+'-'+r['method']+'-FINAL','experiment_id':CONFIG['scope_id'],
             'metric_name':'eligible_original_pair_correct','dataset_name':r['task'],'dataset_version':'Fineract1.14.0_or_ERPNext16.0.0',
             'data_split':'retrospective_exposed_single_round','sample_count':'2' if r['final_execution_eligible'] else '0',
             'raw_value':canonical({'eligible':r['final_execution_eligible'],'pair_symbol':r['final_symbol'],'status':r['status']}),
             'reported_value':r['final_symbol'],'unit':'pair_outcome','aggregation':'separate_case_method_not_pooled_accuracy',
             'source_output_path':str(source.relative_to(ROOT.parents[3])).replace('\\','/'),'source_locator':'final_evaluation;execution_eligible;request_pair_correct',
             'script_path':str(Path(__file__).relative_to(ROOT.parents[3])).replace('\\','/'),'command_or_config':'EXECUTION_CONFIG.json;build_results.py;'+str(output.name),
             'seed':'NOT_SET','environment':'WSL Ubuntu Python3.10 OPA Regal isolated lane','git_commit':'NOT_AVAILABLE_HASH_FROZEN',
             'checksum':sha(source),'rounding_rule':'none','status':'PASS','verified_by':'postrun_primary_reconciliation_and_deterministic_request_replay',
             'verified_at':now(),'notes':'PASS denotes trace reconciliation, not broad scientific validity; adapted peers/single exposed round; no new model calls'})
    ids={r['result_id'] for r in old}
    if any(r['result_id'] in ids for r in additions):raise RuntimeError('Scope ledger already contains comparison; do not overwrite or duplicate')
    proposed=old+additions
    (output/'RESULT_TRACEABILITY_PROPOSED.csv').write_text(csv_text(proposed,fields),encoding='utf-8-sig')
    if write_scope:
        (output/'RESULT_TRACEABILITY_AS_BEFORE.csv').write_bytes(existing_path.read_bytes())
        existing_path.write_text(csv_text(proposed,fields),encoding='utf-8-sig')
    dump(output/'BUILD_RECEIPT.json',{'status':'COMPLETED_RECONCILED_REPORT','scope_id':CONFIG['scope_id'],'builder_sha256':sha(__file__),
        'new_model_calls':0,'actual_paid_attempts':len(ledger),'scope_ledger_written':write_scope,'report_path':str(output/'RESULTS_CN.md'),
        'summary_sha256':sha(output/'COMPARISON_SUMMARY.json'),'qa_sha256':sha(output/'PRIMARY_RECONCILIATION.json'),'completed_at':now()})
    print(json.dumps({'status':'COMPLETED_RECONCILED_REPORT','rows':12,'primary_checks':len(audit),'actual_paid_attempts':len(ledger),
                     'new_model_calls':0,'output':str(output),'scope_ledger_written':write_scope}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'results_review_v1');parser.add_argument('--write-scope-ledger',action='store_true');args=parser.parse_args()
    try:build(args.output,args.write_scope_ledger)
    except Exception as error:
        print(json.dumps({'status':'NOT_READY_OR_QA_BLOCKED','error_type':type(error).__name__,'error':str(error).split('\n')[0][:1200]}));raise SystemExit(2)
