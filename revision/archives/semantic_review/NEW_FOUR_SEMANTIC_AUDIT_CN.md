# 共同目标四例：语义映射阶段核查

日期：2026-10-15。状态：派生的只读审计，供根任务独立复核。新增模型调用 0，新增政策执行 0。

## 核心判断

此前的最终请求对表没有单列语义映射，因此将“读懂主约束”“写成可执行政策”“通过证据准入”“实际请求判对”压进了一个结果。应增加阶段表。但当前原件不支持把“语义理解”笼统写成 ECAS 独有能力：共同目标 B13、B17、B19 的主业务条件，三个适配流程的首次候选均已正确映射。

这里的语义核查指公开来源到约束的对应：字段/状态绑定、允许/禁止方向、且/或条件、例外、适用操作和来源默认值。它不评判模型内部是否“理解”，也不从两条请求的通过反推所有语义均正确。

## 1. 首次候选分阶段比较

| 案例及项目 | 来源主语义 | ECAS 首次候选 | P2P 适配版首次候选 | AutoPAC 适配版首次候选 |
|---|---|---|---|---|
| S03；Apache Fineract 1.14.0 | age 在出现时为 integer；来源未将 age 列为必填，任务也排除额外 presence 约束 | 映射为 strict_type(integer)，on_missing=skip；类型与非必填边界均保留，开发通过 | 识别为类型校验，并按访问控制入口判范围外；没有政策可评，不能判“理解错误” | reason 与 is_integer(age) 均显示整数意图正确；is_integer 不存在，编译失败。default false 且无缺值放行分支，还有静态的额外必填风险，不能称全部语义已正确 |
| B13；ERPNext 16.0.0 | 数量不超过已提供上限，或者具备授权角色可超限 | (qty≤max) OR (qty>max AND authorizedRole=true)，正确 | DSARCP 与 Rego 均为 (qty≤max) OR authorizedRole=true，正确 | 两个 allow 分支分别为 authorizedRole 和 qty≤max，正确 |
| B17；ERPNext 16.0.0 | Disabled 客户不得创建 Sales Order | 允许 customerDisabled=false，方向和可信路径正确 | DSARCP 明确 DENY disabled=true，Rego 为 not disabled；已知布尔状态正确 | not disabled；已知布尔状态正确，Judge 接受 |
| B19；ERPNext 16.0.0 | On Hold 且 Invoices/All 阻止 Purchase Order；Payments 不阻止该操作 | 允许 !onHold OR holdType=Payments；已知合法枚举域正确 | DSARCP、Rego 为禁止 onHold AND holdType∈{Invoices,All}；已知合法枚举域正确 | 同样禁止 onHold AND holdType∈{Invoices,All}；已知合法枚举域正确，Judge 接受 |

B13 的 ECAS 公式在 max/qty 已定义的数值域内，与两同行公式等价。上限计算和角色认证由公共适配器提供，不能归功于某种方法自行从源文件推导或验证。

B17 的缺状态拒绝，以及 B19 的未知状态拒绝，应在工程控制中比较。公开业务文档未给出所有缺输入处理语义，不能直接将这些差异写成同行业务理解错误。

## 2. 首次与修复后分开

共同目标四例中，仅 S03 的 AutoPAC 适配版实际用了一次修复。首次 is_integer 不存在；修复换成 typeof+regex，整数意图保留，但 typeof 仍不存在，因此修复后仍无可执行政策。修复 reason 自称“valid built-ins”，与 OPA 的已保存编译错误矛盾。首次 Judge 为 ACCEPT、issues=[]，没有指出无效函数或额外必填风险；修复后因预算未再运行 Judge。

其余三例的三方法和 S03 的 ECAS 均首次通过开发，无模型修复；P2P 的 S03 在范围识别后退出。不得把本地恢复 P2P 引用格式、OPA 格式化与注释位置兼容，记成模型业务语义修复。

## 3. B19 的来源默认值值得单列，须保留适配器条件

来源 VIS-FSV-B19-01 的完整 §2.4 Payment Terms and Block Supplier 依次说明默认付款模板、可阻止 invoices/payments/both、未选 hold type 时设为 All、三类 hold type 对应操作、未设置 release date 时无限期冻结。默认值原句为：`Choose 'Hold Type', if you do not select a hold type, ERPNext will set it to "All".` 这里有明确的来源默认值线索。

归档结果已有以下观察，本次未重新运行：

| onHold=true，holdType 为空字符串 | ECAS | P2P 适配版 | AutoPAC 适配版 |
|---|---|---|---|
| 原归档 held-empty-type 分支 | deny | allow | allow |

ECAS 的仅 Payments 放行分支使空字符串被拒绝；两同行只列出 Invoices/All 的拒绝分支，没有处理空值默认 All。这可描述为“在适配器将未规范化的空 hold type 暴露给网关的控制下，ECAS 结果与来源默认 All 一致，两同行遗漏了该默认值”。不能声称已发现生产绕过：ERPNext 可能在到达适配器前就规范化为 All，真实数据路径尚未验证。候选本身也未显式写出“把空值变为 All”，所以当前现象不是模型提取该默认语义的直接证明。

按三层区分这条线索：

| 层次 | 已确认 | 未确认 |
|---|---|---|
| 来源业务语义 | 文档未选 hold type 默认 All；Invoices/All 阻止 Purchase Order，Payments 不阻止它 | 不能仅凭文档确认实际运行版本的全部状态迁移 |
| 当前模型可见 ABI | holdType 仅声明 server_state/string，没有 enum、没有“后端已规范化”的保证；common_adapter 写明 trusted 原样保持。Supplier 字段目录的 Select options 为换行空项、All、Invoices、Payments | 字段目录不等于存储/适配器的状态合法性校验，也不证明空项可作为真实可信状态抵达网关 |
| 生产可达性 | 本轮用的是已保存的适配器输入和执行观察 | 是否提前规范化成 All、是否可产生 held=true 且空类型、可信状态认证及新鲜度，均未验证 |

这一节是“默认值语义线索/事后核读”，不是预注册语义探针；旧分支仍保留原 `conservative_empty_type_control` 分类，未改写任何原始记录。“holdType=Unknown”和“trusted 全缺”仍应保留工程控制分类；不能借空值的来源依据，将三者合并为一组语义正确率。

## 4. 证据与可复核入口

所有原件在 `D:\lunwen\EC-CSI投稿\working\exploration\20261014_matched_evidence_labor\matched_generation`：

- 可见材料：`generation_inputs/<case>/packet.json`。S03 的 OpenAPI age 属性、B13 的 Limit Percent/Role Allowed、B17 的 Disabled、B19 的 Block Supplier/hold types 均逐项读取。
- P2P：`method_runs/<case>/P2P_STYLE/p2p_detect.json`、`p2p_extract.json`、`initial/original.rego`。
- AutoPAC：`method_runs/<case>/AUTOPAC_STYLE/autopac_generate.json`、`initial/original.rego`、`autopac_judge.json`；S03 另有 `repair.json` 与 `repaired/original.rego` 和两个 `CHECKS.json`。
- ECAS：`method_runs/<case>/ECAS_MATCHED/first_candidate.json` 和 `initial/admitted_policy.json`。
- 归档资格及已执行分支：各方法的 `RESULT.json`。该文件只用于对照已保存的编译资格与分支事实，不用最终请求对代替来源到政策的语义核读。

对应 JSON 列出 12 个案例—方法条目，每项绑定实际文件绝对路径及 SHA256；来源列表保留原包中的 source_id、source_sha256、evidence_id、locator。`build_new_four_audit.ps1` 只读既有记录并导出此 JSON，不执行模型或政策。

## 5. 使用边界

本轮是两个既有系统、四个暴露过的任务、每方法单轮的事后解释核查。三方法均为共同 GLM 的流程适配，AutoPAC 原微调 CodeT5-small 生成器并未运行。可以补上“语义映射阶段”，不能形成普适语义优势排序。应分别陈述 ECAS 的语义到 IR 映射、确定性编译、证据契约与运行时缺状态处理，避免把它们都命名为语义理解。
