# ECAS Project Handoff

## 七案例与缺值机制验证已完成（2026-10-15，当前权威入口）

- 新版中文简报working/exploration/20261015_seven_case_mechanism/EXPERIMENT_SUMMARY_CN_R2.md；七案例表SEVEN_CASE_TABLE_CN.md及21行CSV；独立来源对账344项通过。A旧三例的事后格式/接口复演与B新四例共同目标实测分批，禁止合并统一准确率。原R1保留，不覆盖其hash与历史QA。
- 零模型的本地机制对照missing-state-mechanism-v1实际SUCCEEDED/exit0，T0 17项；18相关输入×八臂=144行，原件/结果160项及独立2191项静态原始capture对账通过，无新增模型/政策扩测。结果mechanism_control/RESULTS_CN.md及RESULTS.json。run已完成，不再start；当前无在跑任务。
- 已实证：B17/B19只将on_missing=deny改为skip仍full准入，并在trusted={}允许；full/shape所有观察相同。B19空/未知类型拒绝由正向允许式DNF决定。两同行原Rego加人工typed状态guard可关闭这几项保守控制差异、保留已测原请求对。它不是原基线生成结果，不证明其他合法请求覆盖不损失。
- B19两个partial-missing仅观察无gold：false-only均allow，Payments-only ECAS/同行原规则allow而人工guard deny；不得写成已证实漏洞。B06 P2P旧候选本来也缺值deny，不能宣称该结果为ECAS独有。
- 研究继续重点：把必需可信状态/条件依赖/类型/失效处理提升为可核验运行契约，与带同类安全默认值的强同行控制比较；Inventory记录/版本/路径缺失的部署准入与请求trusted值缺失的运行处理必须分开。Judge按源语义检查不是ECAS独有机制。后续新模型任务未启动，上一轮余额不使用。
- 本scope结果账本17行（T0+16配置任务观察行），根科学账本/论文/旧原件/投稿不变。根T0当前指本scope，旧pointer存mechanism_control/PREVIOUS_ROOT_T0_EVIDENCE.json。


## 七案例汇总与缺值机制继续验证（2026-10-15，当前任务）

- 用户要求继续推进缺状态/证据准入差异，并加入B06/S02/S04形成七案例表。新目录working/exploration/20261015_seven_case_mechanism/；SEVEN_CASE_TABLE_CN.md和21行CSV已按两批原件核对、独立344检查通过，A旧三例复演/B新四例共同目标分列，不能汇总同协议准确率。
- 静态归因发现：B17/B19缺值deny来自候选on_missing=deny（schema允许skip）；B19空/未知类型deny来自允许式DNF。full准入不强制该缺值选择。B06的P2P已有缺值deny反例，不能概括为两同行均无法安全缺值处理。
- 已按当前用户继续推进授权启动零API本地机制对照：mechanism_control/TASK_CONTRACT_CN.md、PROTOCOL_CN.md冻结；独立lane /root/ecas_missing_state_mechanism_20261015，T0 17项实际SUCCEEDED、真实scope gate ready。run_id missing-state-mechanism-v1已单次SUBMITTED；查询原run，不重复start。
- 对照ECAS原/仅skip × full/shape，以及两基线原Rego/原Rego+人工状态guard，18相关输入/144行观察；新增2个B19部分缺值仅观测，不设业务gold。无模型调用、不使用上轮剩余预算、不改原件或根科学账本。


## 共同目标与证据机制实验全部完成（2026-10-15，当前入口）

- 总中文简报working/exploration/20261014_matched_evidence_labor/EXPERIMENT_SUMMARY_CN.md；主比较、生成方式、同候选证据消融、同候选Judge均完成。下方运行中条目作为历史保留，不再续跑；本轮无待调用模型或待修复运行。
- 主run matched-generation-main-resume-v3实际SUCCEEDED，12分支、30实际调用；ECAS四例首次合格且原请求对全对，P2P/AutoPAC适配版后三例成功，S03分别范围外及两次无效OPA函数编译失败。方法调用ECAS4/P2P13/AutoPAC9，另4小试；567项主对账及独立412项（168实际复演）通过。报告matched_generation/results_review_v1/RESULTS_CN.md。
- Judge pilot-v1与typed-ir-judge-control-v3实际SUCCEEDED，首条精确复用，共4条/全轮34条≤44；没有重试或追加调用。8个原历史候选full准入/shape编译均通过，Judge指出其中3个已证实主语义缺陷，另5ACCEPT；B19 skip附加理由依据不足，不能把Judge当gold。judge_control/RESULTS_CN.md及FINAL_RECONCILIATION.json 185项通过。
- 证据消融在11父候选/95变体行上显示特定Inventory注册绑定阻断；其中73机制行、22schema行，不是95独立案例。4类元数据失效各11及7路径挑战被full拒绝；3个语义错仍准入，locator/hash11仍准入。7旧案例、原两个项目、单轮暴露任务；不宣称普适性、稳定排名、来源/可信状态真实性或人工劳动节省。
- 全轮glm-5.2 enabled/high，input152100/completion52326，金额UNKNOWN；main30+Judge4=34，剩余预算不使用。scope账本main13行/Judge8行；根科学账本、论文、旧原件及投稿未改。根T0目前指Judge v3，先前pointer已备份。后续新实验须另按当前授权和门禁，禁止据本轮剩余10次自动调用。


## 主比较已完成、同候选Judge继续（2026-10-15，当前状态）

- 主run matched-generation-main-resume-v3已实际SUCCEEDED/exit0，12方法×案例终态、30模型调用，全部已完成；首轮冻结先于最终评价。结果matched_generation/results_review_v1/RESULTS_CN.md，567项原件/政策复演、独立412项（168实际复演）通过。ECAS原请求对4/4，两同行适配各3/4；P2P S03范围外，AutoPAC S03两次不存在的OPA函数编译失败，未执行不当正确拒绝。方法调用分别4/13/9，另4小试。scope本地追溯13行，根科学账本不改。
- Judge内部控制pilot-v1实际SUCCEEDED，已跑最长B19一条，真实MCP token gate PASS；其余3条在typed-ir-judge-control-v3单次SUBMITTED（/root/ecas_semantic_judge_control_20261014/managed_runs/typed-ir-judge-control-v3）。查询原run，不重复start。当前主30+Judge4计划=34≤共享44。它是typed IR按源语义内部控制，非AutoPAC原版性能；准备v3 T0 35项、QA95项通过、真实scope gate ready。
- root T0 pointer现指Judge v3；原主pointer保存在judge_control/PREVIOUS_ROOT_T0_EVIDENCE.json。生成方式与证据消融均完成。论文/旧结果/根账本/投稿状态保持。


## 统一任务实验恢复已提交（2026-10-15，取代下方中断状态）

- 当前实际运行更新为matched-generation-main-resume-v3（同lane managed_runs下同名目录），单次SUBMITTED，查询该run。v2新增14/15响应完整后，被OPA注释大写Location.file路径元数据误拒；不是规则变化。25项独立核验确认规则/注释文本相同、6组合成开发输入相同；v2失败保留在setup_history/as_run_main_resume_v2。最窄修复归一化location/Location，3个回归确保规则/注释变化仍检出。v7 T0 68项、v3独立70项、77请求输入通过；15原响应精确复用，新付费重试0，final此前未读。

- matched_generation/main-resume-v2已单次提交：run_id matched-generation-main-resume-v2，run_dir /root/ecas_matched_generation_20261014/managed_runs/matched-generation-main-resume-v2；SUBMITTED不是完成。只查询原运行，不重复start。
- P2P的可见ID+真实标题locator兼容修复已通过65项T0和79项独立核验；13条原prompt/raw/output精确匹配，原测试输入/标签/引用/政策不变，最终标签此前未读。旧失败与as-run快照保留，未付费重调缓存。
- 真实MCP scope gate ready=true，root T0指向v6，74请求输入哈希验证通过。当前继续同一44次总授权的未调用分支；glm-5.2 enabled/high、每次input/completion≤16384、最多一次开发修复，不自动付费重试。
- 生成方式矩阵及证据消融已完成；三方法均模型自动生成，不做人工计时或人时节省估计。Judge同候选内部控制正修正实际成功run身份绑定，尚未调用。主运行成功后才可审批且共享44次cap。论文、旧结果、根科学账本和投稿不改。


## 统一任务与证据机制实验续接（2026-10-14，当前工作）

- 当前用户授权按诊断路线开展实验并增加生成方式/证据驱动比较；随后澄清不要求人工效率计时。新scope working/exploration/20261014_matched_evidence_labor/，任务契约TASK_CONTRACT_CN.md；人工study取消，不将非聊天LLM视为人工。
- human_effort/MODE_FEATURE_MATRIX_CN.md已按原文确认：P2P提示LLM生成，AutoPAC微调CodeT5-small自动生成，当前三适配均GLM。另比较领域微调、输入来源、规则追溯、硬准入与Judge/工具；不预填劳动节省数字。
- evidence_ablation/已完成零模型同候选有/无契约对照：7例11父候选、95变体行（73机制对照、22 schema控制分列）。独立重算hash/逐行结果无错配；完整契约阻断Inventory已声明不足/版本错配/未绑定等构造挑战，3个历史语义错误候选仍通过。不能概括为自动证明原文充分性、原文真实性或总体优于AutoPAC。最终派生Windows交付正在核验，as-run脚本/结果不改。
- matched_generation/新四例三流程harness已通过T0 v4及独立原件核验，真实MCP scope gate ready；已单次提交模型小试matched-generation-smoke-v1，run_dir /root/ecas_matched_generation_20261014/managed_runs/matched-generation-smoke-v1。查询原任务及CALL_LEDGER.json，不重复start。效果任务尚未启动；新token小试通过后才派发matched-generation-run-v1。glm-5.2 enabled/high，每次input/completion≤16384，总≤44含小试/限定修复。公共目标明确、完整原语说明、每例至多一次开发修复，失败后不获执行资格；不同方法内部Judge/测试/调用链与成本分列，不称完全相同监督或稳定优势。
- 小试原run FAILED(exit2)保留；第3仅做本地外包装恢复，IR/raw/usage不改，无付费重试。恢复run matched-generation-smoke-wrapper-recovery-v2已SUCCEEDED，复用01/02/03，仅新增原计划04，真实token门禁PASS。v5 T0和64文件hash独立通过；实际小试4次。已单次派发主run matched-generation-run-v1，run_dir /root/ecas_matched_generation_20261014/managed_runs/matched-generation-run-v1，当前RUNNING；从原run/CALL_LEDGER查询，不重复start，最终效果尚未生成。
- 主run-v1现已FAILED(exit2)：B13 P2P开发测试source_ref使用VIS-FSV-B13-01#实际章节标题，接口严格ID检查误拒。13条调用均已完成、raw/测试输入/标签未改；独立原文核对标题真实存在。当前仅修正来源locator表示兼容并补新T0/as-run快照，显式resume新run复用全部已完成原件，不付费重调；final_evaluation_read=false，最终效果未生成，不把此工程失败算同行识别失败。
- 每个新任务独立WSL lane、managed run_id和原件hash；不得重复start。根T0_EVIDENCE.json已指向本scope，旧pointer存matched_generation/PREVIOUS_ROOT_T0_EVIDENCE.json。论文/既有冻结结果/根科学账本/投稿状态未改。

## ECAS与AutoPAC差异的只读诊断（2026-10-14）

- 用户质疑当前ECAS优势；新增诊断working/exploration/20261014_experiment_review_brief/ECAS_AUTOPAC_DIAGNOSIS_CN.md。原件及两名独立只读复核确认：ECAS记录共同开发测试失败后仍冻结并离线评价（run_pilot.py:185、run_documented_ecas.py:50），AutoPAC有Judge/开发修复，当前终态表不等价于同监督预算排名。
- S03还存在单规则/多约束输入与目标指定风险；ABI突出age但无独立目标规范，不能把误选全归于模型或表达能力。B17/B19反向/错误原语候选获准入说明本契约语义粒度有限；论文已有Inventory相对保证未被直接反证。
- 后续优先统一任务范围与修复条件，再检验相同候选有/无契约和强基线已有Judge/工具之上的增量；不要继续以增添旧成功案例代替优势证据。新实验/外部调用0，未改论文、历史原件、根科学账本、投稿状态或原简报。

## Gemini评估简报已交付（2026-10-14）

- 用户要求把近期实验写成简报，计划自行让Gemini评估。已交付working/exploration/20261014_experiment_review_brief/ECAS_EXPERIMENT_BRIEF_CN.pdf（4页）及同内容MD/TXT、GEMINI_REVIEW_PROMPT_CN.txt、ECAS_REVIEW_EVIDENCE_EXCERPTS_CN.txt。
- 简报覆盖历史候选重放及27+38次同行适配比较，原请求圆圈与两ECAS配置由原始结果生成；S03小数漏放、v1 B17/B19失败、v2 S03失败、B19候选相关缺状态行为及来源/监督缺口保留。不能将其解释为已证明优势或普适性。
- PDF四页已视觉核读，BRIEF_QA.json 34项PASS，SOURCE_MANIFEST.json绑定来源。本次没有新增模型、实验或Gemini调用，也未自动发送。它是供审查的材料，不是Gemini已返回的意见或投稿冻结。
- 下一步可据作者转回的Gemini意见定点核验；需要具体论文段落或原作材料时再补，不从简报自行推定完整论文主张。论文和既有实验状态保持。

## 四例同行基线比较完成（2026-10-14，取代下方运行中状态）

- 当前结果入口working/exploration/20261014_four_case_peer_baselines/RESULTS_CN.md。S03/B13/B17/B19的P2P/AutoPAC及共同GLM5.2 ECAS已实测；38次enabled/high调用（4小试、34方法/配置调用含5开发修复及4次ECAS配置补跑），input176755/completion79327，费用UNKNOWN，≤40次。
- 基本原请求对：P2P S03范围外，后三例在接口/格式恢复后allow/deny；AutoPAC四例allow/deny。ECAS结构提示v1 S03/B13allow/deny、B17deny/deny、B19deny/allow；补全全部15原语说明的v2 B13/B17/B19allow/deny、S03allow/allow。禁止逐例选两配置最好结果拼成ECAS四例全对。
- 原schema-only ECAS缺用途说明是本轮准备缺口；v1失败保留，不冠以完整方法复现。v2虽修正B17，S03却选allowed_fields漏整数；一例一次、无seed不能从差异识别单一提示因果收益。准入通过不充分保证来源语义或目标覆盖。
- 分支反例：AutoPAC S03修复is_integer→is_number后仍放行31.5；B19缺可信状态时P2P/AutoPAC及ECAS v1 allow，仅ECAS v2 deny。v1 B19将禁止条件写成允许分支，且on_missing=skip；v1 B17状态缺失也允许。P2P在冻结且空/未知类型也allow；AutoPAC该两控制deny。控制与实际业务效果单列，不增加独立案例/样本，不声称ECAS始终失败闭合。
- P2P B13只把精确中立对象转为原组织schema id，不改条件、不重复检测/抽取调用；B17/B19 OPA fmt复演AST除location外相同。原effect_runs与EXECUTION_STATE全部保持，派生format_recovery/、format_replay/及documented_ecas/独立。
- 36项来源变换核验、107项raw/规则/实际执行对账、独立PowerShell179唯一冻结文件/38raw/12结果行验收均PASS。五个managed run均SUCCEEDED，无运行任务，不重复start；剩余2次预算不自动使用。
- 本轮不能支持“另有三四例只有ECAS成功”；可以说明多个同行流程也能提取业务条件，并报告局部结构/缺状态差异及生成不稳定。原版P2P/AutoPAC仍未运行；旧两项目、已暴露任务、无真实API转发/状态接入或普适性证明。论文、根历史账本、投稿状态未改。

## 四例同行基线比较已启动（2026-10-14，当前运行入口）

- 当前用户明确要求开始P2P/AutoPAC同行基线测试；新范围S03/B13/B17/B19，另跑同模型ECAS。目录working/exploration/20261014_four_case_peer_baselines/；授权、任务契约和协议已保存。GLM5.2 thinking enabled/high，总≤40次、单次输入/完成各≤16384 tokens；不借用前三例30次授权。
- 完整中立subject/action/resource对象ABI在生成前说明，三方法共同开发测试已冻结；完整业务条款保留，通用REST只保留Create，字段目录固定剔除布局控件。原片段及两次机械变换存档；Model IR参考因子化保留全部15原语及单规则限制，完整原schema负责验证。
- 本轮独立WSL lane /root/ecas_four_case_peer_20261014，14项T0通过，scope gate ready=true，Git缺commit为warning。根T0_EVIDENCE.json指向新scope，旧pointer另存PREVIOUS_ROOT_T0_EVIDENCE.json，旧receipt未改。
- 三流程token小试已单次提交run_id four-peer-token-smoke-v1，run_dir /root/ecas_four_case_peer_20261014/managed_runs/four-peer-token-smoke-v1。查询原任务，不重复start。CALL_LEDGER.json记录真实调用；小试通过后才派发four-peer-effects-v1。
- 原版复现资格缺口继续保留；本轮结果只称适配版。首次约束/修复与最终判断分列；未完成时不写圆圈胜负。未改论文、旧实验、根科学账本或投稿状态。

## 四例扩展筛选完成（2026-10-14，当前案例发现入口）

- 用户希望在已有区分性案例之外找3–4例，支持非单案例及更广适用性。已核验原两项目的S03/B13/B17/B19；报告working/exploration/20261014_multi_case_extension_screen/REPORT_CN.md。
- 历史GPT四例均完成规则编译、证据准入、原请求allow/deny；24项分支/缺状态/客户端伪装工程探针全部符合本轮预期。12个历史候选中9个准入并执行18条原请求、2个弃权、1个准入拒绝；7个请求对正确、2个DeepSeek反向请求对保留。87份输入哈希一致，PowerShell原件/输出对账PASS。
- Qwen仅S03请求对成功，B13缺binding fact被V3准入拒绝、B17/B19原弃权；DeepSeek B17/B19通过准入但逻辑反向。不得把历史GPT成功概括成所有模型稳定成功；证据准入不充分保证规则逻辑正确。
- S03为strict_type，B13/B17/B19共用bounded_guard_dnf。这是四个不同目标约束及旧候选离线展示，不是四种独立机制、新独立样本、生产转发或普适性证明。可信上限计算、真实状态/身份接入、创建/提交时点及文档与后端版本一致性仍待核。
- 四例P2P/AutoPAC均NOT_RUN，不能预填失败或优势圆圈。前轮27次GLM5.2调用及30次上限限定B06/S02/S04，新四例付费比较范围/预算尚未授权；下一轮先固定中立ABI、相同监督和预先选择规则类别。本轮新模型调用0，论文/旧实验/根账本/投稿状态未改。
- SUMMARY.json保留REPLAY_ISSUES；归档已完成，不重复start。BRANCH_PROBES.json及OUTPUT_RECONCILIATION.json是现有核验入口。

## 三例阶段表已核对（2026-10-14）

- 作者要求用○/◐/●展示差异并定位在哪一步判断。交付working/exploration/20261014_external_baseline_pilot/STAGE_COMPARISON_CN.md；未新增调用或改稿。
- 关键阶段差异：ECAS三例首次候选生成已有目标原语；P2P B06在检测/DSARCP抽取找到条件，S02检测范围外，S04首次只提取身份权限、修复后仅string；AutoPAC B06首次生成含条件，S02白名单及S04格式在操作者开发测试反馈修复后才出现，S04 Judge此前ACCEPT了无格式规则。
- 圆圈仅表示目标功能落实程度。范围外不是错判；编译失败不是半数请求正确；实际请求拒绝出现在执行器，证据准入检查候选资格。此三例不能隔离证据契约相对同候选无契约执行的因果增量。

## 三例外部适配比较完成（2026-10-14，当前结果入口）

- 当前中文报告：working/exploration/20261014_external_baseline_pilot/RESULTS_CN.md；模型原始批次FINAL_SUMMARY.json、CALL_LEDGER.json、effect_runs/；两套统一接口复演binding_replay/与binding_replay_resource_object/，不可混称新正式效果。
- GLM5.2 enabled/high共27次（4开发smoke、23方法阶段含5修复），actual input104975、completion66728，费用未报告。没有越过30次总上限；第3次schema失败与第6次状态词本地恢复保留，未重写raw或隐藏失败。
- 九个方法/案例分支已结束。事后统一格式与中立元数据映射后，B06 P2P/AutoPAC/ECAS皆allow/deny；S02 P2P范围外、AutoPAC已看到字段约束但is_integer编译失败、ECASallow/deny；S04 P2Pallow/allow漏格式、AutoPAC资源对象映射后allow/deny、ECASallow/deny。
- Harness原resource为字符串，部分候选期望资源对象；使用原可见id/system/version元数据做两套对所有方法相同的本地复演，保留原误拒，政策AST不改，不新增模型调用或独立样本。AutoPAC S04正则单独匹配合法开发邮箱，转义错误假设已证伪。
- 105项输入/原响应/策略AST/请求映射/OPA决策/预算对账PASS。不是原版性能、盲测、整体排名或全文科学PASS。原P2P代码、AutoPAC微调权重仍缺，两个原版NOT_RUN。
- 关键待核对：B06只限制Re-Age撤销而target为通用undo；删trusted标志后P2P/ECASdeny、AutoPACallow（事后诊断）。S02封闭字段约定不是OpenAPI默认语义；必须补权威来源并同等提供后再做正式比较。
- 模型batch runner external-three-case-effects-v3已SUCCEEDED，原状态/运行证据在/root/ecas_external_pilot_20261014/managed_runs；无需再start。不要重跑已计费调用。论文、旧实验、根结果账本、投稿状态未改。后续正式比较应先固定完整ABI、适用范围及相同监督；本轮不以工程修复后的成功行冻结优越性主张。

## 三例外部适配比较已授权执行（2026-10-14，当前运行入口）

- 用户已同意具体GLM5.2方案，并要求持续执行、不重复确认。授权见working/exploration/20261014_external_baseline_pilot/AUTHORIZATION_CN.md。保持总调用≤30、每次输入/完成≤16384tokens，原版仍NOT_RUN。
- Linux OPA1.19.0、Regal0.43.0已恢复；11项本范围T0通过，范围门禁ready_for_formal_run=true（Git缺commit警告）。Linux运行目录/root/ecas_external_pilot_20261014；Windows只执行全局批准GLM wrapper及密钥加载。
- 第3次开发smoke原响应完整但3条规则违反原maxItems=1；原因是准备提示schema时遗漏此限制。没有删候选规则冒充PASS；恢复原限制并用一次预留调用检查新提示，共4次smoke，原失败保留。原v1冻结和脚本逐字节归档setup_versions/v1；v2总预算仍30、修复预留降为5。
- 当前token门禁PASS/16384，证据TOKEN_GATE_FAILED_V1.json及TOKEN_GATE_READY.json；EXECUTION_INPUT_MANIFEST.json绑定输入、工具、脚本及wrapper。
- 三例执行已通过官方WSL runner派发一次：run_id external-three-case-effects-v2；request见同目录external-three-case-effects-v2.request.json。查询原run_dir /root/ecas_external_pilot_20261014/managed_runs/external-three-case-effects-v2；禁止重复start新任务或重跑已计费调用。
- CALL_LEDGER.json为计费调用原始状态；EXECUTION_STATE.json和effect_runs逐例记录效果。当前正在运行，不称结果完成。成功后运行finalize_pilot.py对账，交付RESULTS_CN.md，更新项目入口。未经确认的状态不能从旧准备报告推断。

## 三例外部基线准备（2026-10-14，当前待决定事项）

- 用户已要求用P2P、AutoPAC测试B06/S02/S04；中文入口：working/exploration/20261014_external_baseline_pilot/REPORT_CN.md。
- 原版资格实查：P2P有界检索未找到可确认代码；AutoPAC官方固定提交218项完整树及空release缺必需微调权重。HF权重搜索网络失败，不能称没有权重。证据见NATIVE_QUALIFICATION.json。
- 共同源输入与评价请求分离，12文件哈希逐份核对一致；冻结Windows OPA四项人工工程对照PASS。model_calls=0，两个基线效果仍NOT_RUN，不能报告识别结果。
- 本范围正式gate仍block/T0_EVIDENCE_MISSING/scope=null；Regal缺依赖。当前工程PASS不是本轮完整T0。
- 具体适配草案见ADAPTATION_PROTOCOL_CN.md：P2P-style/AutoPAC-style/同模型ECAS，GLM/Z.AI glm-5.2 thinking enabled/high，最多30次、单次最多16384输入和16384完成tokens。价格未核实、不承诺人民币封顶。该配置尚未获得用户确定，不读key、不调用。
- 下一步需用户决定是否接受明确标注的替代实现与具体调用配置。接受后补本轮冻结/T0/Regal/token资格再执行；不重复归档回放、不改稿或旧实验。尤其AutoPAC更换CodeT5是重大偏离，不能作为原版性能。

## 三例基线对比完成（2026-10-14，当前案例分析入口）

- 作者要求记录案例来源并比较其他基线能否识别。报告：working/exploration/20261013_gateway_case_audit/baseline_comparison/BASELINE_COMPARISON_CN.md；CSV 与原始输出在 runs/three_cases_v1/。
- B06/S02 属于 Fineract，S04 属于 ERPNext，仍是原两个项目。S02 的 B1/B2、S04 的 B2 正确允许合法并拒绝违规；B06 的 B1/B2 原本无政策，全拒绝不得冒充识别。ECAS-P 与完整 ECAS 三例结果相同，不能由这些正例声称契约提升判定。
- 54 个历史方法请求回放一致、70 项输入哈希前后核对、独立 PowerShell 核对通过；15 项事后缺来源工程探针单列。未重新生成候选、未运行外部模型/正式实验、未改稿。P2P/AutoPAC 外部比较仍未实测，不从内部结果推断其能力。

## 三个额外案例演示完成（2026-10-14，作者澄清后当前入口）

- 作者确认已有案例仅指 FSV-B01，验证深度为候选→证据准入→请求允许/拒绝。当前交付是 working/exploration/20261013_gateway_case_audit/selected_case_demo/README_CN.md，逐例中文入口在 runs/three_cases_v1/INDEX_CN.md。
- 完整包在 working/exploration/20261013_gateway_case_audit/ECAS_THREE_EXTRA_CASES_REPLAY_20261014.zip；89 项打包文件逐份哈希回读一致，缓存排除。独立 PowerShell 对六十五份输入和九项配置输出核验通过。
- 固定 B06（贷款撤销可信状态）、S02（证件请求字段白名单）、S04（邮箱基本格式）；原 Qwen/GPT/DeepSeek 共九个归档候选全部显式准入，十八个合法/违规请求按预期，九个删来源对照均拒绝准入并 deny。六十五份冻结输入运行前后哈希一致。已保存引擎与 schema 的本包快照，运行只依赖相对路径。
- 完成状态为 THREE_EXTRA_CASES_DEMONSTRATED / ARCHIVED_CANDIDATES / LOCAL_ENGINEERING_REPLAY。候选生成沿用原件与回执；没有新模型调用。生产 API 转发、实时可信状态、新独立样本及外部基线比较均未由这些结果验证。R14 保持当前稿件入口，未修改正文。

## API 网关案例核验交接（2026-10-14）

- 本轮用户授权今晚用最多五小时查找已有案例以外 2–3 个可展示 API 安全网关功能的案例。已完成有界本地调查与离线工程回放；报告：working/exploration/20261013_gateway_case_audit/REPORT_CN.md。早于五小时上限收尾的依据是当前正式 scope 门禁阻断，且候选完整性缺口已查清。
- 旧 FSV 范围：B06、S02、B22 是三个互补演示；B22 原主试验 Qwen 对违规样本误放，必须并列说明。S04 可替换 B22 作稳定结构性正例；B16 因客户端 credit_exposure 与创建/提交时点问题不推荐作安全效果主例。GPT/DeepSeek 五例 20 条历史请求离线重放一致，13 条新工程探针按预期；原 Qwen B06/S02/S04 六条重放一致。结果仅为回顾性一致性核验。
- 新独立系统候选：Blnk、Saleor、Formance 具有版本化 API、两次原生正反例和静态基线语义缺口；尚无当前 V3 完整模型生成、证据准入及真实网关转发轨迹，不写为新完整案例。Stage 4.1 Blnk/Bigcapital 使用 Rego 输出，不等于当前 V3。
- 本次正式门禁 block / T0_EVIDENCE_MISSING / experiment_scope=null；本次未调用外部模型或付费 API、未启动 Docker/GPU、未修改 R14/R12/Revision 3/旧实验。下一步若启动新系统正式实验，先冻结准确 API 操作和可信状态接口，补本次 scope 的 T0、模型与预算、独立请求及真实转发验收；外部 P2P/AutoPAC 比较仍独立待办。

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


## 历史：R13 中文阅读版（2026-10-13，底稿已被作者否定）

- 用户明确要求“给我一个中文版，我看下”，已按academic-zh-translator完成R13主稿中文阅读版：`working/paper/retarget/ASE_20261013_MAJOR_REVISION_R13/delivery/ECAS_ASE_R13_MAIN_CN_REVIEW_20261013.pdf`。
- 主稿内容、表格、图及声明已译，参考文献/正式机构信息保留英文；共24页、正文18页。GLM5.2关闭thinking，9个计划调用全部正常返回且原始响应保留，无模型重试；Codex本地校正和独立核验记录在translation_cn/R13_MAIN_CN_20261013/qa。
- 中文用于作者核读，英文R13和实验保持；未把中文翻译验收作为科学冻结、作者终稿确认或投稿许可。下一步等待作者批注，英文/中文修改应以英文权威语义对应。

## 历史：R13 压缩大修稿（2026-10-13，已被作者否定）

- 状态：`R13_AUTHOR_REVIEW_DRAFT / STRUCTURE_REVISION_COMPLETED / EXTERNAL_COMPARISON_PENDING / NOT_SUBMISSION_FROZEN`。
- 用户本轮明确要求大幅压缩、正文约20页、必要证明和细节转补充文档、逐条遵循全部意见；同意P2P并要求再找一个基线。该授权取代下方历史“仅讨论、未授权改稿”限制；不授权新增模型实验、训练、付费调用、发送、发布或投稿。
- 当前新版本：`D:/lunwen/EC-CSI投稿/working/paper/retarget/ASE_20261013_MAJOR_REVISION_R13`。主稿21总页，标题摘要至结论17页；补充15页。当前核读入口为 `delivery/R13_REVISION_REPORT_CN.md`、主稿/补充PDF、逐条矩阵与英文回复草稿。
- 主要修订：FSV-B01同一冻结贷款轨迹贯穿§3；术语首次解释；正文两个核心公式；完整形式化/协议/逐任务结果转Supplementary Methods；新矢量流程图和可读表；保留原负结果及全部追加配置，分开政策生成与契约增量。
- 外部基线建议：P2P + AutoPAC。AutoPAC官方来源与公开代码已静态核验；缺checkpoint、许可与接口问题未解决。原版复现NOT_READY，自建只能声明style adaptation；没有新外部效果结果。
- 核验：最终主稿21页、补充15页逐页视觉检查；无溢出/未定义引用/重复标签/字体警告。核心数字92项定点重聚合；24项定点源一致性检查中的2项释义建议已修。24条冻结文件快照哈希一致。对应报告在qa和review_control。均不代替全文科学或复现冻结。
- 全部33工作项已独立登记实际修改、位置、状态和英文草稿。E05/E06/E09/R2-06/R2-07等证据/总体闭环项仍部分完成，按矩阵实际状态为准。邮件通知日期、可能附件和硬截止设置仍由作者核实。
- 下一步：作者核读；设计匹配的P2P/AutoPAC比较协议并取得具体实验授权；完成公开artifact回放/复现及引用/源包验收；按新证据补回复、再冻结正式修回包。
- 冻结保护：已提交R12、Revision3、原实验和ESM_1.zip保持。不得用此新草稿或技术QA将历史失败改成成功。源包排除未引用旧R12 tex及第三方基线源码。
- 没有发送或投稿；无需再次询问已授权的压缩和文字修订是否继续。

## 历史：审稿意见讨论交接（2026-10-13，已扩展授权）

- 交接编号：`ECAS-REVIEW-HANDOFF-20261013-01`。
- 状态：已接手；接手方已完成只读核验，路径、R12 文件和授权边界一致，没有阻止第一步的差异。源对话编号未独立核实；接手对话编号：`01a133fb-c059-7f83-a31a-96da08db71ce`（local）。后续状态由接手方维护。
- 用户明确要求：“投稿意见已经出来了，我们新开对话讨论”。本次授权为保存交接、新建并打开同项目对话、分析意见和讨论处理方案；不包含直接修改投稿稿、发送回复、重新投稿、付费模型或实验。
- 目录：`D:\lunwen\EC-CSI投稿`。2026-10-13 核实 `C:\Users\PBCDCI\Documents\EC-CSI投稿` 仍为指向该目录的 Junction，可用于已注册 Codex 项目接续；不要与 `D:\lunwen\ec` 合并。

### 当前已知与待核实

1. 当前投稿是 *Automated Software Engineering* 专刊 `Special Issue on Software Engineering for and with Trustworthy Large Language Models`，不是历史 CSI 投稿。
2. 题名：`ECAS: Evidence-Contracted Construction and Evaluation of LLM-Proposed Field-Level API Security Policies`。Submission ID：`71cf26a4-ec4f-4d3c-9334-0fa6b772e479`；2026-08-12 提交，SNAPP `v1.0`，基准为 R12。
3. 2026-10-13 用户在接手对话粘贴编辑决定、Reviewer 1–3 和修回说明，已读取并对照 R12 相关段落。正式决定是 `major revision`；门户原文建议在 2026-11-27 前修回。邮件通知日期、可能附件及门户是否另有硬截止设置仍待核实。下面 9 月的等待状态为历史，不再作为接续动作。
4. 用户此前提供的门户截图显示超过 10 位被邀请、4 位接受、3 份报告已收到，当时仍为 `Peer Review`；更早截图为 1 份。数量本身不说明意见倾向，也不说明必须等第 4 份。
5. 用户确认 9 月 21 日发过首封询问信；9 月 22 日 Journal Support 回信工单 `11807507`，当时只有 1 份报告，无法承诺决定日期。用户随后在本对话确认第二封礼貌跟进已发出，未独立核验发送回执，准确发送日期待邮件核实。学校要求 2026 年 10 月下旬汇报博士毕业相关进展，这是学校进度节点，不是期刊返修期限或接收期限。
6. 先前“是否做过完整参考文献确认和审计”的问题尚未在本对话形成完整验收结论；R12 两处引文排版修复不能代替 DOI/元数据/全文支持性审计。若意见涉及参考文献，再按 `reference-link-audit` 定位原始审计证据，不凭记忆宣称通过。

### 接手材料（已核对路径存在）

- 后续实验组织与基线建议：`working/review/20261013_ASE_MAJOR_REVISION/EXPERIMENT_AND_BASELINE_ADVICE_20261013_CN.md`。原主试验总体收益门失败；GPT 两方法政策任务结果相同，契约增量来自 7/9→9/9 控制停止。建议保留前期边界与全部追加结果，再准备公平外部比较。20篇 Automated Software Engineering 正式研究 PDF 已核验（16复用、4新下），报告为 `working/literature/ASE_LENGTH_SAMPLE_20261013/REPORT_CN.md`。
- 本轮原始意见：`working/review/20261013_ASE_MAJOR_REVISION/EDITOR_AND_REVIEWERS_USER_PASTED_20261013.txt`，与用户附件字节一致；初步判断及意见清单：同目录 `REVIEW_JUDGMENT_20261013_CN.md`。当前结论为值得认真修回，以全文可理解性、贯穿案例和结构压缩为重点；相关系统比较与可复现性须核对证据，未指定新增实验、未估算录用概率。
- 投稿版本说明：`working/handoff/HANDOFF_20260812_ECAS_ASE_R12_CITATION_FORMAT_FIX_CN.md`。其中“当前上传候选”是历史残留措辞，应与同文件正式提交记录及根目录记录合读，R12 已正式提交。
- 基准目录：`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R12_20260812/`。
- 实际系统稿：该目录内 `ECAS_ASE_PORTAL_GENERATED_R12_20260812.pdf`；本地核对稿 `ECAS_ASE_SUBMISSION_R12_20260812.pdf`；投稿源包 `ECAS_ASE_LATEX_SOURCE_R12_20260812.zip`；源码目录 `ECAS_ASE_LATEX_PORTAL_SOURCE_R12_20260812/`；补充材料 `ESM_1.zip`。此次仅核对存在与历史版本记录，未重新运行编译或科学验收。
- 原截图已从临时目录复制至 `working/handoff/ECAS_REVIEW_HANDOFF_20261013/PORTAL_3_REPORTS_USER_SCREENSHOT.png` 及 `SUPPORT_REPLY_20260922_TICKET_11807507.png`。它们是进度/客服证据，不是审稿意见；门户截图实际拍摄日期未知，20261013 是此次归档日期。
- 当前缺少 `PROJECT_BRIEF.md`；直接以本节及 `LATEST_OUTPUTS.md`、`RESEARCH_DECISIONS.md` 为接续入口，不为交接猜造科研结论。
- 原工作树已有大量未跟踪项目文件；不清理、不覆盖、不提交。交接前这三个被改状态文件的备份位于 `working/handoff/ECAS_REVIEW_HANDOFF_20261013/before/`。

### 新对话第一步与边界

接手核验及源对话继续指令已完成，由接手方维护状态。2026-10-13 意见原文初步分析已完成；下一步与用户讨论贯穿案例、全文重构方向和比较/复现证据缺口。

已收到编辑和三位审稿人正文，不重复索取已提供内容。当前阶段仅判断意见和讨论方案；进一步修改须由用户确认具体范围。意见没有明确指定新增数据集或实验，比较要求能否由现有证据满足仍待核对，不能先承诺不用实验或自动扩充实验。未完成全文科学有效性、实验数字、引用或返修冻结验收。

R12 和保险版 Revision 3 均保持不变；新修改须在用户确认具体范围后建立新版本。后续如起草逐条回复使用 `reviewer-response`，科学问题按 `senior-paper-review`，文献核验按 `reference-link-audit`；不要将用户的“讨论”扩大为付费调用或自动投稿授权。旧对话保留，不自动归档。

## Workspace Migration Completed (2026-09-04)

The canonical physical workspace is now `D:\lunwen\EC-CSI投稿`. The historical
path `C:\Users\PBCDCI\Documents\EC-CSI投稿` is a compatibility Junction whose
target is the canonical D-drive directory. The original C-drive physical tree is
preserved, without deletion, at
`C:\Users\PBCDCI\Documents\EC-CSI投稿_pre_migration_20260904`.

The final switch used a same-volume whole-root rename, a second read-only mirror
comparison after the rename, Junction target verification, and post-switch
backup-to-target verification. The final audit found 30,254 files, 3,251
directories, 0 mirror differences, 29/29 equivalent reparse points, and 19/19
matching root/key SHA-256 checks. C- and D-path reads of `HANDOFF.md` returned the
same NTFS File ID. Use the D-drive path for all new work; retain the C path only
for compatibility with historical tasks and absolute references. Do not delete
the dated backup without explicit author confirmation. Full evidence is in
`MIGRATION_REPORT_20260904.md`.

## ASE R12 in Peer Review at Automated Software Engineering (updated 2026-09-04)

R12 is the submitted manuscript. Open first:

`working/handoff/HANDOFF_20260812_ECAS_ASE_R12_CITATION_FORMAT_FIX_CN.md`

Primary delivery:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R12_20260812/`

R12 changes only two grouped author--year citations that R11 visibly rendered as
`n.d.b,n,n` on pages 6 and 34. The source references, undated status, claims,
experiments, figures, tables, declarations, cover letter, and `ESM_1.zip` are
unchanged. The 44-page PDF and 13-file ZIP were rebuilt; the corrected pages
passed visual review and an extracted ZIP rebuild passed. The author submitted
R12 through Springer Nature SNAPP on 2026-08-12. As observed on 2026-09-04,
the current state is `Peer Review`; technical check, editorial assignment, and
with-editor stages are complete. The portal states that the editor has invited
more than 10 reviewers and that 4 reviewers have accepted. An accepted invitation
is not evidence that a review report has been returned. Cheng Wang's portal affiliation duplication was corrected
before submission. The submission ID is `71cf26a4-ec4f-4d3c-9334-0fa6b772e479`,
submission version `v1.0`. The portal-generated R12 PDF and the 2026-08-20 and
2026-09-04 status screenshots are preserved in the R12 delivery directory.

## ASE R11 Text-Only Model-Label Package (2026-08-12)

R11 is the preserved predecessor of active R12. Its historical handoff is:

`working/handoff/HANDOFF_20260812_ECAS_ASE_R11_TEXT_ONLY_MODEL_LABELS_CN.md`

Primary delivery:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R11_20260812/`

At the author's direction, Figure 1 removes the five Qwen, DeepSeek,
Zhipu/GLM, Kimi, and OpenAI provider logos and retains only evenly spaced plain
text identifiers. The remainder of Figure 1 and all of Figure 2--6 are
unchanged. English and Chinese build to 44 and 35 pages, the affected English
page passed visual review, and the flat 13-file ZIP independently rebuilt to 44
pages from a new ASCII path. `ESM_1.zip` and the cover letter are unchanged.

R10 and earlier candidates remain preserved. The author is operating the portal
manually and reports that the manuscript file has been replaced with R11. The
Data Availability answer is `Yes`, with `ESM_1.zip` supplied as Supplementary
Information / Online Resource 1. Submission remains `NOT_SUBMITTED` until a
manuscript ID or formal receipt is recorded.

The live portal successfully converted R11 and its 44-page generated PDF is
text-identical to the local R11 PDF. A later fine-grained visual pass found the two
OWASP citation-format defects now repaired in R12, so R11 must not be submitted.
The portal-only affiliation duplication and optional preprint decision are recorded
in the active R12 handoff.

## ASE R10 Public-Supplement Alignment Package (2026-08-12)

R10 is the preserved predecessor of the active R11 candidate. Its handoff remains at:

`working/handoff/HANDOFF_20260812_ECAS_ASE_R10_PUBLIC_ESM_ALIGNED_CN.md`

Primary delivery:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R10_20260812/`

R10 aligns the manuscript, Data Availability, Supplementary Information caption,
cover letter, portal field sheet, and upload checklist with the public redacted
`ESM_1.zip` supplied as Online Resource 1. The package retains 30 primary Qwen3.6
raw responses, 120 normalized hosted-model candidates, and 780 evaluation-decision
records; hosted-provider raw API envelopes and reasoning traces are excluded.

English and Chinese build to 44 and 35 pages. The affected pages passed visual
review, the flat 13-file ZIP rebuilt independently from a new ASCII path, and the
69-entry public artifact passed its verifier and conformance smoke after a metadata-only
privacy clarification. No experiment, frozen result, external model, or portal state
changed. R9 and earlier candidates remain preserved. Submission remains
`NOT_SUBMITTED` until the author supplies a portal receipt or manuscript ID.

## ASE R9 Guidelines-Aligned Package (2026-08-12)

R9 is the preserved predecessor of the active R10 candidate. Its handoff remains at:

`working/handoff/HANDOFF_20260812_ECAS_ASE_R9_GUIDELINES_ALIGNMENT_CN.md`

Primary delivery:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R9_20260812/`

The source scripts confirm that Figures 3--6 were generated in Python using Matplotlib with SciencePlots styles, not TikZ; the manuscript and portal-field draft now state the graphics programs. At the author's direction, Codex, code debugging, consistency checks, and analysis support were removed from the public AI wording, and the English manuscript, Chinese review, and portal draft were synchronized.

English and Chinese build to 44 and 35 pages. The relevant pages passed visual review, and the flat 13-file ZIP independently rebuilt to 44 pages from a new ASCII path. No experiment, data, figure content, bibliography, reviewer artifact, external model, or portal state changed. R8 and earlier candidates remain preserved; submission remains `NOT_SUBMITTED` until the author supplies a portal receipt or manuscript ID.

## Historical ASE Portal Execution Handoff (2026-08-12)

This section records the pre-submission boundary and is superseded by the R12
submission record at the top of this file.

The author elected to perform the Springer Nature/ASE portal submission directly. Codex stopped before authentication and performed no login, metadata entry, file upload, draft creation, or final submission. The Edge login page was left open for the author.

R11 is now the active local package. Submission status must remain `NOT_SUBMITTED` until the author reports a successful portal receipt or manuscript ID. After submission, record the submitted date, manuscript ID, portal-generated PDF, uploaded-file list, and confirmation email/receipt; do not infer success merely from reaching the final review page.

## ASE R8 Author-Annotated AI Statement Package (2026-08-12)

R8 is the preserved predecessor of the active R9 candidate. Its handoff remains available at:

`working/handoff/HANDOFF_20260812_ECAS_ASE_R8_AI_STATEMENT_EDIT_CN.md`

Primary delivery:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R8_20260812/`

The author's Chinese-PDF page-30 deletion annotation has been applied to both language sources and all matching submission materials. The detailed GLM/Kimi/Claude/DeepL and early image-generation/provenance passage was removed; the concise ChatGPT/Codex assistance sentence and author review/responsibility sentence remain. English and Chinese build to 44 and 35 pages, the affected pages pass visual review, and the flat 13-file ZIP independently rebuilds from an ASCII path.

The internal provenance record is retained and the factual history is not rewritten by this manuscript edit. Before submission, the authors must confirm that the shortened statement satisfies the journal and portal's complete-disclosure requirement. A portal dry run and final-submit authorization remain pending; no submission occurred. R4--R7 and frozen Revision 3 remain preserved.

## ASE R7 Figure/Table Reference-Closed Package (2026-08-11)

R7 is the active local submission candidate. Open first:

`working/handoff/HANDOFF_20260811_ECAS_ASE_R7_CROSSREF_READY_CN.md`

Primary delivery:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R7_20260811/`

The complete source audit found that Figure 1--6 and Table 1--8 are all cited in body text outside captions/floats in both English and Chinese. R7 strengthens the early Table 1 introduction, the Table 2 record-chain explanation, the Table 3 denominator explanation, and the RQ3 reference to Figure 3(b). English builds to 44 pages; the flat 13-file ZIP independently rebuilds from an ASCII path; the Chinese review remains 35 pages. No experiment, data, figure content, reference database, or reviewer artifact changed.

Remaining gates are author confirmation and a live portal dry run. The submission has not occurred and is not authorized by this handoff. R4, R5, R6, and frozen Revision 3 remain preserved.

## ASE R6 Local Submission Package (2026-08-11)

The author approved both final A-version draw.io figures and asked to update the full manuscript for submission tonight. R6 is now the active local submission candidate; R4, R5 and frozen Revision 3 remain preserved.

Open first:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/README_CN.md`

Primary files:

- English PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/ECAS_ASE_SUBMISSION_R6_20260811.pdf`
- Flat LaTeX ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/ECAS_ASE_LATEX_SOURCE_R6_20260811.zip`
- Reviewer artifact: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/ECAS_ASE_REVIEWER_ARTIFACT_PORTAL_R6_20260811.zip`
- Chinese review PDF: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/ECAS_ASE_SUBMISSION_R6_20260811_CN_REVIEW.pdf`
- Author confirmation list: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_READY_R6_20260811/SUBMISSION_MATERIALS/TONIGHT_AUTHOR_CONFIRMATION_CN.md`

Technical closeout: English 43 pages, figures on pages 3/12, no undefined citations/references or overfull/fatal warnings; flat 13-file ZIP rebuilt independently from an ASCII path. Chinese review 35 pages, figures on pages 3/9. The artifact's manuscript locators are portable, and its verifier and fixed conformance smoke pass. No experiment, frozen result, reference database, or data figure changed.

Remaining gates are author- or portal-controlled: author/affiliation/ORCID mappings, contributions/funding/competing interests, originality and coauthor approval, Data Availability/public-release commitment, the unified AI statement, Figure 1 model-mark third-party-material handling, reviewer nominations, live Article Type/collection/upload fields, and the system-generated PDF preview. Portal submission has not occurred and is not authorized by this handoff.

## Editable Draw.io Figure Comparison (2026-08-11)

Figures 1 and 2 now have two separate, fully editable two-page draw.io candidates. The image-trace version follows the current R5 composition as closely as practical with native shapes; the prompt-redesign version uses the locally preserved Figure 1 prompts and the final Figure 2 design record to create a cleaner alternative. Both preserve the accepted compiler-before-Evidence-Contract order and the Figure 2 `Executable policy / To ECAS gateway` ending.

At the author's request, A Figure 1 now uses 11 native draw.io library stencils in place of the prior `DOC`/`AI`/`EC`/`OK`/`GW`/`API`/`TC`/`RP`/`DX`/`AU`-style text placeholders. The stencils remain independently editable, contain no embedded image or URL, and do not alter Figure 1 topology.

The A-version model strip was subsequently upgraded from Q/D/Z/K/O badges to five embedded SVG marks for Qwen, DeepSeek, Zhipu/GLM, Kimi, and OpenAI while retaining the model names. The Kimi upstream SVG uses a white K intended for a dark background, so only that fill is changed to near-black for the paper's white canvas; the blue dot and path geometry are preserved. The `.drawio` contains no raster logo or external URL.

The author selected A for continued editing. A Figure 2 now uses native draw.io icons for all six success-path nodes and all three fail-closed outcomes. `Typed candidate` uses a content-type stencil; `Unsupported / unbound` uses an editable link-plus-failure composite. The three failure arrows are exact straight vertical centerline connections. Independent visual and structural review found no clipping, collision, distortion, topology change, edge crossing, or through-vertex edge.

Editable sources:

- `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/drawio_conversion/ECAS_Figures_1_2_Image_Trace_20260811.drawio`
- `working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/drawio_conversion/ECAS_Figures_1_2_Prompt_Redesign_20260811.drawio`

QA and provenance record:

`working/paper/retarget/ASE_20260803/analysis/submission/DRAWIO_FIGURE_COMPARISON_20260811_CN.md`

No ImageGen, external model, paid API, experiment, result change or portal action occurred. A is the author-selected continuation candidate, but Figure 2 author confirmation, final embedded export, and any R5 integration remain separate pending decisions.

## Native PowerPoint Figure Redraw (2026-08-11)

Figures 1 and 2 have been redrawn as a two-slide, fully editable PowerPoint source. Every box, label, arrow, dashed region, failure branch, and model badge is an independent native PowerPoint object. The deck contains zero embedded picture objects and zero `ppt/media/` entries. The model-family names remain as scientific identifiers of the evaluated proposal models; graphical Logos were replaced by editable letter badges.

Primary editable source:

`working/paper/retarget/ASE_20260803/manuscript/figure_candidates/20260811/ppt_conversion/ECAS_Figures_1_2_Native_Shapes_20260811.pptx`

QA record:

`working/paper/retarget/ASE_20260803/analysis/submission/NATIVE_POWERPOINT_FIGURE_REDRAW_20260811_CN.md`

The redraw used local Microsoft PowerPoint shapes only and made no ImageGen, external-model, or paid-API call. It is an author-review source candidate and has not yet replaced the R5 manuscript figures. Final package construction and portal submission remain pending.

## R5 Figure-Semantics Preview (2026-08-11)

The R5 submission-source candidate contains two bounded, local deterministic figure corrections. Figure 1 now follows `proposal → deterministic validation/normalization → Evidence Contract → executable policy → gateway`; Figure 2's final box now reads `Executable policy / To ECAS gateway`. The original model row and Logos remain because they identify the evaluated proposal-model configurations. No ImageGen or external model was called in this edit.

An independent R5 build produced 43 pages with Figure 1 on page 3 and Figure 2 on page 12, with zero overfull boxes, undefined citations, undefined references, or regular LaTeX warnings. Full-size and page-scale visual checks found no visible seams, clipping, overlap, border damage, or arrow damage.

Detailed record:

`working/paper/retarget/ASE_20260803/analysis/submission/AI_FIGURE_DISCLOSURE_AND_SEMANTIC_VERIFICATION_20260811_CN.md`

Author visual-preview PDF and pages:

`working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_CANDIDATE_R5_VISUAL_PREVIEW_20260811/`

Status: `AUTHOR_VISUAL_CONFIRMATION_PASS / EDITABLE_FIGURE_SOURCE_SELECTION_PENDING / FINAL_PACKAGE_NOT_BUILT / R4_AND_REVISION3_PRESERVED / NOT_SUBMITTED`.

## ASE Submission-Stage Entry (2026-08-11)

The author has accepted the current Figures 1 and 2 for transition into submission preparation. The isolated R4 candidate is the submission-stage working authority; it is not yet a final frozen package and has not been submitted. Revision 3 remains the immutable insurance fallback.

Authoritative continuation handoff:

`working/handoff/HANDOFF_20260811_ECAS_ASE_SUBMISSION_STAGE_ENTRY_CN.md`

The next task must first re-verify current official ASE/special-issue requirements, then close author metadata/declarations, scientific traceability, page/image/citation QA, clean-package recompilation, cover letter, and portal dry-run gates. Actual portal submission, external paid-model calls, and new experiments remain separately approval-gated.

## Current Figure-Enhancement State (2026-08-11)

Figures 1 and 2 are now integrated in an isolated R4 figure candidate without overwriting the R2 delivery or frozen Revision 3 insurance package. Both figures retain the approved ImageGen content and Times New Roman visual styling, while their top/bottom canvases are deterministically cropped to approximately two high-resolution pixels of safety margin. Figure 1 is 4800×1566; Figure 2 v6 is 4800×1357. No text, icon, arrow, or diagram content was redrawn or stretched. Superseded variants remain provenance-only candidates.

Current candidate PDFs:

- English: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_DRAFT_R4_FIG1_FIG2_20260811/main.pdf` (43 pages; Figure 1 on page 3; Figure 2 on page 12).
- Chinese: `working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_SUBMISSION_DRAFT_R4_FIG1_FIG2_20260811_CN_SOURCE/main.pdf` (35 pages; Figure 1 on page 3; Figure 2 on page 9).

Detailed QA and Figure 2 review:

`working/paper/retarget/ASE_20260803/analysis/FIGURE_1_FINAL_INTEGRATION_AND_FIGURE_2_REVIEW_20260811_CN.md`

`working/paper/retarget/ASE_20260803/analysis/FIGURE_2_IMAGEGEN_FINAL_INTEGRATION_20260811_CN.md`

Next manuscript action: continue the remaining figure discussion, followed by the final page-length/image/grayscale/clean-package submission gates. Ultra-tight Figures 1 and 2 passed English pages 3/12 and Chinese pages 3/9 visual QA. No external paid model was called.

## Current Author-Annotation R2 Delivery (2026-08-10)

The author-completed Chinese-PDF annotations have been integrated into a new English-authoritative R2 draft and synchronized Chinese review version. Detailed handoff:

`working/handoff/HANDOFF_20260810_ASE_AUTHOR_ANNOTATION_R2_CN.md`

Current status:

`R2_READY_FOR_FIGURE_ENHANCEMENT / AUTHOR_ANNOTATIONS_INTEGRATED / BILINGUAL_QA_PASS / CLEAN_PACKAGE_SMOKE_PASS / FIGURES_UNCHANGED / REVISION3_INSURANCE_UNCHANGED`

Primary delivery:

- `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810/`
- `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_R2_20260810_BILINGUAL/OPEN_ME_ECAS_ASE_R2_20260810_BILINGUAL.html`
- English: 43 pages; Chinese: 35 pages; English abstract: 229 words.
- Next manuscript task: discuss figure enhancement, then rerun length and final-submission gates.
- No external paid-model call was made in this R2 revision.

## Current Manuscript Delivery (2026-08-10)

The current author-review candidate is the ASE-formatted, paid-prose-primary submission draft. Its detailed handoff is:

`working/handoff/HANDOFF_20260810_ASE_SUBMISSION_DRAFT_AND_GLM_CN.md`

Current manuscript status:

`ASE_SUBMISSION_DRAFT_READY_FOR_AUTHOR_REVIEW / GLM_CN_REVIEW_VERSION_READY / FIGURES_UNCHANGED / REVISION3_INSURANCE_UNCHANGED`

Primary deliverables:

- English PDF and LaTeX source are under `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810/`.
- Chinese PDF and LaTeX source are in the same delivery directory and are for internal annotation only.
- The synchronized bilingual review page is `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_SUBMISSION_DRAFT_20260810_BILINGUAL_FINAL/OPEN_ME_ECAS_ASE_20260810_BILINGUAL.html`.
- The next manuscript task is author review, followed by a separate figure-enhancement discussion. No figure was redesigned in this round.
- The frozen Revision 3 PDF/source remains the submission-insurance fallback and was not overwritten.

Current authoritative handoff:

`working/exploration/20260807_stage4_five_model_smoke/historical_alignment/preformal_qualification_v1/QUALIFICATION_CLOSEOUT_CN.md`

Current status:

`ASE_SUBMISSION_INSURANCE_FROZEN / REVISION3_AUTHORITATIVE / STAGE2_SUCCESS / STAGE3_SUCCESS / STAGE4_1_QUALIFICATION_SUCCESS / FIVE_MODELS_20_OF_20_PASS / FORMAL_PIPELINE_READY / FORMAL_ECAS_NOT_RUN`

Current next step:

- Stages 1--4.1 have succeeded at their declared non-scientific engineering scope. After Qwen/GLM recovery, the fresh five-model qualification passed 20/20 with zero model retries and all raw responses preserved.
- Current Stage 4.1 authority is `working/exploration/20260807_stage4_five_model_smoke/historical_alignment/preformal_qualification_v1/QUALIFICATION_CLOSEOUT_CN.md`, `QUALIFICATION_FINAL_AUDIT.json` and `QUALIFICATION_FINAL_MANIFEST.sha256`. Earlier failed rounds remain historical diagnostics.
- The technical pipeline is ready; the next action is to draft and freeze the answer-free formal ECAS-versus-Direct protocol. Qualification prompts cannot be reused scientifically without leakage/fairness review.
- Goal-mode plan: `working/exploration/20260807_stage2_task_oracle_freeze/STAGE2_TASK_ORACLE_FREEZE_GOAL_PLAN_20260807_CN.md`.
- WP0 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP0_AUDIT.json` (`PASS`). No model, ECAS, Direct-Rego, paid API, GPU or new Docker/WSL experiment was used.
- WP1 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP1_AUDIT.json` (`PASS`); manifest SHA-256 `23D6B5AB381CE67D0DC596ED2EA12D19215E72E9EFEBA9C9841C6C15548FDE3C`.
- WP2 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP2_AUDIT.json` (`PASS`); 87-entry manifest SHA-256 `CE3B7E24DA531E043E57D048E3E2AEA4CE64218E84D3CAF2712524E582682F8A`.
- WP3 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP3_AUDIT.json` (`PASS`); 521-entry manifest SHA-256 `7EE8DB8CB9EE99CB9C0812FFD111F5E0F115F22C044146A94943A477F9903528`.
- WP4 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP4_AUDIT.json` (`PASS`); rule-Oracle manifest SHA-256 `9C7A10FDBBC91D8F6F48C62A16609D9F1717AC9D33D48EA13740F84EC59F56B0`.
- WP5 audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP5_AUDIT.json` (`PASS`); execution-Oracle manifest SHA-256 `DF4F7F0EAC0B92F2222506B8A09727A81F4C099F258D9801884F4EEC09769836`.
- WP6 technical audit: `working/exploration/20260807_stage2_task_oracle_freeze/WP6_TECHNICAL_AUDIT.json` (`PASS_TECHNICAL`); final artifact manifest SHA-256 `733AB69D926D9BC41080FAADA93C7A318F9D695758726CA877C167373779BBF9`.
- Stage 2 final closeout: `working/review/20260807_stage2_independent_human_review/STAGE2_FINAL_CLOSEOUT_CN.md` (`SUCCESS`).
- Stage 3 final closeout: `working/exploration/20260807_stage3_no_result_engineering_acceptance/STAGE3_CLOSEOUT_CN.md` (`SUCCESS`); final manifest SHA-256 `DE1234431E11BA8CF627D78024092917EB408152A353AB41FCA6F1E20FA3204B`.

Current Stage 1 closeout:

- TigerBeetle 0.17.9, Lago v1.51.0, OpenProject 17.4.0 and Saleor 3.23.7 all completed two clean-state native T0 and two B3 repetitions and are `QUALIFIED`.
- Saleor recovery used the exact frozen image digest through a verified OCI path. Both native runs accepted the valid refund and rejected the over-limit refund with `AMOUNT_GREATER_THAN_AVAILABLE`; normalized results are byte-identical.
- Current closeout: `working/exploration/20260806_stage1_four_system_t0_b3/SALEOR_RECOVERY_CLOSEOUT_20260807_CN.md`.
- The original 3/4 closeout remains a historical pre-recovery record. No model experiment is currently authorized.

Current comparison-design background:

- Draft plan: `working/exploration/20260806_finance_b3_ecas_comparison_plan/FINANCE_B3_ECAS_COMPARISON_DRAFT_FOR_REVIEW_20260806_CN.md`.
- Proposal: 8 systems (6 finance and 2 cross-domain), 32 business tasks, 8 evidence-deficient controls, and four routes: complete B3, Direct-Rego, ECAS and an independent human ceiling.
- Revised model design: Qwen, GLM, Kimi, DeepSeek and an exact OpenAI API model are five coequal formal blocks; there is no primary-versus-later-sensitivity split and no model leaderboard.
- Proposed formal volume is at most 1200 calls (`5 × 40 × 2 × 3`) with no automatic retry authorization. Exact model IDs, reasoning/effort, Token, GPU/cost and call batches remain separately approval-gated.
- The user accepted the coequal five-model revision and Stage 1 was subsequently completed. The draft's old instruction to begin Stage 1 is superseded; the current next-step authority is the Stage 2 goal-mode plan above.

Completed all-ten B3 adaptation:

- All ten cases ran valid, semantic-invalid and schema-invalid-control inputs twice: 60 decisions, 40 accepts, 20 rejects and 30/30 byte-identical repeated pairs.
- All 20 semantic-invalid executions were accepted and all 20 structural controls were rejected; B3 caught `0/10` target semantic cases.
- Authority strata remain `4 HIGH / 5 MEDIUM / 1 LOW`; LedgerSMB remains explicitly `observer_ingress / LOW`.
- Completion report: `working/exploration/20260806_finance_b3_all10/FINANCE_B3_ALL10_COMPLETION_20260806_CN.md`.
- Final artifact manifest: `working/exploration/20260806_finance_b3_all10/FINAL_ARTIFACT_MANIFEST.sha256` (239 entries; SHA-256 `D7BA968411D651C672E4F3038421AE80E0DA6699D372EBBF1E2421C3A4E17746`).
- This is isolated B3 engineering evidence, not an ECAS comparison. ECAS was not run, and Revision 3 is unchanged.
- The next step requires a new authorization: freeze a fair formal-comparison protocol before any ECAS execution.

Historical completed B3 pilot gate:

- Ten-case B3 inventory: `working/exploration/20260806_finance_b3_pilot/B3_ADAPTATION_INVENTORY_10CASE_20260806.csv`.
- Three-case pilot: jPOS, LedgerSMB and BTCPay, each with valid, semantic-invalid and schema-invalid-control inputs repeated twice.
- Audit result: 18 decisions; 12 accept and 6 reject; all 6 semantic-invalid executions accepted, all 6 controls rejected, and 9/9 repeated decision pairs byte-identical.
- Gate report: `working/exploration/20260806_finance_b3_pilot/FINANCE_B3_THREE_CASE_GATE_REPORT_20260806_CN.md`.
- Decision: proceed only to B3 adaptation for the remaining seven cases. Do not run ECAS or a formal comparison under this gate.
- LedgerSMB is explicitly `observer_ingress / LOW`; preserve this limitation in every aggregate.

Completed bounded goal:

- Obtain ten locally reproducible finance-oriented T0 cases under `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_PROTOCOL_20260806_CN.md`.
- Final progress: `10/10 QUALIFIED`; Formance Ledger, Blnk, Freqtrade, LedgerSMB, LNbits, BTCPay Server, Midaz, openIMIS, jPOS, and Bigcapital each passed two clean repetitions. Hyperswitch and Open Bank Project were replaced by jPOS and Bigcapital under the frozen backup rule because their bounded deterministic runtime paths did not close; those replacements are engineering scope boundaries, not scientific failures.
- Completion report: `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_COMPLETION_20260806_CN.md`.
- Completion audit: `working/exploration/20260806_finance_t0_10cases/runs/completion_audit/COMPLETION_AUDIT_20260806.txt` (`PASS`; 190 evidence-manifest entries; zero residual case containers).
- The bounded source download, local Docker startup, deterministic seed, valid plus semantic-invalid requests, and two-repetition authorization has been consumed and closed at ten qualified cases.
- Still forbidden: models, paid APIs, GPUs, formal comparisons, real funds/live trading, production integration, Revision 3 edits, submission and publication.

Current authoritative manuscript:

`working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION3_20260804.pdf`

- PDF SHA-256: `4D2259F65CE16CEAB9F1919FAFE298C65D5760BF27B2CB0752A9E942A8EFBE3F`
- Source ZIP: `working/paper/retarget/ASE_20260803/manuscript/delivery/ECAS_ASE_REVISION3_SOURCE_20260804.zip`
- Source ZIP SHA-256: `C0548460C11520D20DE30A82A874871139F38EBB763CBA64FE7DC9872354E9C5`

Historical Exploration 1 source-screen checkpoint:

- Screening report: `working/exploration/20260806_unseen_system_screening/UNSEEN_SYSTEM_SCREENING_20260806_CN.md`
- Candidate matrix: `working/exploration/20260806_unseen_system_screening/UNSEEN_SYSTEM_SCREENING_20260806.csv`
- Historical status: `SOURCE_SCREEN_PASS_5 / RUNTIME_T0_NOT_RUN / NO_EXPERIMENT_AUTHORIZED`; subsequently superseded by the completed Stage 1 runtime qualification above.
- Qualified shortlist: OpenProject 17.4.0, Saleor 3.23.7, Mattermost 11.7.2, Kill Bill 0.24.18, Lago 1.51.0.
- The former OpenProject/Saleor first-pair recommendation has been executed and closed. It no longer represents a pending authorization.

Current expanded-census checkpoint:

- Frozen protocol: `working/exploration/20260806_unseen_system_screening/EXPANDED_CENSUS_PROTOCOL_20260806_CN.md`
- Candidate universe: `working/exploration/20260806_unseen_system_screening/CANDIDATE_UNIVERSE_75_20260806.csv`
- S1 screen: `working/exploration/20260806_unseen_system_screening/S1_HIGH_POTENTIAL_SCREEN_26_20260806.csv`
- Checkpoint report: `working/exploration/20260806_unseen_system_screening/EXPANDED_CENSUS_CHECKPOINT_20260806_CN.md`
- Historical status before domain reprioritization: `S0_CENSUS_75 / S1_HIGH_POTENTIAL_26 / SOURCE_PASS_16 / SOURCE_CONDITIONAL_10 / T0_NOT_RUN / SATURATION_NOT_REACHED`.

Current finance/banking-priority checkpoint:

- Finance delta: `working/exploration/20260806_unseen_system_screening/FINANCE_BANKING_DELTA_25_20260806.csv`
- Combined universe: `working/exploration/20260806_unseen_system_screening/CANDIDATE_UNIVERSE_FINANCE_PRIORITY_100_20260806.csv`
- Finance screen: `working/exploration/20260806_unseen_system_screening/FINANCE_BANKING_HIGH_POTENTIAL_15_20260806.csv`
- Current S1: `working/exploration/20260806_unseen_system_screening/S1_FINANCE_PRIORITY_SCREEN_30_20260806.csv`
- Report: `working/exploration/20260806_unseen_system_screening/FINANCE_BANKING_PRIORITY_CHECKPOINT_20260806_CN.md`
- Status: `S0_CENSUS_100 / FINANCE_FOCUSED_31 / S1_RESELECTED_30 / S1_FINANCE_19 / SOURCE_PASS_16 / SOURCE_CONDITIONAL_14 / T0_NOT_RUN / STOP_AT_100`.
- S0 expansion is closed at the frozen hard cap. The next source-only work is to close finance conditional blockers and freeze a T0 execution order; T0 remains separately authorization-gated.

The user confirmed Revision 3 as the ASE submission-insurance version: the current submission-ready fallback. This status does not mean the portal submission or any journal decision has occurred. The manuscript, formulas, figures, results, references, PDF, source ZIP, and reviewer artifacts were not changed during this handoff.

The previous CBHG/business--development--security three-Agent branch is historical exploration only and is no longer the active innovation route. It must not be promoted or used to modify Revision 3 merely by renaming the existing Evidence/Inventory mechanism.

The next conversation should isolate experimental exploration from the frozen manuscript. The critical path is:

1. implement and smoke-test a complete OpenAPI 3.1/JSON Schema or native-framework B3 on the existing frozen requests;
2. continue the frozen unseen-system census funnel without full annotation or model execution;
3. apply the B3 stop/go gate;
4. only if justified, pilot one unseen system and confirm on a second with an external policy-as-code baseline and independent human upper bound;
5. run the five-model matrix last as sensitivity analysis.

This handoff authorizes no model/API call, Opus call, Ollama/GPU generation, formal experiment, manuscript promotion, submission, or publication. Read the detailed handoff before any experiment planning or action.

## 2026-08-10 Paid-Prose-Primary Word Candidate

The user clarified that the paid lower-AI manuscript must be the wording base. A new isolated candidate was therefore built at:

`working/paper/retarget/ASE_20260803/manuscript/candidates/ECAS_ASE_PAID_PROSE_MERGE_20260810/ECAS_ASE_PAID_PROSE_MERGE_20260810.docx`

Merge rule: use the paid human-edited wording by default; merge frozen Revision 3 structures and only narrowly necessary scientific/protocol repairs into it. The candidate adopts 49 of the 51 paid paragraph changes, retains two frozen paragraphs solely to protect an internal hyperlink and an Office Math object, and applies nine small accuracy repairs.

QA passed for DOCX package integrity and page-by-page rendering: 6 figures, 9 tables, 117 Office Math objects, 87 hyperlinks, no broken `NULL` relationship, and no missing-image marker. The render is 43 pages because the paid wording changes line flow. LibreOffice previews reproduce the same equation/table-field compatibility artifacts already present when rendering the frozen comparison DOCX; these are not merge regressions.

This is a candidate for the author's Word review and similarity/AI check, not a promoted manuscript. Revision 3 remains the authoritative fallback and must not be overwritten. No external model call, experiment, submission, or publication is authorized.
