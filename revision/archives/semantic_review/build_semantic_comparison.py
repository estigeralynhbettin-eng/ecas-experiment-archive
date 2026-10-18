"""Build a posthoc semantic-stage report from archived evidence; no inference or policy runs."""

from pathlib import Path
import csv
import hashlib
import io
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PREVIOUS = ROOT / "working/exploration/20261015_seven_case_mechanism"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_ref(path):
    return {"path": str(path), "sha256": digest(path)}


def link(path, label):
    return f"[{label}]({path.as_posix()})"


METHODS = ("ECAS_MATCHED", "P2P_STYLE", "AUTOPAC_STYLE")
NAMES = {"ECAS_MATCHED": "ECAS", "P2P_STYLE": "P2P适配版", "AUTOPAC_STYLE": "AutoPAC适配版"}
CASES = {
    "FSV-B06": {
        "name": "B06：撤销条件", "project": "Apache Fineract", "batch": "A",
        "target": "最新Re-Age交易才可撤销",
        "scope": "Re-Age条款与通用undo接口的适用范围尚未闭合；不能由latest条件判全语义正确。",
        "first": ["已表达latest=true", "已表达latest=true", "已表达latest=true"],
        "later": ["首次IR已有主条件；运行结果另列。", "修复只改格式，主条件不变。", "Judge指出Re-Age适用范围；修复未补交易类型区分。"],
    },
    "FSV-S02": {
        "name": "S02：字段白名单", "project": "Apache Fineract", "batch": "A",
        "target": "既有任务约定的四字段闭集白名单",
        "scope": "OpenAPI仅列properties，未声明additionalProperties=false；闭集是任务约定，原文支持尚未闭合。",
        "first": ["已表达四字段白名单¹", "检测范围外，无政策可评", "仅检查必需字段，无白名单"],
        "later": ["首次allowed_fields；不能据任务约定反推原文唯一含义。", "入口限定访问控制，不记语义理解错误。", "Judge接受首次候选；操作者未知键反馈后补出白名单，但is_integer导致编译失败。"],
    },
    "FSV-S04": {
        "name": "S04：邮箱格式", "project": "ERPNext", "batch": "A",
        "target": "email_id的Email字段约束到基本格式校验器的映射",
        "scope": "来源options=Email；ECAS使用已注册email_basic_v1，不能据此宣称完整邮箱规范等价或模型独立发明validator。",
        "first": ["已绑定基本邮箱格式validator", "仅身份/权限，无格式条件", "仅身份/权限，无格式条件"],
        "later": ["首次named_validator/email_basic_v1绑定email_id。", "开发修复仅补is_string，仍缺邮箱格式条件。", "Judge接受首次候选；操作者正负邮箱反馈后才补regex；接口恢复及最终复演另列。"],
    },
    "FSV-S03": {
        "name": "S03：年龄字段类型", "project": "Apache Fineract", "batch": "B",
        "target": "age出现时须为integer，不额外要求字段必填",
        "scope": "源码/任务未要求age必填；AutoPAC额外必填仅静态风险，原代码未编译，不能称缺值行为已实测。",
        "first": ["已表达integer且缺值skip", "检测范围外，无政策可评", "已识别整数要求；代码不可执行²"],
        "later": ["首次strict_type(integer)，on_missing=skip；类型与非必填边界均保留。", "识别为类型校验后按访问控制入口退出，不记理解错误。", "首次is_integer不存在；唯一修复换用同样不存在的typeof，仍无执行资格；静态存在额外必填风险。"],
    },
    "FSV-B13": {
        "name": "B13：数量上限与授权例外", "project": "ERPNext", "batch": "B",
        "target": "qty≤可信上限，或有授权角色例外",
        "scope": "等价性限qty/max已定义数值域；上限与角色状态由公共适配器提供，非各方法自行认证。",
        "first": ["已表达上限或授权例外", "已表达上限或授权例外", "已表达上限或授权例外"],
        "later": ["首次(qty≤max) OR (qty>max AND authorizedRole=true)。", "首次(qty≤max) OR authorizedRole=true。", "首次两个allow分支对应授权与不超限；无需模型修复。"],
    },
    "FSV-B17": {
        "name": "B17：禁用客户", "project": "ERPNext", "batch": "B",
        "target": "禁用客户不得创建Sales Order",
        "scope": "主业务比较限已知布尔状态；trusted缺值是另一控制层，不能自动当业务语义理解优势。",
        "first": ["已表达禁用状态禁止", "已表达禁用状态禁止", "已表达禁用状态禁止"],
        "later": ["首次允许customerDisabled=false；无需模型修复。", "首次DENY disabled=true，Rego为not disabled；已知布尔域正确。", "首次not disabled；已知布尔域正确；无需模型修复。"],
    },
    "FSV-B19": {
        "name": "B19：供应商冻结类型", "project": "ERPNext", "batch": "B",
        "target": "On Hold且类型Invoices/All禁止Purchase Order，Payments不阻止该操作",
        "scope": "已知合法枚举域主条件一致；未选类型默认All另作事后线索，需确认适配器是否暴露未规范化空值，不能由结果反推模型显式提取默认值。",
        "first": ["已表达冻结类型的组合条件³", "已表达冻结类型的组合条件³", "已表达冻结类型的组合条件³"],
        "later": ["首次允许!onHold OR holdType=Payments；无显式empty→All规则。", "首次禁止onHold AND type∈{Invoices,All}；未显式表达空值默认All。", "首次同样禁止onHold AND type∈{Invoices,All}；未显式表达空值默认All。"],
    },
}


def build():
    old_path = OUT / "OLD_THREE_SEMANTIC_AUDIT.json"
    new_path = OUT / "NEW_FOUR_SEMANTIC_AUDIT.json"
    old, new = read_json(old_path), read_json(new_path)
    input_rows = old["rows"] + new["rows"]
    indexed = {(r["case"], r["method"]): r for r in input_rows}
    assert len(input_rows) == len(indexed) == 21
    with (PREVIOUS / "SEVEN_CASE_COMPARISON.csv").open(encoding="utf-8-sig", newline="") as f:
        execution = {(r["task"], r["method"]): r for r in csv.DictReader(f)}
    assert set(indexed) == set(execution)

    # Protect the preceding reports and scientific ledgers; this task only derives explanations.
    protected = [PREVIOUS / "EXPERIMENT_SUMMARY_CN_R2.md", PREVIOUS / "SEVEN_CASE_COMPARISON.csv"]
    protected += [ROOT / n for n in ("RESULT_TRACEABILITY.csv", "CLAIM_EVIDENCE_MATRIX.csv") if (ROOT / n).exists()]
    before = {str(p): digest(p) for p in protected}
    sources = {}

    def collect(value):
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                p = Path(value["path"])
                assert p.is_file(), str(p)
                observed = digest(p)
                assert observed.lower() == value["sha256"].lower(), str(p)
                sources[str(p)] = {"path": str(p), "sha256": observed}
            for v in value.values():
                collect(v)
        elif isinstance(value, list):
            for v in value:
                collect(v)

    collect(old)
    collect(new)
    for p in (old_path, new_path, PREVIOUS / "EXPERIMENT_SUMMARY_CN_R2.md", PREVIOUS / "SEVEN_CASE_COMPARISON.csv"):
        sources[str(p)] = file_ref(p)

    rows, row_index = [], []
    for case, meta in CASES.items():
        for i, method in enumerate(METHODS):
            r = indexed[(case, method)]
            evidence = r.get("evidence", r.get("evidence_files", []))
            assert evidence
            e = execution[(case, method)]
            rows.append({
                "case": case, "case_name_cn": meta["name"], "project_name": meta["project"], "batch": meta["batch"],
                "method": method, "method_name_cn": NAMES[method], "target_main_condition_cn": meta["target"],
                "first_candidate_cn": meta["first"][i], "later_stage_cn": meta["later"][i],
                "source_scope_notes_cn": meta["scope"],
                "execution_status_from_R2": e["displayed_status"], "execution_symbol_from_R2": e["displayed_symbol"],
                "audit_json": str(old_path if meta["batch"] == "A" else new_path),
                "audit_row_key": f"case={case};method={method}",
                "evidence_paths_json": json.dumps(evidence, ensure_ascii=False),
                "label_type": "POSTHOC_QUALITATIVE_CONDITION_FORMATION_NOT_ACCURACY_GOLD",
            })
            row_index.append({"case": case, "method": method, "batch": meta["batch"], "project_name": meta["project"],
                              "audit_row": r, "curated_first": meta["first"][i], "curated_later": meta["later"][i], "scope": meta["scope"]})
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    (OUT / "SEMANTIC_COMPARISON.csv").write_text(buffer.getvalue(), encoding="utf-8-sig", newline="")

    table = "| 批次 | 案例 | 所属项目 | ECAS首次候选 | P2P适配版首次候选 | AutoPAC适配版首次候选 |\n|---|---|---|---|---|---|\n"
    for case, meta in CASES.items():
        table += "| " + " | ".join([meta["batch"], meta["name"], meta["project"], *meta["first"]]) + " |\n"
    notes = """¹ S02可见OpenAPI没有additionalProperties=false。表中“已表达”指已有任务白名单约定进入候选，不表示该闭集是原文唯一正确含义。

² S03 AutoPAC的整数意图正确；但is_integer/typeof不是当前OPA可用函数，默认拒绝且缺少缺值放行分支还有额外必填的静态风险。没有执行资格，不能画成完整语义正确或实际缺值拒绝。

³ B19只对文档已知合法状态下的主业务条件作此判断；来源默认值及生产规范化问题见下文。
"""
    later = "| 案例 | ECAS后续 | P2P适配版后续 | AutoPAC适配版后续 |\n|---|---|---|---|\n"
    for meta in CASES.values():
        later += "| " + " | ".join([meta["name"], *meta["later"]]) + " |\n"

    layers = """| 比较层 | 要回答的问题 | 本组可观察的差别 |
|---|---|---|
| 语义约束提取与映射 | 从来源读出什么条件，绑定哪个字段，且/或、例外与允许/禁止方向是否保留 | S04首次格式条件出现时点不同；S02白名单约定首次形成时点不同；B13/B17/B19主条件三方均形成 |
| 规则可执行性 | 已识别的条件能否变成有效代码或受限IR | S03 AutoPAC整数意图正确但代码失败；ECAS使用受限原语和确定性编译，本轮形成可执行规则 |
| 证据准入 | 候选是否满足Inventory中证据、版本、API、原语、路径及绑定要求 | 配对证据消融显示特定绑定失效被阻断；这不充分证明原文语义正确 |
| 运行时请求处理 | 已准入政策如何处理合法、违规和缺输入请求 | 最终请求对及缺状态机制对照分别报告，不能由deny反推模型理解正确 |
"""
    features = """| 语义相关环节 | ECAS受测流程 | P2P适配版 | AutoPAC适配版 |
|---|---|---|---|
| 从文字到规则 | 来源/ABI/原语说明→Model IR，显式evidence_refs | 检测访问政策→DSARCP→Rego；DSARCP保留来源引用 | 来源/ABI→Rego，另由Judge核读 |
| 表达约束 | 选择已定义原语、路径和参数，再确定性编译 | 模型组合生成Rego，依赖schema/工具/测试 | 模型生成Rego，依赖Judge/工具/测试 |
| 规则与来源绑定 | 强制检查注册证据、目标、版本、原语和路径绑定 | 有组织schema grounding；未验证与ECAS同一证据硬准入机制 | 有来源输入与Judge；未验证与ECAS同一证据硬准入机制 |
| 原文含义是否全部正确 | 当前契约不足以保证；历史三个语义错仍可准入 | 中间抽取与开发测试不能保证全语义正确 | Judge并非gold：S02/S04首次遗漏仍被接受，B06则指出了范围问题 |

三方当前适配版均使用GLM5.2，故观察到的是工作流、表示与监督的差别，不能归因于ECAS使用了更懂语义的基础模型。原AutoPAC使用微调CodeT5-small，当前未运行其原生成器；P2P原作也属于模型生成。ECAS的原语目录、schema和Inventory准备同样影响结果。
"""
    b19 = """来源VIS-FSV-B19-01明确说明：未选择Hold Type时，ERPNext会设为All；Invoices/All禁止Purchase Order。归档held-empty-type输入在onHold=true、holdType为空字符串时，ECAS拒绝，两同行允许。

这是一条值得继续研究的默认值语义线索。当前ABI仅声明holdType为string，未限定枚举，也未保证已规范化；适配器声明保留trusted原值。若未规范化空值确实抵达网关，则ECAS结果与默认All一致，两同行当前规则没有覆盖该默认值。但ECAS候选只是“非冻结或Payments才允许”，没有显式empty→All规则，不能据此认定模型提取了默认值。

生产后端是否已将空值规范化为All、该可信空状态是否可达，尚未验证。旧探针仍是conservative_empty_type_control；本次是事后来源核读，不能改成预冻结语义测试。Unknown类型和trusted全缺仍属工程控制，不并入语义胜负。
"""
    material = """## Material Passport

- 对象：两个既有项目中的七个已暴露任务、21条方法轨迹；批次A与B协议不同。
- 模式：已有证据的事后定性解释，状态ANALYZED_SOURCE_RECONCILED；不是新语义盲测或论文冻结。
- 本轮新增模型/API调用0；新增政策执行0；没有新独立案例。
- 原件：首次候选、抽取、Judge、反馈修复、来源包和既有执行记录。文本标注由本轮核读形成，不是预先独立gold。
"""
    detailed = f"""# 七案例语义约束形成比较

日期：2026-10-15。

**此前遗漏了单独的语义阶段比较。** 最终请求对表把“是否提取目标条件”“是否生成有效规则”“是否通过证据准入”“是否判对请求”压成同一个结果，掩盖了ECAS从来源到可执行约束的特点。本表将这些阶段拆开。

{material}
## 一、先看首次候选形成了什么

这里的“语义”指可核对的约束映射：约束对象、字段绑定、条件方向、且/或、例外、适用操作、非必填与默认值。依据实际政策内容，不用模型reason自述或两条请求结果代替核读。

{table}
{notes}
## 二、反馈修复后发生了什么

{later}
S04最清楚地区分了首次提取与反馈补全：ECAS首次已有基本邮箱validator；AutoPAC经操作者的正负邮箱测试反馈才生成regex，P2P修复后仍只有字符串检查。这个局部差异不能单独归因于证据契约或基础模型能力，因为三流程的原语支持、输出表示和监督环节同时不同。

B06三方虽均形成latest主条件，Re-Age条款与通用undo的适用范围仍未闭合；AutoPAC Judge确实发现了该问题。S02原文未闭合，不能与S04一起简单算作两个“语义获胜案例”。

## 三、ECAS的语义环节应怎样出现在比较中

{layers}
{features}
因此，可以展示ECAS“把来源含义映射到带证据引用的受限IR，并经过确定性准入再执行”的设计特点。当前证据支持部分任务中首次形成目标条件的差别，不支持“只有ECAS理解语义”或“已证明稳定语义优势”。三者均有自然语言到政策的转换能力。

另一个typed IR按源Judge控制确曾指出三个历史主语义错误，但该Judge借鉴AutoPAC思想，属于补充内部控制，并非ECAS原有独有模块；它还对B19 skip给出依据不足的附加理由。不能把其收益重新归给ECAS自身证据准入。

## 四、B19默认值：新的解释线索，尚非新的成功样本

{b19}
## 五、下一步真正需要检验的语义问题

先闭合B06操作范围与S02闭集来源。之后若另行开展生成实验，应预先冻结多条件、例外、否定方向、非必填、默认值和操作范围的来源及独立判据，在相同材料、模型和反馈预算下比较首次/修复后规则；再用有无证据输入与有无硬准入的分开控制，区分语义提取和准入收益。不能继续按已知成功结果挑案例。本轮未启动这项新实验。

## 六、可复核文件

- {link(OUT / 'SEMANTIC_COMPARISON.csv', '21行语义阶段表')}：每条绑定原件路径、审计行键、批次、项目和最终执行资格；不计算语义准确率。
- {link(OUT / 'SEMANTIC_EVIDENCE_INDEX.json', '原件及来源清单')}：保留两份分组核读的字段证据、可见来源locator、文件SHA256及B19完整上下文。
- {link(OUT / 'OLD_THREE_SEMANTIC_AUDIT_CN.md', '旧三例核读')}；{link(OUT / 'NEW_FOUR_SEMANTIC_AUDIT_CN.md', '共同目标四例核读')}。
- {link(OUT / 'EXPERIMENT_SUMMARY_CN_R3.md', '完整实验简报R3')}：保留七案例执行、生成方式、证据准入与缺状态控制，并新增本表。

R1/R2、原候选、旧运行、论文和根科学账本保持原样。来源核读不等于新增实验，也不增加独立样本数量。
"""
    (OUT / "SEMANTIC_COMPARISON_CN.md").write_text(detailed, encoding="utf-8")

    r2 = (PREVIOUS / "EXPERIMENT_SUMMARY_CN_R2.md").read_text(encoding="utf-8-sig")
    execution_section = r2.split("## 一、七案例表", 1)[1].split("## 二、", 1)[0]
    mechanism = link(PREVIOUS / "mechanism_control/RESULTS_CN.md", "既有缺状态机制对照")
    evidence = link(ROOT / "working/exploration/20261014_matched_evidence_labor/evidence_ablation/RESULTS_CN.md", "同候选证据消融")
    mode = link(ROOT / "working/exploration/20261014_matched_evidence_labor/human_effort/MODE_FEATURE_MATRIX_CN.md", "生成方式原作核查")
    summary = f"""# ECAS实验简报R3：七案例的语义、可执行性与证据准入

日期：2026-10-15。**本版补上语义约束形成的比较。** 旧版主要呈现最终请求行为，无法看出目标条件是在首次生成、Judge还是开发反馈之后出现。R3核读已有原件，新增模型/API调用0，新增政策执行0；R1/R2保留。

## 一、当前最有解释力的发现

- **语义形成时点**：S04中ECAS首次已绑定邮箱格式validator，AutoPAC在操作者测试反馈后才补regex，P2P修复后仍无格式条件。S02也有白名单首次形成时点差异，但闭集来源尚未闭合，不能作为独立语义胜利。
- **看懂与写成可执行规则不同**：S03 AutoPAC已识别整数要求，失败是两次使用当前OPA不存在的函数；另有额外必填的静态风险。ECAS首次表达integer及缺值skip并通过开发。
- **复杂主条件不是同行完全不会**：B13的上限/授权例外、B17禁用方向、B19已知冻结类型，三方首次均形成主业务条件。
- **证据驱动有单独的机制证据**：相同候选的特定证据/版本/路径/绑定失效可被完整准入阻断；原文语义正确、trusted值真实性与缺值保守处理仍须分别验证。

## 二、七案例最终请求行为
{execution_section}
## 三、首次语义约束形成：新增比较

“已表达”只评价指定主条件是否进入实际候选，不代表全部业务语义、代码或执行均正确。

{table}
{notes}
### 首次与修复后的差别

{later}
两个协议批次分列；P2P范围外无政策可评，不能计成理解错误。S04映射到已注册基本validator，不代表模型独立推导完整邮箱标准。B06的操作范围未闭合；S02的闭集是任务约定。

## 四、语义理解为什么应与其他层分开

{layers}
{features}
ECAS的重要特点是来源含义→带证据引用的受限IR→确定性准入→执行这一链条。可以比较该链条是否更早形成目标约束、减少无效代码、阻断不具证据资格的部署。现有七例不支持笼统认定“语义理解只有ECAS有”，也不能将多个同时变化的流程差异归于单一机制。

## 五、证据驱动：已有消融支持什么

7个旧案例的11个父候选已有完整准入/shape-only对照。证据不充分、引用记录缺失、版本错配、必需绑定缺失四类构造挑战各11个，以及7个未绑定路径挑战，被完整准入拒绝而无契约可编译。它支持当前Inventory绑定控制的部署阻断增量。

同一对照也保留了三个历史语义错误仍准入、来源locator/hash扰动仍准入的事实；不把Inventory资格当成原文语义正确或文件真实性证明。8个历史IR的按源Judge另指出三个主语义缺陷，另5个ACCEPT；B19 skip的附加理由依据不足。这是借鉴AutoPAC的内部控制，不是ECAS独有模块。详见{evidence}。

## 六、缺可信状态：既有机制对照的结论

R2已完成的144行相关观察表明：ECAS只改on_missing为skip仍通过完整准入，B17/B19的trusted={{}}由拒绝变允许；full与shape-only的对应观察相同。空/未知冻结类型拒绝来自允许条件，而非证据清单强制要求。两同行叠加明确标注的人工typed guard也能闭合被测保守控制差异，保留已测原请求对。

因此，缺值拒绝本身尚非已证实的ECAS独有能力。B19部分缺值Payments-only原ECAS/同行允许、guard拒绝，没有业务gold，不能把更保守直接写成更正确。完整记录见{mechanism}；本轮没有重新执行。

### B19空类型有来源默认值线索

{b19}
## 七、生成方式与可支持的论文表述

三方法当前均用GLM5.2。原P2P是LLM提示管线，原AutoPAC是微调CodeT5-small自动生成，不能归为人工逐条编写。ECAS可表述为无需本任务微调的模型生成流程，但仍需Inventory、ABI、原语与测试准备；当前未测人工劳动节省。详见{mode}。

目前适合表述：在两个既有系统的多类约束上，观察到ECAS把来源目标映射到受限、可追溯规则的可行性；S04等轨迹显示首次提取与反馈补全的差别；证据消融支持特定Inventory绑定控制的增量。语义理解是三方法共同能力，稳定优势和通用性尚未由该批暴露任务建立。

后续研究应先闭合来源边界，冻结未暴露任务与独立语义判据，再分开检验生成时证据输入、受限IR、准入和修复预算的贡献。本版只补齐已有证据解释，没有启动新模型实验。

## 八、交付、追溯与版本

- {link(OUT / 'SEMANTIC_COMPARISON_CN.md', '语义比较详表')}；{link(OUT / 'SEMANTIC_COMPARISON.csv', '21行阶段CSV')}；{link(OUT / 'SEMANTIC_EVIDENCE_INDEX.json', '逐行原件和来源清单')}。
- A批旧三例与B批共同目标四例均来自Apache Fineract、ERPNext，原版P2P/AutoPAC未运行，不合并统一准确率。
- 本轮只读原件核读：新增模型/API0、新增政策执行0；144行机制结果及历史模型调用均为以前已完成的批次，不能重复计入新增产出。
- 原论文、根科学账本、旧候选、R1/R2与投稿状态未修改。本版是内部实验解释，非投稿冻结。
"""
    (OUT / "EXPERIMENT_SUMMARY_CN_R3.md").write_text(summary, encoding="utf-8")

    refs = [
        ROOT / "working/exploration/20261014_matched_evidence_labor/evidence_ablation/RESULTS_CN.md",
        ROOT / "working/exploration/20261014_matched_evidence_labor/human_effort/MODE_FEATURE_MATRIX_CN.md",
        ROOT / "working/exploration/20261014_matched_evidence_labor/judge_control/RESULTS_CN.md",
        PREVIOUS / "mechanism_control/RESULTS_CN.md",
        OUT / "TASK_CONTRACT_CN.md",
    ]
    for p in refs:
        sources[str(p)] = file_ref(p)
    write_json("SEMANTIC_EVIDENCE_INDEX.json", {
        "id": "ECAS-SEMANTIC-STAGE-COMPARISON-20261015-01", "date": "2026-10-15",
        "status": "POSTHOC_QUALITATIVE_SOURCE_POLICY_AUDIT", "new_model_calls": 0, "new_policy_executions": 0,
        "label_definition": "Main-condition formation and later feedback stage; not pre-frozen independent semantic gold.",
        "rows": row_index, "old_visible_source_observations": old["source_observations"],
        "new_visible_sources": new["sources"], "b19_default_value_posthoc_clue": new["b19_default_value_posthoc_clue"],
        "source_files": list(sources.values()),
    })
    assert before == {str(p): digest(p) for p in protected}
    write_json("BUILD_RECEIPT.json", {
        "status": "COMPLETED_SOURCE_HASH_RECONCILED_AWAITING_INDEPENDENT_SEMANTIC_REVIEW",
        "rows": len(rows), "cases": len(CASES), "methods": len(METHODS),
        "source_file_count": len(sources), "all_recorded_hashes_matched": True,
        "new_model_calls": 0, "new_policy_executions": 0, "protected_files_unchanged": before,
        "outputs": [file_ref(OUT / n) for n in ("SEMANTIC_COMPARISON.csv", "SEMANTIC_EVIDENCE_INDEX.json", "SEMANTIC_COMPARISON_CN.md", "EXPERIMENT_SUMMARY_CN_R3.md")],
        "verification_scope": "File hashes, exact 21-key join, no semantic accuracy rate; content review recorded separately.",
    })
    print(json.dumps({"rows": len(rows), "source_files": len(sources), "new_model_calls": 0, "new_policy_executions": 0}, ensure_ascii=False))


if __name__ == "__main__":
    build()
