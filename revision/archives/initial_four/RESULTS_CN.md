# 四例P2P、AutoPAC、ECAS同行测试结果

日期：2026-10-14。状态：COMPLETED；原始证据和独立确定性对账：PASS。

## 1. 结论

**四例已实际测试。P2P和AutoPAC也能识别B13、B17、B19的业务条件；S03在P2P检测阶段被判为范围外。当前结果没有支持“另外三到四个只有ECAS能够成功的案例”。**

不能把这次新增案例全部写成ECAS优势案例。它们可以扩充多规则覆盖展示，但相同模型下ECAS也出现了目标选择和原语选择错误，两种提示配置必须完整分列。

B19存在明确的额外工程差异：缺少可信状态时，P2P/AutoPAC及ECAS v1放行，ECAS v2拒绝；空/未知冻结类型的处理也不完全一致。这些是本例预先冻结的工程控制，不是新增独立业务案例、盲测样本或普适性证明。拒绝取决于本候选的具体规则和on_missing设置，不能概括为所有ECAS配置始终失败闭合。

## 2. 原合法/违规请求对：圆圈总览

本表图例固定为实际原请求对：●两条都符合预期；◐仅一条符合预期；○两条都不符合预期；—未执行或方法声明范围外。**这里的●只表示两条原请求，不能代表完整目标约束、所有分支或总体准确率。**

| 案例 | P2P适配版¹ | AutoPAC适配版² | ECAS结构schema提示v1 | ECAS补全原语说明v2³ |
|---|:---:|:---:|:---:|:---:|
| S03：年龄整数 | —，范围外 | ●⁴ | ● | ◐，字符串误放 |
| B13：数量上限/角色例外 | ● | ● | ● | ● |
| B17：禁用客户下单 | ● | ● | ◐，全拒绝 | ● |
| B19：供应商冻结类型 | ● | ● | ○，允许/禁止反向 | ● |

¹ P2P B13原抽取含目标条件，但中立subject/resource对象未被原字符串组织schema接受。精确对象→其已声明id的表示修复后继续原计划生成；原条件没有改。B17/B19原政策已编译，却因opa-fmt失败；单列OPA格式复演，语法树除位置外一致。三例的原接口/格式拒绝都保留，不能称原流程首轮全通过。

² AutoPAC S03/B19各有一次开发修复；P2P三业务例各有一次开发修复。各分支原始候选、Judge、工具检查、开发反馈与修复都保留。

³ 首批漏附原语用途说明是本次准备缺口。补全所有15操作语义后，四例统一另生成一次，不发送首批候选或测试反馈。v1在B17全拒绝、B19允许/禁止反向；v2修正这两例，但S03漏类型。v2是独立配置，不能与v1按案例择优拼成“ECAS四例全对”。每配置每例只观察一次，未设置seed，不能把两轮差异归因于提示的单一因果效果。

⁴ AutoPAC S03仅通过旧整数/字符串请求对；修复使用is_number，仍允许非整数小数。见下一表。

## 3. 更充分的分支核验

额外探针在模型调用前冻结，沿用四例筛选时的24项协议，三方法同样执行。原请求对与探针分开；探针混合文档业务分支、类型检查和工程控制，不能汇总成方法总体准确率。

| 检查对象 | P2P适配版 | AutoPAC适配版 | ECAS结构提示v1 | ECAS原语说明v2 |
|---|---|---|---|---|
| S03：整数31 | 范围外 | allow | allow | allow |
| S03：字符串"31" | 范围外 | deny | deny | allow，漏类型 |
| S03：布尔true | 范围外 | deny | deny | allow，漏类型 |
| S03：非整数31.5 | 范围外 | allow，未实现严格整数 | deny | allow，漏类型 |
| B13：数量低于/等于/高于上限，及授权超限 | 符合预期 | 符合预期 | 符合预期 | 符合预期 |
| B17：启用/禁用客户 | allow/deny | allow/deny | deny/deny | allow/deny |
| B19：已冻结Invoices/All | deny | deny | allow，条件反向 | deny |
| B19：已冻结Payments | allow | allow | deny，条件反向 | allow |
| B19：已冻结但空类型⁵ | allow | deny | deny | deny |
| B19：已冻结且未知类型⁶ | allow | deny | deny | deny |
| B19：可信状态整体缺失⁶ | allow | allow | allow，on_missing=skip | deny，on_missing=deny |

⁵ 资料说明未选冻结类型时ERPNext默认All，但实际ABI是否先完成默认值归一化尚未验证；当前空类型输入是独立工程控制，不能声称已验证生产状态。

⁶ 未知类型拒绝、缺状态拒绝属于保守执行/接口故障控制，不能把它们当成已在真实系统发生的攻击或文档业务请求准确率。客户端伪造请求体状态/角色的控制也已执行，原request/trusted映射保持不变。

最新配置探针：P2P实际执行20项（S03范围外）、AutoPAC24项、ECAS v2 24项，共68项。ECAS v1的24项另外保存在V1_ECAS_DIAGNOSTICS.json，其中B17可信状态缺失也放行。所有具体输入、预期来源类别及实际输出见audit_rows和COMPARISON_SUMMARY.json。v1原请求结果保留在effect_runs；不按这些混合探针计算整体性能排名。

## 4. 哪一步看到了目标条件

| 案例 | P2P首次识别阶段 | AutoPAC首次生成/修复 | ECAS两配置的规则选择 |
|---|---|---|---|
| S03 | 检测阶段OUT_OF_SCOPE：只有OpenAPI结构和ABI，没有显式访问政策语句 | 首次已有is_integer目标，但OPA没有该builtin；开发修复改成is_number，丢失小数/整数区分 | v1选strict_type；v2选allowed_fields，未落实年龄类型 |
| B13 | 检测/DSARCP抽取已经出现上限及授权例外；随后标识表示被拒绝 | 首次已有可信授权角色或数量≤可信上限 | 两配置均形成bounded_guard_dnf的上限/授权分支 |
| B17 | 检测/DSARCP及首次Rego已有customerDisabled=false；后续opa-fmt阻断 | 首次Rego已有customerDisabled=false | v1误用server_derived_reject，存在可信字段即拒绝；v2用bounded_guard_dnf判断false |
| B19 | 检测/DSARCP及首次Rego已有Invoices/All阻止规则；后续opa-fmt阻断 | 首次阻止Invoices/All；开发修复扩大为已冻结且不是Payments时阻止 | v1把冻结Invoices/All写成允许分支，且缺值skip；v2允许未冻结或Payments，缺值deny |

具体请求错误/允许/拒绝发生在运行时执行，不是在源抽取或证据准入阶段。P2P/AutoPAC的规则形成、工具可执行性与最终效果必须分开解释。

证据准入没有拦住ECAS v1 B17的错误原语、B19反向条件/缺值skip，也没有拦住v2 S03的非目标白名单。准入通过说明满足本注册契约检查，不充分保证候选与原文业务语义等价或目标所需的保守缺值处理。

S03原OpenAPI只列properties，未显式additionalProperties=false。v2选择allowed_fields还包含封闭字段的额外假设；不能据此说成功执行了来源支持的严格类型或完整安全政策。

## 5. 原接口/工具终态与修复边界

原批次12分支均终止：P2P S03范围外；B13组织schema拒绝；B17/B19开发工具拒绝；AutoPAC四例执行；ECAS v1四例执行。该原批次存于EXECUTION_STATE.json和effect_runs，未改写。

- B13：原DSARCP的subject对象精确等于{id,role}，resource对象精确等于{id,system,version}，其id都已在原组织schema中。只转换两者表示；condition、decision、purpose、证据引用及action逐项不变。检测/抽取原调用9/10不重复计费；继续原计划的Rego和测试，结果在format_recovery。
- B17/B19：P2P修复后OPA编译成功，Regal仍报opa-fmt。OPA自动格式化后全部Regal检查和共同/生成开发测试通过；政策AST除location外逐项一致。结果在format_replay，原政策和原拒绝均保留。没有新模型调用或业务条件修改。
- ECAS：首批确实没有提供完整运行语义，不把结构schema-only结果冒称完整ECAS复现。补齐所有15操作说明后四例统一生成；保存两配置全部结果，v2改善B17但S03漏类型，不能以逐例挑选方式掩盖不稳定。

P2P/AutoPAC的开发修复与ECAS配置补跑不是相同监督过程。本轮用于诊断同行流程是否识别这些约束，不能隔离证据契约的因果增量。

## 6. 范围、模型与实际预算

- 来源为原两项目：S03来自Apache Fineract；B13/B17/B19来自ERPNext。旧任务及输出已经暴露，事后筛选，不增加独立项目或盲测样本。
- 原版P2P仍缺可确认代码，原版AutoPAC仍缺必需微调CodeT5权重；本轮执行文献流程适配版，不能称两篇原作的原版性能。资格来源沿用并核对前轮NATIVE_QUALIFICATION.json。
- GLM/Z.AI glm-5.2，thinking enabled，reasoning_effort high；单次input/completion各≤16384 tokens。
- 实际38次调用：4次开发小试、34次方法/配置调用，其中5次外部开发修复、4次ECAS文档配置补跑。基础阶段与配置补跑分列，总量未越过40；未重复计费检测/抽取，没有自动API失败重试。
- 提供方usage：input176755、completion79327。原响应均finish_reason=stop，模型身份一致。未收到实际金额，费用UNKNOWN。
- OPA/Regal及政策编译、检查、评价在WSL独立lane；Windows只运行全局批准GLM wrapper与安全凭据加载。14项T0通过、两层token门禁通过；Git未有commit，输入/代码/工具用哈希冻结。
- 调用前为保守长度估计，调用后以提供方usage确认上限；没有精确GLM本地tokenizer，不将估算称精确token数。
- 共同业务来源及完整条款保持一致；来源机械变换36项核对PASS。第一轮及补充配置、原字段目录、各次输入变换与提示全部留档。

## 7. 论文可以采用的判断

可以写：多个同行流程能够从业务资料提取数量上限、授权例外、禁用客户和冻结类型等条件；结构性校验与访问政策的覆盖范围不同。本轮B19的ECAS v2候选在缺可信状态控制中拒绝，而外部适配策略及ECAS v1候选放行。不能脱离候选版本写“ECAS一律拒绝缺状态”。

不能写：这四例证明ECAS普遍优于两基线、四例只有ECAS能处理、两个提示配置可以逐例拼成四例全对，或P2P范围外等于错误。单个模型、每配置每例一次、有限且已暴露请求，不支持稳定性/普适性/总体优势结论。

这些结果保留了基线成功、ECAS失败及工程差异，适合真实回答审稿人的同行比较要求。正式论证前仍需处理原版复现或明确适配范围、未暴露任务、重复生成、完整目标覆盖及真实API/可信状态绑定等问题。

本轮没有验证生产转发、实时可信状态/身份获取、B13上限计算/累计收货、ERPNext创建/提交生效时点、非版本化业务文档与后端版本一致性。以上限制集中保留，不把离线合成输入执行扩展成真实系统安全效果。

## 8. 核验及文件入口

- 结果：COMPARISON_SUMMARY.json、COMPARISON.csv、audit_rows。
- 首批全部结果：EXECUTION_STATE.json、effect_runs；完整原响应：CALL_LEDGER.json、calls。
- 原语说明配置：DOCUMENTED_ECAS_PROTOCOL_CN.md、DOCUMENTED_OPERATOR_SEMANTICS.json、documented_ecas、DOCUMENTED_EXECUTION_STATE.json。
- 标识表示/格式复演：format_recovery、format_replay、FORMAT_RECOVERY_STATE.json、FORMAT_ONLY_CLOSEOUT.json。
- 输入与代码：EXECUTION_INPUT_MANIFEST.json、FORMAT_RECOVERY_INPUT_MANIFEST.json、DOCUMENTED_INPUT_MANIFEST.json、source_snapshots、generation_inputs、sealed_evaluation。
- 来源/方法/执行对账：INPUT_DELIVERY_QA.json（36项）、FINAL_RECONCILIATION.json（原响应/规则/策略/请求重放）、DELIVERY_QA.json（独立PowerShell179个唯一冻结文件、38次raw、12结果行均PASS）。
- 追溯：本scope RESULT_TRACEABILITY.csv。根历史科学账本与论文未改。

现有五个managed run均已终止为SUCCEEDED；它们是工程完成状态，科学有效性以本报告限定解释和逐项证据为准。没有必要重新start或使用剩余2次预算凑调用。
