# Latest Outputs

## 七案例与安全失效机制简报R2（2026-10-15，当前入口）

- 展示修订：七案例表和R2已增加“所属项目”列，CSV及重建脚本同步；结果字段未改。旧版及原QA保存在presentation_history/，当前展示差异验收见该scope的PROJECT_COLUMN_UPDATE_RECEIPT.json。

- 类型：七案例展示与本地机制识别；路径D:/lunwen/EC-CSI投稿/working/exploration/20261015_seven_case_mechanism/EXPERIMENT_SUMMARY_CN_R2.md；状态COMPLETED_SOURCE_RECONCILED / NOT_MANUSCRIPT_FREEZE；Last Checked 2026-10-15。R1原件保留。
- 七表SEVEN_CASE_TABLE_CN.md、SEVEN_CASE_COMPARISON.csv、TABLE_SOURCES.json及TABLE_INDEPENDENT_AUDIT.json：21行方法来源、344项独立静态检查通过。B06/S02/S04旧复演与S03/B13/B17/B19新协议分批展示，不合并准确率。
- mechanism_control/RESULTS_CN.md：144相关观察、0新增模型调用，实际run SUCCEEDED；160项原件对账、独立2191项检查通过。skip仍准入/全缺trusted允许；两同行+人工guard可复现被测保守拒绝，原业务对保持；缺值拒绝本身尚非已证实的ECAS独有性。
- 后续应检验契约是否能强制生成候选满足可信输入与失效要求，并以加固同行作强对照。证据清单准入、运行trusted缺值、按源Judge分层，部分缺值不预设违规gold。论文/旧实验/根科学账本/投稿未改。


## 本轮统一任务与证据机制实验简报（2026-10-15，全部完成）

- 类型：中文实验汇总；路径D:/lunwen/EC-CSI投稿/working/exploration/20261014_matched_evidence_labor/EXPERIMENT_SUMMARY_CN.md；状态COMPLETED_SOURCE_RECONCILED / NOT_MANUSCRIPT_FREEZE；Last Checked 2026-10-15。
- 四分支均完成：原作生成方式矩阵、7旧例11候选的证据消融、四例三流程共同目标比较、四例8历史候选的按源Judge控制。主30+Judge4=34模型调用，无付费重试。主原件对账567项、独立412项/168实际复演；Judge185项通过。
- ECAS原请求对4/4；P2P和AutoPAC适配各3/4，S03分别范围外/编译失败。三方法均模型生成；本轮不测人工效率。Inventory绑定与语义核读分层：3个历史语义错契约未拒、Judge指出；Judge另有B19 skip理由依据不足。
- 详细入口matched_generation/results_review_v1/RESULTS_CN.md、human_effort/MODE_FEATURE_MATRIX_CN.md、evidence_ablation/RESULTS_CN.md、judge_control/RESULTS_CN.md。仅两个项目旧任务、单轮适配比较；不能据此证明原版性能/稳定排名/普适性。旧运行中条目由本条取代，不再续跑。


## 共同目标主比较完成（2026-10-15，当前效果入口）

- 路径working/exploration/20261014_matched_evidence_labor/matched_generation/results_review_v1/RESULTS_CN.md；类型：四例共同目标的同行流程适配比较；状态COMPLETED_RECONCILED_INDEPENDENTLY_CHECKED，Last Checked 2026-10-15。主run-v3 SUCCEEDED；567原件核验与独立412检查通过，168独立实际复演一致。
- ECAS四例原合法/违规请求对均正确且无开发修复；P2P与AutoPAC后三例均正确，S03分别范围外和两次编译失败。原业务请求与缺状态等工程控制分列。累计30调用（方法26+小试4）；ECAS方法4、P2P13、AutoPAC9，不是原版性能/总体稳定排名/人工效率测量。
- Judge同候选语义内部控制主30+计划4≤44，pilot最长一条已通过真实token门禁，typed-ir-judge-control-v3正在继续。其结果未完成前不填发现率或语义胜负。旧协议结果、原稿、根科学账本与投稿未改。


## 共同目标比较续跑（2026-10-15，运行中）

- 当前run更新为matched-generation-main-resume-v3，run_dir /root/ecas_matched_generation_20261014/managed_runs/matched-generation-main-resume-v3。v2的OPA注释Location.file元数据误报已通过最窄归一化修复；V3_RESUME_INDEPENDENT_AUDIT.json 70/70、T0 v7 68项和77请求输入哈希通过，15缓存精确复用。v2失败快照保留，不把工程中断计为基线效果失败。

- 类型：已授权实验恢复；路径working/exploration/20261014_matched_evidence_labor/matched_generation/；状态MAIN_RESUME_V2_SUBMITTED，Last Checked 2026-10-15。实际run_id matched-generation-main-resume-v2，run_dir /root/ecas_matched_generation_20261014/managed_runs/matched-generation-main-resume-v2。等待最终12分支，未完成不填效果结果。
- RESUME_INDEPENDENT_AUDIT.json：79/79 PASS；T0 v6 65项PASS；原13条已完成调用精确缓存复用，标题引用在可见原文可定位，无测试业务修改/付费重调。旧失败原件完整保留。
- 已完成入口human_effort/MODE_FEATURE_MATRIX_CN.md、evidence_ablation/RESULTS_CN.md；三方法均模型生成，证据契约对特定Inventory绑定提供准入控制，但不能自动保证来源语义正确。RUN_STATUS.json供后续查询，旧“main-v1运行中”条目已由本条取代。


## 生成方式与证据机制比较（2026-10-14，当前scope）

- 目录D:/lunwen/EC-CSI投稿/working/exploration/20261014_matched_evidence_labor/，TASK_CONTRACT_CN.md绑定当前授权与44次新模型调用上限；用户已取消人工计时，labour只是创建时内部路径名。
- 特征矩阵human_effort/MODE_FEATURE_MATRIX_CN.md：SOURCE_VERIFIED；原作及适配分列，两基线均模型生成。原作微调/标注、规则追溯/证据硬准入/语义检查分别比较；human_effort/FOUR_TASK_TARGET_SCOPE_CN.md为共同目标提议。
- evidence_ablation/RESULTS_CN.md及COMPARISON_SUMMARY.json：LOCAL_SAME_CANDIDATE_ABLATION_COMPLETED；7例11父候选，schema失败/未执行/构造控制分列。输入及逐行输出独立核验无错配；最终Windows交付核验进行中。保留3个语义错候选获准入及Inventory真实性未核读的边界。
- matched_generation/：TOKEN_SMOKE_COMPLETE / MAIN_EFFECT_RUN_SUBMITTED；原smoke失败的外包装问题0API恢复，recovery-v2 SUCCEEDED，4次实际调用token PASS。T0 v5及原语schema恢复64文件独立核验通过；主run matched-generation-run-v1已单次提交，未完成前不补效果圆圈。续接RUN_STATUS.json及CALL_LEDGER.json，禁止重复派发。论文及旧简报不覆盖。

## ECAS与AutoPAC结果诊断（2026-10-14）

- 中文补充：D:/lunwen/EC-CSI投稿/working/exploration/20261014_experiment_review_brief/ECAS_AUTOPAC_DIAGNOSIS_CN.md。类型：既有结果及比较协议的定点科学诊断；状态RAW_AND_CODE_CHECKED / INDEPENDENT_READ_ONLY_REVIEW / NO_NEW_EXPERIMENT / NOT_FULL_MANUSCRIPT_REVIEW。Last Checked：2026-10-14。
- 确认首轮说明缺口、ECAS开发失败仅记录的流程差异、S03目标指定风险、Inventory准入与语义正确性的区分；提出先统一任务/监督再验证机制增量的顺序。两个项目旧例不提供稳定总体优势；四页简报与冻结结果不改写。

## 实验简报与Gemini复核材料（2026-10-14）

- PDF：D:/lunwen/EC-CSI投稿/working/exploration/20261014_experiment_review_brief/ECAS_EXPERIMENT_BRIEF_CN.pdf，4页。类型：已完成实验的独立评估简报；状态DELIVERED / SOURCE_TABLES_VERIFIED / VISUAL_QA_PASS / NOT_EXTERNAL_REVIEW_RESULT。Last Checked：2026-10-14。
- 同目录可编辑ECAS_EXPERIMENT_BRIEF_CN.md、纯文本副本、GEMINI_REVIEW_PROMPT_CN.txt、ECAS_REVIEW_EVIDENCE_EXCERPTS_CN.txt。可转发文件不依赖作者本地路径；SOURCE_MANIFEST.json保留内部原件哈希。
- 覆盖旧候选重放、27次三例比较、38次四例比较。两种ECAS配置、范围外/编译失败、基线成功及ECAS失败完整分列；圆圈由原请求对计算，没有择优拼列或总体准确率。六项复核问题包括基线资格、任务粒度、准入语义、适用性边界、监督差异和最小后续实验。
- 四页视觉核读、34项来源/表格/文本/版式验收PASS，证据摘录附实际策略和关键源条款。本次新增模型/实验0，未调用或发送给Gemini；由作者自行评估转发，论文未改。

## 四例同行基线测试已完成（2026-10-14，当前比较入口）

- 中文报告D:/lunwen/EC-CSI投稿/working/exploration/20261014_four_case_peer_baselines/RESULTS_CN.md。类型：回顾性同行流程适配实测与分配置/格式复演；状态COMPLETED / SOURCE_AND_RAW_RECONCILED / NATIVE_NOT_RUN / NOT_SUBMISSION_FROZEN。Last Checked：2026-10-14。
- 结果COMPARISON_SUMMARY.json、COMPARISON.csv、audit_rows/；原流程effect_runs/，补充format_recovery/、format_replay/、documented_ecas/。38次GLM5.2 high调用；36项输入核验、107项原件/请求重放、PowerShell179冻结文件/38raw/12结果行对账PASS。
- P2P三业务例和AutoPAC四例均通过原请求对；S03 P2P范围外。ECAS v1 B17全拒绝、B19允许/禁止反向，v2 S03漏类型；禁止两配置择优合列。AutoPAC S03额外小数漏放；B19两外部方法及ECAS v1缺状态放行，仅ECAS v2拒绝。v1补充分支在V1_ECAS_DIAGNOSTICS.json，均有实际轨迹。
- 本轮没有获得三四个稳定ECAS独有胜出案例；输入/工具修复与业务差异分列，仍只有两个原项目及暴露样本。下方“运行中”是历史阶段，五个run已终止；论文和投稿未改。

## 四例同行基线测试运行入口（2026-10-14）

- 路径D:/lunwen/EC-CSI投稿/working/exploration/20261014_four_case_peer_baselines/。类型：当前获授权的共同模型适配比较；状态AUTHORIZED / INPUTS_FROZEN / T0_PASS / TOKEN_SMOKE_RUNNING。Last Checked：2026-10-14。
- 范围S03/B13/B17/B19，P2P/AutoPAC/同模型ECAS；GLM5.2 enabled/high、最多40次。协议FROZEN_PROTOCOL_CN.md；输入与代码EXECUTION_INPUT_MANIFEST.json；原调用CALL_LEDGER.json；运行ID与路径见HANDOFF.md。
- 四例效果尚未完成，不以此前历史GPT的成功填入同模型比较。原版复现缺口及真实业务状态/时点边界保留，论文未修改。

## 四例多规则覆盖筛选（2026-10-14）

- 中文入口：D:/lunwen/EC-CSI投稿/working/exploration/20261014_multi_case_extension_screen/REPORT_CN.md。类型：回顾性案例筛选与工程分支核验；状态：SCREEN_COMPLETED_WITH_FAILURES_RETAINED / EXTERNAL_BASELINES_NOT_RUN / NO_NEW_MODEL_CALL。Last Checked：2026-10-14。
- 四例S03/B13/B17/B19来自原Fineract/ERPNext；历史GPT四例原请求对成功，24项额外工程探针通过。原Qwen准入缺口/弃权及DeepSeek两个反向错误并列保留，87份输入原件对账一致。
- 原件、候选、请求、分支协议及结果在cases/、sources/、SUMMARY.json、BRANCH_PROBES.json；确定性验收OUTPUT_RECONCILIATION.json。原SUMMARY状态REPLAY_ISSUES来自Qwen B13准入拒绝，不能抹去。
- 支持注册ABI下多类约束可执行；不支持四个独立机制、跨项目普适性、生产转发或外部基线优势。P2P/AutoPAC四例尚未比较；本轮未改论文或投稿。

## 三例圆圈表与阶段定位（2026-10-14）

- 中文入口：D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/STAGE_COMPARISON_CN.md。类型：作者核读用规则形成/执行轨迹表；状态：SOURCE_RECONCILED / NO_NEW_MODEL_CALL / NOT_MANUSCRIPT_EDIT。Last Checked：2026-10-14。
- ○/◐/●表示目标规则落实程度，范围外、编译失败及测试反馈后的修复另加注；若仅表示最终请求对错，S02未执行分支必须使用—。
- 新核对点：AutoPAC S02首次只检查必需字段存在，开发测试反馈后的修复才加白名单；S04首次无邮箱格式且Judge接受，开发测试反馈后才加正则。ECAS三例首次候选已有目标原语，具体违规由运行时规则执行发现；不从此推断证据契约因果收益。

## 三例外部适配比較已完成（2026-10-14，当前实验入口）

- 类型：共同模型适配实验与工程复演；状态：COMPLETED / RETROSPECTIVE_ADAPTED_PILOT / NOT_NATIVE_PERFORMANCE / NOT_SUBMISSION_FROZEN。Last Checked：2026-10-14。
- 中文结果：D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/RESULTS_CN.md。原生成流程：FINAL_SUMMARY.json、ADAPTED_COMPARISON.csv；事后统一接口：binding_replay_resource_object/SUMMARY.json及binding_replay/SUMMARY.json；完整105项对账FINAL_OUTPUT_AUDIT.json。
- 共27次GLM5.2 high调用，未越过30次上限，费用未知。B06两基线适配版也能判对；S04 P2P只作字符串类型检查而漏格式、AutoPAC对象映射后判对；S02 P2P范围外、AutoPAC编译失败。ECAS同模型三例原请求对均allow/deny。接口故障、纯格式恢复和原失败都单列，不用它们构造原版方法排名。
- 边界待办见SEMANTIC_REVIEW_FINDINGS_CN.md：B06通用撤销操作与Re-Age规则范围、S02封闭字段约定来源、AutoPAC开发测试额外监督。旧准备/运行中条目是历史状态；R14仍为当前稿件，未修改正文。

## 三例外部适配比较运行中（2026-10-14，取代下方待决定状态）

- 状态：AUTHORIZED / T0_PASS / TOKEN_GATE_PASS / EFFECT_RUNNING。Last Checked：2026-10-14。
- 当前目录：D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/；授权AUTHORIZATION_CN.md，协议FROZEN_PROTOCOL_CN.md，调用CALL_LEDGER.json，执行EXECUTION_STATE.json。
- 原第3次开发smoke因提示schema遗漏maxItems=1失败，修正后新提示小试通过；4次开发调用全部保留，总预算仍30。WSL官方runner external-three-case-effects-v2只派发一次，结果未收尾。
- 原P2P/AutoPAC缺代码/权重仍未执行；当前运行的是明确标注的适配比较，不用于原版性能或整体优势主张。下方准备阶段的“配置待用户确定/调用0”已成为历史。

## 三例外部基线准备报告（2026-10-14）

- 类型：实现资格核查与测试协议草案；状态：PREPARATION_VERIFIED / NATIVE_NOT_RUN / ADAPTATION_PENDING_DECISION。Last Checked：2026-10-14。
- 中文入口：D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/REPORT_CN.md；协议、TASK_CONTRACT_CN.md、NATIVE_QUALIFICATION.json、GATE_SNAPSHOT.json、PREPARATION_QA.json及隔离输入在同目录。
- 原版P2P缺可确认代码，AutoPAC缺必需微调权重；共同12份输入哈希一致、OPA四项工程对照通过。外部模型调用0、基线效果结果0；正式范围T0与Regal仍待补。不能将本报告引用为能否识别的实测证据。
- 共同GLM5.2适配方案具体配置待用户确定，AutoPAC生成器替换必须明确说明；历史ECAS结果不直接当同模型公平参照。R14仍是当前稿件，未改稿或投稿。

## 三例基线识别对比（2026-10-14）

- 中文报告：working/exploration/20261013_gateway_case_audit/baseline_comparison/BASELINE_COMPARISON_CN.md。三例属于原两项目，来源记账已完成。
- 已核实 S02 的 B1/B2、S04 的 B2 也能识别；B06 的 B1/B2 无政策而全拒绝。ECAS-P 和 ECAS 的合法/违规判定相同。54 条逐方法历史记录重放一致，不是新增独立测试准确率。
- 对账、政策快照、CSV 和原始 JSON 均在 baseline_comparison；P2P/AutoPAC 未形成这三例的外部实测结果。

## 三例完整策略执行演示（2026-10-14，按作者确认范围完成）

- 阅读入口：working/exploration/20261013_gateway_case_audit/selected_case_demo/README_CN.md；逐例说明：runs/three_cases_v1/INDEX_CN.md。固定 B01 之外的 B06/S02/S04。
- 完整离线包：working/exploration/20261013_gateway_case_audit/ECAS_THREE_EXTRA_CASES_REPLAY_20261014.zip，89 个文件逐份回读一致，缓存文件排除；独立核验见 selected_case_demo/INDEPENDENT_QA.json 与 SELECTED_PACKAGE_CHECK.json。
- 九个归档候选显式准入、十八个正反请求按预期、九个缺来源对照拒绝准入并 deny；本包引擎运行与六十五份输入哈希前后核对完成。原模型生成输出保留，未重新调用模型。
- 本次范围是候选→契约准入→允许/拒绝，已经完成。可用于作者选例和核读，属于回顾性工程演示；论文 R14 未修改。

## API 网关案例夜间核验（2026-10-14，案例选择入口）

- 中文结论与证据链：working/exploration/20261013_gateway_case_audit/REPORT_CN.md；任务契约、离线脚本、原始重放 JSON、输入哈希和独立对账均在同目录。
- 旧 FSV 批次可选 B06（可信状态）、S02（字段白名单），B22 可作复杂逻辑及主试验误放的对照；若需要第三个稳定正例，用 S04（邮箱格式）。这不是新增独立系统样本或生产网关转发结果。
- FSV 批次外优先 Blnk、Saleor，Formance 备选；原生 T0 和静态基线语义缺口已有历史证据，但当前 V3 Model IR、Evidence Contract 与真实网关绑定尚未完成。本次正式门禁为 block / T0_EVIDENCE_MISSING / scope=null，未运行新正式实验或外部模型。
- R14 英文稿及中文阅读版仍为当前稿件入口；此次仅新增案例核验材料，未改稿、投稿或发送。

## R14 中文核读交付（2026-10-13，当前中文入口）

- 中文主稿：`working/paper/retarget/ASE_20261013_MAJOR_REVISION_R14/delivery/ECAS_ASE_R14_MAIN_CN_REVIEW_20261013.pdf`（57页）；同目录有`-pdftotext.txt`、`_SOURCE.zip`及`R14_CHINESE_REVIEW_README_CN.md`。
- 译自当前R14原稿定点返修版，保持章节和原论证逻辑，没有精简；R13压缩稿和旧中文稿未作底稿。正文、表格、图注、声明及两张流程图中文化，参考文献、正式作者机构信息及数值图内部英文标注保留；英文仍为科学主张权威。
- GLM5.2/thinking disabled/17次计划调用已结束，0模型重试；第3块首尾标记变形，保留STOPPED并用已有raw本地重解析，状态RECOVERED_LOCAL_VALIDATION。111条本地校正、前后半篇独立修正闭合及17块结构数字一致性完成；7项英文来源快照保持。
- XeLaTeX编译57页，全部页面与两张流程图已视觉核读；最终只补译关键词模板标签并重编译、核对首页。保留6条横向output宽度警告，未见可见裁切、缺字或重叠。源包按依赖白名单生成并回读一致；没有另作解包后的独立重编译。
- 状态：`R14_CHINESE_AUTHOR_REVIEW_DELIVERED / NO_SHORTENING / ENGLISH_AUTHORITY_PRESERVED / NOT_SUBMISSION_FROZEN`。范围为翻译核读交付，不代表科学有效性、复现或逐条回复正式闭环；没有新增实验、外部模型评审、发送、发布或投稿。
- 下一步：作者阅读中文稿、批注并手工精简；原R14比较、完整复现和正式返修待办继续保留。具体原文→新文改动见R14中文修改说明及逐句对照。


## R14 原稿定点返修交付（2026-10-13，当前核读入口）

- 用户已否定R13压缩稿；R14从已提交R12复制，保留摘要句序、章节及原论证，只加入审稿意见所需定义、贯穿案例、释义、复现入口和定点修正。停止代理精简，篇幅由作者手工处理。
- 目录：`working/paper/retarget/ASE_20261013_MAJOR_REVISION_R14`。清稿：`delivery/ECAS_ASE_R14_REVIEWER_AMENDMENTS_20261013.pdf`（55页）；中文说明：`delivery/R14_REVISION_REPORT_CN.md`；逐句对照：`delivery/R14_CHANGE_REVIEW_CN.html`；可编辑源包：`delivery/ECAS_ASE_R14_DRAFT_SOURCE_20261013.zip`。
- 62条修改有完整台账，独立复核四文件可逆恢复R12；原表体、算法、书目及原图3–6保持。主稿编译与55页视觉核对完成；横向页模板警告经过可见内容检查，不称零警告或科学冻结。
- 33项矩阵和英文内部回复在delivery：20项定点修改已核对、10项部分、3项作者手工处理，0项宣称正式闭环。外部P2P/AutoPAC实测、完整复现、全文英语和正式化/全文缩短仍待完成。
- 状态：`R14_R12_BASED_LOCAL_AMENDMENTS / AUTHOR_REVIEW_DRAFT / SHORTENING_BY_AUTHOR / EXTERNAL_COMPARISON_PENDING / NOT_SUBMISSION_FROZEN`。
- R13是保留的、被作者否定的压缩尝试；不作当前正文/翻译底稿。R12、Revision 3、原实验和ESM_1.zip保持。没有新增外部模型、付费调用、正式实验、发送、发布或投稿。
- 下一步：作者按原文→新文逐处核读并手工精简；再明确外部比较/完整复现实验范围，取得具体授权后补齐证据与正式回复。普通核读不扩大实验授权。


## 历史：R13 中文核读版（2026-10-13，底稿已被作者否定）

- 路径：`D:/lunwen/EC-CSI投稿/working/paper/retarget/ASE_20261013_MAJOR_REVISION_R13/delivery/ECAS_ASE_R13_MAIN_CN_REVIEW_20261013.pdf`，正文18页、共24页，含声明及保留英文的参考文献；同名-pdftotext.txt和_SOURCE.zip。
- 来源：当前21页英文R13主稿（正文17页），英文文件与原实验均保持不变；英文仍为论文科学主张权威版本。
- 状态：中文author-review阅读版已交付；GLM5.2/thinking disabled/9次/零重试，独立21项问题已校正，结构数字9/9一致，24页视觉核读。宋体粗斜体回退已目视核对。
- 说明：`delivery/R13_CHINESE_REVIEW_README_CN.md`；复现/外部实测/正式返修冻结状态未改变。Last Checked:2026-10-13。

## 历史：R13大修压缩稿（2026-10-13，已被作者否定）

- 类型：英文论文修订稿、独立补充文档、逐条回复草稿与审稿定位矩阵。
- 标题：ECAS R13 major-revision author-review draft。
- 路径：`D:/lunwen/EC-CSI投稿/working/paper/retarget/ASE_20261013_MAJOR_REVISION_R13/delivery/`。
- 主稿：`ECAS_ASE_R13_MAIN_20261013.pdf`，21总页，标题摘要至结论17页；补充：`ECAS_ASE_R13_SUPPLEMENT_20261013.pdf`，15页。两份均有-pdftotext.txt。
- 源包：`ECAS_ASE_R13_DRAFT_SOURCES_20261013.zip`；中文报告：`R13_REVISION_REPORT_CN.md/txt`；33项矩阵：`REVIEWER_RESPONSE_MATRIX_CN.md/CSV`；英文草稿：`RESPONSE_TO_REVIEWERS_DRAFT.md`。
- 状态：author-review draft；结构、文字和版面修订已完成，外部实测与完整复现仍待证据，未冻结或提交。下方“没有创建返修稿”属于本轮扩展授权前的历史记录。
- Last Checked：2026-10-13；最终两PDF可读，关键数字定点对账，冻结输入24条一致。具体边界见报告和矩阵，技术QA不是全文科学PASS。

## 历史：审稿意见讨论接续（2026-10-13，改稿授权前）

- 当前入口：`D:\lunwen\EC-CSI投稿\HANDOFF.md` 顶部 `ECAS-REVIEW-HANDOFF-20261013-01`。
- 实验组织与外部基线定点判断：`working/review/20261013_ASE_MAJOR_REVISION/EXPERIMENT_AND_BASELINE_ADVICE_20261013_CN.md`。核对原主试验收益门失败与 GPT 契约旁路/完整方法的真实增量；属于作者讨论建议，未启动实验或改稿。
- 同刊长度参照：`working/literature/ASE_LENGTH_SAMPLE_20261013/REPORT_CN.md`、`length_audit.csv`、`summary.json` 及 `pdfs/`。20篇正式原始研究（16复用、4新下；20唯一 DOI/哈希）全文均值36.05页、中位35.5页，范围13–52页；References前完整页均值32.30页，此口径含部分附录/声明。R12 为44页、References前37完整页。样本有主题便利/OA偏差，不代表全刊均值或官方篇幅门限；根任务独立重算统计并核对20文件哈希。
- 状态：已读取用户粘贴的编辑决定、Reviewer 1–3 和修回说明；正式决定 `MAJOR_REVISION`，建议修回日期 2026-11-27。邮件通知日期、可能附件和门户硬截止设置仍待核实。
- 原始意见及初步判断：`working/review/20261013_ASE_MAJOR_REVISION/EDITOR_AND_REVIEWERS_USER_PASTED_20261013.txt`、`REVIEW_JUDGMENT_20261013_CN.md`。报告含意见工作编号及尚未实施的处理建议；不是返修闭环或全文科学验收。
- 稿件基准仍为已提交的 ASE R12；没有创建返修稿，也没有修改论文或实验。
- 已归档用户此前的 3 份报告门户截图及 2026-09-22 客服回信：`working/handoff/ECAS_REVIEW_HANDOFF_20261013/`。原图实际内容为进度证据，不是正式审稿意见。
- 下一步：讨论贯穿案例和全文重构方案，核对相关系统比较及复现证据缺口，再由用户决定具体修改范围。下方 2026-09-04 的 `Peer Review / 4_REVIEWERS_ACCEPTED` 为历史快照，已被本次大修通知取代。
- Last Checked: 2026-10-13；本次完成意见判断和 R12 相关段落核对，未作全文数字、科学或引用审计。R12 与 Revision 3 保持冻结。

## Workspace Migration Completed (2026-09-04)

- Canonical physical directory: `D:\lunwen\EC-CSI投稿`.
- Compatibility entry: `C:\Users\PBCDCI\Documents\EC-CSI投稿`, verified as a Junction targeting the canonical directory.
- Recoverable original tree: `C:\Users\PBCDCI\Documents\EC-CSI投稿_pre_migration_20260904`, retained as a physical directory and not authorized for deletion.
- Final verification covered 30,254 files, 3,251 directories and approximately 2.42 GiB: backup-to-target read-only mirror comparison returned 0 copied/mismatch/failed/extras; 29/29 reparse points and 19/19 root/key SHA-256 checks matched; C/D reads of `HANDOFF.md` had the same NTFS File ID.
- Migration authority and idempotent checker: `MIGRATION_REPORT_20260904.md` and `FINALIZE_MIGRATION_TO_D_20260904.ps1`.
- Status: `FINALIZED_AND_VERIFIED / D_CANONICAL / C_JUNCTION / BACKUP_RETAINED`.

## ASE R12 Citation-Format Fix Submission Package (2026-08-12)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R12_20260812/`.
- Upload manuscript: `ECAS_ASE_LATEX_SOURCE_R12_20260812.zip` (13 root-level files); review PDF: `ECAS_ASE_SUBMISSION_R12_20260812.pdf` (44 pages).
- R12 changes only two grouped OWASP citations that R11 rendered as `n.d.b,n,n` on pages 6 and 34. It preserves the same undated references and separates their author--year items; no research content or reference metadata was changed.
- Corrected pages 6 and 34 passed visual review. The flat ZIP independently rebuilt to 44 pages with no undefined citation/reference or fatal error, and the malformed pattern is absent.
- The submitted file set is the R12 LaTeX ZIP, `ESM_1.zip`, and the existing cover-letter PDF; the cover-letter content is unchanged from the verified R10/R11/R12 version.
- The portal-generated R12 PDF is 44 pages and text-identical to the local authority; all 44 pages passed visual review, including the repaired citations on pages 6 and 34. Cheng Wang's duplicated portal affiliation was corrected before submission.
- The author submitted through Springer Nature SNAPP on 2026-08-12. At submission, the tracking page reported `Submission received` and `Technical Check`; submission ID `71cf26a4-ec4f-4d3c-9334-0fa6b772e479`, version `v1.0`.
- The portal-generated submitted PDF is preserved in the delivery directory as `ECAS_ASE_PORTAL_GENERATED_R12_20260812.pdf`.
- As observed on 2026-09-04, the portal remains at `Peer Review`; technical check, editorial assignment, and with-editor stages are complete. The editor has invited more than 10 reviewers, and 4 reviewers have accepted the invitation.
- The acceptance count does not establish that any review report has been returned; the screenshot shows no `reviews received` count or editorial decision.
- Current status evidence: `ECAS_ASE_PORTAL_STATUS_4_REVIEWERS_ACCEPTED_20260904.png`; the earlier `ECAS_ASE_PORTAL_STATUS_PEER_REVIEW_20260820.png` is retained as history.
- Status: `SUBMITTED_TO_ASE / PEER_REVIEW / 4_REVIEWERS_ACCEPTED`.

## ASE R11 Text-Only Model-Label Submission Package (2026-08-12)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R11_20260812/`.
- English manuscript: `ECAS_ASE_SUBMISSION_R11_20260812.pdf` (44 pages); internal Chinese review: `ECAS_ASE_SUBMISSION_R11_20260812_CN_REVIEW.pdf` (35 pages; not for upload).
- Flat portal LaTeX ZIP: `ECAS_ASE_LATEX_SOURCE_R11_20260812.zip` (13 root-level files; independent ASCII-path extracted rebuild PASS at 44 pages).
- Figure 1 now contains only the plain-text identifiers Qwen, DeepSeek, GLM, Kimi, and OpenAI. The five embedded provider logos were removed; all other Figure 1 content and Figure 2--6 are unchanged.
- The editable two-page draw.io source and deterministic text-only builder are under `FIGURE_SOURCES/`. Figure 1 is 4800×1596 at 600 DPI and passed manuscript-page visual review.
- `ESM_1.zip` and the cover letter are carried forward unchanged from R10. Submission materials no longer retain a logo/trademark authorization gate; the supplementary artifact's own licence/privacy boundary remains an author confirmation item.
- The author reports that the manuscript file in the live portal has been replaced with R11. The correct Data Availability selection is `Yes`, conditional on retaining `ESM_1.zip` as Supplementary Information / Online Resource 1; no external DOI/accession is claimed.
- The portal reports successful LaTeX conversion, and its downloaded 44-page generated PDF is text-identical to the local R11 PDF. Fine-grained visual review found two visible OWASP citation-compression defects (`n.d.b,n,n`) on pages 6 and 34; R12 repairs them.
- The Review page also duplicates Cheng Wang's second affiliation in web metadata. The PDF title page is correct. This portal-only defect remains to be fixed after uploading R12.
- The uploaded `ECAS_ASE_COVER_LETTER_R10_20260812.pdf` is byte-for-byte identical to the R11 cover letter; the old filename is cosmetic and does not require another upload. Choose no Research Square preprint unless all authors explicitly approve permanent CC BY posting.
- No experiment, frozen data, manuscript prose, result, table, reference, external-model state, or portal state changed.
- Status: `R11_PORTAL_PDF_REVIEWED / CITATION_FORMAT_DEFECT_FOUND / SUPERSEDED_BY_R12 / NOT_SUBMITTED`.

## ASE R10 Public-Supplement-Aligned Submission Package (2026-08-12)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R10_20260812/`.
- English manuscript: `ECAS_ASE_SUBMISSION_R10_20260812.pdf` (44 pages).
- Internal Chinese review PDF: `ECAS_ASE_SUBMISSION_R10_20260812_CN_REVIEW.pdf` (35 pages; not for upload).
- Flat portal LaTeX ZIP: `ECAS_ASE_LATEX_SOURCE_R10_20260812.zip` (13 root-level dependencies; new ASCII-path extracted rebuild PASS at 44 pages).
- Public Supplementary Information: `ESM_1.zip` (69 entries; verifier and conformance smoke PASS), cited in the manuscript as Online Resource 1.
- Cover letter: `ECAS_ASE_COVER_LETTER_R10_20260812.pdf` (one visually reviewed page) with an editable `ECAS_ASE_COVER_LETTER_R10_20260812.docx` counterpart.
- The manuscript and submission materials distinguish 30 primary Qwen3.6 raw responses, 120 hosted normalized candidates, and 780 evaluation-decision records; hosted-provider raw API envelopes and reasoning traces are excluded from the public package.
- The public artifact privacy statement now explicitly exempts the corresponding-author contact intentionally included in the README; no experiment data, model record, metric, figure, table, or conclusion changed.
- The old reviewer ZIP is absent from the R10 upload-facing directory and mapping.
- Status: `R10_PRESERVED_PREDECESSOR / SUPERSEDED_BY_R11 / NOT_SUBMITTED`.

## ASE R9 Guidelines-Aligned Submission Package (2026-08-12)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R9_20260812/`.
- English manuscript: `ECAS_ASE_SUBMISSION_R9_20260812.pdf` (44 pages).
- Internal Chinese review PDF: `ECAS_ASE_SUBMISSION_R9_20260812_CN_REVIEW.pdf` (35 pages).
- Flat portal LaTeX ZIP: `ECAS_ASE_LATEX_SOURCE_R9_20260812.zip` (13 root-level dependencies; new ASCII-path extracted rebuild PASS at 44 pages).
- Figure 3--6 provenance is now confirmed as Python + Matplotlib + SciencePlots, not TikZ; Figure 1--2 are diagrams.net (draw.io). The manuscript and portal-field draft state these graphics programs.
- At the author's direction, Codex, code debugging, consistency checks, and analysis support were removed from the public AI wording. English, Chinese, and portal-field text now match.
- Relevant English/Chinese pages passed visual review. No experiment, data, figure content, bibliography, reviewer artifact, external model, or portal state changed.
- Status: `R9_LOCAL_PACKAGE_READY / AUTHOR_CONFIRMATION_PENDING / PORTAL_DRY_RUN_PENDING / NOT_SUBMITTED`.

## ASE R8 Author-Annotated AI Statement Package (2026-08-12)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R8_20260812/`.
- English manuscript: `ECAS_ASE_SUBMISSION_R8_20260812.pdf` (44 pages; declarations on page 38).
- Internal Chinese review PDF: `ECAS_ASE_SUBMISSION_R8_20260812_CN_REVIEW.pdf` (35 pages; declarations on page 30).
- Flat portal LaTeX ZIP: `ECAS_ASE_LATEX_SOURCE_R8_20260812.zip` (13 root-level dependencies; ASCII-path extracted rebuild PASS).
- The author's page-30 annotation is implemented: the detailed GLM/Kimi/Claude/DeepL and early image-generation/provenance passage is deleted. The statement retains the ChatGPT/Codex assistance sentence and the authors' review/responsibility sentence.
- Submission materials and portal-field draft now mirror the shortened statement. The actual internal provenance record remains preserved; complete-disclosure compliance still requires author confirmation before submission.
- The verified R6 reviewer artifact is unchanged because R8 changes no experiment, data, results, figures, or artifact content.
- Status: `R8_LOCAL_PACKAGE_READY / AUTHOR_PDF_ANNOTATION_APPLIED / AI_DISCLOSURE_CONFIRMATION_PENDING / PORTAL_DRY_RUN_PENDING / NOT_SUBMITTED`.

## ASE R7 Figure/Table Reference-Closed Submission Package (2026-08-11)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R7_20260811/`.
- English manuscript: `ECAS_ASE_SUBMISSION_R7_20260811.pdf` (44 pages).
- Flat portal LaTeX ZIP: `ECAS_ASE_LATEX_SOURCE_R7_20260811.zip` (13 root-level dependencies; ASCII-path extracted rebuild PASS).
- Internal Chinese review PDF: `ECAS_ASE_SUBMISSION_R7_20260811_CN_REVIEW.pdf` (35 pages).
- Figure/table audit: `working/paper/retarget/ASE_20260803/analysis/submission/ASE_FIGURE_TABLE_REFERENCE_AUDIT_R7_20260811_CN.md`.
- English and Chinese each have 6/6 figures and 8/8 tables cited in body text outside their float/caption environments; 19 effective cross-references per language and zero missing/undefined labels.
- Table 1 now has an early section-level reference before its rendered appearance; Table 2 has an explicit record-chain explanation; Table 3 has a denominator clarification; Figure 3(b) is explicitly linked to RQ3.
- Reviewer artifact remains the already verified `ECAS_ASE_REVIEWER_ARTIFACT_PORTAL_R6_20260811.zip` because R7 changes no experiment, data, claim evidence, or artifact content.
- Status: `R7_LOCAL_PACKAGE_READY / FIGURE_TABLE_REFERENCE_PASS / AUTHOR_CONFIRMATION_PENDING / PORTAL_DRY_RUN_PENDING / NOT_SUBMITTED`.

## ASE R6 Local Submission Package (2026-08-11)

- Delivery directory: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/`.
- English manuscript: `ECAS_ASE_SUBMISSION_R6_20260811.pdf` (43 pages; Figure 1 on page 3; Figure 2 on page 12).
- Flat portal LaTeX ZIP: `ECAS_ASE_LATEX_SOURCE_R6_20260811.zip` (13 root-level dependencies; extracted ASCII-path rebuild PASS).
- Portal reviewer artifact: `ECAS_ASE_REVIEWER_ARTIFACT_PORTAL_R6_20260811.zip` (34 claim rows, 78 result rows, 30/300 primary and 120/480 hosted dimensions; verifier PASS; fixed conformance smoke PASS).
- Internal Chinese review PDF: `ECAS_ASE_SUBMISSION_R6_20260811_CN_REVIEW.pdf` (35 pages; Figures 1/2 on pages 3/9).
- Author-approved A draw.io source and all final exports are preserved under `FIGURE_SOURCES/`. The manuscript PNGs are 4800 px wide at 600 DPI; the final schematics contain no AI-generated raster pixels.
- English build has 0 undefined citation/reference, 0 overfull and 0 fatal/regular LaTeX warning. Figure pages and the declarations page passed visual review.
- Submission materials and the one-page author confirmation list are under `SUBMISSION_MATERIALS/`.
- Status: `R6_LOCAL_PACKAGE_READY / AUTHOR_CONFIRMATION_PENDING / PORTAL_DRY_RUN_PENDING / REVISION3_INSURANCE_PRESERVED / NOT_SUBMITTED`.

## Editable Draw.io Figure Comparison (2026-08-11)

- Two-page image-trace source: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/drawio_conversion/ECAS_Figures_1_2_Image_Trace_20260811.drawio`.
- Two-page prompt-redesign source: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/drawio_conversion/ECAS_Figures_1_2_Prompt_Redesign_20260811.drawio`.
- Four draw.io-rendered previews and comparison instructions are in the same directory. All boxes, text, badges, boundaries and connectors are editable draw.io objects; no raster image is embedded in either source.
- In A Figure 1, all 11 workflow/evaluation letter placeholders have been replaced by editable native draw.io library stencils (document, CPU, settings, certificate, policy, filter, server, clipboard, sync, search, and report).
- A Figure 1 now also replaces the Q/D/Z/K/O model badges with five self-contained SVG marks for Qwen, DeepSeek, Zhipu/GLM, Kimi, and OpenAI. The Kimi mark is adapted for the white paper canvas by changing only its white K to near-black while retaining its blue dot and vector geometry.
- The author selected A for continued editing. A Figure 2 now replaces all six success-path and three fail-closed text badges with editable native draw.io icons. Its three downward fail-closed arrows are straight vertical centerline connections; layout, wording, boundaries, and method semantics are unchanged.
- The current corrected semantics are preserved in both versions. Model names remain as scientific identifiers; candidate B retains editable letter badges.
- QA report: `working/paper/retarget/ASE_20260803/analysis/submission/DRAWIO_FIGURE_COMPARISON_20260811_CN.md`.
- Status: `A_SELECTED_FOR_CONTINUATION / A_FIG1_NATIVE_ICON_PASS / A_FIG1_MODEL_LOGO_SVG_PASS / A_FIG2_NATIVE_ICON_PASS / A_FIG2_VERTICAL_BRANCH_PASS / AUTHOR_FIG2_REVIEW_PENDING / NOT_INTEGRATED_IN_R5 / NOT_SUBMITTED`.

## Native PowerPoint Figure Redraw (2026-08-11)

- Fully editable two-slide PowerPoint: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/ppt_conversion/ECAS_Figures_1_2_Native_Shapes_20260811.pptx`.
- Rendered previews and instructions: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/ppt_conversion/`.
- All boxes, text, connectors, dashed regions, branches, and model badges are native PowerPoint objects. Package inspection found 0 picture objects and 0 embedded media files.
- Model-family names remain for scientific identification; graphical Logos are replaced by editable letter badges.
- QA report: `working/paper/retarget/ASE_20260803/analysis/submission/NATIVE_POWERPOINT_FIGURE_REDRAW_20260811_CN.md`.
- Status: `NATIVE_SHAPES_REDRAW_PASS / AUTHOR_PPT_REVIEW_PENDING / NOT_INTEGRATED_IN_R5 / NOT_SUBMITTED`.

## R5 Figure-Semantics Preview Candidate (2026-08-11)

- R5 source candidate: `working/paper/retarget/ASE_20260803/manuscript/submission_source/ECAS_ASE_SUBMISSION_CANDIDATE_R5_20260811/`.
- Author visual-preview PDF and rendered pages: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_CANDIDATE_R5_VISUAL_PREVIEW_20260811/`.
- Figure 1 now places deterministic validation/normalization before the Evidence Contract while preserving the model row, layout, icons, arrows, colors, and independent-evaluation lane.
- Figure 2 changes only the final success-box wording to `Executable policy / To ECAS gateway`.
- Independent build: 43 pages; Figures 1 and 2 on pages 3 and 12; 0 overfull, 0 undefined citation/reference, and 0 regular LaTeX warning.
- Verification report: `working/paper/retarget/ASE_20260803/analysis/submission/AI_FIGURE_DISCLOSURE_AND_SEMANTIC_VERIFICATION_20260811_CN.md`.
- Status: `R5_SEMANTIC_CORRECTION_PASS / AUTHOR_VISUAL_CONFIRMATION_PASS / EDITABLE_FIGURE_SOURCE_SELECTION_PENDING / R4_AND_REVISION3_PRESERVED / NOT_SUBMITTED`.

## ASE Submission-Stage Entry (2026-08-11)

- Current submission-stage handoff: `working/handoff/HANDOFF_20260811_ECAS_ASE_SUBMISSION_STAGE_ENTRY_CN.md`.
- Working authority: the R4 English/Chinese candidate listed below, with ultra-tight Figures 1 and 2 and full-page QA pass.
- Frozen fallback: ASE Revision 3 remains unchanged and is not superseded until a versioned final submission package passes all gates and receives explicit author promotion.
- Status: `ASE_SUBMISSION_STAGE_READY / R4_WORKING_AUTHORITY / REVISION3_INSURANCE_PRESERVED / FINAL_PACKAGE_PENDING / PORTAL_NOT_SUBMITTED`.

## Figure 1 + Figure 2 Integrated R4 Draft (2026-08-11)

- English manuscript PDF: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_DRAFT_R4_FIG1_FIG2_20260811/main.pdf` (43 pages; Figure 1 on page 3; Figure 2 on page 12).
- Chinese review PDF: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_DRAFT_R4_FIG1_FIG2_20260811_CN_SOURCE/main.pdf` (35 pages; Figure 1 on page 3; Figure 2 on page 9).
- Final Figure 1 files: `Figure_1_style_preserved_times_v2_ultratight_native.png`, `Figure_1_style_preserved_times_v2_ultratight_600dpi.png`, and `.tif` (4800×1566; 600 DPI).
- Final Figure 2 files: `Figure_2_imagegen_v6_ultratight_times_native.png`, `Figure_2_imagegen_v6_ultratight_times_600dpi.png`, and `.tif` (4800×1357; 600 DPI).
- Figure 2 integration/QA: `working/paper/retarget/ASE_20260803/analysis/FIGURE_2_IMAGEGEN_FINAL_INTEGRATION_20260811_CN.md`.
- Both figures now use deterministic ultra-tight top/bottom canvas cropping with approximately two high-resolution pixels of safety margin. No diagram content was redrawn or stretched; English/Chinese full-page QA passed.
- Status: `FIGURE_1_ULTRATIGHT_PASS / FIGURE_2_V6_ULTRATIGHT_INTEGRATED / TIMES_STYLE / 600_DPI / FULL_PAGE_QA_PASS / FINAL_PACKAGE_GATE_PENDING`.

## Superseded Figure-1-Only R3 Draft (2026-08-11)

- English manuscript PDF: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_DRAFT_R3_FIG1_20260811/main.pdf` (43 pages; Figure 1 on page 3).
- Chinese review PDF: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_DRAFT_R3_FIG1_20260811_CN_SOURCE/main.pdf` (35 pages; Figure 1 on page 3).
- Style-preserving native image: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/Figure_1_style_preserved_times_native.png`.
- 600 DPI derivatives: `Figure_1_style_preserved_times_600dpi.png` and `Figure_1_style_preserved_times_600dpi.tif` (4800×1699; 600 DPI).
- Integration/QA and Figure 2 review: `working/paper/retarget/ASE_20260803/analysis/FIGURE_1_FINAL_INTEGRATION_AND_FIGURE_2_REVIEW_20260811_CN.md`.
- Figure 1 keeps the author's preferred ImageGen layout/icons and uses Times New Roman visual styling. Its 2.8252:1 aspect ratio is preserved by width-only scaling; full-page English and Chinese renders passed visual inspection.
- The rejected TikZ vector redraw remains only as a failed candidate for provenance.
- Status: `SUPERSEDED_BY_R4_FIG1_FIG2 / RETAINED_FOR_PROVENANCE`.

## Superseded Figure 1 ImageGen Candidate (2026-08-11)

- Current v3 600 DPI PNG: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/Figure_1_imagegen_v3_models_no_reverse_arrow_600dpi.png` (4800×1680).
- Current v3 600 DPI TIFF: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/Figure_1_imagegen_v3_models_no_reverse_arrow_600dpi.tif` (4800×1680, LZW).
- v3 design notes and prompt: `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/FIGURE_1_IMAGEGEN_V3_MODELS_NOTES_CN.md`.
- Decision comparison contains no directional arrow; Qwen, DeepSeek, GLM, Kimi, and OpenAI are explicitly shown as alternative proposal models.
- v1 and v2 remain in the same directory for comparison.
- Status: `SUPERSEDED_BY_STYLE_PRESERVING_TIMES_EDIT / RETAINED_FOR_PROVENANCE`.

## ASE Author-Annotation R2 Draft

- English PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810_EN.pdf` (43 pages; 229-word abstract).
- English clean LaTeX ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810_LATEX_SOURCE.zip`.
- Chinese internal-review PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810_CN.pdf` (35 pages).
- Chinese clean LaTeX ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810_CN_LATEX_SOURCE.zip`.
- Bilingual synchronized review page: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810_BILINGUAL/OPEN_ME_ECAS_ASE_R2_20260810_BILINGUAL.html`.
- Revision and QA report: `working/paper/retarget/ASE_20260803/analysis/author_annotation_revision_20260810/REVISION_SUMMARY_CN.md` and `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810/SUBMISSION_AND_TRANSLATION_QA_R2.json`.
- Status: `AUTHOR_ANNOTATIONS_INTEGRATED / BILINGUAL_QA_PASS / CLEAN_PACKAGE_SMOKE_PASS / FIGURES_UNCHANGED / REVISION3_INSURANCE_UNCHANGED`.
- Next manuscript task: figure enhancement and a final length/submission gate. No paid external model was called in this revision.

## ASE Submission Draft and GLM Chinese Review Version

- English submission-draft PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810/ECAS_ASE_SUBMISSION_DRAFT_20260810_EN.pdf` (42 pages).
- Clean English LaTeX ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810/ECAS_ASE_SUBMISSION_DRAFT_20260810_LATEX_SOURCE.zip`.
- Chinese internal-review PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810/ECAS_ASE_SUBMISSION_DRAFT_20260810_CN.pdf` (34 pages).
- Clean Chinese LaTeX ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810/ECAS_ASE_SUBMISSION_DRAFT_20260810_CN_LATEX_SOURCE.zip`.
- Bilingual synchronized review page: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810_BILINGUAL_FINAL/OPEN_ME_ECAS_ASE_20260810_BILINGUAL.html`.
- Final QA: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810/SUBMISSION_AND_TRANSLATION_QA.json` (`PASS`). English and Chinese PDFs have zero undefined citations, zero undefined references, zero overfull boxes, and passed 42-page and 34-page visual inspection respectively.
- The English wording is based primarily on the paid human-edited lower-AI version while preserving Revision 3's verified scientific structures and boundaries. The Chinese draft was translated through 15 authorized GLM-5.2 calls with no paid retry and passed the bilingual LaTeX structure/number/citation audit.
- Figures are deliberately unchanged in this delivery. Figure enhancement is the next author-discussion item.
- Status: `SUBMISSION_DRAFT_READY_FOR_AUTHOR_REVIEW / REVISION3_INSURANCE_UNCHANGED`.

## Stage 4.1 Pre-Formal Five-Model Qualification

- Current outcome: `SUCCESS / 20_OF_20_FULL_PIPELINE_PASS / TOKEN_GATES_PASS / ZERO_MODEL_RETRY / FORMAL_PIPELINE_READY / NON_SCIENTIFIC / REVISION3_UNCHANGED`.
- Current closeout: `working/exploration/20260807_stage4_five_model_smoke/historical_alignment/preformal_qualification_v1/QUALIFICATION_CLOSEOUT_CN.md`.
- Final audit: `QUALIFICATION_FINAL_AUDIT.json`; call table: `QUALIFICATION_CALL_RESULTS.csv`; Token gate: `QUALIFICATION_TOKEN_GATE.json`; final manifest: `QUALIFICATION_FINAL_MANIFEST.sha256`.
- Provider results: Qwen 4/4, GLM 4/4, Kimi 4/4, DeepSeek 4/4 and ChatGPT/Codex 4/4. All 20 raw responses passed integrity capture; model-call retries were zero.
- The technical pipeline is ready, but a separate answer-free formal protocol, leakage review, denominator, statistics and promotion gate must be frozen before formal calls.


## Stage 4 Historical-Parameter-Aligned Five-Model Smoke

- Current outcome: `SUCCESS / 20_OF_20_ATTEMPTED_AND_RAW_CAPTURED / 14_OF_20_FULL_PIPELINE_PASS / NON_SCIENTIFIC / REVISION3_UNCHANGED`.
- Current closeout: `working/exploration/20260807_stage4_five_model_smoke/historical_alignment/aligned_rerun/ALIGNED_CLOSEOUT_CN.md`.
- Final audit: `working/exploration/20260807_stage4_five_model_smoke/historical_alignment/aligned_rerun/ALIGNED_FINAL_AUDIT.json` (`PASS`).
- Call results and failures: `ALIGNED_CALL_RESULTS.csv` and `ALIGNED_FAILURE_LEDGER.csv`; Token/failure gate: `TOKEN_GATE_AND_FAILURE_CLASSIFICATION.json`.
- Provider full-pipeline passes: Qwen 0/4, GLM 2/4, Kimi 4/4, DeepSeek 4/4, ChatGPT/Codex 4/4. All 20 raw responses passed integrity capture; wrapper retries were zero.
- No token truncation occurred. The six failures are non-scientific generated-policy schema/protocol failures, not MAXTOKEN, parameter-freeze or transport failures.
- The older Stage 4 main/recovery audit is retained only as historical interim evidence. This aligned rerun is the current Stage 4 smoke output and still cannot modify Revision 3 or support a model-performance claim.

## Stage 3 No-Result Engineering Acceptance

- Current outcome: `SUCCESS / 196_OF_196_PASS / 98_OF_98_REPEAT_PAIRS_IDENTICAL / ZERO_LEAKAGE / NON_SCIENTIFIC / MODELS_NOT_RUN / REVISION3_UNCHANGED`.
- Frozen plan: `working/exploration/20260807_stage3_no_result_engineering_acceptance/STAGE3_GOAL_PLAN_CN.md`.
- Final closeout: `working/exploration/20260807_stage3_no_result_engineering_acceptance/STAGE3_CLOSEOUT_CN.md`.
- Final audit: `working/exploration/20260807_stage3_no_result_engineering_acceptance/STAGE3_FINAL_AUDIT.json` (`PASS`).
- Final artifact manifest: 2045 entries, zero failures, SHA-256 `DE1234431E11BA8CF627D78024092917EB408152A353AB41FCA6F1E20FA3204B`.
- The 98 base fixtures comprise 80 valid integration outputs across all 40 blinded tasks and both blinded routes plus 18 faults covering 9 failure classes on both routes. Both repetitions matched all expectations; all 98 normalized pairs are byte-identical.
- OPA 1.19.0 exact binary SHA-256 is `ED4EE673B2182352AF3A9D5F0DE4A74D23A063CBBB447723FB21AC5EAD8CD599`.
- No model, paid API, ECAS/Direct-Rego formal generation or GPU was used. This is engineering acceptance, not scientific comparison evidence.
- Historical entry handoff: `working/handoff/HANDOFF_20260807_STAGE4_FIVE_MODEL_SMOKE_ENTRY_CN.md`. Its pre-call instruction is complete and superseded by the Stage 4 aligned closeout above.

## Stage 2 Task-and-Oracle Freeze Handoff and Goal Plan

- Current outcome: `SUCCESS / WP0_TO_WP6_PASS / INDEPENDENT_HUMAN_REVIEW_PASS / STAGE2_FROZEN / MODELS_NOT_RUN / REVISION3_UNCHANGED`.
- New authoritative handoff: `working/handoff/HANDOFF_20260807_STAGE2_TASK_ORACLE_FREEZE_ENTRY_CN.md`.
- Goal-mode plan: `working/exploration/20260807_stage2_task_oracle_freeze/STAGE2_TASK_ORACLE_FREEZE_GOAL_PLAN_20260807_CN.md`.
- WP0 protocol: `working/exploration/20260807_stage2_task_oracle_freeze/STAGE2_PROTOCOL_FREEZE_CN.md`.
- System register: `working/exploration/20260807_stage2_task_oracle_freeze/SYSTEM_VERSION_REGISTER.csv` (`8/8` frozen and unique).
- WP0 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP0_AUDIT.json` (`PASS`); initial manifest has 11 entries and SHA-256 `D28A75AFD0C053C9CEC22C9D78618F69295815D0E6F75CB294C461AE1570D068`.
- WP1 candidate register: `working/exploration/20260807_stage2_task_oracle_freeze/BUSINESS_TASK_CANDIDATES.csv` (`48/48`, exactly 6 per system).
- WP1 selected task register: `working/exploration/20260807_stage2_task_oracle_freeze/BUSINESS_TASK_REGISTER_32.csv` (`32/32`, exactly 4 per system and at least 3 primary families per system).
- WP1 control register: `working/exploration/20260807_stage2_task_oracle_freeze/EVIDENCE_DEFICIENT_CONTROL_REGISTER_8.csv` (`8/8`; source-wide absence audit continues in WP2).
- WP1 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP1_AUDIT.json` (`PASS`); all 21 registered source files exist and portfolio families cover A--G. WP1 manifest SHA-256 is `23D6B5AB381CE67D0DC596ED2EA12D19215E72E9EFEBA9C9841C6C15548FDE3C`.
- WP2 packet register: `working/exploration/20260807_stage2_task_oracle_freeze/EVIDENCE_PACKET_REGISTER_40.csv` (`40/40`), with `32/32` source hashes revalidated, `32/32` bindings frozen and `8/8` control absence audits complete.
- WP2 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP2_AUDIT.json` (`PASS`); 40 generation-evidence views have zero reserved-label leakage. Its 87-entry manifest SHA-256 is `CE3B7E24DA531E043E57D048E3E2AEA4CE64218E84D3CAF2712524E582682F8A`.
- WP3 request register: `working/exploration/20260807_stage2_task_oracle_freeze/REQUEST_FIXTURE_REGISTER.csv` (`128` business plus `32` structural controls).
- WP3 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP3_AUDIT.json` (`PASS`); two B3 repetitions achieved `320/320` gate matches and `160/160` byte-identical pairs. The 521-entry WP3 manifest SHA-256 is `7EE8DB8CB9EE99CB9C0812FFD111F5E0F115F22C044146A94943A477F9903528`.
- WP4 rule register: `working/exploration/20260807_stage2_task_oracle_freeze/RULE_ORACLE_REGISTER.csv` (`32/32`) and `RULE_ORACLE_DECISIONS_128.csv` (`128/128`), plus `8/8` evidence-insufficient control rulings.
- WP4 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP4_AUDIT.json` (`PASS`); rule-Oracle manifest SHA-256 `9C7A10FDBBC91D8F6F48C62A16609D9F1717AC9D33D48EA13740F84EC59F56B0`.
- WP5 execution register: `working/exploration/20260807_stage2_task_oracle_freeze/EXECUTION_ORACLE_REGISTER.csv` (`32/32`); adjudication ledger has `128/128` agreements and `0` unresolved divergences.
- WP5 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP5_AUDIT.json` (`PASS`); execution-Oracle manifest SHA-256 `DF4F7F0EAC0B92F2222506B8A09727A81F4C099F258D9801884F4EEC09769836`.
- WP6 technical audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP6_TECHNICAL_AUDIT.json` (`PASS_TECHNICAL`), with zero Generation/Execution leakage and a 1104-entry zero-error artifact manifest; final manifest SHA-256 `733AB69D926D9BC41080FAADA93C7A318F9D695758726CA877C167373779BBF9`.
- Independent reviewer `yi lv` completed all ten checks, confirmed the single-file reseal delta and retained `PASS`; the fail-closed validator returned `PASS` with zero failures.
- Final Stage 2 closeout: `working/review/20260807_stage2_independent_human_review/STAGE2_FINAL_CLOSEOUT_CN.md`.
- Next handoff: `working/handoff/HANDOFF_20260807_STAGE3_NO_RESULT_ENGINEERING_ACCEPTANCE_ENTRY_CN.md`. Stage 3 is not started or authorized; the next action is plan review only.
- No Qwen, GLM, Kimi, DeepSeek, OpenAI, ECAS, Direct-Rego, paid API or GPU was used in Stage 2.

## Stage 1 Four-System T0＋B3 Recovery

- Current outcome: `SUCCESS / STAGE1_4_OF_4_QUALIFIED / SALEOR_T0_RECOVERED`.
- Saleor 3.23.7 was acquired through an exact-digest OCI path and completed two independent clean-state native T0 runs. Both accepted the 50/100 valid refund and rejected the 500/100 refund with `AMOUNT_GREATER_THAN_AVAILABLE`.
- The two normalized Saleor native results are byte-identical with SHA-256 `A7865939897140BFCA204EFB2AB3535E4F3F56DD4EB2262CF8780B6C69BB7E33`; the existing B3 pair remains `ALLOW / ALLOW / DENY`.
- Current closeout: `working/exploration/20260806_stage1_four_system_t0_b3/SALEOR_RECOVERY_CLOSEOUT_20260807_CN.md`.
- Current handoff: `working/handoff/HANDOFF_20260807_STAGE1_FOUR_SYSTEM_RECOVERED_CN.md`.
- Current artifact manifest: `working/exploration/20260806_stage1_four_system_t0_b3/FINAL_ARTIFACT_MANIFEST.sha256` (741 entries; SHA-256 `EE5B967F24C7A2397EFB028CE735B00E3FB6524ADAA84262B5B0C0CB067BF0DB`).
- The pre-recovery 3/4 closeout remains historical evidence. No model, paid API, GPU, ECAS or Direct-Rego was used; Revision 3 remains unchanged.

## Historical Stage 1 Four-System T0＋B3 Closeout Before Recovery

- Overall: `STAGE1_NOT_COMPLETE / 3_OF_4_QUALIFIED / SALEOR_NOT_QUALIFIED_ENGINEERING`.
- Qualified twice from clean state: TigerBeetle 0.17.9, Lago v1.51.0 and OpenProject 17.4.0.
- Saleor 3.23.7: exact source/schema/remote image digest fixed and GraphQL B3 repeated identically, but native T0 was not run because two exact-image pulls each reached the frozen 20-minute acquisition limit.
- Closeout: `working/exploration/20260806_stage1_four_system_t0_b3/STAGE1_FOUR_SYSTEM_T0_B3_CLOSEOUT_20260806_CN.md`.
- Case matrix: `working/exploration/20260806_stage1_four_system_t0_b3/CASE_MATRIX.csv`.
- Final artifact manifest: `working/exploration/20260806_stage1_four_system_t0_b3/FINAL_ARTIFACT_MANIFEST.sha256` (700 entries; SHA-256 `0354BA3B5315B61736DE183B87D7C8320586801D2D55B6AA3001891284EFD232`).
- Handoff: `working/handoff/HANDOFF_20260806_STAGE1_FOUR_SYSTEM_T0_B3_PARTIAL_CN.md`.
- No model, paid API, GPU, ECAS or Direct-Rego was used. Revision 3 PDF/ZIP hashes remain unchanged.

## Historical Parent Finance B3—ECAS Comparison Plan

- Review draft: `working/exploration/20260806_finance_b3_ecas_comparison_plan/FINANCE_B3_ECAS_COMPARISON_DRAFT_FOR_REVIEW_20260806_CN.md`
- SHA-256: `46965A1FCACB1F3F34E0EB0354F80C16B09FF4596446BF76C9D60DE5EDDC843B`
- Proposed design: 8 systems (6 finance, 2 cross-domain), 32 business-semantic tasks, 8 evidence-deficient controls, complete B3, Direct-Rego, ECAS and an independent human ceiling.
- Revised model design: Qwen, GLM, Kimi, DeepSeek and an exact OpenAI API model are five coequal blocks in the same formal matrix; there is no primary-versus-later-sensitivity split.
- Proposed formal volume: at most 1200 calls (`5 models × 40 task packets × 2 generative routes × 3 repetitions`), with no automatic retry authorization. Exact model IDs, Token, GPU/cost and call batches require separate approval.
- Historical document status remains `REVISED_DRAFT_FOR_USER_REVIEW / FIVE_MODEL_COEQUAL / NO_EXPERIMENT_AUTHORIZED / REVISION3_UNCHANGED`; its Stage 1 next-step pointer is superseded by the completed Stage 1 evidence and the current Stage 2 goal-mode plan.

## Finance B3 All-Ten Adaptation Complete

- Completion report: `working/exploration/20260806_finance_b3_all10/FINANCE_B3_ALL10_COMPLETION_20260806_CN.md`
- Result summary: `working/exploration/20260806_finance_b3_all10/B3_ALL10_RESULT_SUMMARY_20260806.csv`
- Audit: `working/exploration/20260806_finance_b3_all10/runs/audit/ALL10_AUDIT.json` (`SUCCESS`; SHA-256 `2111E69D581480E15D9F33BAEFA4CD07C474CBBC4ED4B8495DF1068988BF1941`)
- Final artifact manifest: `working/exploration/20260806_finance_b3_all10/FINAL_ARTIFACT_MANIFEST.sha256` (239 entries; SHA-256 `D7BA968411D651C672E4F3038421AE80E0DA6699D372EBBF1E2421C3A4E17746`)
- Status: `B3_ALL10_ADAPTATION_SUCCESS / ECAS_NOT_RUN / NO_FORMAL_COMPARISON / REVISION3_UNCHANGED`.
- All 10 cases completed valid, semantic-invalid and schema-invalid-control inputs twice: 60 decision files, 40 accepts, 20 rejects, all 20 semantic-invalid executions accepted, all 20 controls rejected, and 30/30 repeated pairs byte-identical.
- B3 caught `0/10` target business-semantic cases. This establishes an operational strong-baseline portfolio, not an ECAS advantage; ECAS was not run.
- Contract authority remains `4 HIGH / 5 MEDIUM / 1 LOW`; LedgerSMB remains explicitly `observer_ingress / LOW`.
- Exact validator image: `sha256:4e0c59ccbc79a4ebeb6c6db45a86f73ff1797322581ae79b0ad14b4599f57c33`; zero residual B3 containers.

## Finance B3 Three-Case Pilot Gate

- Protocol: `working/exploration/20260806_finance_b3_pilot/B3_PILOT_PROTOCOL_20260806_CN.md`
- Ten-case adaptation inventory: `working/exploration/20260806_finance_b3_pilot/B3_ADAPTATION_INVENTORY_10CASE_20260806.csv`
- Result summary: `working/exploration/20260806_finance_b3_pilot/B3_PILOT_RESULT_SUMMARY_20260806.csv`
- Gate report: `working/exploration/20260806_finance_b3_pilot/FINANCE_B3_THREE_CASE_GATE_REPORT_20260806_CN.md`
- Audit: `working/exploration/20260806_finance_b3_pilot/runs/audit/result_audit.txt` (`PASS`; SHA-256 `FB49BC77DE9601FFE0EE93FB575768B3B6B5655929EA234100E587FD993B4585`)
- Status: `B3_PILOT_PASS / GO_TO_ALL_10_B3_ADAPTATION_ONLY / ECAS_NOT_RUN / NO_FORMAL_COMPARISON / REVISION3_UNCHANGED`.
- jPOS, LedgerSMB and BTCPay each completed two isolated repetitions over one valid input, one semantic-invalid input and one schema-invalid negative control. All 6 semantic-invalid executions were accepted, all 6 controls were rejected, and all 9 paired decision outputs were byte-identical across repetitions.
- The result means the operational pre-execution B3 surfaces do not express the three target business rules. It does not establish an ECAS advantage because ECAS was not run.
- The ten-case inventory contains 4 high-authority, 5 medium-authority and 1 low-authority B3 surface. LedgerSMB remains explicitly tagged `observer_ingress / LOW` and may not be pooled as product-published B3 without a stronger native contract.
- Exact validator image: `sha256:4201fc5465401ccdd8dd26c09a1483ba5713f015c6626bdc11ce9b760f7d0580`; zero residual B3 containers.

## Finance T0 Ten-Case Goal

- Frozen protocol: `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_PROTOCOL_20260806_CN.md`
- Qualification matrix: `working/exploration/20260806_finance_t0_10cases/CASE_QUALIFICATION_MATRIX.csv`
- Execution ledger: `working/exploration/20260806_finance_t0_10cases/T0_EXECUTION_LEDGER.csv`
- Completion report: `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_COMPLETION_20260806_CN.md`
- Completion audit: `working/exploration/20260806_finance_t0_10cases/runs/completion_audit/COMPLETION_AUDIT_20260806.txt` (`PASS`; SHA-256 `FA1E2BDC8A0CEE510865C7504EED0997CF9B7464569E144306054D903EF66E98`)
- Reproduction boundary: `REPRODUCE.md`
- Status: `GOAL_COMPLETE / 10_OF_10_QUALIFIED / 2_PRIMARY_REPLACEMENTS / 0_PENDING / LOCAL_NO_MODEL_T0_ONLY`.
- The user authorized local repository acquisition, WSL-native Docker, deterministic seeding, and two clean T0 repetitions per case. No model, paid API, GPU, formal comparison, real funds, live trading, production integration, manuscript change, submission, or publication is authorized.
- The only runtime lane is Ubuntu WSL2 native Docker 29.1.3 with ASCII work root `/root/ecas_finance_t0_20260806`. Preflight found zero containers and reverified both frozen Revision 3 hashes.
- T0 artifacts are engineering qualification evidence only and support no Revision 3 manuscript claim.
- First qualified case: Blnk v0.15.2. Two clean repetitions both returned HTTP 200 with an `APPLIED` child on the first synchronous inflight commit and HTTP 409 `TXN_ALREADY_COMMITTED` on the identical second commit. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-02-blnk/RESULT_SUMMARY.md`.
- Second qualified case: Formance Ledger v2.4.12. Two clean repetitions both accepted the world-to-user posting (HTTP 200), rejected an unfunded user debit (HTTP 400 `INSUFFICIENT_FUND`), and retained exactly one transaction. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-01-formance/RESULT_SUMMARY.md`.
- Third qualified case: LNbits v1.5.6. Two clean repetitions both applied the first 300 sat internal payment (HTTP 201/success), rejected a structurally valid second 300 sat payment after the sender balance fell to 200 sat (HTTP 520 `Insufficient balance.`), and ended with sender/receiver balances of 200/300 sat. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-05-lnbits/RESULT_SUMMARY.md`.
- Fourth qualified case: Freqtrade 2026.7. Two network-isolated repetitions accepted the bounded dry-run portfolio configuration and rejected the individually schema-valid combination of unlimited open trades and unlimited stake with the native `ConfigurationError`. No exchange, market-data, or trading connection occurred. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-03-freqtrade/RESULT_SUMMARY.md`.
- Fifth qualified case: Midaz v3.8.0. Two network-isolated repetitions accepted projected overdraft usage exactly at the configured limit (500) and rejected projected usage above the limit (501) with the release-native structured error code `0167`. The local-only Elastic-2.0 evaluation boundary is retained; no bank connection or real funds were used. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-08-midaz/RESULT_SUMMARY.md`.
- Sixth qualified case: LedgerSMB 1.13.7. Two fresh-state repetitions accepted a transaction date one day after the latest account checkpoint and rejected the checkpoint boundary date as a closed accounting period through the release-native Workflow condition. Each run used a new internal-only network and PostgreSQL tmpfs. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-04-ledgersmb/RESULT_SUMMARY.md`.
- Seventh qualified case: openIMIS 26.04 with its pinned `openimis-be-claim` 1.11.0 component. Two network-isolated repetitions accepted a claim date equal to care start and rejected a claim date one day earlier with native reason/error code 9. Only synthetic claim data was used. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-10-openimis/RESULT_SUMMARY.md`.
- Eighth qualified case: BTCPay Server v2.4.1. Two network-isolated repetitions applied the official release assembly's refund rule: an expired partially paid invoice was refundable, while an expired invoice with no payment exception was not. No BTCPay service, Bitcoin/Lightning node, merchant account, or real funds were used. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-06-btcpay/RESULT_SUMMARY.md`.
- Ninth qualified case: jPOS 2.1.10 (backup for Hyperswitch). Two network-isolated repetitions accepted USD 12.34 at currency scale 2 and rejected PYG 12.34 through the release-native `ISOAmount` constructor because currency 600 has scale 0. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-B01-jpos/SUMMARY.json`.
- Tenth qualified case: Bigcapital v0.25.25 (backup for Open Bank Project). Two network-isolated repetitions accepted an unpublished manual journal and rejected the same publish action with a non-null `published_at` using the release-native `MANUAL_JOURNAL_ALREADY_PUBLISHED`/400 rule. Summary: `working/exploration/20260806_finance_t0_10cases/runs/FT0-B02-bigcapital/SUMMARY.json`.
- Hyperswitch and Open Bank Project remain source-frozen but were replaced under the pre-frozen backup rule because their bounded deterministic runtime paths did not close. This is an engineering scope boundary, not a scientific failure.
- Final audit: 10 qualified cases, 2 replaced primaries, zero pending cases, 190 evidence-manifest entries verified, zero residual case containers, and unchanged Revision 3 PDF/source ZIP hashes.

## ASE Submission-Insurance Freeze and Experiment-Exploration Entry

- Current detailed handoff: `working/handoff/HANDOFF_20260806_ASE_SUBMISSION_INSURANCE_FREEZE_AND_EXPERIMENT_EXPLORATION_CN.md`
- Current status: `ASE_SUBMISSION_INSURANCE_FROZEN / REVISION3_AUTHORITATIVE / EXPERIMENT_EXPLORATION_ISOLATED / FINANCE_T0_10CASE_GOAL_COMPLETE`.
- Authoritative manuscript PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION3_20260804.pdf`
  - 896,759 bytes
  - SHA-256: `4D2259F65CE16CEAB9F1919FAFE298C65D5760BF27B2CB0752A9E942A8EFBE3F`
- Authoritative source ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION3_SOURCE_20260804.zip`
  - 361,451 bytes
  - SHA-256: `C0548460C11520D20DE30A82A874871139F38EBB763CBA64FE7DC9872354E9C5`
- The user confirmed Revision 3 as the ASE submission-ready fallback (the “submission-insurance” version). This records a project freeze, not a completed portal submission or journal decision.
- The prior CBHG/three-Agent Revision 4 branch is retained only as historical exploration and audit evidence; it is not the current approved innovation route.
- New experimental work is isolated from Revision 3 and focuses on complete standard validation, an external policy-as-code baseline, and genuinely unseen systems. No model, GPU, paid API, Opus, submission, or publication action is authorized by this handoff.

## Unseen-System Source Screening (Exploration 1)

- Authoritative screening report: `working/exploration/20260806_unseen_system_screening/UNSEEN_SYSTEM_SCREENING_20260806_CN.md`
- Machine-readable matrix: `working/exploration/20260806_unseen_system_screening/UNSEEN_SYSTEM_SCREENING_20260806.csv`
- Status: `SOURCE_SCREEN_PASS_5 / RUNTIME_T0_NOT_RUN / NO_EXPERIMENT_AUTHORIZED`.
- Five source-qualified candidates: OpenProject 17.4.0, Saleor 3.23.7, Mattermost 11.7.2, Kill Bill 0.24.18, and Lago 1.51.0.
- Recommended first pair: OpenProject as pilot and Saleor as cross-domain confirmation; Mattermost, Kill Bill, and Lago remain ordered alternates.
- This is a source/license/version/API-contract/business-constraint/local-execution-path screening result only. It is not runtime qualification, a B3 result, an ECAS comparison, or manuscript evidence.
- Revision 3 remains authoritative and unchanged. No repository download, container startup, model/API/GPU call, formal experiment, submission, or publication occurred.

## Expanded Unseen-System Census and Funnel Checkpoint

- Frozen funnel protocol: `working/exploration/20260806_unseen_system_screening/EXPANDED_CENSUS_PROTOCOL_20260806_CN.md`
- Candidate universe: `working/exploration/20260806_unseen_system_screening/CANDIDATE_UNIVERSE_75_20260806.csv`
- High-potential source screen: `working/exploration/20260806_unseen_system_screening/S1_HIGH_POTENTIAL_SCREEN_26_20260806.csv`
- Checkpoint report: `working/exploration/20260806_unseen_system_screening/EXPANDED_CENSUS_CHECKPOINT_20260806_CN.md`
- Status: `S0_CENSUS_75 / S1_HIGH_POTENTIAL_26 / SOURCE_PASS_16 / SOURCE_CONDITIONAL_10 / T0_NOT_RUN / SATURATION_NOT_REACHED`.
- The original five-system screen remains valid as the seed audit, but it no longer defines the exploration scope. The expanded design uses a 50--100-system census, a 20--30-system source screen, an 8--12-system T0 queue, a later 5--8-system formal set, and a 3--5-system primary analysis.
- The current 12-system T0 queue is OpenProject, Saleor, Mattermost, Firefly III, authentik, OpenEMR, Cal.com, Directus, NetBox, Mayan EDMS, Twenty, and Kill Bill. Queue membership is not runtime qualification or experiment authorization.
- The frozen saturation rule stops at 100 systems, or after at least 50 candidates when 10 consecutive eligible systems add no new domain x API x semantic-constraint cell, or after two documented no-progress expansion rounds. The present checkpoint has not reached saturation.
- No Docker/container startup, repository checkout, runtime T0, model/API/GPU call, formal experiment, or manuscript change occurred.

## Finance and Banking Priority Census Checkpoint

- Finance delta: `working/exploration/20260806_unseen_system_screening/FINANCE_BANKING_DELTA_25_20260806.csv`
- Combined 100-system universe: `working/exploration/20260806_unseen_system_screening/CANDIDATE_UNIVERSE_FINANCE_PRIORITY_100_20260806.csv`
- New finance high-potential screen: `working/exploration/20260806_unseen_system_screening/FINANCE_BANKING_HIGH_POTENTIAL_15_20260806.csv`
- Reselected S1 matrix: `working/exploration/20260806_unseen_system_screening/S1_FINANCE_PRIORITY_SCREEN_30_20260806.csv`
- Checkpoint report: `working/exploration/20260806_unseen_system_screening/FINANCE_BANKING_PRIORITY_CHECKPOINT_20260806_CN.md`
- Current status: `S0_CENSUS_100 / FINANCE_FOCUSED_31 / S1_RESELECTED_30 / S1_FINANCE_19 / SOURCE_PASS_16 / SOURCE_CONDITIONAL_14 / T0_NOT_RUN / STOP_AT_100`.
- The 25-system delta covers core/open banking, payment/clearing/card interchange, financial ledgers/accounting, wealth and tax, algorithmic trading/market risk, and insurance claims. Fineract and ERPNext are excluded from unseen-system primary selection because they are historical ECAS protected systems/evidence sources.
- The current T0 queue is finance-weighted: Formance Ledger, Blnk, Hyperswitch, Midaz, Open Bank Project, Freqtrade, LedgerSMB, and openIMIS, plus OpenProject, Saleor, authentik, and OpenEMR as cross-domain confirmation. Conditional systems must close their source/runtime prerequisites before T0.
- Reaching 100 triggers the frozen census hard stop. It is not evidence that domain x API x semantic coverage naturally saturated, and it is not a generality claim.
- No repository checkout, Docker/container startup, runtime T0, model/API/GPU call, formal experiment, or manuscript change occurred.

## Historical Revision 4 Independent-Handoff and Five-Model Planning Branch

This branch is superseded as the active route by the 2026-08-06 submission-insurance freeze and strong-baseline/unseen-system exploration decision. Its files remain historical protocol and failure-audit evidence and must not modify Revision 3.

- Detailed v0.2 plan: `working/paper/retarget/ASE_20260803/revision4_planning/20260805_inventory_handoff_multimodel/ECAS_REVISION4_INVENTORY_HANDOFF_MULTIMODEL_PLAN_20260805_CN.md`
- Smoke, independent-adversarial review, and Codex adjudication: `working/paper/retarget/ASE_20260803/revision4_planning/20260805_inventory_handoff_multimodel/ECAS_REVISION4_PLAN_SMOKE_AND_SELF_REVIEW_20260805_CN.md`
- Draft 2020-12 study schema: `working/paper/retarget/ASE_20260803/revision4_planning/20260805_inventory_handoff_multimodel/schemas/REVISION4_STUDY_RECORDS_V0.schema.json`
- Authoritative non-scientific smoke: `working/paper/retarget/ASE_20260803/revision4_planning/20260805_inventory_handoff_multimodel/smoke/outputs/REV4-PROTOCOL-SMOKE-20260805T045504Z/SMOKE_SUMMARY.json`
- Schema validation receipt: `working/paper/retarget/ASE_20260803/revision4_planning/20260805_inventory_handoff_multimodel/smoke/SCHEMA_VALIDATION_RESULT_20260805.json`
- Reproduction entry: `working/paper/retarget/ASE_20260803/revision4_planning/20260805_inventory_handoff_multimodel/REPRODUCE.md`
- Current status: `DESIGN_CONTRADICTION_REPAIRED / PROTOCOL_SMOKE_PASS_WITH_PENDING / NO-GO_FOR_FORMAL_PREREGISTRATION`.
- Protocol smoke: `9 CONFIRMED / 1 PENDING / 1 UNRESOLVED / 0 FAIL`; all 20 recorded output hashes match; participant forbidden-field scan has 0 matches.
- Schema validation: 16 symmetric Raw/ECAS full-chain synthetic records and 9 dynamic role templates pass; four schema-level and six cross-record negative controls are rejected as expected; relational errors are zero.
- A second independent read-only adversarial recheck found no overturning residual and closed P0-4 at the protocol layer; this does not close the remaining experimental traceability gates.
- The independent review correctly rejected v0.1 because the Security role could carry rule/admission answers. v0.2 restricts Security to an answer-free claim--binding handoff graph; Raw and ECAS share the same evidence/catalog/schema, and only ECAS receives the graph.
- No model/API call, Key read, formal experiment, result mutation, or manuscript edit occurred. Revision 3 remains the only authoritative manuscript.

## Valid Revision 3 Opus 5 Review and Codex Adjudication

- Verified normalized Opus review: `working/paper/retarget/ASE_20260803/external_reviews/20260805_revision3_opus5_innovation_review_authorized_call1/offline_reparse_20260805/OPUS5_HIGH_REVISION3_REVIEW_20260805_CALL1_OFFLINE_REPARSED_CN.md`
- Codex adjudication: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION3_OPUS5_INNOVATION_REVIEW_AND_CODEX_ADJUDICATION_20260805_CN.md`
- Wrapper and deterministic-reparse audit: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION3_OPUS5_WRAPPER_REPAIR_AND_DETERMINISTIC_REPARSE_AUDIT_20260805_CN.md`
- Current handoff: `working/handoff/HANDOFF_20260805_ASE_OPUS5_REVIEW_AND_INNOVATION_DECISION_CN.md`
- Status: `VALID REVIEW VIA HASH-IDENTICAL OFFLINE REPARSE / CODEX ADJUDICATED / REVISION 3 FROZEN`.
- Opus verdict: Major Revision; strong ASE/SI fit, partial novelty resolution, subjective current overall acceptance 18%–30%.
- Codex planning range: current 13%–23%; route-1 narrative/closest-work strengthening 17%–27%; successful independent new evidence 26%–43%.
- Exactly one paid call was consumed; no retry or second paid call occurred.

## Historical 2026-08-04 External-Review Attempt (Invalid; Not an Opus Review)

- Failure audit and Codex-only interim assessment: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION3_OPUS5_FAILURE_AUDIT_AND_CODEX_INTERIM_ASSESSMENT_20260804_CN.md`
- One authorized Opus 5 call was consumed and failed closed on a generic `sk-` secret-regex false positive; the normalized report is empty, no Opus正文 is admissible, and no retry was attempted.
- Continuation handoff: `working/handoff/HANDOFF_20260804_ASE_OPUS5_FALSE_POSITIVE_REVIEW_FAILURE_CN.md`
- This failure does not supersede or modify Authoritative ASE Revision 3.

## Authoritative ASE Revision 3

- Final author-review PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION3_20260804.pdf`
  - 42 pages; 896,759 bytes
  - SHA-256: `4D2259F65CE16CEAB9F1919FAFE298C65D5760BF27B2CB0752A9E942A8EFBE3F`
- Clean source directory: `working/paper/retarget/ASE_20260803/manuscript/submission_source/ECAS_ASE_REVISION3_20260804/`
- Clean source ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION3_SOURCE_20260804.zip`
  - SHA-256: `C0548460C11520D20DE30A82A874871139F38EBB763CBA64FE7DC9872354E9C5`
- Formula typography QA: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION3_FORMULA_TYPOGRAPHY_QA_20260804_CN.md`
- Detailed handoff: `working/handoff/HANDOFF_20260804_ASE_REVISION3_FORMULA_TYPOGRAPHY_CN.md`
- Current gate: `FORMULA_TYPOGRAPHY_PASS / READY_FOR_AUTHOR_FINAL_REVIEW`.
- Fourteen standalone equations are continuously numbered; named operators, states, multi-line alignment, enclosing delimiters, and Algorithm 1 placement are normalized.
- Frozen results, figures, tables, references, traceability, and reviewer artifacts are unchanged from Revision 2. The two Revision 2 reviewer-artifact ZIPs below remain authoritative attachments.

## Innovation-Exploration Checkpoint

- Frozen stage baseline: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_STAGE_BASELINE_BEFORE_INNOVATION_20260804_CN.md`
- Cross-conversation handoff: `working/handoff/HANDOFF_20260804_ASE_INNOVATION_EXPLORATION_ENTRY_CN.md`
- Exploration status: `REVISION3_BASELINE_FROZEN / INNOVATION_EXPLORATION_READY`.
- Revision 3 remains the only authoritative manuscript. Any innovation candidate must be created in an isolated sandbox and pass the documented promotion gates before it can supersede Revision 3.

## Superseded ASE Revision 2

- Final author-review PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION2_20260804.pdf`
  - 42 pages; 896,757 bytes
  - SHA-256: `515083DA38E4F0FD2B2B29238B6241103FED54F7D8403CF53D836C01FF309514`
- Clean source directory: `working/paper/retarget/ASE_20260803/manuscript/submission_source/ECAS_ASE_REVISION2_20260804/`
- Clean source ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION2_SOURCE_20260804.zip`
- Submission reviewer artifact ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVIEWER_ARTIFACT_SUBMISSION_20260804.zip`
- Portal reviewer artifact ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVIEWER_ARTIFACT_PORTAL_20260804.zip`
- Submission closeout report: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION2_SUBMISSION_CLOSEOUT_20260804_CN.md`
- Detailed handoff: `working/handoff/HANDOFF_20260804_ASE_REVISION2_SUBMISSION_CLOSEOUT_CN.md`
- Current gate: `SUBMISSION_FREEZE_PASS / READY_FOR_AUTHOR_FINAL_REVIEW`.
- Current matrix status: `33 PASS / 1 ROUNDING_PASS / 0 P0`; matrix SHA-256 `856C0DB6F11DA77747A6CBADA081640BBDD07255B12EA0A092006102239E396A`.
- Both packaged reviewer artifacts pass verifier and smoke tests after ZIP extraction.

## Superseded ASE Revision 1

- Author-review PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION1_20260804.pdf`
  - 40 pages; 873,263 bytes
  - SHA-256: `795419FE17E4F983F57371B4351ED1D68D45D7BAC33FE6FB5D538334CF5987BF`
- Active manuscript source: `working/paper/retarget/ASE_20260803/manuscript/source/main.tex`
- Springer wrapper: `working/paper/retarget/ASE_20260803/manuscript/ase_source/ecas_ase_main.tex`
- Author-year bibliography: `working/paper/retarget/ASE_20260803/manuscript/ase_source/ecas_ase_references_author_year_v1.bib`
- Revision and QA report: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION1_AUTHOR_STYLE_AND_P0_CLOSEOUT_20260804_CN.md`
- Detailed handoff: `working/handoff/HANDOFF_20260804_ASE_REVISION1_CN.md`

## Historical Revision 1 Three-Model Review

- Codex adjudication: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION1_THREE_MODEL_REVIEW_AND_CODEX_ADJUDICATION_20260804_CN.md`
- Plain-text preview fallback: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_REVISION1_THREE_MODEL_REVIEW_AND_CODEX_ADJUDICATION_20260804_CN.txt`
- Current review handoff: `working/handoff/HANDOFF_20260804_ASE_REVISION1_THREE_MODEL_REVIEW_CN.md`
- Common protocol and frozen inputs: `working/paper/retarget/ASE_20260803/external_reviews/20260804_revision1_three_model_review/`
- GLM complete review: `working/paper/retarget/ASE_20260803/external_reviews/20260804_revision1_three_model_review/GLM52_HIGH_REVISION1_REVIEW_CN.md`
- Kimi partial review (`finish_reason=length`): `working/paper/retarget/ASE_20260803/external_reviews/20260804_revision1_three_model_review/KIMI_K3_HIGH_REVISION1_REVIEW_CN.md`
- Opus partial captured review: `working/paper/retarget/ASE_20260803/external_reviews/20260804_revision1_three_model_review/OPUS5_HIGH_REVISION1_REVIEW_CN.md`
- Historical pre-repair gate: `RESULTS_FREEZE_PASS / ARTIFACT_EXECUTION_PASS / SUBMISSION_FREEZE_HOLD`.
- Historical pre-repair matrix status: `28 PASS / 1 ROUNDING_PASS / 5 MISMATCH / 5 P0`; Revision 2 closes these five P0 items.

## Current Evidence and Artifact Outputs

- Claim--evidence matrix: `working/paper/retarget/ASE_20260803/analysis/traceability/ASE_CLAIM_EVIDENCE_MATRIX_20260804.csv`
- Traceability adjudication: `working/paper/retarget/ASE_20260803/analysis/traceability/ASE_CLAIM_EVIDENCE_ADJUDICATION_20260804_CN.md`
- Author-review provenance reconciliation: `working/paper/retarget/ASE_20260803/analysis/traceability/AUTHOR_REVIEW_PROVENANCE_RECONCILIATION_20260804.md`
- Artifact repair audit: `working/paper/retarget/ASE_20260803/analysis/ECAS_ASE_ARTIFACT_IMPORTABILITY_REPAIR_AUDIT_20260804_CN.md`
- Full reviewer artifact: `working/paper/reviewer_artifact_submission/`
- Portal reviewer artifact: `working/paper/reviewer_artifact_portal/`

## External-Review Wrapper Repair

- Offline guard suite: `working/tests/external_model_wrapper_guards/ExternalModelWrapperGuards.Tests.ps1`
- Fake Claude process fixture: `working/tests/external_model_wrapper_guards/FakeClaude.exe`
- Test documentation: `working/tests/external_model_wrapper_guards/README.md`
- Verification: current suite `16/16` offline Pester tests passed; real-process FakeClaude and hash-identical raw replay also passed without network access or paid model calls.
- Global Kimi/Opus wrappers and external-model rules were hardened on 2026-08-04. Existing partial Kimi/Opus review files remain failure audits and were not regenerated.

## Superseded for Current Review

- `working/paper/retarget/ASE_20260803/manuscript/archive/phase2_first_draft_20260804/` is the preserved Phase 2 baseline, not the current review copy.
- The frozen CSI package remains historical evidence and must not replace the current ASE source.
- Legacy CSI claim--evidence matrices are archived under `working/paper/retarget/ASE_20260803/analysis/traceability/archive/legacy_csi_matrices_20260804/`.

## 2026-08-10 Paid-Prose-Primary Merge Candidate

- Candidate DOCX: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_PAID_PROSE_MERGE_20260810/ECAS_ASE_PAID_PROSE_MERGE_20260810.docx`.
- Merge audit: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_PAID_PROSE_MERGE_20260810/MERGE_AUDIT.json`.
- Merge notes: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_PAID_PROSE_MERGE_20260810/MERGE_NOTES_CN.md`.
- The paid human-edited lower-AI DOCX is the prose authority. Of 51 differing paragraphs, 49 use its wording; two frozen paragraphs were retained to protect an internal hyperlink and the `30 × 5 × 2 = 300` equation object.
- Nine narrow scientific/protocol phrase repairs were applied without manuscript-wide rewriting.
- Structural QA: 6 figures, 9 tables, 117 Office Math objects, 87 hyperlinks, and no `NULL` relationship. The merged text is 97.83% similar to the paid prose and 96.28% similar to the frozen comparison DOCX.
- The 43-page headless render was inspected page by page. LibreOffice formula/table compatibility artifacts match the frozen comparison render and were not introduced by this merge.
- Status: `CANDIDATE_ONLY / AUTHOR_REVIEW_REQUIRED`. Revision 3 remains unchanged and authoritative.
