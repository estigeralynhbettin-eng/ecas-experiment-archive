# 缺可信状态与证据准入：静态归因核验

## Material Passport

- 日期：2026-10-15。
- 模式：`academic-research-suite / experiment-agent / validate + plan`。
- 权限：只读核对既有原件；本文件与配套JSON为新派生记录。没有调用模型，没有运行新政策或修改旧原件。
- 初始状态：`STATIC_AUDIT_COMPLETED_RUNTIME_COUNTERFACTUALS_PENDING`。正文保留运行前的代码推导措辞；后续实际确认见末节。
- 研究对象：既有两个项目中的B17、B19政策及B06历史反例。不是新独立案例，也不把工程探针当真实攻击。

## 一、核心判断

这块值得继续推进，但应把两个问题分开验证：**注册证据是否满足执行准入条件**，以及**已准入政策如何处理运行时状态缺失**。当前B17/B19表中的请求拒绝，直接来源于生成候选的条件和缺值参数；它们尚不能证明“只有证据契约才能得到这种拒绝”。

静态代码没有发现完整契约对`bounded_guard_dnf`强制`on_missing=deny`。IR schema允许`deny`和`skip`。因此，仅把原候选的这一参数改为`skip`，预计仍能通过完整准入，在所有替代条件都没有满足且存在缺值时允许请求。该预计不得在实际运行前写成已完成实验结果。

## 二、现有观察的具体来源

| 观察 | 原候选/代码 | 当前可确认的归因 |
|---|---|---|
| B17 `trusted={}`，ECAS拒绝、两同行允许 | ECAS要求`customerDisabled == false`且`on_missing=deny`；同行以`not input.trusted.customerDisabled`允许 | ECAS执行器返回`required_input_missing`；同行对未定义值的否定成立。差异是本轮生成条件和缺值语义 |
| B19 `trusted={}`，ECAS拒绝、两同行允许 | ECAS允许`(supplierOnHold == false) OR (holdType == "Payments")`且`on_missing=deny`；同行允许`not blocked` | ECAS两个替代条件均未满足且存在缺值；同行blocked不可证即允许 |
| B19已冻结且`holdType=""/"Unknown"`，ECAS拒绝、两同行允许 | ECAS只有Payments或未冻结的允许分支；同行只禁止All/Invoices | 正向允许集合与负向禁止集合的差异。此时值存在，拒绝码为`bounded_guard_rejected`，不是缺证据错误 |
| B17/B19客户端body伪造状态，三种方法均拒绝 | 三种候选均读`trusted`路径，不读body伪造字段 | 该探针没有显示ECAS独占优势 |

### 不能遗漏的边界

B19求值器先检查是否有任一替代条件全真，有则立即允许；`on_missing`只在没有真替代条件时生效。因此静态预计：

1. `trusted={"holdType":"Payments"}`：即使`supplierOnHold`缺失，当前ECAS仍允许。
2. `trusted={"supplierOnHold":false}`：即使`holdType`缺失，当前ECAS仍允许；未冻结时类型可能确实无需使用。

第一项可以用于检查“是否必须知道供应商冻结状态”的工程契约，第二项应保留为避免过度拒绝的控制。没有新明确的运行契约前，不把这两项直接标成有来源支持的业务错误。当前已有表格只测了全部可信状态为空，应准确写成“B19可信状态对象为空”，不能外推为“任何可信字段缺失都拒绝”。

## 三、完整证据准入实际强制了什么

`compile_policy`检查目标、已登记证据ID、可见性、supports关系、系统/版本/操作、原语许可、路径绑定、必需binding fact及命名校验器上下文。对`bounded_guard_dnf`，没有额外检查每个比较方向/常量、`on_missing`是否正确或所有运行字段是否存在。

`evaluate`中的`fail_closed=true`是固定输出字段；它不能单独证明所有缺状态请求都被拒绝。实际请求决策要看`violations`、`engine_error`和候选条件。后续报告应同时保留准入状态、执行状态、决策及拒绝码；准入拒绝不计作一次正确业务deny。

主比较使用的引擎V2/V3、IR V3 schema、政策V3 schema，与本次读取的证据消融Windows副本SHA256均相同。核对记录见配套JSON。

## 四、同行已经可以实现缺值拒绝的历史反例

B06 P2P已生成：

```rego
default allow := false
allow if {
    input.trusted.reAgeIsLatestTransaction == true
}
```

其既有开发测试`p2p_test_reversal_latest_missing`实际返回deny。不能概括为“P2P缺可信状态时只能允许”或“缺状态拒绝是ECAS独有功能”。应研究的是，ECAS能否通过固定准入与受限执行更系统地阻止失效，而不是某个语言是否能写出缺值拒绝。

## 五、建议最窄零API对照

在新scope，保留全部原件；使用相同执行器与OPA，先T0再实际复演，不重新生成候选。

### A. 隔离证据契约与执行语义

1. B17/B19原IR：完整准入与shape-only编译，逐字相同政策运行相同历史原请求对和分支。预计已注册合格候选的决策完全相同。
2. 每例仅改`rules[0].params.on_missing`为`skip`：完整准入与shape-only编译；保存逐字段diff，其他字段完全相同。重点观察`trusted={}`；预计完整准入仍通过而缺状态被允许。
3. B19原IR及skip变体增加上述两个partial-missing探针。报告应把“新工程要求的预期”与“已有来源明确约束”分列。

### B. 最小确定性同行控制

两同行原政策不改，另存`+CONTEXT_GUARD`版本。不能把加人工guard后的版本称为原生成基线，不能加回原七案例的模型生成成绩。

- B17：在原allow体追加`input.trusted.customerDisabled == false`。这一条同时约束存在、布尔类型和值；预计拒绝原missing探针且保留原合法/违规结果。
- B19：原allow再与下列guard合取：未冻结`== false`，或冻结`== true`且类型`== "Payments"`。预计拒绝全缺、已冻结空/未知类型，保留原业务请求；对缺冻结状态但Payments也保守拒绝，单独记录与当前ECAS的差异。
- 同时跑原请求对、全部历史分支和partial-missing探针，防止只改善deny而牺牲合法覆盖。
- B06原P2P仅复演原缺状态输入，作为不可唯一性反例。

这组对照回答：表面优势能否由很小的执行保护重现；完整证据准入是否独立贡献该效果。它不会检验自动生成长期稳定性、额外人工成本或原作模型性能。

## 六、精确原件入口

以下均相对`D:/lunwen/EC-CSI投稿/`：

- 主输入根：`working/exploration/20261014_matched_evidence_labor/matched_generation/`（下称M）。
- M `method_runs/FSV-B17/ECAS_MATCHED/first_candidate.json`：`rules[0].params.alternatives[0].clauses[0]`及`on_missing`。
- M `method_runs/FSV-B19/ECAS_MATCHED/first_candidate.json`：`rules[0].params.alternatives[0..1]`及`on_missing`。
- M `method_runs/{FSV-B17,FSV-B19}/{ECAS_MATCHED,P2P_STYLE,AUTOPAC_STYLE}/RESULT.json`：`final_evaluation.branches`，包括输入、期待、实际值与分类。
- M `method_runs/{FSV-B17,FSV-B19}/{P2P_STYLE,AUTOPAC_STYLE}/initial/external_pilot/policy.rego`：原Rego。
- M `execution_inputs/{FSV-B17,FSV-B19}/contract.json`：注册路径与binding facts。
- M `EXECUTION_INPUT_MANIFEST.json`：冻结引擎/schema原件hash。
- `working/exploration/20261014_matched_evidence_labor/evidence_ablation/evidence_files/runtime/scripts/ec_field_security_engine_v2.py:273`：完整准入；330：shape-only；343：IR编译；527：求值入口。
- 同目录`ec_field_security_engine_v3.py:147`：DNF求值；153先接受真分支；155仅其余情况处理skip。
- `working/exploration/20261014_matched_evidence_labor/evidence_ablation/evidence_files/runtime/EC_FIELD_SECURITY_MODEL_IR_SCHEMA_V3.json:1019`：DNF参数允许deny、skip。
- `working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/P2P_STYLE/formatted/validated/external_pilot/policy.rego`：B06原正向允许规则。
- 同B06方法目录`RESULT.json:134`：既有缺状态开发测试实际deny。

## 七、可以推进的研究主张

应推进“生成政策在证据绑定失效、可信状态缺失与未定义值下的准入和执行保障”。目前能够支持的是确定性注册绑定准入，以及本轮候选在具体探针上的保守处理差异。是否能形成ECAS相较同行的独特机制增量，取决于上述反事实及加guard对照；不能由现有三个deny格子直接推出。

## 八、后续实际运行与独立对账

root在独立WSL lane完成`missing-state-mechanism-v1`，实际`SUCCEEDED/exit0`，144行观察，0模型调用。独立核验读取全部既有结果、OPA原始输出、输入、政策、manifest与原件快照，2191项检查通过，没有再次执行政策。记录：`MECHANISM_INDEPENDENT_AUDIT.json`。

- 原IR与只改skip的IR各自比较full/shape，在全部18输入上的政策与实际输出完全相同。
- 仅改`on_missing=skip`的两个候选均通过full准入，且在`trusted={}`时允许；静态归因得到实际确认。
- 两同行各加独立人工typed guard后，关闭B17全缺、B19全缺/空类型/未知类型四种已观察允许，并保留原业务请求和正常已知状态的行为。它们是人为工程控制，不能回填模型生成成绩。
- B19当前ECAS确实允许“仅Payments、缺supplierOnHold”和“仅supplierOnHold=false、缺holdType”两个输入。二者没有新设业务gold；不能把允许自动称为漏洞。
- 144行是两个旧任务、相关请求与配置臂的观察，不是144独立案例。该结果否定了从现有缺值deny直接推出ECAS独有性的解释；不否定独立证据注册与路径绑定准入的实测作用。
