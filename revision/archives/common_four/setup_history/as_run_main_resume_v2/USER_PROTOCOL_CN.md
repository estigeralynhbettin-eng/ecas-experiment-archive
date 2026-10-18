# 统一任务与修复流程协议

## 输入与目标
三方法使用同一 packet、组织schema、中立ABI与TARGET_OBJECTIVE；公开来源不删选成功证据，保留上一轮可追溯的统一压缩变换。TARGET_OBJECTIVE只指定约束对象与范围，不提供最终规则谓词或测试标签。ECAS额外获取原完整输出schema的无信息损失分解表示及全部15操作语义。P2P可对严格类型任务报告范围外。

## 方法和首次输出
P2P：detect→extract→Rego→内部developer tests；AutoPAC：Rego→内部Judge；ECAS：Model IR→确定性编译→证据契约准入。所有首次输出立即冻结。P2P抽取只准精确声明的中立subject/resource对象→id转换，不改条件；保留原抽取与转换凭证。所有Rego保留原文本、OPA fmt派生文本，AST忽略location必须相同；P2P继续完整Regal（仅关闭目录/包名规则），不能用fmt跳过lint。

## 开发与修复
各方法使用同一共同开发请求，P2P自动tests和AutoPAC Judge是其内部流程。首次失败至多一次模型修复，只反馈公开来源、编译/lint、准入、共同developer结果和本方法自身tests/Judge，不给原最终请求标签。ECAS修复仍返回原Model IR schema。最终编译/准入或共同开发不通过则REJECTED/ABSTAIN，无执行资格，不将all-deny算识别成功。AutoPAC修复后不额外Judge，保留其初次Judge以及修复后工具/开发结果。

## 冻结与评价
所有方法候选/修复终态冻结后才由独立评价阶段读取sealed原合法/违规对和原24项branch probes。first-candidate诊断可在dev失败时执行已编译/准入的政策，但显式标为非合格诊断，不能算实际执行资格；修复后主结果仅对合格政策执行。未执行为—。首次、修复后、原pair、业务branch与工程控制分列；合法允许率、违规误放、准入拒绝、弃权、调用数/token/latency/UNKNOWN成本均保持不同意义。

## 资源与解释
GLM5.2 enabled/high，每次input和completion16384，maxcalls44=4smoke+4×(P2P5+AutoPAC3+ECAS2)。这些是相同单次上限和相同一次修复机会，各方法内部步骤与总调用数不同；不称监督或总预算完全相同，不填充无用调用。无自动API重试、temperature provider默认、seed未设置。单轮历史暴露诊断，不称稳定或新系统泛化。证据契约的独立收益由另一离线消融范围验证，不能从本轮方法差异直接推出因果结论。

输入token预估依据旧38次GLM已核对raw/usage的校准，用ceil(UTF8字节/3)+128；同时保留旧bytes/2诊断列。估算不是精确token或硬上界；本轮小试及每次正式调用后必须核提供方真实input/completion≤16384，超界立即停批。公共packet在渲染提示时对所有方法统一移除与common文字完全重复的neutral envelope描述和notice，原packet、路径/类型/authority和来源正文保持冻结。
