"""Derive source/rule-chain tables and local result records without executing policies."""
from pathlib import Path
import csv
import hashlib
import io
import json
from collections import defaultdict

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[2]
EX = PROJECT / 'working/exploration'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path': str(p), 'sha256': sha(p)}
def dump(name, data): (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def table_csv(rows, fields):
    s = io.StringIO(newline=''); w = csv.DictWriter(s, fieldnames=fields, extrasaction='ignore')
    w.writeheader(); w.writerows(rows); return s.getvalue()
def link(file, label): return f'[{label}]({file.as_posix()})'


META = {
    'FSV-B06': ['B06 撤销条件', '文档中的最新Re-Age交易约束', 'bounded_guard_dnf：reAgeIsLatestTransaction=true',
                '历史抽取/布尔判定演示；专用undoReAge与旧通用undo目标不一致，映射未闭合'],
    'FSV-S02': ['S02 字段白名单', 'OpenAPI四字段清单；未声明禁止额外字段', 'allowed_fields：四字段闭集',
                '历史网关策略约定；静态HTTP链先DTO绑定、关闭未知键报错，拒绝未知键未证成'],
    'FSV-S04': ['S04 邮箱格式', 'Lead.email_id的options=Email', 'named_validator：email_basic_v1',
                '可展示Email属性到注册基本格式原语的映射；未证明与后端全部邮箱规范等价'],
    'FSV-S03': ['S03 整数类型', 'OpenAPI age为integer，未要求必填', 'strict_type(integer)，on_missing=skip',
                '支持指定类型子约束的来源到IR及离线执行链'],
    'FSV-B13': ['B13 上限与授权例外', '数量容差上限及授权角色例外', 'bounded_guard_dnf：qty≤max，或超限且authorizedRole',
                '支持指定数量子约束；上限计算、角色认证与真实状态获取由公共ABI提供，未单独验证'],
    'FSV-B17': ['B17 禁用客户', 'Disabled客户不得创建Sales Order', 'bounded_guard_dnf：customerDisabled=false',
                '支持已知布尔状态下的方向映射；状态认证及生产转发未验证'],
    'FSV-B19': ['B19 冻结类型', 'Supplier冻结类型控制Purchase Order；完整源码还含默认值与解冻日期',
                'bounded_guard_dnf：supplierOnHold=false OR holdType=Payments',
                '支持冻结类型子规则；原ABI未声明规范化和有效期语义，完整冻结生命周期未闭合'],
}


def paths_in(value):
    found = set()
    if isinstance(value, dict):
        for k, v in value.items():
            if k in ('path', 'left_path', 'right_path') and isinstance(v, str) and v.startswith('/'):
                found.add(v)
            found.update(paths_in(v))
    elif isinstance(value, list):
        for v in value: found.update(paths_in(v))
    return found


def main():
    protected = [PROJECT / 'RESULT_TRACEABILITY.csv', PROJECT / 'CLAIM_EVIDENCE_MATRIX.csv',
                 EX / '20261015_semantic_comparison/EXPERIMENT_SUMMARY_CN_R3.md',
                 EX / '20261015_seven_case_mechanism/EXPERIMENT_SUMMARY_CN_R2.md']
    before = {str(p): sha(p) for p in protected}
    with (EX / '20261015_seven_case_mechanism/SEVEN_CASE_COMPARISON.csv').open(encoding='utf-8-sig', newline='') as f:
        prior = [r for r in csv.DictReader(f) if r['method'] == 'ECAS_MATCHED']
    assert len(prior) == 7
    chains, csv_rows, source_files = [], [], {}
    def register(p): source_files[str(p)] = ref(p); return ref(p)
    for p in protected: register(p)
    for old in prior:
        case = old['task']; meta = META[case]
        base = EX / ('20261014_external_baseline_pilot' if old['batch'] == 'A' else '20261014_matched_evidence_labor/matched_generation')
        packet_path = base / 'generation_inputs' / case / 'packet.json'
        contract_path = base / 'execution_inputs' / case / 'contract.json'
        policy_path = Path(old['final_policy_source'])
        candidate_path = policy_path.parent / ('candidate.json' if old['batch'] == 'A' else '../first_candidate.json')
        candidate_path = candidate_path.resolve()
        result_path = Path(old['result_source'])
        packet, contract, candidate, policy, result = map(read, (packet_path, contract_path, candidate_path, policy_path, result_path))
        evidence = {r['evidence_id']: r for r in contract['evidence']}
        visible = {r['evidence_id']: r for r in packet['visible_sources']}
        refs = set(candidate['evidence_refs'])
        for rule in candidate['rules']: refs.update(rule['evidence_refs'])
        assert refs <= visible.keys() and refs <= evidence.keys()
        binding_rows = []
        for i, rule in enumerate(candidate['rules']):
            relevant = [evidence[x] for x in rule['evidence_refs']]
            bound = set(p for e in relevant for p in e.get('bound_paths', []))
            paths = paths_in(rule['params'])
            assert paths <= bound, (case, paths - bound)
            for e in relevant:
                assert e['relation'] == 'supports' and e['visibility'] == 'visible'
                assert candidate['target']['operation'] in e['operations']
                assert candidate['target']['version'] in e['versions']
                assert rule['primitive_id'] in e['supports_primitives']
            binding_rows.append({'rule_pointer': f'/rules/{i}', 'rule': rule, 'registered_evidence': relevant,
                                 'referenced_runtime_paths': sorted(paths), 'registered_bound_paths': sorted(bound),
                                 'interpretation': 'Inventory declaration consistency only; does not prove source meaning or runtime provenance'})
        admission = result.get('admission') if old['batch'] == 'A' else result['first_checks']['admission_status']
        assert admission == 'ADMITTED'
        row = {'case': case, 'project': old['project_name'], 'batch': old['batch'], 'target': candidate['target'],
               'source_condition_cn': meta[1], 'ir_condition_cn': meta[2], 'scope_status_cn': meta[3],
               'visible_sources': [visible[r] for r in sorted(refs)], 'binding_rows': binding_rows,
               'archive_admission': admission, 'archived_legal_decision': old['original_legal_decision'],
               'archived_violation_decision': old['original_violation_decision'],
               'evidence_files': [register(p) for p in (packet_path, contract_path, candidate_path, policy_path, result_path)],
               'raw_to_candidate_semantic_audit': register(EX / '20261015_semantic_comparison' / ('OLD_THREE_SEMANTIC_AUDIT.json' if old['batch'] == 'A' else 'NEW_FOUR_SEMANTIC_AUDIT.json'))}
        chains.append(row)
        csv_rows.append({'case': case, 'project_name': old['project_name'], 'batch': old['batch'],
                         'source_condition_cn': meta[1], 'ir_condition_cn': meta[2], 'evidence_ids': ';'.join(sorted(refs)),
                         'registered_runtime_paths': ';'.join(sorted(set(p for r in binding_rows for p in r['referenced_runtime_paths']))),
                         'archive_admission': admission, 'archived_legal_decision': old['original_legal_decision'],
                         'archived_violation_decision': old['original_violation_decision'], 'scope_status_cn': meta[3],
                         'candidate_path': str(candidate_path), 'candidate_sha256': sha(candidate_path),
                         'contract_path': str(contract_path), 'contract_sha256': sha(contract_path)})
    dump('SEVEN_CASE_CHAIN.json', {'status': 'SOURCE_RULE_BINDING_ARCHIVE_CHAIN_AUDIT', 'rows': chains,
         'new_model_calls': 0, 'note': 'Historical admission and request decisions; structural reconciliation is not a new compiler or policy run.'})
    (OUT / 'SEVEN_CASE_CHAIN.csv').write_text(table_csv(csv_rows, list(csv_rows[0])), encoding='utf-8-sig', newline='')
    table = '| 案例 | 所属项目 | 来源到IR的映射 | 当前证据定位 |\n|---|---|---|---|\n'
    for row in chains:
        table += '| ' + ' | '.join([META[row['case']][0], row['project'], row['ir_condition_cn'], row['scope_status_cn']]) + ' |\n'
    (OUT / 'SEVEN_CASE_CHAIN_CN.md').write_text('# 七案例：来源→受限IR→证据准入→离线执行\n\n'
         '本表逐案绑定来源、候选、Inventory、注册路径和归档请求结果；全部曾准入且归档原请求对为allow/deny。这是既有输出链核对，不能据此宣称全部来源语义或生产行为正确。\n\n'
         + table + '\nB06、S02保留历史演示身份，不纳入来源/API语义充分闭合的主证据；B19保留类型子规则身份。所有案例仍假定公共ABI提供真实且适当的上下文，本轮没有证明认证、新鲜度、生产HTTP转发或全业务规则覆盖。\n\n'
         + link(OUT / 'SEVEN_CASE_CHAIN.json', '逐字段证据链JSON') + '；' + link(OUT / 'SEVEN_CASE_CHAIN.csv', '链条CSV') + '\n', encoding='utf-8')

    results = read(OUT / 'RESULTS.json')
    assert len(results['source_rows']) == 32 and len(results['rows']) == 288
    grouped = defaultdict(list)
    for r in results['rows']: grouped[(r['arm'], r['method'])].append(r)
    summary_rows = []
    for (arm, method), rows in sorted(grouped.items()):
        summary_rows.append({'arm': arm, 'method': method, 'related_states': len(rows),
            'source_check_not_blocked_but_policy_deny': sum(r['source_decision'] == 'allow' and r['decision'] == 'deny' for r in rows),
            'source_check_blocked_but_policy_allow': sum(r['source_decision'] == 'deny' and r['decision'] == 'allow' for r in rows),
            'disagreement_count': sum(not r['agrees'] for r in rows),
            'disagreement_state_ids': [r['state_id'] for r in rows if not r['agrees']]})
    dump('PROBE_SUMMARY.json', {'rows': summary_rows, 'source_scope': 'Only supplier hold check; allow means this check did not block, not full Purchase Order acceptance.',
                               'denominator_scope': '32 related manually constructed states, not independent cases or model accuracy.'})
    (OUT / 'PROBE_SUMMARY.csv').write_text(table_csv(summary_rows, list(summary_rows[0])), encoding='utf-8-sig', newline='')
    for name in ('SOURCE_GAP_CLOSURE.json', 'B19_SOURCE_PATH.json', 'RESULTS.json', 'T0_RECEIPT.json', 'SOURCE_MANIFEST.json',
                 'INPUT_MANIFEST.json', 'RUN_REQUEST.json', 'PROTOCOL_CN.md', 'TASK_CONTRACT_CN.md'):
        register(OUT / name)
    dump('CHAIN_SOURCE_MANIFEST.json', {'source_files': list(source_files.values()), 'protected_files_before': before})

    contract_proposal = {
        'status': 'DESIGN_PROPOSAL_NOT_IMPLEMENTED_IN_CURRENT_ENGINE',
        'purpose': 'Bind runtime-path business meaning and lifecycle assumptions to source-supported policy scope.',
        'existing_B19_ABI': {'supplierOnHold': 'boolean, server_state; raw/effective definition unspecified', 'holdType': 'string; normalization unspecified'},
        'required_profile_fields': ['target_operation_and_version', 'field_semantic_definition', 'raw_or_effective_state',
                                    'snapshot_lifecycle_point', 'normalization_rule_source', 'dependency_fields',
                                    'time_reference_and_timezone', 'adapter_implementation_id_and_hash',
                                    'qualification_vectors_and_result_refs', 'state_provenance_and_freshness_policy'],
        'B19_alternatives': [
            {'id': 'RAW_WITH_EXPIRY', 'meaning': 'Read actual on_hold, normalized hold_type and release_date; rule explicitly evaluates expiry using a bound clock.'},
            {'id': 'EFFECTIVE_ACTIVE_HOLD', 'meaning': 'Adapter provides derived active hold after before_save normalization and expiry; derivation implementation/source/time are registered.'}],
        'proposed_rejection_conditions': ['Full hold-lifecycle claim but raw flag with no expiry/date mapping',
            'Policy and adapter profiles disagree about normalized versus unsaved state',
            'Required qualification/provenance/version binding unavailable'],
        'limitations': 'Metadata alone cannot prove actual adapter semantics or input authenticity. The selected implementation must be verified and its runtime provenance observed; current engine does not enforce this proposal.'}
    dump('RUNTIME_SEMANTIC_CONTRACT_PROPOSAL.json', contract_proposal)
    proposal_text = '''# 运行时字段语义契约：待实现方案

本方案由本轮来源核查和隔离实验提出，**不是当前ECAS已实现的保证**。

当前Inventory能检查“规则引用了注册路径”。B19说明同一个boolean路径还可能分别代表数据库原on_hold或已考虑解冻日期的有效冻结状态；路径、类型和来源ID全部匹配，也不能区分这两种业务含义。

建议为适配器登记：目标操作/版本、字段的业务定义、原始或派生状态、取得状态的生命周期位置、规范化规则来源、依赖字段、时钟与时区、实现ID/hash、资格测试及状态来源/新鲜度要求。

B19可选择两种明确配置：提供原on_hold、规范化hold_type和release_date，由规则判断有效期；或由已验证适配器生成active-hold状态，绑定其派生函数和日期。effective_manual只是后一种方案的本地工程示范，不是已部署实现，也没有证明状态认证与新鲜度。

拟新增的准入条件：若声称覆盖完整冻结生命周期，却只有原始布尔标志且无日期映射，则拒绝相应部署资格；若只验证冻结类型子约束，应把该范围写明。源文、适配器和IR的状态定义必须一致。

后续实现应保持同类安全适配器可提供给所有方法，并同时统计合法覆盖与错误放行。不能将通用适配器补全回填成ECAS模型生成优势；元数据自报也不代替对实现及运行来源的验证。本轮不继续扩充实验或修改原引擎。
'''
    (OUT / 'RUNTIME_SEMANTIC_CONTRACT_PROPOSAL_CN.md').write_text(proposal_text, encoding='utf-8')

    report = f'''# ECAS实验简报R4：把来源到执行的链条落实到源码与接口语义

日期：2026-10-15。本轮已完成固定源码核查和B19隔离函数/适配器实验。新增外部模型/API调用0；新生成案例0。R1/R2/R3、旧候选、旧运行与论文均保留。

## 一、这次推进得到什么

**链条可以逐项追溯，但运行时字段的业务含义还必须补齐。** 本轮将七例绑定到原文、IR条件、证据引用、注册路径、实际历史准入和请求结果，并用固定源码核查此前未闭合之处。B19实验进一步表明：上游规范化及有效期定义，会改变同一份规则的正确适用条件；证据ID和路径一致不充分证明这部分语义一致。

最直接的研究问题可收敛为：生成规则对应哪些来源约束和运行前提；这些前提是否有可验证的适配器实现；前提不满足时能否阻止执行。当前实现已检查部分证据/绑定资格，尚未自动核验完整字段业务定义。

## 二、七案例逐环节证据

{table}
七例的Inventory引用、版本、操作、原语及路径登记均已结构性对账，归档准入均ADMITTED、原合法/违规请求对均allow/deny。它们支持既有工程链可追溯，不能抵消表中来源/API/接口定义的缺口。A/B协议分列，仍来自两个项目，不能汇总同协议准确率。

完整字段与原件见{link(OUT / 'SEVEN_CASE_CHAIN_CN.md', '七案例证据链表')}、{link(OUT / 'SEVEN_CASE_CHAIN.json', '逐字段原件JSON')}。

## 三、两项来源核查改变了案例定位

### B06：文档条款与旧API目标存在实际差别

固定Fineract 1.14.0源码有专用transactions?command=undoReAge；旧target的transactions/{{transactionId}}?command=undo进入通用Adjust路径。两者等价未建立，不能把旧可信布尔求值演示直接当作Re-Age真实API完整验证。专用服务选择最新未撤销Re-Age，直接validator仅检查存在Re-Age；通用adjust还存在特定schedule的最新日期检查，本轮不把复杂调用链简化成整个项目“有/无最新交易检查”。

### S02：内部白名单不等于HTTP拒绝未知键

固定源码内部命令确有四字段SUPPORTED和额外参数检查；但HTTP先绑定四字段DTO，Jackson关闭未知属性报错，再序列化进入命令链。静态证据倾向原始未知键先被忽略。没有运行HTTP，不能声称已观察后端接受，也不能宣称原API要求拒绝未知键。网关闭集可以另立为显式加固策略，不能追溯回填旧gold。

两例继续保留历史演示身份，暂不作为来源/API行为充分闭合的主证据。详见{link(OUT / 'SOURCE_GAP_CLOSURE_CN.md', '固定Fineract源码核查')}。

## 四、B19：实际源码函数的隔离验证

### 来源和执行范围

ERPNext 16.0.0源码与本地归档entry字节一致，Frappe 16.1.1文档保存调用顺序另作静态核对。实际抽取完整Supplier.before_save和AccountsController.ensure_supplier_is_not_blocked函数体，以最小对象和日期/取文档/抛异常stub执行，没有启动Frappe、数据库或HTTP。

**此处源码结果只表示该供应商冻结检查是否阻止，不表示完整Purchase Order被接受或拒绝。** 原模型当时未见本轮新增的实现源码，释放日期诊断也超出旧ABI的类型子规则，不能回填为原任务的模型错误率。

冻结32个相关人工状态：冻结两态×空/All/Invoices/Payments四类型×无日期/已过期/当天/未来四日期。先运行真实before_save，再运行真实冻结检查；每行与运行前冻结的独立来源判据一致。解冻当天仍阻止、次日不再阻止。三方法原规则不改，分别用三种状态投影执行，共288个相关政策观察。

### 三种投影的结果

下表是与该源码检查分歧的状态数；每格来自同一组32个相关状态，**不是模型语义准确率、独立样本或方法排名**。

| 状态投影 | ECAS | P2P适配版 | AutoPAC适配版 | 分歧来自哪里 |
|---|---|---|---|---|
| 保存前raw，仅作未规范化挑战 | 3项额外拒绝 | 2项额外拒绝、3项漏阻止 | 2项额外拒绝、3项漏阻止 | 空类型未归一化，加上ABI不含有效期 |
| 实际before_save后的saved | 3项额外拒绝 | 3项额外拒绝 | 3项额外拒绝 | 空类型差异消失；三方均缺释放日期含义 |
| saved加人工有效冻结状态effective_manual | 0项分歧 | 0项分歧 | 0项分歧 | 人工适配器考虑日期，三方共同获得同一输入 |

saved配置的3项分歧分别是已过释放日期、类型来源为空（保存后为All）/All/Invoices。raw的漏阻止仅发生于保存前空类型且冻结仍有效；它不代表正常保存后的生产可达状态。effective_manual补全同一接口状态后，三方在本有限域与该源码检查一致；这说明接口语义是关键条件，不能把手工适配收益归为ECAS模型优势。

T0和main均实际SUCCEEDED；没有新模型调用。原函数执行、前后状态、每条政策输入与原始输出可追溯到{link(OUT / 'RESULTS.json', '原始汇总')}、{link(OUT / 'OBSERVATIONS.csv', '288条观察')}、{link(OUT / 'PROBE_SUMMARY.json', '按配置统计')}。源码链条及正常保存/特殊写入的边界见{link(OUT / 'B19_SOURCE_PATH_CN.md', 'B19固定源码核查')}。

## 五、ECAS链条现在应如何推进

已验证的Inventory准入继续承担来源记录、目标、版本、原语和路径的注册资格检查。新增研究重点是把路径背后的业务定义也变成可核验前提：字段代表保存前还是保存后状态、原字段还是有效状态、默认值在哪里归一化、日期依赖由谁计算。

本轮提供{link(OUT / 'RUNTIME_SEMANTIC_CONTRACT_PROPOSAL_CN.md', '运行时字段语义契约方案')}及机器可读JSON。该方案尚未进入原引擎，不能描述为ECAS已有保证；后续需要绑定实际适配器实现和资格证据，元数据声明本身不等于真实性证明。

### 当前可以使用的表述

ECAS展示了将API资料和业务文档中的多类约束映射到带来源引用的受限IR，并经过注册证据准入与离线执行的可行性。源码核查和B19状态实验进一步明确了该链条依赖的操作范围、规范化与有效期前提；运行时字段定义是需要显式核验的环节。

多类约束的主展示可使用S03类型、S04基本格式、B13数量/例外、B17状态方向，并将B19明确限定为冻结类型子规则。B06/S02的归档表现保留在历史展示；不将七例统称完整生产语义均已跑通，也不声称ECAS独有业务理解或整体优于同行。

## 六、交付和复现

- {link(OUT / 'TASK_CONTRACT_CN.md', '任务契约')}、{link(OUT / 'PROTOCOL_CN.md', '冻结协议')}、{link(OUT / 'FROZEN_VECTORS.json', '32状态清单')}；新WSL lane/root/ecas_source_rule_chain_20261015，原run不重复启动。
- 实验结果只登记本scope的RESULT_TRACEABILITY.csv，根科学账本、原论文和投稿状态未改；根T0指针更新到本scope，旧指针已备份。
- 三方法均为先前GLM适配版，原版P2P/AutoPAC未运行。新源码后见分析、人工适配器和原模型输出身份分列。
- 独立核验记录另存PROBE_INDEPENDENT_AUDIT与CHAIN_INDEPENDENT_REVIEW；只有实际交付的核验通过后，本简报才成为当前解释入口。
'''
    (OUT / 'EXPERIMENT_SUMMARY_CN_R4.md').write_text(report, encoding='utf-8')
    (OUT / 'REPRODUCE.md').write_text('''# Reproduction scope

This is a source-function and adapter interpretation experiment on one exposed historical case. It is not a production Frappe test or a model-generation benchmark.

1. Inspect TASK_CONTRACT_CN.md, PROTOCOL_CN.md, source reports, INPUT_MANIFEST.json, SOURCE_MANIFEST.json and the pinned inputs.
2. Read the existing managed run receipts for source-rule-chain-t0-v1 and source-rule-chain-main-v1. Query their status; do not start them again.
3. A fresh reproduction requires a new independent WSL lane and run IDs, rebinding paths/hashes and the normal experiment gates. Use source_chain_probe.py prepare, managed T0, the actual scoped gate, make-request and managed run in that order.
4. The two source functions are extracted unchanged from their AST; stubs cover only one supplier object, translations, date access and blocking exceptions. A source `allow` means only that this hold check did not block.
5. Compare RESULTS.json with all raw WSL captures and the independently frozen oracle. effective_manual is a human-authored adapter control shared by all methods, not a generated ECAS result.
6. build_chain_report.py reads old seven-case evidence and the completed local results; it performs no model or policy execution. Preserve all original R1-R3 reports and scientific ledgers.
''', encoding='utf-8')

    ledger_path = OUT / 'RESULT_TRACEABILITY.csv'
    with ledger_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; ledger = list(reader)
    ledger = [r for r in ledger if not r['result_id'].startswith('SOURCE-CHAIN-DIFF-')]
    claims = []
    for row in summary_rows:
        rid = 'SOURCE-CHAIN-DIFF-' + row['arm'] + '-' + row['method']
        locator = f"rows[arm={row['arm']},method={row['method']},agrees=false]"
        ledger.append({'result_id': rid, 'experiment_id': 'ECAS-SOURCE-RULE-CHAIN-20261015-01',
            'metric_name': 'source_hold_check_disagreement_related_states', 'dataset_name': 'FSV-B19_source_state_grid',
            'dataset_version': 'frozen-v1', 'data_split': 'posthoc_source_function_adapter_control', 'sample_count': 32,
            'raw_value': row['disagreement_count'], 'reported_value': row['disagreement_count'], 'unit': 'related_states',
            'aggregation': 'count agrees=false within arm/method; not model accuracy', 'source_output_path': str((OUT / 'RESULTS.json').relative_to(PROJECT)),
            'source_locator': locator, 'script_path': str(Path(__file__).relative_to(PROJECT)), 'command_or_config': 'PROTOCOL_CN.md;RUN_REQUEST.json',
            'seed': 'NOT_APPLICABLE', 'environment': 'WSL Python OPA; source functions with stubs', 'git_commit': 'NOT_AVAILABLE_HASH_FROZEN',
            'checksum': sha(OUT / 'RESULTS.json'), 'rounding_rule': 'none', 'status': 'PASS', 'verified_by': 'derived_count_reconciled_with_raw_rows',
            'verified_at': results['completed_at'], 'notes': 'One exposed case; manual adapters shared; only hold check, not full API acceptance'})
        claims.append({'claim_id': 'CLAIM-' + rid, 'manuscript_file': str((OUT / 'EXPERIMENT_SUMMARY_CN_R4.md').relative_to(PROJECT)),
            'section': '四/B19/三种投影', 'locator': row['arm'] + ';' + row['method'], 'claim_text': '与隔离源码hold检查分歧的相关状态数量',
            'number_as_written': row['disagreement_count'], 'number_type': 'related_states_not_accuracy', 'result_id': rid,
            'source_locator': locator, 'verification_status': 'VERIFIED_DERIVED_COUNT', 'verified_by': 'build_chain_report',
            'verified_at': results['completed_at'], 'notes': 'Report only, not manuscript freeze'})
    ledger_path.write_text(table_csv(ledger, fields), encoding='utf-8-sig', newline='')
    claim_path = OUT / 'CLAIM_EVIDENCE_MATRIX.csv'
    with claim_path.open(encoding='utf-8-sig', newline='') as f: claim_fields = next(csv.reader(f))
    claim_path.write_text(table_csv(claims, claim_fields), encoding='utf-8-sig', newline='')
    assert before == {str(p): sha(p) for p in protected}
    dump('BUILD_RECONCILIATION.json', {'status': 'DERIVED_RECONCILED_AWAITING_INDEPENDENT_REPORT_REVIEW',
        'chain_rows': 7, 'source_states': 32, 'policy_rows': 288, 'new_model_calls': 0,
        'protected_files_unchanged': before, 'source_files': len(source_files),
        'outputs': [ref(OUT / f) for f in ('SEVEN_CASE_CHAIN.json', 'SEVEN_CASE_CHAIN.csv', 'SEVEN_CASE_CHAIN_CN.md',
            'PROBE_SUMMARY.json', 'EXPERIMENT_SUMMARY_CN_R4.md', 'RUNTIME_SEMANTIC_CONTRACT_PROPOSAL.json', 'RUNTIME_SEMANTIC_CONTRACT_PROPOSAL_CN.md')]})
    print(json.dumps({'chain_rows': 7, 'source_states': 32, 'policy_observations': 288, 'new_model_calls': 0}))


if __name__ == '__main__': main()
