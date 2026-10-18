# Judge控制准备v2：根任务派发入口

状态：**PREPARED_NOT_DISPATCHED**。本次准备、修正、T0、QA均零外部模型调用；尚无Judge语义结果。

## 已核验

- 原代码固定要求`matched-generation-run-v1`成功；已改为root审批显式选择实际成功run，支持之后任何经过核验的恢复run。
- 必须绑定主request路径及hash、run_id/目录、实际status/receipt hash和最终EXECUTION_STATE/CALL_LEDGER hash。派发前逐条重核；实际启动请求须与所选项目请求内容一致，实际状态须为SUCCEEDED且exit=0。
- 原v1准备文件已保存在`setup_history/preparation_v1/`。四个prompt、八份父候选、公开来源、操作语义和回应schema保持原hash。
- `typed-ir-judge-t0-v2`实际managed状态SUCCEEDED，exit=0；28项T0检查通过。其中新增的恢复身份正反例属于工程夹具，不是方法效果结果。
- `PREPARATION_QA.json`为PASS，90项输入/来源/交付检查通过；实际T0回执副本在`t0_run_receipts_v2/`。
- 当前无`CALL_LEDGER.json`、无`ROOT_DISPATCH_APPROVAL.json`。审批模板始终authorized=false。

## 根任务实际派发步骤

1. 等主实验真正完成，核对最终EXECUTION_STATE为COMPLETED、最终managed run实际SUCCEEDED、原始调用账本与交付原件一致。失败旧run保留，不改其状态。
2. 从`ROOT_DISPATCH_APPROVAL_TEMPLATE.json`另建`ROOT_DISPATCH_APPROVAL.json`。填写真实成功request/run各项绑定及最终hash、当前用户授权引用；由root设置authorized=true。
3. 共享调用数按**主CALL_LEDGER全部已尝试条目 + Judge全部已尝试条目**计算，包含主小试、失败与缓存来源。四条Judge须整体放得下44总上限；原主输出精确缓存复用不产生新调用，也不清除已有消耗。
4. 复制`RUN_REQUEST_PENDING_ROOT_APPROVAL.json`为最终`RUN_REQUEST.json`，追加实际审批文件和SHA256到inputs。建议同时把已审批主request、主state/ledger、managed status/receipt及SHA256加入inputs，形成runner级绑定。输入已冻结，不改四份提示或候选。
5. 在实际WSL通道以`judge_control.root_gate()`做本地只读最终核对（该函数不调用模型）；当前阶段因无root审批应拒绝。
6. 先validate最终请求，确认成功后仅start一次，之后只等待该run。预计Judge run_id为`typed-ir-judge-control-v2`，不使用旧v1请求派发。

执行入口：`D:\lunwen\tools\wsl-experiment-runner\Invoke-WslExperiment.ps1`。

主恢复run尚未成功时，不填写最终主hash，不启动Judge。此文档不签root授权，也不代表正式实验门禁放行。

## 解释限制

这是借鉴AutoPAC Judge思想的typed-IR源语义内部控制，没有原作微调生成器、Rego转换或OPA等价性验证，不能称AutoPAC原版性能复现。四个任务、八个已暴露父候选，不构成独立盲测或普适性证明。没有人工计时。
