# ECAS实验简报R3：七案例的语义、可执行性与证据准入

日期：2026-10-15。**本版补上语义约束形成的比较。** 旧版主要呈现最终请求行为，无法看出目标条件是在首次生成、Judge还是开发反馈之后出现。R3核读已有原件，新增模型/API调用0，新增政策执行0；R1/R2保留。

## 一、当前最有解释力的发现

- **语义形成时点**：S04中ECAS首次已绑定邮箱格式validator，AutoPAC在操作者测试反馈后才补regex，P2P修复后仍无格式条件。S02也有白名单首次形成时点差异，但闭集来源尚未闭合，不能作为独立语义胜利。
- **看懂与写成可执行规则不同**：S03 AutoPAC已识别整数要求，失败是两次使用当前OPA不存在的函数；另有额外必填的静态风险。ECAS首次表达integer及缺值skip并通过开发。
- **复杂主条件不是同行完全不会**：B13的上限/授权例外、B17禁用方向、B19已知冻结类型，三方首次均形成主业务条件。
- **证据驱动有单独的机制证据**：相同候选的特定证据/版本/路径/绑定失效可被完整准入阻断；原文语义正确、trusted值真实性与缺值保守处理仍须分别验证。

## 二、七案例最终请求行为


●：原合法/违规两条请求均判对；◐：只有一条判对；—：未执行。范围外与编译失败不能填成正确拒绝，也不能把编译失败算为“一半判对”。

| 批次 | 案例 | 所属项目 | ECAS | P2P适配版 | AutoPAC适配版 |
| --- | --- | --- | --- | --- | --- |
| A | B06：撤销条件 | Apache Fineract | ● | ● | ● |
| A | S02：字段白名单 | Apache Fineract | ● | — 范围外 | — 编译失败 |
| A | S04：邮箱格式 | ERPNext | ● | ◐ 错误邮箱也允许 | ● |
| B | S03：年龄字段类型 | Apache Fineract | ● | — 范围外 | — 编译失败 |
| B | B13：数量上限与授权例外 | ERPNext | ● | ● | ● |
| B | B17：禁用客户 | ERPNext | ● | ● | ● |
| B | B19：供应商冻结类型 | ERPNext | ● | ● | ● |

A是旧三例经过接口映射/OPA格式恢复的事后复演；原开发资格失败另有记录。B是共同目标、完整操作说明、一次修复机会和执行资格检查的新协议。七例放在一起方便展示，不能合计统一准确率或写成七个同协议独立样本。它们仍来自Fineract、ERPNext两个项目，均为已暴露任务。

B06通用undo与Re-Age条款的适用范围、S02封闭字段约定来源仍需保留解释边界；S04仅为注册基本邮箱校验器。原版P2P/AutoPAC未运行，表中是GLM适配实现。

详细轨迹及原流程状态：[七案例详细表](D:/lunwen/EC-CSI投稿/working/exploration/20261015_seven_case_mechanism/SEVEN_CASE_TABLE_CN.md)。


## 三、首次语义约束形成：新增比较

“已表达”只评价指定主条件是否进入实际候选，不代表全部业务语义、代码或执行均正确。

| 批次 | 案例 | 所属项目 | ECAS首次候选 | P2P适配版首次候选 | AutoPAC适配版首次候选 |
|---|---|---|---|---|---|
| A | B06：撤销条件 | Apache Fineract | 已表达latest=true | 已表达latest=true | 已表达latest=true |
| A | S02：字段白名单 | Apache Fineract | 已表达四字段白名单¹ | 检测范围外，无政策可评 | 仅检查必需字段，无白名单 |
| A | S04：邮箱格式 | ERPNext | 已绑定基本邮箱格式validator | 仅身份/权限，无格式条件 | 仅身份/权限，无格式条件 |
| B | S03：年龄字段类型 | Apache Fineract | 已表达integer且缺值skip | 检测范围外，无政策可评 | 已识别整数要求；代码不可执行² |
| B | B13：数量上限与授权例外 | ERPNext | 已表达上限或授权例外 | 已表达上限或授权例外 | 已表达上限或授权例外 |
| B | B17：禁用客户 | ERPNext | 已表达禁用状态禁止 | 已表达禁用状态禁止 | 已表达禁用状态禁止 |
| B | B19：供应商冻结类型 | ERPNext | 已表达冻结类型的组合条件³ | 已表达冻结类型的组合条件³ | 已表达冻结类型的组合条件³ |

¹ S02可见OpenAPI没有additionalProperties=false。表中“已表达”指已有任务白名单约定进入候选，不表示该闭集是原文唯一正确含义。

² S03 AutoPAC的整数意图正确；但is_integer/typeof不是当前OPA可用函数，默认拒绝且缺少缺值放行分支还有额外必填的静态风险。没有执行资格，不能画成完整语义正确或实际缺值拒绝。

³ B19只对文档已知合法状态下的主业务条件作此判断；来源默认值及生产规范化问题见下文。

### 首次与修复后的差别

| 案例 | ECAS后续 | P2P适配版后续 | AutoPAC适配版后续 |
|---|---|---|---|
| B06：撤销条件 | 首次IR已有主条件；运行结果另列。 | 修复只改格式，主条件不变。 | Judge指出Re-Age适用范围；修复未补交易类型区分。 |
| S02：字段白名单 | 首次allowed_fields；不能据任务约定反推原文唯一含义。 | 入口限定访问控制，不记语义理解错误。 | Judge接受首次候选；操作者未知键反馈后补出白名单，但is_integer导致编译失败。 |
| S04：邮箱格式 | 首次named_validator/email_basic_v1绑定email_id。 | 开发修复仅补is_string，仍缺邮箱格式条件。 | Judge接受首次候选；操作者正负邮箱反馈后才补regex；接口恢复及最终复演另列。 |
| S03：年龄字段类型 | 首次strict_type(integer)，on_missing=skip；类型与非必填边界均保留。 | 识别为类型校验后按访问控制入口退出，不记理解错误。 | 首次is_integer不存在；唯一修复换用同样不存在的typeof，仍无执行资格；静态存在额外必填风险。 |
| B13：数量上限与授权例外 | 首次(qty≤max) OR (qty>max AND authorizedRole=true)。 | 首次(qty≤max) OR authorizedRole=true。 | 首次两个allow分支对应授权与不超限；无需模型修复。 |
| B17：禁用客户 | 首次允许customerDisabled=false；无需模型修复。 | 首次DENY disabled=true，Rego为not disabled；已知布尔域正确。 | 首次not disabled；已知布尔域正确；无需模型修复。 |
| B19：供应商冻结类型 | 首次允许!onHold OR holdType=Payments；无显式empty→All规则。 | 首次禁止onHold AND type∈{Invoices,All}；未显式表达空值默认All。 | 首次同样禁止onHold AND type∈{Invoices,All}；未显式表达空值默认All。 |

两个协议批次分列；P2P范围外无政策可评，不能计成理解错误。S04映射到已注册基本validator，不代表模型独立推导完整邮箱标准。B06的操作范围未闭合；S02的闭集是任务约定。

## 四、语义理解为什么应与其他层分开

| 比较层 | 要回答的问题 | 本组可观察的差别 |
|---|---|---|
| 语义约束提取与映射 | 从来源读出什么条件，绑定哪个字段，且/或、例外与允许/禁止方向是否保留 | S04首次格式条件出现时点不同；S02白名单约定首次形成时点不同；B13/B17/B19主条件三方均形成 |
| 规则可执行性 | 已识别的条件能否变成有效代码或受限IR | S03 AutoPAC整数意图正确但代码失败；ECAS使用受限原语和确定性编译，本轮形成可执行规则 |
| 证据准入 | 候选是否满足Inventory中证据、版本、API、原语、路径及绑定要求 | 配对证据消融显示特定绑定失效被阻断；这不充分证明原文语义正确 |
| 运行时请求处理 | 已准入政策如何处理合法、违规和缺输入请求 | 最终请求对及缺状态机制对照分别报告，不能由deny反推模型理解正确 |

| 语义相关环节 | ECAS受测流程 | P2P适配版 | AutoPAC适配版 |
|---|---|---|---|
| 从文字到规则 | 来源/ABI/原语说明→Model IR，显式evidence_refs | 检测访问政策→DSARCP→Rego；DSARCP保留来源引用 | 来源/ABI→Rego，另由Judge核读 |
| 表达约束 | 选择已定义原语、路径和参数，再确定性编译 | 模型组合生成Rego，依赖schema/工具/测试 | 模型生成Rego，依赖Judge/工具/测试 |
| 规则与来源绑定 | 强制检查注册证据、目标、版本、原语和路径绑定 | 有组织schema grounding；未验证与ECAS同一证据硬准入机制 | 有来源输入与Judge；未验证与ECAS同一证据硬准入机制 |
| 原文含义是否全部正确 | 当前契约不足以保证；历史三个语义错仍可准入 | 中间抽取与开发测试不能保证全语义正确 | Judge并非gold：S02/S04首次遗漏仍被接受，B06则指出了范围问题 |

三方当前适配版均使用GLM5.2，故观察到的是工作流、表示与监督的差别，不能归因于ECAS使用了更懂语义的基础模型。原AutoPAC使用微调CodeT5-small，当前未运行其原生成器；P2P原作也属于模型生成。ECAS的原语目录、schema和Inventory准备同样影响结果。

ECAS的重要特点是来源含义→带证据引用的受限IR→确定性准入→执行这一链条。可以比较该链条是否更早形成目标约束、减少无效代码、阻断不具证据资格的部署。现有七例不支持笼统认定“语义理解只有ECAS有”，也不能将多个同时变化的流程差异归于单一机制。

## 五、证据驱动：已有消融支持什么

7个旧案例的11个父候选已有完整准入/shape-only对照。证据不充分、引用记录缺失、版本错配、必需绑定缺失四类构造挑战各11个，以及7个未绑定路径挑战，被完整准入拒绝而无契约可编译。它支持当前Inventory绑定控制的部署阻断增量。

同一对照也保留了三个历史语义错误仍准入、来源locator/hash扰动仍准入的事实；不把Inventory资格当成原文语义正确或文件真实性证明。8个历史IR的按源Judge另指出三个主语义缺陷，另5个ACCEPT；B19 skip的附加理由依据不足。这是借鉴AutoPAC的内部控制，不是ECAS独有模块。详见[同候选证据消融](D:/lunwen/EC-CSI投稿/working/exploration/20261014_matched_evidence_labor/evidence_ablation/RESULTS_CN.md)。

## 六、缺可信状态：既有机制对照的结论

R2已完成的144行相关观察表明：ECAS只改on_missing为skip仍通过完整准入，B17/B19的trusted={}由拒绝变允许；full与shape-only的对应观察相同。空/未知冻结类型拒绝来自允许条件，而非证据清单强制要求。两同行叠加明确标注的人工typed guard也能闭合被测保守控制差异，保留已测原请求对。

因此，缺值拒绝本身尚非已证实的ECAS独有能力。B19部分缺值Payments-only原ECAS/同行允许、guard拒绝，没有业务gold，不能把更保守直接写成更正确。完整记录见[既有缺状态机制对照](D:/lunwen/EC-CSI投稿/working/exploration/20261015_seven_case_mechanism/mechanism_control/RESULTS_CN.md)；本轮没有重新执行。

### B19空类型有来源默认值线索

来源VIS-FSV-B19-01明确说明：未选择Hold Type时，ERPNext会设为All；Invoices/All禁止Purchase Order。归档held-empty-type输入在onHold=true、holdType为空字符串时，ECAS拒绝，两同行允许。

这是一条值得继续研究的默认值语义线索。当前ABI仅声明holdType为string，未限定枚举，也未保证已规范化；适配器声明保留trusted原值。若未规范化空值确实抵达网关，则ECAS结果与默认All一致，两同行当前规则没有覆盖该默认值。但ECAS候选只是“非冻结或Payments才允许”，没有显式empty→All规则，不能据此认定模型提取了默认值。

生产后端是否已将空值规范化为All、该可信空状态是否可达，尚未验证。旧探针仍是conservative_empty_type_control；本次是事后来源核读，不能改成预冻结语义测试。Unknown类型和trusted全缺仍属工程控制，不并入语义胜负。

## 七、生成方式与可支持的论文表述

三方法当前均用GLM5.2。原P2P是LLM提示管线，原AutoPAC是微调CodeT5-small自动生成，不能归为人工逐条编写。ECAS可表述为无需本任务微调的模型生成流程，但仍需Inventory、ABI、原语与测试准备；当前未测人工劳动节省。详见[生成方式原作核查](D:/lunwen/EC-CSI投稿/working/exploration/20261014_matched_evidence_labor/human_effort/MODE_FEATURE_MATRIX_CN.md)。

目前适合表述：在两个既有系统的多类约束上，观察到ECAS把来源目标映射到受限、可追溯规则的可行性；S04等轨迹显示首次提取与反馈补全的差别；证据消融支持特定Inventory绑定控制的增量。语义理解是三方法共同能力，稳定优势和通用性尚未由该批暴露任务建立。

后续研究应先闭合来源边界，冻结未暴露任务与独立语义判据，再分开检验生成时证据输入、受限IR、准入和修复预算的贡献。本版只补齐已有证据解释，没有启动新模型实验。

## 八、交付、追溯与版本

- [语义比较详表](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/SEMANTIC_COMPARISON_CN.md)；[21行阶段CSV](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/SEMANTIC_COMPARISON.csv)；[逐行原件和来源清单](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/SEMANTIC_EVIDENCE_INDEX.json)。
- A批旧三例与B批共同目标四例均来自Apache Fineract、ERPNext，原版P2P/AutoPAC未运行，不合并统一准确率。
- 本轮只读原件核读：新增模型/API0、新增政策执行0；144行机制结果及历史模型调用均为以前已完成的批次，不能重复计入新增产出。
- 原论文、根科学账本、旧候选、R1/R2与投稿状态未修改。本版是内部实验解释，非投稿冻结。
