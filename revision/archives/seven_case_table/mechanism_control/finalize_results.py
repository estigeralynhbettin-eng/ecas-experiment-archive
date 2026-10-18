"""Reconcile frozen offline counterfactuals and write a source-linked report."""
import csv
from pathlib import Path
from mechanism_probe import ROOT,PROJECT,LANE,SCOPE,read,dump,sha,verify,csvtext,now

verify()
result=read(ROOT/'RESULTS.json');rows=result['rows'];audit=[]
def check(name,ok):audit.append({'check':name,'pass':bool(ok)})
status=read(LANE/'managed_runs/missing-state-mechanism-v1/status.json')
check('actual_managed_run_succeeded',status['state']=='SUCCEEDED' and status['exit_code']==0)
check('144_related_observations_not_independent_cases',len(rows)==144 and result['new_model_calls']==0 and result['new_cases']==0)
keyed={(r['task'],r['arm'],r['probe_id']):r for r in rows}
check('unique_task_arm_probe',len(keyed)==144)
check('all_actual_decisions_boolean_outcomes',all(r['decision'] in ('allow','deny') for r in rows))
for item in read(ROOT/'INPUT_MANIFEST.json'):check('frozen_'+item['path'],sha(item['path'])==item['sha256'])
for item in read(ROOT/'SOURCE_MANIFEST.json'):check('source_'+item['source'],sha(item['source'])==sha(item['snapshot'])==item['sha256'])
for task in ['FSV-B17','FSV-B19']:
    for variant in ['original','missing_skip']:
        for r in rows:
            if r['task']==task and r['arm']=='ECAS_'+variant+'_full':
                check(task+variant+r['probe_id']+'_full_shape_equal',r['decision']==keyed[(task,'ECAS_'+variant+'_shape',r['probe_id'])]['decision'])
    admissions=[a for a in result['admissions'] if a['task']==task and a['mode']=='full'] if any('mode'in a for a in result['admissions']) else [a for a in result['admissions'] if a['task']==task and a['arm'].endswith('_full')]
    check(task+'_deny_and_skip_both_admitted',len(admissions)==2 and all(a['status']=='ADMITTED' for a in admissions))
    check(task+'_original_missing_deny',keyed[(task,'ECAS_original_full','missing-trusted')]['decision']=='deny')
    check(task+'_skip_missing_allow',keyed[(task,'ECAS_missing_skip_full','missing-trusted')]['decision']=='allow')
    original=read(LANE/'results'/task/'original.candidate.json');skip=read(LANE/'results'/task/'missing_skip.candidate.json')
    skip['rules'][0]['params']['on_missing']='deny'
    check(task+'_counterfactual_only_changes_missing_parameter',original==skip==read(ROOT/'inputs'/task/'candidate.json'))
    for method in ['P2P_STYLE','AUTOPAC_STYLE']:
        check(task+method+'_original_missing_allows',keyed[(task,method+'_original','missing-trusted')]['decision']=='allow')
        check(task+method+'_manual_guard_missing_denies',keyed[(task,method+'_manual_guard','missing-trusted')]['decision']=='deny')
for r in rows:
    if r['kind']=='original_pair':check(r['task']+r['arm']+r['probe_id']+'_original_pair_coverage',r['agrees_with_historical_label'] is True)
    if r['kind']=='partial_missing_observation_no_gold':check(r['arm']+r['probe_id']+'_no_gold',r['historical_expected'] is None and r['agrees_with_historical_label'] is None)
check('all_partial_payments_original_ecas_allow',all(r['decision']=='allow' for r in rows if r['probe_id']=='partial-payments-only' and r['method']=='ECAS'))
if any(not x['pass'] for x in audit):
    dump(ROOT/'FINAL_RECONCILIATION.json',{'status':'FAIL','checks':audit});raise RuntimeError('Reconciliation failure')
dump(ROOT/'FINAL_RECONCILIATION.json',{'status':'PASS','checks':audit,'new_model_calls':0,'result_sha256':sha(ROOT/'RESULTS.json'),
      'result_rows':144,'independent_cases_added':0,'scope_id':SCOPE,'completed_at':now()})

text='''# 缺可信状态行为的本地机制对照

## 结论

本地对照已完成，无新增模型调用。当前缺状态/未知类型差异有实际意义，但本轮不能把它认定为证据准入带来的独有保证。

1. ECAS只改变on_missing=skip，仍通过原Inventory准入，B17/B19的全缺trusted输入均从deny变为allow。
2. 同一候选full与shape-only的运行观察逐项相同；因此本组请求上的差异来自候选参数和规则逻辑，而非准入开关。
3. 给两同行的原Rego叠加人工编写的最小typed状态guard后，原先四类allow观察均可变为deny，并保留两例各自原合法/违规请求对。不能把这种手工控制回填成同行原生成结果。

## 核心对照

| 配置 | B17 trusted={} | B19 trusted={} | B19冻结且类型为空/未知 | 两例原请求对 |
|---|---|---|---|---|
| ECAS原候选/full | deny | deny | deny | 各2/2匹配 |
| ECAS原候选/shape-only | deny | deny | deny | 各2/2匹配 |
| ECAS只改on_missing=skip/full | allow | allow | deny | 各2/2匹配 |
| ECAS只改on_missing=skip/shape-only | allow | allow | deny | 各2/2匹配 |
| P2P适配版原候选 | allow | allow | allow | 各2/2匹配 |
| P2P原候选+人工guard | deny | deny | deny | 各2/2匹配 |
| AutoPAC适配版原候选 | allow | allow | allow | 各2/2匹配 |
| AutoPAC原候选+人工guard | deny | deny | deny | 各2/2匹配 |

B19的空/未知类型拒绝来自正向允许条件：supplierOnHold=false或holdType=Payments。只改缺值参数不改变这两种有值但未命中条件的结果。

## 部分缺值不能混称全缺

| B19输入trusted | ECAS原/full及shape | 两同行原政策 | 两同行+人工guard |
|---|---|---|---|
| 只有supplierOnHold=false | allow | allow | allow |
| 只有holdType=Payments | allow | allow | deny |

这两项只有观察值，没有预设业务正确标签。一个允许分支已经能成立时，另一字段缺失未必构成业务违规；也不能把人工guard更保守的结果自动算作更正确。此前“缺少可信供应商状态时拒绝”须精确限定为原trusted={}探针，不能泛化为任意部分信息缺失都拒绝。

## 两种缺失发生在不同阶段

- Inventory证据记录、版本或绑定事实失效：规则准入阶段判断是否可部署，已有配对消融证明被测硬检查会拒绝候选。
- 请求trusted运行值缺失：执行阶段由候选运算语义和on_missing参数决定；当前准入没有对本组规则强制on_missing=deny。

源语义Judge是第三种检查：核读目标和允许/禁止方向，不负责证明来源或运行状态真实。先前Judge指出三个主语义问题的结果继续有效，但不能据此自动补全上述硬运行保证。

## 对继续研究的影响

应该继续研究证据约束下的安全执行。下一步需要把所需可信输入、条件依赖、类型和失效处理明确成为可核验契约，检验能否在模型漏写安全默认值时仍保证一致执行；并把已加入安全guard的同行作为强对照。当前的缺值拒绝现象本身不能单独充当独特性证据。

本轮18个相关输入、八配置臂、144行是机制干预观察，不是144个独立案例。四类allow→deny控制涉及两个旧任务和两个同行配置；原合法覆盖只对已测试请求负责。没有新增生成任务、独立系统、真实攻击或生产状态认证验证。

## 复现与证据

运行missing-state-mechanism-v1实际SUCCEEDED；INPUT_MANIFEST/SOURCE_MANIFEST绑定不变引擎、OPA、原候选和快照。RESULTS.json、OBSERVATIONS.csv保留全部行，FINAL_RECONCILIATION.json保留逐项对账。人工guard独立放在guards/，两同行原Rego未修改。旧原件、论文和根科学账本不改。
'''
(ROOT/'RESULTS_CN.md').write_text(text,encoding='utf-8')
ledger=ROOT/'RESULT_TRACEABILITY.csv'
with ledger.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;old=list(reader)
if len(old)!=1:raise RuntimeError('Expected T0-only scope ledger before local acceptance')
add=[]
for task in ['FSV-B17','FSV-B19']:
    for arm in sorted({r['arm'] for r in rows if r['task']==task}):
        subset=[r for r in rows if r['task']==task and r['arm']==arm]
        add.append({'result_id':task+'-'+arm,'experiment_id':SCOPE,'metric_name':'counterfactual_request_observations','dataset_name':task,
           'dataset_version':'frozen_exposed_prior_inputs_plus2_no_gold_partial','data_split':'posthoc_mechanism_control','sample_count':len(subset),
           'raw_value':len(subset),'reported_value':len(subset),'unit':'related_observations','aggregation':'not_independent_sample_or_accuracy',
           'source_output_path':str((ROOT/'RESULTS.json').relative_to(PROJECT)),'source_locator':'rows.task='+task+';arm='+arm,
           'script_path':str((ROOT/'mechanism_probe.py').relative_to(PROJECT)),'command_or_config':'PROTOCOL_CN.md;RUN_REQUEST.json','seed':'NOT_APPLICABLE',
           'environment':'WSL Python OPA isolated lane','git_commit':'NOT_AVAILABLE_HASH_FROZEN','checksum':sha(ROOT/'RESULTS.json'),
           'rounding_rule':'none','status':'PASS','verified_by':'actual_execution_and_source_reconciliation','verified_at':now(),
           'notes':'No new model calls; manual guard and counterfactual variants are not original model generation results'})
(ROOT/'RESULT_TRACEABILITY_BEFORE_RESULTS.csv').write_bytes(ledger.read_bytes())
ledger.write_text(csvtext(old+add,fields),encoding='utf-8-sig')
print({'status':'COMPLETED_RECONCILED','checks':len(audit),'observations':len(rows),'new_model_calls':0})
