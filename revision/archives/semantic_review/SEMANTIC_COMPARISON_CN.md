# 七案例语义约束形成比较

日期：2026-10-15。

**此前遗漏了单独的语义阶段比较。** 最终请求对表把“是否提取目标条件”“是否生成有效规则”“是否通过证据准入”“是否判对请求”压成同一个结果，掩盖了ECAS从来源到可执行约束的特点。本表将这些阶段拆开。

## Material Passport

- 对象：两个既有项目中的七个已暴露任务、21条方法轨迹；批次A与B协议不同。
- 模式：已有证据的事后定性解释，状态ANALYZED_SOURCE_RECONCILED；不是新语义盲测或论文冻结。
- 本轮新增模型/API调用0；新增政策执行0；没有新独立案例。
- 原件：首次候选、抽取、Judge、反馈修复、来源包和既有执行记录。文本标注由本轮核读形成，不是预先独立gold。

## 一、先看首次候选形成了什么

这里的“语义”指可核对的约束映射：约束对象、字段绑定、条件方向、且/或、例外、适用操作、非必填与默认值。依据实际政策内容，不用模型reason自述或两条请求结果代替核读。

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

## 二、反馈修复后发生了什么

| 案例 | ECAS后续 | P2P适配版后续 | AutoPAC适配版后续 |
|---|---|---|---|
| B06：撤销条件 | 首次IR已有主条件；运行结果另列。 | 修复只改格式，主条件不变。 | Judge指出Re-Age适用范围；修复未补交易类型区分。 |
| S02：字段白名单 | 首次allowed_fields；不能据任务约定反推原文唯一含义。 | 入口限定访问控制，不记语义理解错误。 | Judge接受首次候选；操作者未知键反馈后补出白名单，但is_integer导致编译失败。 |
| S04：邮箱格式 | 首次named_validator/email_basic_v1绑定email_id。 | 开发修复仅补is_string，仍缺邮箱格式条件。 | Judge接受首次候选；操作者正负邮箱反馈后才补regex；接口恢复及最终复演另列。 |
| S03：年龄字段类型 | 首次strict_type(integer)，on_missing=skip；类型与非必填边界均保留。 | 识别为类型校验后按访问控制入口退出，不记理解错误。 | 首次is_integer不存在；唯一修复换用同样不存在的typeof，仍无执行资格；静态存在额外必填风险。 |
| B13：数量上限与授权例外 | 首次(qty≤max) OR (qty>max AND authorizedRole=true)。 | 首次(qty≤max) OR authorizedRole=true。 | 首次两个allow分支对应授权与不超限；无需模型修复。 |
| B17：禁用客户 | 首次允许customerDisabled=false；无需模型修复。 | 首次DENY disabled=true，Rego为not disabled；已知布尔域正确。 | 首次not disabled；已知布尔域正确；无需模型修复。 |
| B19：供应商冻结类型 | 首次允许!onHold OR holdType=Payments；无显式empty→All规则。 | 首次禁止onHold AND type∈{Invoices,All}；未显式表达空值默认All。 | 首次同样禁止onHold AND type∈{Invoices,All}；未显式表达空值默认All。 |

S04最清楚地区分了首次提取与反馈补全：ECAS首次已有基本邮箱validator；AutoPAC经操作者的正负邮箱测试反馈才生成regex，P2P修复后仍只有字符串检查。这个局部差异不能单独归因于证据契约或基础模型能力，因为三流程的原语支持、输出表示和监督环节同时不同。

B06三方虽均形成latest主条件，Re-Age条款与通用undo的适用范围仍未闭合；AutoPAC Judge确实发现了该问题。S02原文未闭合，不能与S04一起简单算作两个“语义获胜案例”。

## 三、ECAS的语义环节应怎样出现在比较中

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

因此，可以展示ECAS“把来源含义映射到带证据引用的受限IR，并经过确定性准入再执行”的设计特点。当前证据支持部分任务中首次形成目标条件的差别，不支持“只有ECAS理解语义”或“已证明稳定语义优势”。三者均有自然语言到政策的转换能力。

另一个typed IR按源Judge控制确曾指出三个历史主语义错误，但该Judge借鉴AutoPAC思想，属于补充内部控制，并非ECAS原有独有模块；它还对B19 skip给出依据不足的附加理由。不能把其收益重新归给ECAS自身证据准入。

## 四、B19默认值：新的解释线索，尚非新的成功样本

来源VIS-FSV-B19-01明确说明：未选择Hold Type时，ERPNext会设为All；Invoices/All禁止Purchase Order。归档held-empty-type输入在onHold=true、holdType为空字符串时，ECAS拒绝，两同行允许。

这是一条值得继续研究的默认值语义线索。当前ABI仅声明holdType为string，未限定枚举，也未保证已规范化；适配器声明保留trusted原值。若未规范化空值确实抵达网关，则ECAS结果与默认All一致，两同行当前规则没有覆盖该默认值。但ECAS候选只是“非冻结或Payments才允许”，没有显式empty→All规则，不能据此认定模型提取了默认值。

生产后端是否已将空值规范化为All、该可信空状态是否可达，尚未验证。旧探针仍是conservative_empty_type_control；本次是事后来源核读，不能改成预冻结语义测试。Unknown类型和trusted全缺仍属工程控制，不并入语义胜负。

## 五、下一步真正需要检验的语义问题

先闭合B06操作范围与S02闭集来源。之后若另行开展生成实验，应预先冻结多条件、例外、否定方向、非必填、默认值和操作范围的来源及独立判据，在相同材料、模型和反馈预算下比较首次/修复后规则；再用有无证据输入与有无硬准入的分开控制，区分语义提取和准入收益。不能继续按已知成功结果挑案例。本轮未启动这项新实验。

## 六、可复核文件

- [21行语义阶段表](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/SEMANTIC_COMPARISON.csv)：每条绑定原件路径、审计行键、批次、项目和最终执行资格；不计算语义准确率。
- [原件及来源清单](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/SEMANTIC_EVIDENCE_INDEX.json)：保留两份分组核读的字段证据、可见来源locator、文件SHA256及B19完整上下文。
- [旧三例核读](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/OLD_THREE_SEMANTIC_AUDIT_CN.md)；[共同目标四例核读](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/NEW_FOUR_SEMANTIC_AUDIT_CN.md)。
- [完整实验简报R3](D:/lunwen/EC-CSI投稿/working/exploration/20261015_semantic_comparison/EXPERIMENT_SUMMARY_CN_R3.md)：保留七案例执行、生成方式、证据准入与缺状态控制，并新增本表。

R1/R2、原候选、旧运行、论文和根科学账本保持原样。来源核读不等于新增实验，也不增加独立样本数量。
