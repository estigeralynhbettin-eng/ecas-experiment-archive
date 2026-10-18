"""Prepare a new retrospective scope without credentials or model access."""
import hashlib
import copy
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parents[1] / '20261014_four_case_peer_baselines'
LANE = Path('/root/ecas_matched_generation_20261014')
TASKS = ['FSV-S03', 'FSV-B13', 'FSV-B17', 'FSV-B19']
SCOPE = 'ECAS-MATCHED-EVIDENCE-LABOR-20261014-01'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p, value): Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

objectives = {
 'FSV-S03': {'constraint_object': 'The age field of a family-member creation request', 'constraint_kind': 'The published API type requirement for age', 'scope': 'Only the age type requirement in the supplied OpenAPI. Other fields, identity/authentication, age range and presence are outside this task unless the target source requires them for this type constraint.'},
 'FSV-B13': {'constraint_object': 'Quantity on a Purchase Receipt represented by request.body.qty, supplied quantity limit and authenticated role context', 'constraint_kind': 'Receipt quantity allowance and the documented authorized-role exception', 'scope': 'Implement the supplied Stock Settings quantity policy for this target; upstream supplies trusted derivedMaximumQty and authorizedRole. Do not add unrelated field, item, range or full-document validation.'},
 'FSV-B17': {'constraint_object': 'Customer disabled status relevant to Sales Order creation', 'constraint_kind': 'The documented disabled-customer condition for the target operation', 'scope': 'Use the provided trusted customer state for this target only; do not add unrelated Customer or Sales Order validation.'},
 'FSV-B19': {'constraint_object': 'Supplier on-hold status and hold type relevant to Purchase Order creation', 'constraint_kind': 'The documented supplier hold-type condition for the target operation', 'scope': 'Implement the supplier hold policy for this Purchase Order target only; do not add restrictions for invoices, payments, other endpoints or unrelated fields.'}
}

derivations = []
for task in TASKS:
    path = ROOT / 'generation_inputs' / task / 'packet.json'
    original = read(OLD / 'generation_inputs' / task / 'packet.json')
    packet = json.loads(json.dumps(original))
    packet['TARGET_OBJECTIVE'] = objectives[task]
    dump(path, packet)
    without = json.loads(json.dumps(packet)); without.pop('TARGET_OBJECTIVE')
    assert without == original
    derivations.append({'task': task, 'source_path': str(OLD / 'generation_inputs' / task / 'packet.json'),
                        'source_sha256': sha(OLD / 'generation_inputs' / task / 'packet.json'), 'derived_path': str(path),
                        'derived_sha256': sha(path), 'only_added': 'TARGET_OBJECTIVE', 'source_content_changed': False,
                        'contains_correct_predicate': False, 'contains_final_fixture_or_label': False})

config = read(OLD / 'EXECUTION_CONFIG.json')
config.update(scope_id=SCOPE, authorization='AUTHORIZATION_CN.md', runtime_lane=str(LANE), max_calls=44,
              repair_per_external_case=1, repair_per_method_case=1, max_total_external_repair_calls=12,
              classification='RETROSPECTIVE_MATCHED_OBJECTIVE_ADAPTED_PEERS_SINGLE_ROUND_NOT_BLIND',
              methods=['P2P_STYLE','AUTOPAC_STYLE','ECAS_MATCHED'], max_method_case_calls={'P2P_STYLE':5,'AUTOPAC_STYLE':3,'ECAS_MATCHED':2})
config['contracts'] = {t: str(ROOT / 'execution_inputs' / t / 'contract.json') for t in TASKS}
config['prompt_estimator']='UTF8_BYTES_DIV_3_PLUS_128_CALIBRATED_ESTIMATE_NOT_HARD_BOUND'
dump(ROOT / 'EXECUTION_CONFIG.json', config)
templates = read(OLD / 'PROMPT_TEMPLATES.json')
# Derive the factorization directly from the original full schema. The prior
# historical prompt reference omitted 25 bounds/uniqueness/pattern constraints.
full_schema=read(ROOT/'execution_inputs/ecas_output_schema.json')
original_variants=full_schema['$defs']['rule']['oneOf']
common=copy.deepcopy(original_variants[0])
for field in ['op','primitive_id','params']:common['properties'].pop(field)
factored={k:copy.deepcopy(v) for k,v in full_schema.items() if k!='$defs'}
factored['$defs']={k:copy.deepcopy(v) for k,v in full_schema['$defs'].items() if k!='rule'}
factored['rule_common']=common
factored['rule_variant_columns']=['op','primitive_id','params_schema']
factored['rule_variants']=[[v['properties']['op']['const'],v['properties']['primitive_id']['const'],copy.deepcopy(v['properties']['params'])] for v in original_variants]
factored['representation_notice']='Lossless factorization: combine rule_common with one row, using op/primitive_id as const properties and params_schema as params. Rebuilt rule.oneOf is byte-semantically equal to the original full schema; refs resolve in the preserved complete defs.'
rebuilt=copy.deepcopy(full_schema)
rebuilt['$defs']['rule']['oneOf']=[]
for op,primitive,params in factored['rule_variants']:
    variant=copy.deepcopy(common)
    variant['properties'].update(op={'const':op},primitive_id={'const':primitive},params=copy.deepcopy(params))
    rebuilt['$defs']['rule']['oneOf'].append(variant)
assert rebuilt==full_schema
templates['ecas_prompt_schema']=factored
dump(ROOT/'execution_inputs/ecas_prompt_schema.json',factored)
dump(ROOT/'SCHEMA_FACTORIZATION_QA.json',{'status':'PASS','classification':'LOSSLESS_DECOMPOSITION_FROM_FULL_SCHEMA',
     'original_schema_sha256':sha(ROOT/'execution_inputs/ecas_output_schema.json'),'factored_schema_sha256':sha(ROOT/'execution_inputs/ecas_prompt_schema.json'),
     'reconstructed_full_schema_equal':rebuilt==full_schema,'all_definitions_preserved_except_factored_rule':True,'variant_count':len(original_variants),
     'historical_prompt_schema_omitted_constraints':25,'model_calls':0})
templates['common'] += '\nEvery method must implement only packet.TARGET_OBJECTIVE. Do not implement unrelated endpoint requirements or choose another grounded rule. Derive the predicate from the visible source; the objective fixes task scope, not the answer. First-generation prompts never contain developer/final request labels. Deterministic OPA fmt is applied before checks and is accepted only with AST equality excluding locations.\n'
templates['stages']['p2p_extract'] += ' Return only declared literal organization IDs. An exact object equal to the declared neutral subject/resource envelope can be deterministically converted to its id before generation; no other object mapping, condition edit or alias is allowed.'
templates['stages']['ecas_generate'] += ' Choose exactly one supported rule that implements TARGET_OBJECTIVE; otherwise abstain. The supplied operation semantics define constraint polarity and strict type behavior.'
templates['stages']['ecas_repair'] = 'Repair the prior ECAS Model IR candidate using only the same visible sources, complete schema/operator semantics and source/compile/admission/common developer feedback. Return {candidate:object} using the identical EC-FIELD-MODEL-IR-V3 schema. No final fixture feedback is given. Exactly one target rule if proposing; otherwise valid abstain. Do not change target, runtime paths or invent evidence.'
dump(ROOT / 'PROMPT_TEMPLATES.json', templates)
dump(ROOT / 'INPUT_DERIVATIONS.json', derivations)
scope = {'kind':'new-experiment-block','status':'FROZEN','protocol_path':'FROZEN_PROTOCOL_CN.md',
         'scope_id': SCOPE, 'project_id': 'EC-CSI', 'experiment_id': 'matched-evidence-labor', 'tasks': TASKS,
         'classification': config['classification'], 'source_scope_id': read(OLD / 'EXECUTION_CONFIG.json')['scope_id'],
         'runtime_lane': str(LANE), 'historical_exposure': 'All four cases have previous generation and evaluation exposure. This is a diagnostic rerun, not holdout, blind testing or a stability estimate.',
         'paid_calls_authorized_total_cap': 44, 'automatic_api_retries': 0, 'new_systems': 0, 'new_cases': 0}

auth = '''# 本轮授权与调用边界\n\n当前用户明确要求“按照这个思路来做吧”，即统一任务、首次与修复后分列、失败退出，以及比较证据驱动；用户随后明确取消人工计时研究，只比较生成方式。根 Agent 已向用户声明 GLM5.2、thinking enabled、reasoning high，每次输入/输出上限16384，本轮总上限44。\n\n本子范围只占用该44次累计预算，不刷新预算：小试至多4次，四例每例P2P至多5、AutoPAC至多3、ECAS至多2（含各自至多一次开发修复），实际按需要调用。不得自动 API 重试、换模型、换样本或另开预算。付费派发仍须根 Agent 完成本轮 scope、T0 与 token 门禁并明确派发；本文件不授权子 Agent 独立调用。成本不可观测则UNKNOWN。\n'''
(ROOT / 'AUTHORIZATION_CN.md').write_text(auth, encoding='utf-8')
contract = '''# 任务契约\n\n目标：定位先前四例 ECAS 与同行适配版比较的任务和修复混杂；不以获得 ECAS 正结果为验收条件。只做 S03/B13/B17/B19 单轮回顾性诊断，资料来自原 Fineract/ERPNext 两项目。\n\n范围：新目录及独立WSL lane；保留原协议、raw与旧结果，不写正文、科学账本或投稿状态。生成方式核验与证据契约消融由独立支持范围提供，本入口只做模型生成比较。\n\n交付：统一来源 packet+TARGET_OBJECTIVE、完整15原语说明、冻结脚本与工具、离线T0、token统计、小试记录、调用账本、首次候选冻结、至多一次修复及执行资格、最终原请求对和额外探针分列。\n\n完成条件：12方法案例均有终态或明确协议阻断；全部实际调用与raw/usage/身份对应；首次/修复后不可混列；开发失败不获执行资格；未执行不计作拒绝成功；原请求与分支/工程探针分别统计；无人工工作量节省比例。\n\n停止：raw、模型身份、sentinel、token、schema、输入哈希、格式AST或通信门禁失败立即停批，费用尝试留账。无自动付费重试。最多44累计调用（包括4小试）；每方法每例最多1开发修复。首次使用暴露过的请求与有限布尔任务，不称盲测或稳定性。\n'''
(ROOT / 'TASK_CONTRACT.md').write_text(contract, encoding='utf-8')
protocol = '''# 统一任务与修复流程协议\n\n## 输入与目标\n三方法使用同一 packet、组织schema、中立ABI与TARGET_OBJECTIVE；公开来源不删选成功证据，保留上一轮可追溯的统一压缩变换。TARGET_OBJECTIVE只指定约束对象与范围，不提供最终规则谓词或测试标签。ECAS额外获取原完整输出schema的无信息损失分解表示及全部15操作语义。P2P可对严格类型任务报告范围外。\n\n## 方法和首次输出\nP2P：detect→extract→Rego→内部developer tests；AutoPAC：Rego→内部Judge；ECAS：Model IR→确定性编译→证据契约准入。所有首次输出立即冻结。P2P抽取只准精确声明的中立subject/resource对象→id转换，不改条件；保留原抽取与转换凭证。所有Rego保留原文本、OPA fmt派生文本，AST忽略location必须相同；P2P继续完整Regal（仅关闭目录/包名规则），不能用fmt跳过lint。\n\n## 开发与修复\n各方法使用同一共同开发请求，P2P自动tests和AutoPAC Judge是其内部流程。首次失败至多一次模型修复，只反馈公开来源、编译/lint、准入、共同developer结果和本方法自身tests/Judge，不给原最终请求标签。ECAS修复仍返回原Model IR schema。最终编译/准入或共同开发不通过则REJECTED/ABSTAIN，无执行资格，不将all-deny算识别成功。AutoPAC修复后不额外Judge，保留其初次Judge以及修复后工具/开发结果。\n\n## 冻结与评价\n所有方法候选/修复终态冻结后才由独立评价阶段读取sealed原合法/违规对和原24项branch probes。first-candidate诊断可在dev失败时执行已编译/准入的政策，但显式标为非合格诊断，不能算实际执行资格；修复后主结果仅对合格政策执行。未执行为—。首次、修复后、原pair、业务branch与工程控制分列；合法允许率、违规误放、准入拒绝、弃权、调用数/token/latency/UNKNOWN成本均保持不同意义。\n\n## 资源与解释\nGLM5.2 enabled/high，每次input和completion16384，maxcalls44=4smoke+4×(P2P5+AutoPAC3+ECAS2)。这些是相同单次上限和相同一次修复机会，各方法内部步骤与总调用数不同；不称监督或总预算完全相同，不填充无用调用。无自动API重试、temperature provider默认、seed未设置。单轮历史暴露诊断，不称稳定或新系统泛化。证据契约的独立收益由另一离线消融范围验证，不能从本轮方法差异直接推出因果结论。\n'''
(ROOT / 'USER_PROTOCOL_CN.md').write_text(protocol+'\n输入token预估依据旧38次GLM已核对raw/usage的校准，用ceil(UTF8字节/3)+128；同时保留旧bytes/2诊断列。估算不是精确token或硬上界；本轮小试及每次正式调用后必须核提供方真实input/completion≤16384，超界立即停批。公共packet在渲染提示时对所有方法统一移除与common文字完全重复的neutral envelope描述和notice，原packet、路径/类型/authority和来源正文保持冻结。\n', encoding='utf-8')
(ROOT / 'FROZEN_PROTOCOL_CN.md').write_text(protocol, encoding='utf-8')
scope['protocol_sha256']=sha(ROOT/'FROZEN_PROTOCOL_CN.md')
dump(ROOT/'EXPERIMENT_SCOPE.json',scope)

source_files = []
for sub in ('generation_inputs', 'execution_inputs', 'sealed_evaluation', 'source_snapshots'):
    for path in sorted((ROOT / sub).rglob('*')):
        if path.is_file():
            source = OLD / path.relative_to(ROOT)
            source_files.append({'original_path': str(source), 'original_sha256': sha(source), 'new_path': str(path), 'new_sha256': sha(path), 'equal': sha(source) == sha(path)})
runtime = []
old_lane = Path('/root/ecas_four_case_peer_20261014')
for sub in ('runtime','tools'):
    for path in sorted((LANE/sub).rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            source=old_lane/path.relative_to(LANE)
            assert sha(source) == sha(path)
            runtime.append({'original_path':str(source), 'original_sha256':sha(source), 'new_path':str(path), 'new_sha256':sha(path), 'equal':True})
            path.chmod(0o555 if sub=='tools' else 0o444)
dump(ROOT / 'SOURCE_COPY_RECEIPT.json', {'inputs':source_files,'runtime_tools':runtime,'old_runtime_written':False,'new_lane':str(LANE)})
calibration=[]
for item in read(OLD/'CALL_LEDGER.json'):
    if item.get('status')!='COMPLETED':continue
    prompt=Path(item['prompt_path']);raw=Path(item['raw_response_path'])
    if sha(prompt)!=item['prompt_sha256'] or sha(raw)!=item['raw_response_sha256']:raise RuntimeError('Historical calibration evidence hash mismatch')
    if prompt.stat().st_size!=item['prompt_bytes']:raise RuntimeError('Historical calibration prompt bytes mismatch')
    observed=read(raw)
    if observed.get('model')!='glm-5.2' or observed['usage']['prompt_tokens']!=item['usage']['prompt_tokens']:raise RuntimeError('Historical calibration provider identity/usage mismatch')
    calibration.append({'index':item['index'],'task':item['task'],'stage':item['stage'],'prompt_path':str(prompt),'prompt_sha256':sha(prompt),
                        'prompt_bytes':prompt.stat().st_size,'raw_response_path':str(raw),'raw_response_sha256':sha(raw),
                        'provider_input_tokens':observed['usage']['prompt_tokens'],'returned_model':observed['model'],
                        'thinking':'enabled','reasoning_effort':'high','settings_source_config':str(OLD/'EXECUTION_CONFIG.json'),
                        'input_tokens_per_utf8_byte':observed['usage']['prompt_tokens']/prompt.stat().st_size})
ratios=[x['input_tokens_per_utf8_byte'] for x in calibration]
assert len(calibration)==38
dump(ROOT/'TOKEN_ESTIMATOR_CALIBRATION.json',{'classification':'HISTORICAL_OBSERVED_CALIBRATION_NOT_NEW_SMOKE_OR_HARD_BOUND',
     'source_ledger_sha256':sha(OLD/'CALL_LEDGER.json'),'source_config_sha256':sha(OLD/'EXECUTION_CONFIG.json'),'rows':calibration,
     'count':len(calibration),'min_ratio':min(ratios),'max_ratio':max(ratios),'mean_ratio':sum(ratios)/len(ratios),
     'new_estimator':'ceil(utf8_bytes/3)+128','headroom_relative_to_highest_ratio':(1/3)/max(ratios)-1,
     'legacy_diagnostic_estimator':'ceil(utf8_bytes/2)+128','observed_provider_token_cap_mandatory':16384})
dump(ROOT / 'PREPARED.json', {'status':'PREPARED_OFFLINE_ONLY','scope_id':SCOPE,'tasks':TASKS,'raw_model_calls':0,'api_key_loaded':False,
                             'gate':'T0_AND_TOKEN_GATE_REQUIRED','max_calls':44,'manifest_not_yet_frozen':True})
print(json.dumps({'status':'PREPARED_OFFLINE_ONLY','source_files':len(source_files),'runtime_files':len(runtime),'max_calls':44}))
