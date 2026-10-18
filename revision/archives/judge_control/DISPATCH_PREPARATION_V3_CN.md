# Judge控制准备v3：真实小试暂停与精确复用

状态：**PREPARED_NOT_DISPATCHED**。准备阶段仍为零模型调用，尚无Judge语义结果。主实验是否完成以root另行核对的实际回执为准。

## 当前冻结与工程验收

- 实际`typed-ir-judge-t0-v3`为SUCCEEDED、exit=0，35项T0检查通过。
- `PREPARATION_QA.json`为PASS，95项来源/输入/交付检查通过。
- 四份prompt、八份父候选、公共输入和回应schema保持准备v2的原hash；schema除字面ID外结构一致，见`PILOT_COVERAGE_QA.json`。
- `EXPERIMENT_SCOPE.json`引用当前`PROTOCOL_CN.md`及其hash；`T0_EVIDENCE.json`绑定实际T0；`RESULT_TRACEABILITY.csv`只有1条工程T0观察，`CLAIM_EVIDENCE_MATRIX.csv`只有规范表头，没有科学claim。
- 准备v2已保存在`setup_history/preparation_v2/`，原v1失败历史不改。未修改根T0指针，未签root授权。

## root派发第一阶段：1条原计划调用

1. 实际scope gate通过、主实验真完成后，由root填写`ROOT_DISPATCH_APPROVAL_TEMPLATE.json`中的真实成功request/run/status/receipt/state/ledger绑定，另存`ROOT_DISPATCH_APPROVAL.json`并设置authorized=true。
2. 从`PILOT_REQUEST_PENDING_ROOT_APPROVAL.json`建立最终`PILOT_REQUEST.json`，把实际审批文件及hash加入inputs。validate成功后start一次。
3. `typed-ir-judge-pilot-v1`只执行CALL_PLAN[0]即B19，落盘实际raw、parsed、usage及唯一调用账本。它消耗原定四条中的第1条，不是额外smoke调用。
4. 成功回执状态为`COMPLETED_PENDING_REAL_TOKEN_GATE`，并生成`PILOT_RECORDS.json`、`PILOT_CALL_LEDGER.json`、`PILOT_COMPLETED.json`。此时不派发另外三条。

## root真实MCP token门禁

使用`PILOT_RECORDS.json`的唯一一条观察调用真实`evaluate_llm_token_smoke`，设置`required_coverage=["longest_typed_ir_judge_input"]`、`max_retry_rate=0`。不复制同一次响应冒充多条观察。

真实plan回执已在`TOKEN_SMOKE_PLAN_ACTUAL.json`，p95/p99/max均对应B19。统一schema结构、2候选、fragile case与dataset映射见`PILOT_COVERAGE_MAP.json`。provider实测token必须满足每条input/completion均≤16384。

将真实工具返回保存到`TOKEN_GATE_RECEIPT.json`，按`TOKEN_GATE_READY_TEMPLATE.json`另存`TOKEN_GATE_READY.json`。填写status=pass、allow_formal_run=true、dispatch_owner=root，以及实际PILOT_RECORDS、PILOT_CALL_LEDGER和MCP receipt的SHA256。真实receipt必须是`evaluate_llm_token_smoke`、pass、预算16384、calls=1，无失败/重试/缺覆盖。

## root派发第二阶段：缓存1条、新调3条

1. 从`RUN_REQUEST_PENDING_ROOT_APPROVAL.json`建立最终`RUN_REQUEST.json`；将实际审批、TOKEN_GATE_READY/RECEIPT、PILOT_RECORDS、PILOT_CALL_LEDGER及hash加入inputs。
2. validate成功后仅start一次`typed-ir-judge-control-v3`。入口先核真实token门禁和首条缓存身份，随后精确复用B19，只新调另外3条。
3. run结果的`model_calls=4`表示整个Judge块已有4条调用；新派发数量由pilot后账本差值计算为3。最终总消耗按主CALL_LEDGER+Judge CALL_LEDGER的全部尝试计数，不按run个数重复统计。

任何gate缺失、失败、hash漂移或未解决尝试均在新增模型调用前阻断。Judge总计划仍4，主+Judge共享44；root核得主30条时，全部完成应共34条。失败不自动付费重试。

这是借鉴AutoPAC Judge思想的typed-IR源语义内部控制；不称AutoPAC原版性能复现、真实网关转发或普适性证明，没有人工计时。
