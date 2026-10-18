# 同候选源语义Judge内部控制：准备协议

## 目的与资格

对先前四个案例S03、B13、B17、B19的v1/v2八个历史原IR候选，补充一个按公开来源核读语义的Judge控制。它借鉴AutoPAC的语义Judge思路，但候选表示为ECAS typed IR，**不能称为AutoPAC原版、原作性能或Rego效果复现**。

与证据消融引用同一份父候选，不重新生成候选，不做Rego转换，不声称OPA执行语义等价。局部工具层只有原IR shape编译与原Inventory准入；语义Judge是另一个观察层。

## 输入冻结与信息条件

- 每任务一次批量核读两个候选，共最多四次。候选使用A/B标识，四任务交替配置顺序；版本映射只在本地`CANDIDATE_MAPPING.json`，不发Judge。
- 发送新matched_generation的共同packet/TARGET_OBJECTIVE、完整公开visible_sources、全部15项操作语义、两份未经改动的原typedIR及回应schema。
- 不发送hidden requests、开发测试/期望标签、我们已有的正确/错误标签、合同准入或本地编译观察、旧RESULT，也不发送根论文或私人审稿意见。
- Judge分别检查共同目标是否落实、允许/禁止语义方向、额外无依据约束及显式缺失处理。它不修改候选、不生成测试、不联网检索。
- `SOURCE_MANIFEST.json`绑定来源与快照hash，`INPUT_MANIFEST.json`绑定实际脚本、packet、原候选、schema、prompt、原运行时及批准wrapper。密钥文件不登记、不读取、不复制。

## 输出与工程检查

每候选返回slot/id、`ACCEPT|REVISE|ABSTAIN`、目标实现状态、语义方向、无依据额外约束、issues及简短理由；issues引用已公开的证据ID。固定begin/end/stage标记。

ACCEPT要求目标落实、语义方向一致、未发现无据约束且issues为空；REVISE要求至少一条具体问题；ABSTAIN说明公开材料不足。schema或字段一致性失败不作为语义结果。

零API T0检查：输入hash、八份IR shape/合同编译、15项操作覆盖、四份JSONschema工程正例/错误ID反例及公开packet不含测试/反馈字段。工程夹具不形成科学判定，也不发送模型。

## 模型预算及根任务独占派发

计划模型`glm-5.2`，thinking enabled，reasoning_effort high；每次input/output分别不超过16384 tokens，共最多4次，无自动重试。提示长度先用历史校准的UTF8_BYTES_DIV_3_PLUS_128估算，**估算不是硬界限**；第一条最长任务兼作真实schema/token小试，失败停止其余派发，provider实际usage还须满足上下限。

准备本身零模型调用。仅root可按以下条件启动：

1. 主matched_generation的`EXECUTION_STATE.json`为COMPLETED，主managed run为SUCCEEDED。
2. 主CALL_LEDGER实际记录数+4不超过共享44次尝试上限。所有STARTED/失败尝试均消费一次，不能借Judge开新预算。
3. root另写`ROOT_DISPATCH_APPROVAL.json`，绑定最终主ledger SHA256，明确当前任务授权、精确模型/推理/次数/总预算；先向用户统一说明。
4. 每条派发前再次核对主ledger冻结hash及主+Judge ledger计数；Judge最多4条，无未解决/失败历史尝试。
5. 仅通过全局批准`invoke_glm_api.ps1`，直接落盘raw及wrapper summary/content，核对raw hash、model、finish、sentinel、schema与usage；任何失败停止，不自动重试。

### 恢复运行身份绑定（准备v2，2026-10-15）

主实验原`matched-generation-run-v1`的失败状态保留。Judge不再把这个固定run视为唯一成功条件；root审批必须填写实际成功运行的request路径及hash、run_id、run目录、实际status/receipt hash，以及最终主EXECUTION_STATE/CALL_LEDGER hash。Judge核对项目请求与runner实际启动请求相同、真实status为SUCCEEDED且exit=0、执行状态为COMPLETED、主ledger各尝试均已完成。每次派发前再核这些绑定；不允许用审批文字把FAILED运行说成成功。

准备v1快照保存在`setup_history/preparation_v1/`。v2仅修正派发身份接口和零调用工程检查，四份提示、八个候选、公共来源及判断schema保持原hash；不新增模型调用。主流程小试等所有实际尝试都包含在主CALL_LEDGER中，主+Judge共享44上限，不因为恢复、缓存或新目录重置预算。

`RUN_REQUEST_PENDING_ROOT_APPROVAL.json`只是请求文件；缺root独立审批时`run`在网络前拒绝。root可将审批文件及其hash加入最终runner request，不修改已经冻结的输入。

## 解读边界

这批任务和候选已暴露，是事后机制比较；一次判断不构成稳定错误率或推广性结论。Judge的输出仍需与原来源、IR及实际原候选结果对账，不能以Judge自报替代科学正确性。合同本身假定预结构且可信；本轮不要求Judge审查人为破坏Inventory的假来源变体。

本轮不新增人工计时，不改旧消融as-run、论文、投稿状态或根科学账本。结果只在本目录登记。
