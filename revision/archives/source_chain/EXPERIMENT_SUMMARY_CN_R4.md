# ECAS实验简报R4：把来源到执行的链条落实到源码与接口语义

日期：2026-10-15。本轮已完成固定源码核查和B19隔离函数/适配器实验。新增外部模型/API调用0；新生成案例0。R1/R2/R3、旧候选、旧运行与论文均保留。

## 一、这次推进得到什么

**链条可以逐项追溯，但运行时字段的业务含义还必须补齐。** 本轮将七例绑定到原文、IR条件、证据引用、注册路径、实际历史准入和请求结果，并用固定源码核查此前未闭合之处。B19实验进一步表明：上游规范化及有效期定义，会改变同一份规则的正确适用条件；证据ID和路径一致不充分证明这部分语义一致。

最直接的研究问题可收敛为：生成规则对应哪些来源约束和运行前提；这些前提是否有可验证的适配器实现；前提不满足时能否阻止执行。当前实现已检查部分证据/绑定资格，尚未自动核验完整字段业务定义。

## 二、七案例逐环节证据

| 案例 | 所属项目 | 来源到IR的映射 | 当前证据定位 |
|---|---|---|---|
| B06 撤销条件 | Apache Fineract | bounded_guard_dnf：reAgeIsLatestTransaction=true | 历史抽取/布尔判定演示；专用undoReAge与旧通用undo目标不一致，映射未闭合 |
| S02 字段白名单 | Apache Fineract | allowed_fields：四字段闭集 | 历史网关策略约定；静态HTTP链先DTO绑定、关闭未知键报错，拒绝未知键未证成 |
| S04 邮箱格式 | ERPNext | named_validator：email_basic_v1 | 可展示Email属性到注册基本格式原语的映射；未证明与后端全部邮箱规范等价 |
| S03 整数类型 | Apache Fineract | strict_type(integer)，on_missing=skip | 支持指定类型子约束的来源到IR及离线执行链 |
| B13 上限与授权例外 | ERPNext | bounded_guard_dnf：qty≤max，或超限且authorizedRole | 支持指定数量子约束；上限计算、角色认证与真实状态获取由公共ABI提供，未单独验证 |
| B17 禁用客户 | ERPNext | bounded_guard_dnf：customerDisabled=false | 支持已知布尔状态下的方向映射；状态认证及生产转发未验证 |
| B19 冻结类型 | ERPNext | bounded_guard_dnf：supplierOnHold=false OR holdType=Payments | 支持冻结类型子规则；原ABI未声明规范化和有效期语义，完整冻结生命周期未闭合 |

七例的Inventory引用、版本、操作、原语及路径登记均已结构性对账，归档准入均ADMITTED、原合法/违规请求对均allow/deny。它们支持既有工程链可追溯，不能抵消表中来源/API/接口定义的缺口。A/B协议分列，仍来自两个项目，不能汇总同协议准确率。

完整字段与原件见[七案例证据链表](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/SEVEN_CASE_CHAIN_CN.md)、[逐字段原件JSON](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/SEVEN_CASE_CHAIN.json)。

## 三、两项来源核查改变了案例定位

### B06：文档条款与旧API目标存在实际差别

固定Fineract 1.14.0源码有专用transactions?command=undoReAge；旧target的transactions/{transactionId}?command=undo进入通用Adjust路径。两者等价未建立，不能把旧可信布尔求值演示直接当作Re-Age真实API完整验证。专用服务选择最新未撤销Re-Age，直接validator仅检查存在Re-Age；通用adjust还存在特定schedule的最新日期检查，本轮不把复杂调用链简化成整个项目“有/无最新交易检查”。

### S02：内部白名单不等于HTTP拒绝未知键

固定源码内部命令确有四字段SUPPORTED和额外参数检查；但HTTP先绑定四字段DTO，Jackson关闭未知属性报错，再序列化进入命令链。静态证据倾向原始未知键先被忽略。没有运行HTTP，不能声称已观察后端接受，也不能宣称原API要求拒绝未知键。网关闭集可以另立为显式加固策略，不能追溯回填旧gold。

两例继续保留历史演示身份，暂不作为来源/API行为充分闭合的主证据。详见[固定Fineract源码核查](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/SOURCE_GAP_CLOSURE_CN.md)。

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

T0和main均实际SUCCEEDED；没有新模型调用。原函数执行、前后状态、每条政策输入与原始输出可追溯到[原始汇总](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/RESULTS.json)、[288条观察](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/OBSERVATIONS.csv)、[按配置统计](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/PROBE_SUMMARY.json)。源码链条及正常保存/特殊写入的边界见[B19固定源码核查](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/B19_SOURCE_PATH_CN.md)。

## 五、ECAS链条现在应如何推进

已验证的Inventory准入继续承担来源记录、目标、版本、原语和路径的注册资格检查。新增研究重点是把路径背后的业务定义也变成可核验前提：字段代表保存前还是保存后状态、原字段还是有效状态、默认值在哪里归一化、日期依赖由谁计算。

本轮提供[运行时字段语义契约方案](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/RUNTIME_SEMANTIC_CONTRACT_PROPOSAL_CN.md)及机器可读JSON。该方案尚未进入原引擎，不能描述为ECAS已有保证；后续需要绑定实际适配器实现和资格证据，元数据声明本身不等于真实性证明。

### 当前可以使用的表述

ECAS展示了将API资料和业务文档中的多类约束映射到带来源引用的受限IR，并经过注册证据准入与离线执行的可行性。源码核查和B19状态实验进一步明确了该链条依赖的操作范围、规范化与有效期前提；运行时字段定义是需要显式核验的环节。

多类约束的主展示可使用S03类型、S04基本格式、B13数量/例外、B17状态方向，并将B19明确限定为冻结类型子规则。B06/S02的归档表现保留在历史展示；不将七例统称完整生产语义均已跑通，也不声称ECAS独有业务理解或整体优于同行。

## 六、交付和复现

- [任务契约](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/TASK_CONTRACT_CN.md)、[冻结协议](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/PROTOCOL_CN.md)、[32状态清单](D:/lunwen/EC-CSI投稿/working/exploration/20261015_source_rule_chain/FROZEN_VECTORS.json)；新WSL lane/root/ecas_source_rule_chain_20261015，原run不重复启动。
- 实验结果只登记本scope的RESULT_TRACEABILITY.csv，根科学账本、原论文和投稿状态未改；根T0指针更新到本scope，旧指针已备份。
- 三方法均为先前GLM适配版，原版P2P/AutoPAC未运行。新源码后见分析、人工适配器和原模型输出身份分列。
- 独立核验记录另存PROBE_INDEPENDENT_AUDIT与CHAIN_INDEPENDENT_REVIEW；只有实际交付的核验通过后，本简报才成为当前解释入口。
