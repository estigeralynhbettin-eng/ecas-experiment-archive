# Experiment Results

## 七案例语义形成阶段的事后核读（2026-10-15，完成）

Status: POSTHOC_QUALITATIVE_SOURCE_RECONCILED / ZERO_NEW_MODEL_CALLS / ZERO_NEW_POLICY_EXECUTIONS / NOT_SEMANTIC_ACCURACY_BENCHMARK.

- 报告working/exploration/20261015_semantic_comparison/EXPERIMENT_SUMMARY_CN_R3.md及SEMANTIC_COMPARISON_CN.md；21方法行CSV保留所属项目、首次与修复时点和证据路径。162来源哈希及独立363项限定核验通过，核验项不计独立样本。原R2执行状态/符号/项目/批次逐行一致。
- S04 ECAS首次映射基本邮箱validator，AutoPAC经开发反馈补regex，P2P修复仅字符串检查；S02首次白名单差异受原文闭集未闭合限制。S03 AutoPAC识别integer但两次无效OPA函数导致无执行资格，presence仅静态风险；P2P范围外不能计语义错。B13/B17/B19主条件三方首次均形成；B06操作范围仍未闭合。
- B19空类型控制回源发现默认All依据；当前ECAS结果一致、同行allow，但ECAS未显式提取默认值、ABI/生产规范化路径未知。保留原conservative_empty_type_control分类，不作新预冻结语义实验或生产漏洞。
- 本轮不重跑政策，不增加模型调用；R2既有144行机制结果与本轮核读分开。三流程共享GLM适配而非原版同行复现，语义提取/代码资格/准入/运行控制分层，不形成合并准确率。论文、旧原件及根科学账本保持。

## 七案例展示与缺值机制对照（2026-10-15，完成）

Status: OFFLINE_COUNTERFACTUAL_COMPLETED / ZERO_NEW_MODEL_CALLS / TWO_EXPOSED_TASKS / NOT_INDEPENDENT_SAMPLES.

- 当前报告working/exploration/20261015_seven_case_mechanism/EXPERIMENT_SUMMARY_CN_R2.md，详细七表SEVEN_CASE_TABLE_CN.md。七例分A旧三例事后复演/B新四例共同目标，21方法行和原件哈希独立344项检查通过，不能汇总统一准确率。
- 独立lane /root/ecas_missing_state_mechanism_20261015，T0 17项、run missing-state-mechanism-v1实际SUCCEEDED。18相关输入×八臂144行，原件与执行160项、独立2191项静态capture检查通过；新增模型/API0。
- ECAS原/仅skip ×full/shape：两版本均准入，full/shape同输出；只改skip使B17/B19全缺trusted从deny变allow。B19冻结且类型空/未知仍deny，源于允许式DNF。原合法/违规对在全部臂各2/2匹配。
- P2P/AutoPAC原Rego+人工typed状态guard可使被测全缺/空/未知控制deny，保留已测原请求对；原模块不改，不回填为原模型生成结果。B19 partial false-only全部allow；Payments-only原ECAS及原同行allow、guard deny，无预设业务gold。
- 不支持缺值拒绝是ECAS独有或契约强制保证；继续检验证据绑定及可核验运行契约相对加固同行的增量。原稿、旧科学结果和根账本未修改。


## 共同目标与证据机制比较（2026-10-15，完成）

Status: COMPLETED_RECONCILED / ADAPTED_PEERS / SINGLE_EXPOSED_ROUND / NOT_SUBMISSION_FROZEN.

- 总入口working/exploration/20261014_matched_evidence_labor/EXPERIMENT_SUMMARY_CN.md。主run-v3和Judge pilot/run-v3均实际SUCCEEDED；主567项对账、独立412项（168实际复演）、Judge185项对账通过；根科学账本未修改。
- 主四例S03/B13/B17/B19：ECAS4/4首次合格及原请求对正确；P2P/AutoPAC适配均3/4，S03分别OUT_OF_SCOPE、首次is_integer及修复typeof不存在而编译失败。未执行决策None，不能填为成功deny。方法调用4/13/9，含4小试主总30。
- B17缺可信客户状态、B19缺可信供应商状态/空或未知冻结类型，两同行适配allow、当前ECAS deny；与原业务请求分列，属于额外工程/保守控制，不是新独立样本或真实攻击。
- 证据消融7旧例11父候选、95行（73机制/22schema控制）；4类Inventory失效各11与7路径替换被full拒绝，无契约可编译。locator/hash扰动11仍准入，3语义错仍准入，清单真实性/语义保证不由该实现提供。
- 相同四例v1/v2共8历史IR：full8准入、shape8可编译；typed IR按源Judge5 ACCEPT/3 REVISE，三主语义缺陷被指出，B19 skip附加断言依据不足。是AutoPAC Judge思想的内部控制，不是原作性能复现；Judge ACCEPT不是gold。
- 全轮34实际调用≤44，input152100/completion52326（含推理），费用UNKNOWN；不测人时，不声称稳定排名/普适性/原版成本。报告各方法首次/修复后、执行资格与工程控制分列；旧结果及原稿保持。


Updated: 2026-10-14 (Asia/Shanghai)

## 四例同行基线共同模型比较（2026-10-14，完成）

Status: FOUR_CASE_ADAPTED_PEER_COMPARISON_COMPLETED / CONFIGURATIONS_SEPARATE / NATIVE_NOT_RUN / NOT_SUBMISSION_FROZEN.

- 范围S03/B13/B17/B19，原Fineract/ERPNext。GLM5.2 enabled/high共38次：小试4、方法/配置34（开发修复5、ECAS原语说明配置生成4）；实际input176755/completion79327。单次≤16384输入/完成，≤40总调用，金额UNKNOWN，无API失败重试。
- 原请求对：P2P S03范围外，三业务例格式/标识恢复后allow/deny；AutoPAC四例allow/deny。ECAS v1 S03/B13allow/deny、B17deny/deny、B19deny/allow；ECAS v2 S03allow/allow，其余三例allow/deny。不能两ECAS配置逐例择优。
- 扩展探针最新配置共68项（P2P20、AutoPAC24、ECAS v2 24）。AutoPAC S03非整数小数漏放；ECAS v2 S03字符串/布尔/小数漏放。B19 P2P空/未知类型及缺可信状态允许，AutoPAC仅缺可信状态允许，ECAS v2拒绝这三工程控制；ECAS v1 B19因on_missing=skip缺状态允许，v1 B17状态缺失也允许，另有24项v1诊断。绑定候选解释，不称ECAS始终失败闭合，不汇总混合探针作总体准确率。
- 首批输入仅有原语结构，缺ECAS运行语义说明；补全全15操作后四例统一重生成，原失败保留。P2P B13 subject/resource精确中立对象→id转换不改条件；B17/B19 OPA fmt恢复前后AST除location等价。原批次及原接口/格式拒绝未改写。
- 36项来源变换核验、107项raw/生成候选/政策/请求复演、独立PowerShell179唯一冻结文件/38raw/12行对账PASS。五个WSL managed run已SUCCEEDED。Git缺commit警告保留，哈希冻结；模型随机种子未设。
- 结果目录working/exploration/20261014_four_case_peer_baselines/，入口RESULTS_CN.md、COMPARISON_SUMMARY.json、COMPARISON.csv、FINAL_RECONCILIATION.json、DELIVERY_QA.json；本scope追溯表独立，未修改根账本/论文/投稿。本轮不支持四例独占优势或普适性。

## 四例归档筛选与分支核验（2026-10-14）

Status: RETROSPECTIVE_SCREEN_COMPLETED / FAILURE_ROWS_RETAINED / ENGINEERING_ONLY / EXTERNAL_COMPARISON_NOT_RUN.

- 范围S03/B13/B17/B19，原Fineract/ERPNext。12个归档候选经冻结V3引擎：9个准入并执行18条原请求，2个原弃权，1个缺binding fact的准入拒绝；7个请求对全对、2个全错。不能把该事后筛选数写成整体准确率。
- 历史GPT四例8条原请求符合原标签；额外24项分支/缺可信状态/客户端伪装工程探针符合本轮预存预期。9项删来源控制均拒绝准入；未额外执行其请求。新增独立科学样本0、新模型调用0。
- 原主试验Qwen仅S03完成原请求对；B13缺visible_plain_language_invariant被准入拒绝，B17/B19弃权。DeepSeek B17/B19逻辑反向却通过准入，原合法请求deny、违规请求allow。所有原件与失败保留，未修改候选。
- WSL Ubuntu本地执行，无真实业务服务/GPU/Docker。87份输入原件前后哈希一致，PowerShell对候选内容、逐例输出与分支协议复核PASS；初次JSON键顺序误报审计保留并修正比较器。SUMMARY保留REPLAY_ISSUES，不称所有分支成功。
- 证据目录working/exploration/20261014_multi_case_extension_screen/：REPORT_CN.md、SUMMARY.json、BRANCH_PROBE_PROTOCOL.json、BRANCH_PROBES.json、OUTPUT_RECONCILIATION.json。P2P/AutoPAC四例NOT_RUN；生产绑定、业务时点及独立推广验证待补。未修改论文、原实验或根追溯表。

## 外部基线三例适配实验与接口复演（2026-10-14，完成）

Status: EXTERNAL_ADAPTED_PILOT_COMPLETED / RETROSPECTIVE / NATIVE_NOT_RUN / POSTHOC_BINDING_REPLAY_SEPARATE.

- 范围B06/S02/S04，两个原项目。GLM5.2 enabled/high实际27次，4开发smoke、23方法阶段（含5修复）；input104975、completion66728，单次输入和完成均≤16384，未越过30次总预算，提供方未返回金额。
- 原模型批次9分支及原错误保持；第3次schema问题和第6次状态词本地恢复单列。纯OPA格式修复让B06 P2P完成allow/deny；中立身份别名/资源对象表示的两套事后复演不新增模型或独立样本，业务请求、trusted和政策AST保持。
- 资源对象复演：B06 P2P、AutoPAC、ECAS皆allow/deny；S02 P2P范围外、AutoPAC最终is_integer编译失败、ECASallow/deny；S04 P2Pallow/allow，AutoPAC与ECASallow/deny。不得将编译/接口问题计为方法识别失败或将范围外记为错误deny。
- 单个事后缺状态诊断：删B06 trusted.reAgeIsLatestTransaction，P2Pdeny、ECASdeny、AutoPACallow；不并入准确率。AutoPAC S04原正则匹配合法开发邮箱，原转义错误怀疑已证伪；初次对账的错误诊断预期保留为FINAL_OUTPUT_AUDIT_V1_DIAGNOSTIC_EXPECTATION_FAIL.json。
- 原始文件和105项确定性对账：working/exploration/20261014_external_baseline_pilot/RESULTS_CN.md、CALL_LEDGER.json、FINAL_SUMMARY.json、binding_replay*/SUMMARY.json、FINAL_OUTPUT_AUDIT.json。本轮不修改根追溯表、论文或投稿状态，未形成整体性能排名或全文科学验收。

## 外部基线准备性工具验证（2026-10-14，无效果结果）

Status: PREPARATION_VERIFIED / BASELINE_EFFECT_NOT_RUN / MODEL_CALLS_ZERO.

- P2P/AutoPAC三例原版/拟适配行均NOT_RUN、判定null；共同12输入文件哈希核对一致。未新增科学分母或修改根追溯账本。
- 冻结Windows OPA1.19.0执行人工allow/deny、畸形语法拒绝、禁止builtin拒绝四项均PASS；仅验证判定器。本范围完整T0尚缺，Regal未可用；WSL release下载失败已分类为环境问题。
- 原始日志local_opa_conformance/SUMMARY.json，资格NATIVE_QUALIFICATION.json，输入核验PREPARATION_QA.json；均位于working/exploration/20261014_external_baseline_pilot。中文结论见同目录REPORT_CN.md。当前没有P2P/AutoPAC能否识别的实测结论。

## 三例内部基线回放（2026-10-14，回顾性局部对比）

Status: ARCHIVED_BASELINE_COMPARISON_PASS / NO_NEW_MODEL_CALL / NOT_NEW_SCIENTIFIC_RESULT.

- B06/S02/S04 的 B0/B1/B2 各执行原合法/违规一对，ECAS-P/ECAS 在原 Qwen/GPT/DeepSeek 同一候选上分别执行原请求，共54条，全部与历史决策/错误/原因一致；70份冻结输入前后哈希一致。独立 PowerShell 复核通过。
- 以合法 allow 且违规 deny 的局部请求对判定，B0为0/3，B1为1/3，B2为2/3；三个归档模型配置的 ECAS-P与ECAS均为3/3。B06的B1/B2及S04的B1无政策而全拒绝，不能算识别。事后选例、小请求对不外推总体效果。
- 15项删引用来源探针按方法定义返回；其中ECAS-P允许、完整ECAS拒绝，有政策的B1/B2也因共享语义准入拒绝。此为工程负控，不并入原科学分母。
- 证据：working/exploration/20261013_gateway_case_audit/baseline_comparison/BASELINE_COMPARISON_CN.md、runs/three_cases_v1/SUMMARY.json、INDEPENDENT_BASELINE_QA.json。外部P2P/AutoPAC实测未执行。

## 三例显式证据准入与请求执行（2026-10-14，作者澄清后）

Status: THREE_EXTRA_CASES_DEMONSTRATED / LOCAL_ENGINEERING_REPLAY / NO_NEW_MODEL_CALL.

- 范围是 B01 之外的 B06/S02/S04；本包冻结 V3 引擎、schema、来源、契约、九个历史模型候选与回执和正反请求。WSL Python 3.10.12 / jsonschema 4.26.0 的三例执行退出零：九次显式 compile_policy 准入、十八次允许/拒绝按预期，九次删引用来源拒绝准入并 deny。
- 六十五份输入在运行前后核对哈希；本包使用相对路径，保留单例小试与三例实际输出。入口 working/exploration/20261013_gateway_case_audit/selected_case_demo/README_CN.md；原始汇总 runs/three_cases_v1/SUMMARY.json。
- 沿用归档生成结果，不计为新模型效果或独立样本，不据此宣称生产网关转发与实时可信状态接入通过。

## 2026-10-14 API 网关旧案例离线核验（非科学结果）

Status: RETROSPECTIVE_OFFLINE_REPLAY_PASS / FORMAL_GATE_BLOCKED / NO_NEW_MODEL_CALL.

- GPT 与 DeepSeek 的 B06/B16/B22/S02/S04：20 条已选历史合法/违规请求的 V3 离线重放与原始记录一致；13 条事后设计的工程负控及分支探针按预期。原主试验 Qwen 的 B06/S02/S04 六条另行重放一致；B22 的违规误放保持原始失败，不改写。
- 两份独立输入对账分别核对 64 和 35 个脚本/源/引擎/候选/契约/请求文件哈希，输出检查 33 和 6 项均通过。第一次小试因把规范化 JSON 哈希误作文件哈希而失败，保留原件，修正核验器后通过。
- 这些数字只证明已选旧文件和离线执行的一致性，不是新模型效果、独立测试准确率、正式网关转发或新系统验证。当前 MCP 正式门禁为 block / T0_EVIDENCE_MISSING / experiment_scope=null。完整报告：working/exploration/20261013_gateway_case_audit/REPORT_CN.md。

## Stage 4.1 Pre-Formal Five-Model Qualification

Status: `SUCCESS / 20_OF_20_FULL_PIPELINE_PASS / TOKEN_GATES_PASS / ZERO_MODEL_RETRY / FORMAL_PIPELINE_READY / NON_SCIENTIFIC / REVISION3_UNCHANGED`

- After isolated Qwen/GLM recovery, a new frozen 20-call qualification covered Qwen, GLM, Kimi, DeepSeek and ChatGPT/Codex across Blnk/Bigcapital and Direct/ECAS routes.
- Every provider passed 4/4; all 20 raw responses passed integrity capture and all 20 passed JSON parsing, the common schema, OPA strict compilation, valid-input `ALLOW` and invalid-input `DENY`.
- Token gates passed at Qwen 1024, GLM 16384, Kimi 8192 and DeepSeek 8192; ChatGPT/Codex remained host-managed. No output was truncated or empty and no model call was retried.
- This establishes technical readiness to design and freeze the formal experiment. It is not an ECAS-versus-Direct scientific result or manuscript evidence.


## Stage 4 Historical-Parameter-Aligned Five-Model Smoke

Status: `SUCCESS / 20_OF_20_ATTEMPTED_AND_RAW_CAPTURED / 14_OF_20_FULL_PIPELINE_PASS / NON_SCIENTIFIC / REVISION3_UNCHANGED`

- The frozen 20-call ledger completed with zero wrapper retries: Qwen `qwen3.5:9b` 4/4, GLM `glm-5.2` 4/4, Kimi `kimi-k3` 4/4, DeepSeek `deepseek-v4-pro` 4/4 and ChatGPT/Codex `gpt-5.6-sol` 4/4.
- Full parser/schema/Rego/OPA pipeline outcomes were: Qwen 0/4, GLM 2/4, Kimi 4/4, DeepSeek 4/4 and ChatGPT/Codex 4/4, for 14/20 overall.
- All 20 raw responses passed integrity capture. The six failed outputs comprise five Rego compilation failures (Qwen four, GLM one) and one GLM undefined/invalid OPA decision. They are classified as non-scientific schema/protocol failures.
- The provider-specific Token gate passed at Qwen 1024, GLM 16384, Kimi 8192 and DeepSeek 8192; ChatGPT/Codex used host-managed output. No call was truncated, empty or retried, so the six failures are not MAXTOKEN failures.
- The declared paid-API ceiling was CNY 80. Providers returned token usage but no authoritative monetary-cost field, so actual monetary cost is intentionally recorded as `NOT_PROVIDER_REPORTED` rather than estimated.
- Frozen Revision 3, Stage 2 and Stage 3 artifacts were not modified. This smoke is pipeline evidence only and is not a model ranking, ECAS-versus-Direct comparison or manuscript result.

Authoritative evidence: `working/exploration/20260807_stage4_five_model_smoke/historical_alignment/aligned_rerun/ALIGNED_CLOSEOUT_CN.md`; final audit `ALIGNED_FINAL_AUDIT.json`; final manifest SHA-256 is recorded in `ALIGNED_FINAL_MANIFEST.sha256`.

## Stage 3 No-Result Engineering Acceptance

Status: `SUCCESS / 196_OF_196_PASS / 98_OF_98_REPEAT_PAIRS_IDENTICAL / NON_SCIENTIFIC / REVISION3_UNCHANGED`

- The frozen matrix contained 80 valid and 18 fault human-synthetic base fixtures across 40 blind tasks and two blind routes, each repeated twice.
- All 160 valid executions passed strict schema validation, Rego compilation, OPA evaluation and common-decision normalization.
- All 36 injected-fault executions failed closed across nine fault classes; no invalid output became `ALLOW`, `DENY` or `ABSTAIN`.
- All 98 repeat pairs are byte-identical. Real-label leakage, unresolved mismatches and final-manifest failures are zero.
- The final artifact manifest has 2045 entries and SHA-256 `DE1234431E11BA8CF627D78024092917EB408152A353AB41FCA6F1E20FA3204B`.

Interpretation: the shared parser/compiler/OPA/decision/logging pipeline is ready for a separately gated model smoke. This does not measure ECAS, Direct-Rego or model performance; no model was called.

Authoritative closeout: `working/exploration/20260807_stage3_no_result_engineering_acceptance/STAGE3_CLOSEOUT_CN.md`.

## Stage 2 Task and Dual-Oracle Freeze

Status: `SUCCESS / WP0_TO_WP6_PASS / INDEPENDENT_HUMAN_REVIEW_PASS / NON_SCIENTIFIC / REVISION3_UNCHANGED`

- All 8 systems, 32 business tasks, 8 evidence-deficient controls, 40 evidence packets, 128 business requests and 32 structural controls were frozen without denominator reduction.
- All 32 rule Oracles and 32 deterministic fixed-source execution Oracles were completed; 128/128 request decisions agree and unresolved divergences are zero.
- Generation and Execution leakage are zero. The resealed 1104-entry technical manifest has zero failures and SHA-256 `733AB69D926D9BC41080FAADA93C7A318F9D695758726CA877C167373779BBF9`.
- Independent reviewer `yi lv` completed all ten checks and confirmed the one-file reseal delta. The human-review validator returned `PASS` with zero failures.

Interpretation: Stage 2 successfully freezes reproducible inputs, Oracles and blinded views for later comparison. It is not an ECAS, Direct-Rego or model result; none of those methods was run.

Authoritative closeout: `working/review/20260807_stage2_independent_human_review/STAGE2_FINAL_CLOSEOUT_CN.md`.

## Stage 1 Saleor Recovery

Status: `SUCCESS / STAGE1_4_OF_4_QUALIFIED / NON_SCIENTIFIC / REVISION3_UNCHANGED`

- The exact Saleor 3.23.7 OCI manifest digest was acquired and verified without changing version or image source.
- Both clean-state native T0 repetitions accepted a refund of 50 against a charged amount of 100 and rejected a refund of 500 with `AMOUNT_GREATER_THAN_AVAILABLE`.
- Both normalized native results have SHA-256 `A7865939897140BFCA204EFB2AB3535E4F3F56DD4EB2262CF8780B6C69BB7E33`; the previous GraphQL B3 pair remains `ALLOW / ALLOW / DENY`.
- All four Stage 1 systems are now qualified. The direct skopeo-to-daemon API failure was repaired through Docker archive import and is recorded only as a protocol compatibility event.

Interpretation: the four systems now provide paired native-versus-B3 engineering evidence. ECAS, Direct-Rego and all models remain unrun, so this is still not a method-comparison or superiority result.

Authoritative evidence: `working/exploration/20260806_stage1_four_system_t0_b3/SALEOR_RECOVERY_CLOSEOUT_20260807_CN.md`.

## Historical Stage 1 Four-System T0＋B3 Before Saleor Recovery

Status: `STAGE1_NOT_COMPLETE / 3_OF_4_QUALIFIED / NON_SCIENTIFIC / REVISION3_UNCHANGED`

- TigerBeetle: both runs produced native `CREATED` for the valid transfer and `EXCEEDS_CREDITS` for the semantic-invalid transfer; B3 was `ALLOW / ALLOW / DENY`.
- Lago: both runs produced HTTP 200 for the valid wallet and HTTP 422 with `customer_not_found` for the semantic-invalid wallet; B3 was `ALLOW / ALLOW / DENY`.
- OpenProject: both runs changed status 1→7 with HTTP 200 for admin and returned HTTP 404 to the non-member for the same PATCH; B3 was `ALLOW / ALLOW / DENY`.
- Saleor: GraphQL B3 was `ALLOW / ALLOW / DENY` twice, but native T0 was not run because the exact image acquisition timed out twice. Status is `NOT_QUALIFIED_ENGINEERING`.
- Successful result JSON hashes are identical between each run pair. Stage-owned residual containers, volumes and networks are zero.

Interpretation: three native systems exhibit the predeclared semantic gap against their static B3 contracts. Saleor cannot be included in that paired statement. ECAS and all models were not run, so this is not a method-comparison or superiority result.

Authoritative evidence: `working/exploration/20260806_stage1_four_system_t0_b3/STAGE1_FOUR_SYSTEM_T0_B3_CLOSEOUT_20260806_CN.md`.

## Finance B3 All-Ten Adaptation

Status: `B3_ALL10_ADAPTATION_SUCCESS / NON_SCIENTIFIC_ISOLATED_BASELINE / ECAS_NOT_RUN / REVISION3_UNCHANGED`

The frozen B3 definition was adapted to all ten qualified finance-oriented cases. Each case ran one valid input, one structurally valid semantic-invalid input and one schema-invalid negative control in two isolated repetitions.

- Cases: 10; decision files: 60.
- Accepted: 40; rejected: 20.
- Semantic-invalid inputs: 20/20 accepted by B3; target semantic cases caught: 0/10.
- Schema-invalid controls: 20/20 rejected by B3.
- Cross-repetition byte-identical decision pairs: 30/30.
- Contract authority: 4 HIGH, 5 MEDIUM and 1 LOW.
- Residual B3 containers: 0; Revision 3 PDF and source ZIP hashes unchanged.

Interpretation: the B3 portfolio is operational and reproducible but does not express any of the ten target business rules. This is not an ECAS superiority result because ECAS was not executed.

Authoritative evidence:

- `working/exploration/20260806_finance_b3_all10/FINANCE_B3_ALL10_COMPLETION_20260806_CN.md`
- `working/exploration/20260806_finance_b3_all10/B3_ALL10_RESULT_SUMMARY_20260806.csv`
- `working/exploration/20260806_finance_b3_all10/runs/audit/ALL10_AUDIT.json`

## Finance B3 Three-Case Pilot

Status: `B3_PILOT_PASS / GO_TO_ALL_10_B3_ADAPTATION_ONLY / NON_SCIENTIFIC_ISOLATED_BASELINE / ECAS_NOT_RUN / REVISION3_UNCHANGED`

Under the pre-run frozen protocol, jPOS FT0-B01, LedgerSMB FT0-04 and BTCPay FT0-06 each ran one valid input, one structurally valid semantic-invalid input and one schema-invalid negative control in two independent network-isolated repetitions.

- Decision files: 18.
- Accepted: 12; rejected: 6.
- Semantic-invalid inputs: 6/6 accepted by B3.
- Schema-invalid controls: 6/6 rejected by B3.
- Cross-repetition byte-identical decision pairs: 9/9.
- Residual B3 containers: 0.
- Traceability audit: `PASS`, 15 result rows and 15 claim-boundary rows, P0=0 and P1=0.

Interpretation: the tested pre-execution B3 contract surfaces are operational but do not express the three target business rules. This is not an ECAS superiority result because ECAS was not executed. LedgerSMB uses an explicitly downgraded `observer_ingress / LOW` surface.

Authoritative evidence:

- `working/exploration/20260806_finance_b3_pilot/FINANCE_B3_THREE_CASE_GATE_REPORT_20260806_CN.md`
- `working/exploration/20260806_finance_b3_pilot/B3_PILOT_RESULT_SUMMARY_20260806.csv`
- `working/exploration/20260806_finance_b3_pilot/runs/audit/result_audit.txt`
- `working/exploration/20260806_finance_b3_pilot/FINAL_ARTIFACT_MANIFEST.sha256`

## Finance T0 Ten-Case Qualification

The preceding bounded T0 goal completed at `10/10 QUALIFIED`; details and engineering-failure boundaries remain authoritative in `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_COMPLETION_20260806_CN.md`. T0 and B3 artifacts support no Revision 3 manuscript claim.
