# B19源码函数与适配器实验：独立复核

日期：2026-10-15。结论：**在明确的有限范围内通过复核**。本次仅核文件、哈希、AST、人工判据与已保存执行输出，没有重新运行政策、源码函数或模型。

## 1. 实际终态与原件

- main-v1 的 managed status 为 SUCCEEDED、exit_code=0；scope `RESULTS.json` 与 managed `outputs/result.json` 字节相同，SHA256 为 `102b573248b04db8bcbae74cec79f5fb55175f4d362f9785ae8c86ca01e5089c`。
- T0 实际 SUCCEEDED；18项工程检查均通过；scope formal gate 为 ready、blockers为空。
- 冻结清单、源码原件与 snapshot、runner 的输入前后记录均对账；本轮运行前后没有发现已登记输入漂移。
- 32个 source state 唯一完整；288个 state×arm×method 身份唯一完整；CSV与逐条 observation 相符；192份 OPA实际输入及原始stdout逐条对账，stderr为空；96份ECAS实际输出均有allow/deny和无engine_error。
- 运行产出的ECAS admitted policy与旧实验原始 admitted policy对象完全相同；两个同行快照与原合格Rego哈希相同。没有把人工修订规则回填成原模型候选。

## 2. AST提取与stub边界

冻结脚本从 source snapshot 中唯一类、唯一无decorator的目标FunctionDef做deepcopy，完整函数体作为单个模块函数编译，未重写分支。每个source row记录的行号与AST哈希，均与独立解析原snapshot所得一致。

提取对象为 Supplier.before_save（88–93）与 AccountsController.ensure_supplier_is_not_blocked（157–174）。两函数没有依赖super或类闭包，省略类容器不会改变本有限输入中的函数体解释；但这不是运行完整Frappe回调链。

stub只替代：单个Supplier对象、frappe.get_lazy_doc、msgprint抛错、翻译、getdate和固定nowdate。get_lazy_doc不实现数据库与缓存，且无真实权限、状态认证、新鲜度、hooks、事务或HTTP路径。源码里确实请求Supplier和目标供应商；stub本身不验证任意doctype/name查找正确性，因此不能推广为多供应商绑定验证。

源码检查不抛异常时记录的allow，含义是**这一项供应商hold检查没有阻止**；它不表示采购单满足其他业务校验、获得完整授权或真的保存成功。

## 3. 冻结判据和日期临界点

独立核读固定源码后确认：未冻结清空类型/日期；冻结且空类型设All；Purchase Order只在All/Invoices且“无release_date，或today≤release_date”时被此检查阻止。固定today为2026-10-15，因此10月14日已解除该hold阻止，10月15日当天仍阻止，10月16日仍阻止。

冻结向量是bool两态×四类型×四日期的完整32组合。32行before与冻结向量、after与正常before_save结果、source decision与预冻结来源判据均相符。对当天等号单独核对，未出现把到期日当天提前放行的问题。

人工判据在此网格运行前冻结，但任务和历史输出早已暴露。应称来源函数的有限域核验，不是独立盲测，也不是模型语义准确率。

## 4. 三方是否同条件

每一state和arm的request/trusted对象在三方法间完全相同。Rego额外收到原公共适配器的中性subject/action/resource包，192份实际输入与该确定性包逐条相同；ECAS按原candidate→完整Inventory准入→原engine执行。未新增只对一方提供的状态值、来源条款或默认答案。

| 配置 | 身份及边界 |
|---|---|
| raw | 规范化前on_hold/hold_type直接进入原ABI；包含正常保存会清理或改变的状态，只是接口挑战，不是正常已存供应商状态，更不是生产漏洞证据 |
| saved | 对实际before_save后的状态投影原ABI；正常化空值→All后，三方法类型子规则一致；原ABI仍没有release_date |
| effective_manual | 人工把已过release_date的supplierOnHold投影为false，同样应用于三方法；是新增人工工程适配，不是模型生成收益、已部署适配器或ECAS独占能力 |

## 5. 结果逐项重算

“过拒”仅指此hold检查不阻止但政策拒绝；“漏拒”仅指此hold检查阻止但政策允许。它们均是32个相关人工状态内的诊断计数。

| 配置 | 方法 | 与hold检查一致 | 过拒 | 漏拒 |
|---|---|---:|---:|---:|
| raw | ECAS | 29 | 3 | 0 |
| raw | P2P适配版 | 27 | 2 | 3 |
| raw | AutoPAC适配版 | 27 | 2 | 3 |
| saved | ECAS | 29 | 3 | 0 |
| saved | P2P适配版 | 29 | 3 | 0 |
| saved | AutoPAC适配版 | 29 | 3 | 0 |
| effective_manual | ECAS | 32 | 0 | 0 |
| effective_manual | P2P适配版 | 32 | 0 | 0 |
| effective_manual | AutoPAC适配版 | 32 | 0 | 0 |

raw下两同行的3项漏拒来自未规范化空类型、有效期仍活跃；saved经真实before_save将空值设All后该分歧消失。saved下三方均有的3项过拒来自已过release_date的空值→All、All与Invoices：原ABI没传日期，现有类型政策无法区分它们与仍活跃的冻结状态。effective_manual在三方共同补上人工有效期投影，故均一致。

以上是原task聚焦类型子约束之外的接口/到期日诊断，不回写旧实验标签，不合并为模型准确率，也不作为新增独立案例或新系统。

## 6. 可用结论与剩余缺口

可用结论：来源含义、受限IR/代码、证据准入与接口状态含义必须分别核对。确定性证据准入不能补齐未传入的到期日含义；同样的人工适配能改善三种方法。该实验支持继续落实来源到接口的语义契约，尚不能证明ECAS独有语义优势。

仍未闭合：真实适配器究竟提供原on_hold还是已含有效期的有效冻结状态；正常和异常持久化路径；多供应商绑定；生产状态认证、新鲜度、缓存、并发与HTTP转发；完整Purchase Order其他校验。没有将这些缺口改写为已观察失败，也没有将stub逻辑通过写成生产通过。

机器可核对证据见同目录 `PROBE_INDEPENDENT_AUDIT.json`；核验脚本 `audit_source_chain_probe.py` 仅用标准库读文件、算哈希、解析AST和对账已保存输出，本次共2623项逐文件/逐行检查通过。
