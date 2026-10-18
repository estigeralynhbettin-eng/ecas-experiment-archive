# Research Decisions

## 语义约束形成必须单列比较（2026-10-15）

- 原最终请求对表不足以体现语义环节，已补七例首次候选/反馈修复阶段表。新入口working/exploration/20261015_semantic_comparison/EXPERIMENT_SUMMARY_CN_R3.md及SEMANTIC_COMPARISON_CN.md；R1/R2保留，论文未改。
- 当前核读支持S04基本邮箱格式目标的首次形成时点差异；S02闭集来源未闭合，只比较已有任务约定进入候选的时点。S03 AutoPAC整数意图正确但代码无效，不可把编译失败等同语义不理解；P2P范围外无政策可评，不作语义错误。B13/B17/B19已知合法域主业务含义三方首次均形成；B06范围缺口及同行Judge贡献保留。
- ECAS的可讨论特点是来源含义到带evidence_refs的受限IR、确定性编译和Inventory准入的链条；三方法均有自然语言到规则的转换。原语说明、schema、监督与流程同时影响结果，现有事后定性表不识别单因果、不算语义准确率、不证明基础模型或方法普适优越。
- B19来源明确未选类型默认All；既有空值控制ECAS结果一致而两同行allow，属于事后默认语义线索。ECAS并无显式empty→All规则，ABI未保证规范化，生产是否可达未验证；不改变原工程控制分类，不外推真实绕过。Unknown与全缺trusted继续分列工程控制。
- 21行和162来源哈希核对并通过限定独立复核；本轮0模型/0政策执行。未来语义比较需先闭合来源，冻结未暴露任务和独立判据，再分别检验证据输入、受限表示、准入与反馈。按源Judge仍为借鉴AutoPAC的内部控制，不能回填为ECAS独有机制；原科学账本与投稿未改。

## 七案例汇总与缺值行为的机制归因（2026-10-15）

- 用户要求继续推进原缺可信状态/证据机制观察并加入前三例。七案例是两个旧项目的不同批次展示，不是七例同协议试验；保留原资格失败与事后复演，S04 P2P为allow/allow的◐，编译失败/范围外为—。新R2作为当前说明，R1保留。
- 已完成0API本地反事实144行：ECAS只改on_missing=skip仍经完整准入，并在B17/B19 trusted={}下allow；full/shape逐行相同。B19未知/空类型拒绝来自允许条件而非证据元数据检查。因此这组运行差异不能直接归因于Inventory准入的独有保证。
- 两同行加人工独立typed guard即可在这几项工程约定上deny，仍通过已测原业务对；这是手工控制而非新模型/原基线效果。B06 P2P原有缺值deny，是唯一性概括的反例。额外B19 partial inputs无业务gold，不能把allow叫漏洞或把更保守叫更正确。
- 继续研究焦点是证据契约约束所需可信输入、条件依赖、类型及失效处理，测试其是否独立于生成模型的安全参数选择成立；保留加固同行，统计合法覆盖损失。历史元数据/路径准入消融与请求状态缺失为不同失效阶段；Judge核读语义是补充检查，不能算ECAS独有。
- 本轮外部模型0，未使用前轮剩余预算，未启动新生成/独立样本任务；原论文、旧候选/运行及根科学账本不改。入口working/exploration/20261015_seven_case_mechanism/EXPERIMENT_SUMMARY_CN_R2.md。


## 统一任务实测与证据/语义分层结论（2026-10-15）

- 当前授权范围已完成，主30+Judge4=34≤44；余量不自动使用。原中断只做raw确定性本地恢复，没有重调完成响应，没有用环境/协议失败作同行效果失败。权威简报working/exploration/20261014_matched_evidence_labor/EXPERIMENT_SUMMARY_CN.md。
- 明确目标、完整操作说明、至多一次开发修复及失败不获执行资格后，本轮ECAS四例首次完成原请求对；同行适配后三例均完成，P2P S03范围外，AutoPAC S03首次和修复引用不存在函数而编译失败。不能因当前四例结果改写旧失败，也不能把多条件同时变化归因于某一提示因子。
- P2P原作提示LLM、AutoPAC原作微调CodeT5-small，均非人工逐条生成；当前共同GLM替换，尤其AutoPAC生成器替换限制原版效果解释。ECAS4/P2P13/AutoPAC9方法调用只反映当前流程资源，不换算人时或原作小模型成本。
- 同候选证据准入控制注册证据/版本/路径/绑定条件；未证明源文件真实性或语义正确。8历史IR全准入而Judge给3REVISE，3主缺陷回源/重放成立；Judge对B19 skip的附加“不支持”理由不成立/依据不足。契约和语义核读覆盖不同失效，不能写证据驱动自动保证规则正确，也不能写Judge准确率100%。
- 四任务同目标主比较与历史候选机制控制分别引用；工程缺状态/保守控制单列。仅原两个项目、暴露任务、每方法每例一轮，原版基线未复现，不宣称稳定总体优势/普适性。论文、旧原件、根账本和投稿状态保持。


## 当前授权：生成方式特征与证据机制实测（2026-10-14）

- 用户已授权按诊断思路执行，并新增生成方式与证据驱动；明确不做人工效率计时。原作P2P是提示LLM管线，AutoPAC用微调CodeT5-small自动生成，非人工逐条起草；当前GLM替换不等于原作。微调训练准备与推理生成成本分开，不能自动推出ECAS极大省工。
- 同候选消融已完成：11父候选原始full/shape执行观察一致；4类有效契约形状的Inventory负控制各11被full拒绝、shape可编译，可信路径未登记挑战7被full拒绝。来源locator/hash扰动仍准入，属于未核读清单对应文件的实现边界；3原语/逻辑/目标错误仍准入。该对照支持特定注册证据控制的增量，不支持生成语义正确、真实攻击或总体优势。
- 新四例三流程生成比较计划总≤44次glm-5.2 enabled/high（每次input/completion≤16384），先新lane T0与token小试。公共目标、全15原语说明、最多1开发修复，失败后拒绝执行资格，首次/修复后分列。方法自身Judge/自动tests仍不同，真实调用及成本分列；每方法每例1轮、任务已暴露，不声称稳定性。
- 原稿、旧结果、根科学账本与投稿未修改；本轮输出仅新scope。续接入口HANDOFF.md和working/exploration/20261014_matched_evidence_labor/TASK_CONTRACT_CN.md。

## 当前优势质疑的诊断与续接优先级（2026-10-14）

- 四例原请求对AutoPAC适配版4例通过、ECAS v2 3例通过；确认不构成整体排名。开发监督不同：外部流程含修复；ECAS即使common_developer_results.passed=false仍冻结后离线评价。该行为是实验诊断流程，不是错误规则已部署，不能静默把拒绝错误候选改成任务全对。
- S03可见输入含多字段，ECAS强制select one grounded rule；ABI突出age但无独立目标要求。单规则限制与任务指定可能共同造成目标错位，唯一原因未验证。strict_type可以表达目标，不先扩大IR或换模型挽救结果。
- 证据契约检查注册来源/目标/原语族/路径等，没有充分证明候选与原文语义等价。此发现不直接反证主稿已限定的Inventory相对准入保证；更强正确性、稳定优势或契约因果增量尚未建立。
- 建议顺序：一致任务目标→固定首次/修复预算与失败处理→同候选有/无契约及与AutoPAC Judge/工具的增量比较→独立任务重复。若匹配后无增量，应收窄贡献或调整机制，不继续事后找更多成功案例。本轮不授权或启动新调用/实验。
- 依据及未检查范围见working/exploration/20261014_experiment_review_brief/ECAS_AUTOPAC_DIAGNOSIS_CN.md；两名独立只读复核已对关键原件/代码交叉检查，论文与既有科学账本未改。

## 四例同行实测的结果与ECAS配置稳定性（2026-10-14）

- 当前用户已明确启动S03/B13/B17/B19同行基线比较，新范围GLM5.2 high总≤40；实际38次完成。此前“新四例预算尚未授权”条目已由本次授权与执行取代。
- P2P/AutoPAC也能形成B13数量/角色、B17禁用客户、B19冻结类型条件；S03 P2P声明范围外。新增四例不能作为三个或四个ECAS独有优势样本。AutoPAC S03原请求对成功但is_number允许31.5，目标覆盖仅部分完成。
- ECAS结构schema-only提示漏原语运行说明，B17误用server_derived_reject导致全拒绝，B19把禁止条件写成允许分支且缺值skip；补齐全部15操作后统一另生成四例，B17/B19正确但S03选择allowed_fields漏类型。两配置均完整保留，不按案例择优拼表；说明补全与随机生成未隔离，不能称因果改善。
- S03 OpenAPI未显式additionalProperties=false，v2白名单含额外封闭假设；证据准入并未拦住非目标规则或错误原语，不能把准入等同充分语义验证。历史GPT四例离线成功保持，但不能替代本轮相同模型的失败。
- B19缺可信状态控制：P2P/AutoPAC及ECAS v1放行，ECAS v2拒绝；v1 B17缺状态也放行。空/未知冻结类型的控制也有差异。这是预冻工程控制，须绑定具体候选与on_missing设置，不是ECAS全配置保证、新增独立业务案例、真实攻击或总体准确率。
- 只允许对精确匹配中立metadata的DSARCP对象做id表示转换；P2P OPA格式恢复需AST等价。原流程拒绝和原raw保留；原版复现资格缺口不被适配成功覆盖。中文入口working/exploration/20261014_four_case_peer_baselines/RESULTS_CN.md。
- 根论文、历史科学账本及投稿未改。本轮结果优先用于如实回答同行识别及生成稳定性问题，正式推广结论继续需要独立未暴露任务、重复生成和真实绑定。

## 四例扩展的适用性与优势边界（2026-10-14）

- 固定S03（严格整数）、B13（数量上限与角色例外）、B17（禁用客户）、B19（冻结类型分支）作为原两项目的补充展示对象；旧输出已暴露、事后筛选，不增加独立系统或盲测样本。
- 历史GPT四例规则形成→准入→原请求对成功，并通过24项单列分支/工程控制；可支持多规则可执行及非单例展示。S03用strict_type，后三例复用bounded_guard_dnf，不称四种机制。真实上限计算、状态/身份接入、业务生效时点及文档版本一致性未核验。
- 保留Qwen B13准入拒绝、B17/B19弃权，以及DeepSeek B17/B19禁止条件被写成允许条件。两个逻辑反向候选仍能准入，说明当前契约准入不等于充分业务语义验证；不得用正例声称准入自动保证逻辑正确。
- 多案例ECAS成功与多案例相对优势分开判断。新四例P2P/AutoPAC均NOT_RUN，不填○或◐；后续同模型比较须固定完整中立ABI与相同监督。既有B06/S02/S04的限定调用预算不扩大为新四例预算。
- 中文报告working/exploration/20261014_multi_case_extension_screen/REPORT_CN.md，87输入及12候选/24探针确定性对账PASS。新模型调用0，未改稿、根实验账本或投稿状态。

## 三例差异发生阶段与圆圈口径（2026-10-14）

- 圆圈展示采用目标规则落实程度：○未形成目标约束，◐部分形成或执行链未完成，●已形成并通过归档请求对；范围外、编译失败和开发测试修复单独注记。若只表示请求准确性，未执行必须填—，不能误计为0或50%。
- 原始stage逐项核对确认：AutoPAC S02首次只覆盖必需字段存在，S04首次只覆盖认证/创建，Judge均接受；开发测试反馈后的修复才分别新增字段白名单和邮箱正则。P2P S04也直到修复加入string检查，但仍未形成格式约束。
- ECAS首次候选分别形成bounded_guard_dnf、allowed_fields、named_validator/email_basic_v1；编译/证据准入后由运行时执行产生实际allow/deny。不得把证据准入描述成直接识别请求中的错误字段/邮箱，也不得将监督条件不同的轨迹当作契约因果效果。
- 来源和图例见working/exploration/20261014_external_baseline_pilot/STAGE_COMPARISON_CN.md。本轮仅核对既有结果，27次总模型调用数未增加，论文未改。

## 三例外部比较的实际结论及公平性边界（2026-10-14）

- 已完成27次GLM5.2 high调用的三例适配比较（4开发smoke，23方法调用含5修复）。原版P2P/AutoPAC未运行；AutoPAC更换微调生成器的结果不得冠以原作性能。
- B06并非ECAS独有：两个外部适配流程均提取相关条件，统一中立接口后两条请求allow/deny。S04 P2P只检查string而漏邮箱格式，AutoPAC正确提取格式且对象资源映射后allow/deny；S02 P2P显式范围外，AutoPAC提取字段约束但生成is_integer导致编译失败，不把该错误写成没看懂业务。
- 原提示schema漏maxItems=1及阶段状态词EXTRACTED/READY造成的失败保留；本地修复、一次新提示smoke、OPA格式修正均有版本和回执。原resource字符串/对象的Harness错配必须修正或分类；两套对所有方法相同的事后映射复演保留，不挑成功行充当新正式效果。
- 第三方Judge指出B06规则仅针对Re-Age交易，target却是通用undo；现有ABI没有交易类型字段。正式/生产主张必须核实该政策只接收Re-Age撤销，或补可信交易类型绑定。删可信标志后AutoPAC允许，P2P/ECAS拒绝，仅为事后诊断。
- S02的OpenAPI properties未显式additionalProperties=false。未知字段拒绝是归档任务约定，不能从OpenAPI默认语义推出；正式公平比较必须补封闭约定的权威来源，并记录AutoPAC收到操作者开发测试的额外监督。
- 中文报告working/exploration/20261014_external_baseline_pilot/RESULTS_CN.md；105项原件对账通过。本轮可用于作者理解案例与流程差异，不证明整体优越性、不增加独立项目/样本数，未改稿或投稿。

## 共同模型适配比较授权与接口修复（2026-10-14）

- 用户明确同意此前GLM5.2/30次总上限/三例公开材料配置，并要求持续实验、不重复确认；因此继续执行必要本地依赖和接口修复。
- 原运行资格缺口已处理：Linux OPA和Regal、11项本范围T0通过；对应scope的正式本地门禁无blocker。Windows仅承担批准wrapper及全局密钥加载，科学判定仍在WSL。
- 第3次开发smoke的三规则输出违反原schema单规则限制；该限制被我在提示schema精简中错误遗漏。保留原失败，不手工删规则或进入效果分母；恢复限制并挪用一次预留调用检查新提示。总调用授权仍≤30，开发smoke 4、基础≤21、条件修复总≤5；v1/v2版本与失败均归档。
- 当前仅原始接口输出资格PASS，并不表示三个方法效果已通过；原版仍NOT_RUN。三例效果运行与原主试验、历史追加实验分开记账。

## 外部原版资格与适配方案边界（2026-10-14）

- 用户已授权测试P2P/AutoPAC对B06/S02/S04的局部识别目标。本轮实查原版分别缺可确认代码、必需微调CodeT5权重；未执行两个原版效果，不把缺依赖或网络失败计作科学失败。
- 本轮共同输入删除ECAS专属focus但保留原源和运行ABI；生成端隔离最终请求/标签，12份冻结文件已逐份核对。三例已暴露、事后选取，不是新增独立样本。
- 提议按论文流程适配共同glm-5.2并重新生成ECAS以比较流程；尤其AutoPAC更换生成器是重大偏离，仅能报告适配结果。用户尚未确定该替代与具体调用配置；model_calls=0。
- 本范围T0/Regal/token资格待补；Windows OPA四项人工对照仅为准备性验证。协议见working/exploration/20261014_external_baseline_pilot/ADAPTATION_PROTOCOL_CN.md，人民币价格未核实。

## 三例来源记账与基线对比结论（2026-10-14）

- 用户要求记住：B06/S02 来自原选 Apache Fineract，S04 来自原选 ERPNext；三个额外展示案例仍只涉及两个原项目，不能称作新增独立项目或样本。已写入用户授权的 Codex 记忆备注，研究事实以本文件和原件为准。
- 同原请求对回放冻结 B0/B1/B2/ECAS-P/ECAS，54 个逐方法结果全部与历史一致。S02 被 B1/B2 正确识别，S04 被 B2 正确识别；B06 的 B1/B2 没有政策，全拒绝导致合法误拒，不能计作识别违规。
- 三种历史模型配置的 ECAS-P 与完整 ECAS 三例均 allow/deny；三例业务判定没有契约增量。B06 的局部增量属于相对受限元数据参照的规则覆盖，S02/S04 仅展示共同能力。
- 15 个事后删来源工程对照确认准入路径的预期行为：完整 ECAS 拒绝，ECAS-P 忽略契约；有政策的 B1/B2 使用共享准入引擎，也拒绝。它们不是新正式机制效果。P2P/AutoPAC 没有同三例实测结果，不能填写能否识别。
- 中文报告：working/exploration/20261013_gateway_case_audit/baseline_comparison/BASELINE_COMPARISON_CN.md。原件、论文和根结果追溯表未改；后续外部比较仍需正式范围门禁、实现资格与明确模型预算。

## 作者确认范围与三例固定（2026-10-14）

- 作者明确已有案例为 FSV-B01，完成条件为实际候选、证据准入和请求允许/拒绝。据此固定 B06/S02/S04 三例，不再把批次外新系统或生产转发当成本轮前置要求。
- 三例的原 Qwen/GPT/DeepSeek 九个候选均重新编译并显式准入，十八条请求与九个缺来源对照通过；候选来源保持历史生成回执。六十五份输入及引擎已快照到独立演示包。
- 本次是事后选例的本地工程演示，不增加独立样本数。演示与完整中文轨迹供下一步作者决定如何纳入正文/附录，尚未改稿。入口见 working/exploration/20261013_gateway_case_audit/selected_case_demo/README_CN.md。

## API 网关案例选择边界（2026-10-14）

1. R14 贯穿案例继续为 FSV-B01；本轮不修改正文。旧 FSV 中 B06、S02 可作两个互补正向说明；B22 适合作模型敏感性和证据契约局限对照，不得遮蔽原主试验误放。S04 可作第三个稳定结构性说明。此为回顾性选例，不增加独立系统样本。
2. B16 的 credit_exposure 在旧运行 ABI 标为 client，且 ERPNext 同版本源码与文档把信用检查置于订单提交；目标 POST /api/resource/Sales Order 是创建。B22 也存在 Stock Entry 创建与库存提交时点的绑定缺口。两例的离线判定正确不能外推为生产拦截已验证。
3. 新独立系统以 Blnk、Saleor 为优先，Formance 为备选；旧 T0/B3 和旧 Rego 技术资格只能提供候选证据。当前 V3 及真实前置网关未在这些系统上跑通，本次 scope 正式门禁阻断。后续新增效果结果须单独冻结并通过门禁。
4. 详细依据和 64+35 项输入哈希独立复核见 working/exploration/20261013_gateway_case_audit/REPORT_CN.md；本决策不改变投稿稿件、外部基线待办或已冻结结果。

## R14 原稿定点返修交付（2026-10-13，当前核读入口）

- 用户已否定R13压缩稿；R14从已提交R12复制，保留摘要句序、章节及原论证，只加入审稿意见所需定义、贯穿案例、释义、复现入口和定点修正。停止代理精简，篇幅由作者手工处理。
- 目录：`working/paper/retarget/ASE_20261013_MAJOR_REVISION_R14`。清稿：`delivery/ECAS_ASE_R14_REVIEWER_AMENDMENTS_20261013.pdf`（55页）；中文说明：`delivery/R14_REVISION_REPORT_CN.md`；逐句对照：`delivery/R14_CHANGE_REVIEW_CN.html`；可编辑源包：`delivery/ECAS_ASE_R14_DRAFT_SOURCE_20261013.zip`。
- 62条修改有完整台账，独立复核四文件可逆恢复R12；原表体、算法、书目及原图3–6保持。主稿编译与55页视觉核对完成；横向页模板警告经过可见内容检查，不称零警告或科学冻结。
- 33项矩阵和英文内部回复在delivery：20项定点修改已核对、10项部分、3项作者手工处理，0项宣称正式闭环。外部P2P/AutoPAC实测、完整复现、全文英语和正式化/全文缩短仍待完成。
- 状态：`R14_R12_BASED_LOCAL_AMENDMENTS / AUTHOR_REVIEW_DRAFT / SHORTENING_BY_AUTHOR / EXTERNAL_COMPARISON_PENDING / NOT_SUBMISSION_FROZEN`。
- R13是保留的、被作者否定的压缩尝试；不作当前正文/翻译底稿。R12、Revision 3、原实验和ESM_1.zip保持。没有新增外部模型、付费调用、正式实验、发送、发布或投稿。
- 下一步：作者按原文→新文逐处核读并手工精简；再明确外部比较/完整复现实验范围，取得具体授权后补齐证据与正式回复。普通核读不扩大实验授权。


## R13 用户授权与大修决策（2026-10-13，取代历史仅讨论阶段）

1. 用户明确授权大幅压缩和实质文字修订，正文目标约20页，详细形式化/证明和逐任务细节移至独立补充；不扩大为新增正式实验、付费模型、发布、邮件或投稿。
2. 新建R13保留R12/Revision3保险与冻结实验。正文用同一FSV-B01候选—证据—契约—请求轨迹，不拼接最佳模型片段，不伪装现场流量。
3. 主稿21总页、正文17页，补充15页；保持Springer模板正常字号和边距，核心机制、负结果与必要边界仍在正文。新稿供作者核读，未完成投稿冻结。
4. 原预设收益门阈值是5个百分点；零误放基线不定义相对下降，原总体收益门仍失败。GPT17/21合法与0/21误放两方法相同；契约增量为7/9到9/9控制停止。四追加配置为事后敏感性检查。
5. 两个外部候选为P2P和AutoPAC；相关工作分别说明前者自动测试、后者微调CodeT5及用户测试。AutoPAC原版复现缺checkpoint等条件，自建适配须准确标注来源和改动。
6. 编辑/三审稿人的33项意见分别映射，不能因共用修改省略回复。结构/语言完成与外部比较、全面复现未完成分开记录；比较和总体闭环项不写全通过。
7. 输出、核验和剩余项：`working/paper/retarget/ASE_20261013_MAJOR_REVISION_R13/delivery/R13_REVISION_REPORT_CN.md`。无新模型调用、正式实验、发送或投稿状态变化。

## ASE Experiment Organization and External Baseline Advice (2026-10-13)

1. 用户提出前期没有证成有用、追加实验才有改善的疑惑，并要求基线意见及约 20 篇同刊论文长度参照。当前按已提交 44 页 ASE 稿核对，R12 只是内部版本号，不要求用户记住。
2. 原主试验两个预设总体收益路线均失败，仍保留机制与边界证据。追加 GPT 的 ECAS-P/ECAS 均为合法 17/21、违规误放 0/21；契约可识别增量为证据不足控制停止 7/9→9/9。这些判断已回到原稿引用的原始 JSON 定点核对。
3. 建议保留原负结果和全部托管配置，以贯穿案例解释机制，以外部公平比较识别相对收益；不把追加最佳行改写成原预设实验成功，不把生成配置差异归因于单一模型。
4. 建议建立最接近的外部方法或明确按文献实现的对照，配合同模型直接生成、同候选契约消融和完整确定性元数据参照。候选 P2P、AutoPAC 与新结构化政策生成预印本尚待代码和兼容性核对；未授权搭建、调用或执行正式实验。
5. 八系统/任务/Direct-Rego/B3 历史准备可作发现入口，MODELS_NOT_RUN 的阶段材料不是 ECAS 正式效果；复用须审计后续资格调用暴露和协议变化。
6. 详细意见：`working/review/20261013_ASE_MAJOR_REVISION/EXPERIMENT_AND_BASELINE_ADVICE_20261013_CN.md`。本节为建议与核对结果，尚未形成用户确认的返修方案；本轮授权只扩展到文献获取和长度分析，原稿仍冻结。
7. 同刊便利样本20篇正式研究（2024–2026在线发表）全文均值36.05、中位35.5、范围13–52；5/20达到44页或更长。R12的44页高于样本均值7.95页，References前37完整页高于样本均值4.70页；成品版与投稿版版式不同。篇幅并非极端异常，不作为反驳共同可读性意见的理由，也不据平均数机械设官方页限。来源、选择排除理由、完整页边界与PDF在 `working/literature/ASE_LENGTH_SAMPLE_20261013/`。

## ASE Major Revision: Initial Interpretation (2026-10-13)

1. 用户粘贴的编辑决定明确为 `major revision`，门户建议在 2026-11-27 前修回；记录收到文本的日期为 2026-10-13，不推断通知邮件日期、硬截止设置或接收概率。原始意见与初判存于 `working/review/20261013_ASE_MAJOR_REVISION/`。
2. 编辑和 R1–R3 的共同重点是可理解性：首次定义、Section 3 贯穿案例、正文压缩、减少重复与长列表、形式化联系实例、可读图与英语。可读性改善不明显可能被拒稿。
3. 相关系统比较与可复现性是编辑明确要求；R12 内部参照/消融和研究路线表不自动证明已满足。原文没有指定新增实验；先核对现有证据，再决定是否需补公平比较。当前未授权改稿、补实验或付费调用。
4. R3 的字段脱敏例子与 R12 主要请求字段校验范围有差异，应澄清真实对象，不自动新增脱敏能力。式 (2)/(3) 已定位解释问题，未据此宣布算法错误或正确性通过。
5. 以上仅为意见初判与建议，尚未成为用户确认的返修方案；原 R12 和 Revision 3 冻结，无论文、实验或公开材料修改。未作全文科学有效性、数据追溯或投稿冻结结论。此前 9 月状态保留为历史。

## Workspace Migration Completion Decision (2026-09-04)

1. Migrate the ECAS submission workspace to the distinct canonical path `D:\lunwen\EC-CSI投稿`; do not merge it with the separate experiment project `D:\lunwen\ec`.
2. The old path `C:\Users\PBCDCI\Documents\EC-CSI投稿` is now a verified compatibility Junction targeting the canonical D-drive directory, so historical absolute paths remain usable but are no longer a second writable copy.
3. Preserve the original physical tree at `C:\Users\PBCDCI\Documents\EC-CSI投稿_pre_migration_20260904`. It matched the D-drive authority at finalization and must not be deleted without explicit author confirmation.
4. Use `D:\lunwen\EC-CSI投稿` for all new project work and authoritative path records. The C-drive Junction is compatibility-only; the dated backup is recovery-only.
5. The final switch is accepted because the pre-rename, post-rename and post-switch comparisons passed; 29 reparse points, 19 root/key SHA-256 checks and same-file access through C/D were independently verified.

## ASE Reviewer-Acceptance Status Record (observed 2026-09-04)

1. The Springer Nature SNAPP tracking page still states `Your submission is in peer review`; retain `Peer Review` as the current stage.
2. The portal states that the editor has invited more than 10 reviewers and that 4 reviewers have accepted the invitation.
3. Treat the 4 strictly as accepted invitations. The screenshot does not show a `reviews received` count, completed reports, an editorial recommendation, or decision timing.
4. Preserve the portal screenshot as `ECAS_ASE_PORTAL_STATUS_4_REVIEWERS_ACCEPTED_20260904.png` in the R12 delivery directory, while retaining the earlier 2026-08-20 screenshot as historical evidence.
5. Take no submission action now; wait for a formal revision request, decision, or explicit returned-review indication.

## ASE Peer-Review Status Record (observed 2026-08-20)

1. The Springer Nature SNAPP tracking page states `Your submission is in peer review`; record the current state as `Peer Review`.
2. The progress panel marks technical check, editorial assignment, and with-editor stages complete.
3. The portal states that the editor has invited more than 10 reviewers. Treat this strictly as invitations issued; do not infer reviewer acceptances, completed reports, or decision timing.
4. Preserve the portal screenshot as `ECAS_ASE_PORTAL_STATUS_PEER_REVIEW_20260820.png` in the R12 delivery directory.
5. Continue to use submission ID `71cf26a4-ec4f-4d3c-9334-0fa6b772e479`, version `v1.0`; wait for a formal editorial notification before recording any revision or decision.

## ASE Formal Submission Record (2026-08-12)

1. The author formally submitted R12 to *Automated Software Engineering* through Springer Nature SNAPP on 2026-08-12.
2. The portal initially placed the manuscript at `Technical Check`; this historical state was superseded by the confirmed `Peer Review` state observed on 2026-08-20.
3. The submitted manuscript is the R12 13-file LaTeX ZIP. `ESM_1.zip` and the verified cover-letter PDF were retained with the submission. The portal-generated 44-page R12 PDF passed full text and visual review.
4. Cheng Wang's duplicated second affiliation was corrected before submission. The exact preprint selection was author-controlled and is not restated beyond the portal record.
5. The tracking page records submission ID `71cf26a4-ec4f-4d3c-9334-0fa6b772e479` and submission version `v1.0`. Preserve the confirmation email when available; current status is governed by the peer-review record above.

## ASE R12 Citation-Format Repair Decision (2026-08-12)

1. Preserve R11 and create R12 because the live portal PDF exposed two visible author--year compression defects (`n.d.b,n,n`) on pages 6 and 34.
2. Keep all reference records and their undated status unchanged. Repair only the two citation commands by rendering each OWASP author--year item separately; do not invent publication years or alter scientific content.
3. Rebuild only the English manuscript and flat 13-file portal ZIP. `ESM_1.zip`, cover letter, title, abstract, authors, declarations, experiments, figures, tables, equations, and bibliography entries remain unchanged.
4. Replace only the manuscript in the live portal with `ECAS_ASE_LATEX_SOURCE_R12_20260812.zip`; do not repeat unrelated uploads or gates.
5. R12 became the submitted manuscript on 2026-08-12 after the portal affiliation was corrected; its initial state was `Technical Check`, now superseded by the 2026-08-20 `Peer Review` record. Submission ID remains `71cf26a4-ec4f-4d3c-9334-0fa6b772e479`.

## ASE Portal Final-Review Decision (2026-08-12)

1. The live portal successfully converted the R11 LaTeX ZIP, and its downloaded 44-page PDF is text-identical to the local R11 PDF. Fine-grained visual review then found two visible OWASP citation-compression defects; the resulting minimal rebuild is R12.
2. Do not press final submit while the Review page duplicates Cheng Wang's second affiliation. Delete and recreate the live Authors record as `Key Laboratory of Embedded System and Service Computing, Ministry of Education`, city `Shanghai`, country `China`, without duplicating text in the optional institution-details field. The manuscript PDF is already correct.
3. The portal-listed R10 cover-letter PDF is byte-for-byte identical to the R11 cover-letter PDF. Treat the filename difference as cosmetic and avoid an unnecessary re-upload.
4. Select `No, we don't want to post our work as a preprint at this time` unless both authors explicitly agree to permanent Research Square posting under CC BY 4.0.
5. The affiliation correction and final review were completed, and the author submitted R12. The portal's `Submission received` confirmation is sufficient to record submission; the manuscript ID remains a separate pending field.

## ASE Portal Data-Availability Decision (2026-08-12)

1. Select `Yes` for Data Availability. ECAS generated and analysed model-response records, normalized policy candidates, compiled proposals, and evaluation-decision records; `No or not applicable` is factually incorrect.
2. Use the journal's “included in the paper or Supplementary Information” route. `ESM_1.zip` is Supplementary Information / Online Resource 1 and contains the supporting records described in the R12 manuscript (unchanged from R11).
3. Do not invent a repository DOI, accession code, or other persistent identifier. The package is supplied with the submission rather than deposited in a separate persistent repository.
4. Keep the portal statement aligned with the R12 manuscript, including the explicit exclusion of hosted-provider raw API envelopes and reasoning traces.
5. R11 was subsequently superseded by R12. R12 was formally submitted on 2026-08-12; see the formal submission record above.

## ASE R11 Figure 1 Text-Only Model-Identifier Decision (2026-08-12)

1. Preserve R10 and create R11 as the active local submission candidate; do not overwrite any earlier package or frozen CSI/ASE baseline.
2. Remove the five Qwen, DeepSeek, Zhipu/GLM, Kimi, and OpenAI provider logos from Figure 1. Retain the scientific model identifiers as evenly spaced plain text: Qwen, DeepSeek, GLM, Kimi, and OpenAI.
3. Keep every other Figure 1 node, connector, label, color, process order, and evaluation element unchanged. Keep Figure 2--6 unchanged.
4. Treat the logo-specific trademark/permission gate as closed. Continue to answer any portal third-party-material question according to its exact wording and the independent licence boundary documented inside `ESM_1.zip`; removing logos does not rewrite the supplementary artifact's notices.
5. Carry forward the R10 manuscript prose, evidence, results, tables, references, declarations, public supplementary artifact, and cover letter without scientific changes.
6. Rebuild English, Chinese, and the flat 13-file source ZIP once, visually review the affected manuscript page, and perform one ASCII-path extracted rebuild. Do not rerun experiments, call external models, or repeat unrelated SHA gates.
7. R11 became the active local package for the author's manual portal submission and is now preserved as the predecessor of R12. Status remains `NOT_SUBMITTED` until a manuscript ID or formal receipt is supplied.

## ASE R10 Public-Supplement Alignment Decision (2026-08-12)

1. Preserve R9 and create R10 as the active local candidate. Do not overwrite R9, earlier submission candidates, or frozen Revision 3.
2. Use `ESM_1.zip` as the only public Supplementary Information file and cite it as Online Resource 1. Do not upload the historical R6 reviewer ZIP.
3. Describe the public package precisely: it retains 30 primary Qwen3.6 raw responses, all 120 hosted normalized candidates, compiled proposals, and 780 evaluation-decision records; hosted-provider raw API envelopes and reasoning traces are excluded.
4. Replace the manuscript's old reviewer-artifact and future-release wording with present-tense Online Resource wording, add a concise Supplementary Information caption, and synchronize Data Availability, cover letter, portal fields, checklist, English authority, and Chinese internal review.
5. Correct only the artifact metadata inconsistency concerning the corresponding-author email intentionally included in the README. Refresh the manifest, rerun the existing verifier and conformance smoke, and rebuild the ZIP; do not change experimental records, metrics, figures, tables, or conclusions.
6. Validate English, Chinese, and the flat 13-file source package once, including affected-page visual review and one new ASCII-path extracted rebuild. Do not rerun experiments, call external models, or repeat unrelated SHA gates.
7. R10 is locally ready for author-led portal work but remains `NOT_SUBMITTED`. Authors must confirm metadata, declarations, third-party model marks, public-artifact licensing/privacy scope, the live Supplementary Information mapping, and the portal-generated PDF.

## ASE R9 Guidelines-Alignment Decision (2026-08-12)

1. Preserve R8 and create R9; R9 becomes the active local candidate without changing frozen Revision 3 or earlier submission candidates.
2. Treat the original plotting scripts as the authority for graphics-program disclosure. Figure 3--6 are Python/Matplotlib/SciencePlots outputs, not TikZ; Figure 1--2 are diagrams.net (draw.io) schematics.
3. Follow the author's explicit wording decision by deleting Codex, code debugging, consistency checks, and analysis support from the public AI statement. Synchronize the English manuscript, Chinese review, and portal-field draft.
4. Preserve detailed production provenance internally; the wording edit does not rewrite historical records.
5. Rebuild English, Chinese, and the flat portal ZIP once, with page-level visual review and one ASCII-path ZIP rebuild. Do not rerun experiments, modify data/figures/references, call external models, or repeat unrelated SHA gates.
6. R9 is locally ready for author-led portal work but remains `NOT_SUBMITTED` until a successful portal receipt or manuscript ID is recorded.

## ASE Portal Responsibility Decision (2026-08-12)

1. The author will perform the ASE/Springer Nature portal submission manually.
2. Stop Codex-controlled browser work before authentication; do not enter credentials, metadata, upload files, create a portal draft, or click final submit.
3. Keep R8 as the active local package and keep project status at `NOT_SUBMITTED` until the author provides a successful manuscript ID or portal receipt.
4. After author submission, record the exact submitted files, portal-generated PDF, submission date, manuscript ID, and any portal-specific declarations or deviations from the local field draft.

## ASE R8 AI-Statement Annotation Decision

1. Preserve R7 and create R8; do not overwrite prior candidates or frozen Revision 3.
2. Interpret the highlighted page-30 deletion as removal of the detailed GLM/Kimi/Claude/DeepL and early image-generation/draw.io provenance expansion, while retaining the opening ChatGPT/Codex assistance sentence and the closing author review/responsibility sentence.
3. Apply the same wording to the English authority, Chinese review source, delivery README, portal-field draft, metadata confirmation, checklist, and cover-letter package where applicable.
4. Preserve the actual tool and figure-production history in internal provenance records. The author annotation controls manuscript wording but does not erase factual history; complete-disclosure compliance remains an author confirmation gate.
5. Rebuild English, Chinese, and the flat 13-file portal ZIP once. Do not rerun experiments, artifact checks, citation searches, or SHA gates because the change affects disclosure prose only.
6. R8 is ready for author review and portal dry run, not autonomous submission.

## ASE R7 Figure/Table Reference Decision

1. Treat the user's concern as a full body-reference audit, not a search for labels or captions alone. Require every numbered Figure 1--6 and Table 1--8 to have an environment-external body reference in both English and Chinese.
2. Preserve R6 and create R7. Do not change experiments, data, figure/table contents, references, author metadata, declarations, or reviewer-artifact evidence.
3. Add an early Table 1 reference because the R6 top-of-page float visually preceded its nearby lead-in. Strengthen Table 2 with an explicit five-record/fail-closed audit-chain explanation, clarify Table 3's separate 21/9 denominators, and explicitly connect Figure 3(b) to the RQ3 4/9-to-9/9 result.
4. Accept normal `sn-jnl` top-of-page float behavior for other already well-explained objects; do not force global float placement or add redundant citations merely to make every rendered float appear after its closest prose sentence.
5. Validate the final flat 13-file ZIP once by ASCII-path extraction/rebuild. Do not rerun experiments or repeat unrelated citation/SHA gates.
6. Continue using the verified R6 reviewer artifact because R7 changes no claim evidence or artifact content. R7 is ready for author confirmation and portal dry run, not autonomous submission.

## ASE R6 Submission-Package Decision

1. Promote author-selected draw.io candidate A for both Figure 1 and Figure 2 into a new R6 candidate derived from R5; do not overwrite R4, R5, or frozen Revision 3.
2. Use 4800 px, 600-DPI PNG exports in `pdflatex`. Preserve the two-page `.drawio` source and TIFF/PDF/SVG/editable-PNG alternatives outside the portal LaTeX ZIP.
3. Keep the corrected method semantics: Figure 1 orders deterministic compilation before the Evidence Contract; Figure 2 ends with the executable policy passed to the ECAS gateway and uses three straight vertical fail-closed branches.
4. Describe the production history factually: the authors own the concepts and workflow semantics; OpenAI image generation was used only in early visual-design exploration; final schematics were reconstructed in draw.io and contain no AI-generated raster imagery or experimental data. Reconcile the statement with the prior GLM/Kimi/Claude/DeepL disclosures rather than silently shortening it.
5. Retain the five model marks because the author selected them as configuration identifiers, but keep third-party material/trademark treatment as an explicit author/portal confirmation item; Lobe Icons MIT licensing does not itself grant brand trademark rights.
6. Package the Snapp/LaTeX upload as a flat 13-file root ZIP, because portal compilation should not depend on a `figures/` subdirectory. Validate it once by extracting to an ASCII empty directory and rebuilding.
7. Do not rerun experiments, unchanged numeric/figure-data audits, external citation searches, or repeated SHA gates. Refresh the reviewer-artifact manifest once only because its manuscript locators were intentionally made portable, then run the existing verifier and conformance smoke.
8. R6 is ready for author confirmation and a portal dry run, not for autonomous submission. Actual final-submit action remains separately authorization-gated; Revision 3 remains the preserved insurance fallback.

## Draw.io Dual-Candidate Decision

1. At the author's request, create two independent two-page draw.io sources: an image-trace version of the accepted R5 figures and a second version redesigned from the locally preserved prompt/design record.
2. Apply the already accepted scientific corrections to both candidates. Do not reproduce the stale Figure 1 prompt order; keep `Deterministic compiler -> Evidence Contract`. Keep Figure 2's final success node as `Executable policy / To ECAS gateway`.
3. Use only local draw.io native shapes, text and connectors. Retain the evaluated model-family names as scientific identifiers, but use editable letter badges instead of embedding raster Logos.
4. Record that Figure 2's exact original ImageGen prompt was not found; its prompt-redesign candidate is reconstructed from the final integration record and current R5 figure.
5. Treat both sources as comparison candidates. They do not replace the accepted R5 raster figures until the author explicitly selects A, B or a mixed revision and a subsequent integration gate passes.
6. Following the author's A-version revision request, replace all 11 Figure 1 workflow/evaluation text placeholders with local native draw.io library stencils while keeping the model strip, labels, node geometry, connectors, semantic order, and Figure 2 unchanged. This icon revision remains part of candidate A and is not an R5 integration decision.
7. Following the later model-strip request, replace A's Q/D/Z/K/O badges with self-contained SVG marks from the pinned Lobe Icons 1.91.0 package. Use the Zhipu mark beside `GLM`, keep all five model names, and make only a white-to-near-black fill adaptation to Kimi's K for white-canvas visibility while preserving its blue dot and geometry. Candidate B and R5 remain unchanged.
8. Record the author's selection of A for continued editing. This selects the editable design direction but does not yet authorize replacing the accepted R5 raster assets.
9. Replace A Figure 2's six success-path and three fail-closed text badges with local native draw.io stencils. Preserve all wording, node geometry, process boundaries, success-path topology, `valid`/`admitted` labels, and fail-closed semantics. Use exact target anchor offsets so all three downward failure arrows are straight vertical centerline connections.

## Native PowerPoint Figure Redraw Decision

1. Following the author's acceptance of the corrected figure semantics, create a separate two-slide PowerPoint source in which every box, arrow, label, boundary, branch, and model marker is a native editable object.
2. Reproduce the accepted visual hierarchy and colors without embedding the existing raster figures. Preserve the corrected method order and fail-closed semantics.
3. Retain Qwen, DeepSeek, GLM, Kimi, and OpenAI names because they identify actual evaluated proposal-model families rather than advertisements. Replace graphical Logos with editable letter badges so the deck remains entirely native.
4. Use local Microsoft PowerPoint drawing only. No ImageGen, external model, paid API, new experiment, result change, or portal action is authorized or performed.
5. Treat the PPTX as an author-review source candidate. It does not automatically replace the R5 manuscript images; integration and final export remain a separate author decision.

## R5 Figure-Semantics Correction Decision

1. Correct only the two manuscript-figure defects identified during final submission review: Figure 1's compiler/Evidence-Contract order and Figure 2's post-admission destination label.
2. Use local deterministic image editing rather than regenerating either figure. Preserve the original ImageGen visual base, evaluated-model row and Logos, layout, icons, arrows, colors, and Figure 1 evaluation lane.
3. Treat the model names as scientific identification of actual evaluated proposal-model configurations, not as advertising or endorsement.
4. Retain the manuscript's transparent AI-figure disclosure and provenance. No external model or paid API was called for this correction.
5. Hold final packaging until the author visually accepts the rendered R5 pages. R4 and frozen Revision 3 remain unchanged, and no portal submission is authorized.

## ASE Submission-Stage Entry Decision

1. Enter ASE submission preparation using the current isolated R4 English candidate as the working authority; keep the Chinese candidate as an internal review aid only.
2. Preserve frozen Revision 3 as the immutable submission-insurance fallback. R4 does not supersede it until a versioned final package passes current official-requirement, author-field, scientific-traceability, layout, clean-source, artifact, and cover-letter gates and receives explicit author promotion.
3. Treat Figures 1 and 2 as visually accepted for submission preparation. Do not replace or regenerate the R5 assets without a new explicit author decision. Author-requested editable-source comparisons may be produced in isolation, but remain non-integrated candidates until a separate selection and integration gate passes.
4. The new stage authorizes preparation and portal dry-run only. Actual submission, publication, external paid-model calls, Opus, new experiments, GPU work, and public artifact release remain separately approval-gated.
5. Use `working/handoff/HANDOFF_20260811_ECAS_ASE_SUBMISSION_STAGE_ENTRY_CN.md` as the continuation contract.

## Figure 2 ImageGen Integration Decision

1. Replace the old 7.82:1 text-heavy Figure 2 with an ImageGen figure that follows the approved Figure 1 visual language: Times New Roman styling, light line icons, blue/green process regions, black success arrows, and orange-red failure paths.
2. Preserve the six-step method semantics exactly: visible task package, one proposal-model call, schema-only response check, typed candidate, Evidence Contract, and admitted proposal to the deterministic compiler.
3. Place Response check inside the deterministic post-response region. This is a presentation correction consistent with the implementation; it does not add another model or semantic judge.
4. Reject the v1/v2 lower layouts. Use three equal aligned fail-closed cards connected by short vertical arrows, rather than long convergence lines or one isolated shared result card.
5. Keep all three failure outcomes explicit: abstention, malformed response, and unsupported/unbound evidence each produces no executable policy.
6. The new R4 figure candidate supersedes the Figure-1-only R3 candidate but does not overwrite the R2 delivery or frozen Revision 3 insurance version. No experiment, result, equation, citation, or claim changes, and no external paid-model call occurred.
7. Supersede the initially integrated v3 because its 2.2563:1 aspect ratio still appeared vertically tall in the manuscript. Adopt v4 at 1989×711 (2.7975:1), generated by compacting the layout and removing only 40 px of pure-white margin from both the top and bottom. Reject non-uniform horizontal stretching because it would distort labels and icons.
8. Supersede v4 as the manuscript asset only because its remaining top/bottom white canvas was still visually noticeable. Adopt v5 at 1989×580 (3.4293:1) by cropping fixed top/bottom coordinates from v4 and retaining about 10 native pixels of safety margin on each side. Reject the ImageGen crop attempt because it subtly redrew content; the adopted v5 preserves v4's content pixels exactly.
9. At the author's request, apply one final deterministic ultra-tight crop to both Figures 1 and 2. Retain approximately two high-resolution pixels above and below the measured non-white content boundary. Adopt Figure 1 at 4800×1566 and Figure 2 v6 at 4800×1357; do not alter LaTeX spacing because full-page inspection shows the remaining figure-caption separation is normal typesetting space rather than image canvas.

## Figure 1 Style-Preserving Font Integration Decision

1. Reject the TikZ vector redraw: exact embedded-font compliance does not justify degrading the author-approved icon quality, spacing, and light visual style.
2. Use the author-selected ImageGen figure as the visual authority and make a bounded font-only visual edit toward Times New Roman. Export the accepted edit as 4800×1699 / 600 DPI and include it by width only; do not force it back to another aspect ratio.
3. The five model families are evaluated alternatives at one proposal-model role. They are not a multi-agent chain, and the deterministic evaluator is not presented as a second LLM.
4. The upper delivery path and lower independent-evaluation path each use a single left-to-right direction. The decision-comparison icon contains no bidirectional arrow.
5. Figure 2 may be edited next, but it must preserve the current light visual language rather than adopting the rejected TikZ redraw. Its method semantics, Model IR boundary, Evidence Contract behavior, and fail-closed outcomes must not change.
6. This figure change modifies no experiment, result, equation, reference, claim, or frozen artifact and uses no external paid model call. Final packaging remains pending until the Figure 2 decision is closed.

## ASE Author-Annotation R2 Decision

1. Treat the paid human-edited wording plus the author's completed Chinese-PDF annotations as the language authority for R2, while retaining frozen evidence and Revision 3 boundaries.
2. Use the English R2 manuscript as the current proposed-submission authority and the Chinese R2 manuscript only as an internal review aid.
3. Reframe the main narrative as LLM-accelerated policy construction followed by explicit evidence support and API-context binding checks; do not imply that ECAS invented policy generation or directly incorporates all cited prior methods.
4. Retain exactly three contributions, lead the third with validation in real source code/APIs/executable environments, and retain the distinction among evidence admission, contradiction detection, and semantic validation.
5. Preserve all existing figures, formula semantics, frozen tasks/results, and the bibliography database. Defer figure enhancement to a separate bounded round.
6. R2 passes compilation, bilingual, package, and visual QA at 43 English and 35 Chinese pages. It is ready for figure-enhancement discussion but has not been submitted and does not remove Revision 3's insurance status.
7. No external paid model was called in this annotation-integration round.

## ASE Submission-Draft and Chinese-Review Decision

1. Create an isolated ASE submission draft using the Springer Nature `sn-jnl` / `sn-basic` source layout. Do not overwrite the frozen Revision 3 insurance version.
2. Use the paid human-edited lower-AI manuscript as the primary language authority, while retaining Revision 3 as the authority for verified scientific structure, equations, figures, tables, citations, results, and protocol boundaries.
3. Treat the English PDF and English LaTeX source as the proposed submission authority. Treat the Chinese translation only as an internal review and annotation aid; Chinese wording cannot silently modify an English scientific claim.
4. Translate with the user-authorized GLM-5.2 route using `thinking=disabled`, temperature 0.1, 8192 maximum output tokens per call, 15 planned calls, and no automatic retry. Preserve every raw response and fail closed on truncation or structural incompleteness.
5. The provider completed all 15 calls with `finish_reason=stop`. Chunk 01's initial failure was a local placeholder-manifest bug; the immutable raw response was reparsed without a network call and passed. Total paid retries remained zero.
6. Require structural, numerical, citation, compilation, and visual gates before delivery. The final English and Chinese drafts passed these gates at 42 and 34 pages respectively.
7. Keep all six current figures unchanged in this round. Figure redesign or data-visual enhancement is deferred to a separate author discussion and must preserve the verified data semantics.
8. This draft is ready for author review but does not constitute journal submission or supersede the frozen Revision 3 fallback until the author explicitly promotes it.

## Stage 4.1 Pre-Formal Qualification Decision

0. The user required technical problems to be resolved before formal execution and authorized Qwen/GLM recovery followed by a fresh five-model 20-call qualification.
1. The first recovery established GLM 4/4 but Qwen 0/4 due a policy transport/schema artifact. A second Qwen OpenAI-compatible round exposed a distinct MAXTOKEN failure: four reasoning-only outputs exhausted 1024 tokens and left content empty. Neither failed round was overwritten or counted scientifically.
2. The third Qwen round returned to native Ollama with explicit `think=false`, retained output 1024, and passed 4/4. Its frozen exact syntax dewrapper was not activated in the successful round or final qualification.
3. The fresh five-model qualification passed 20/20: each provider passed 4/4, raw integrity passed 20/20 and model-call retries were zero.
4. The pipeline is ready for a separately frozen formal design. Qualification prompts contain explicit type/truth-table guidance and must not be reused scientifically without leakage/fairness review.


## Stage 4 Historical-Alignment Completion Decision

0. The user authorized direct continuation of the current Stage 4 parameter-aligned smoke without repeated in-scope confirmation prompts. The immutable ledger remained 20 calls, four per model family, with zero content retry or repair.
1. Stage 4 is complete as a non-scientific pipeline smoke: all 20 calls were attempted and raw-captured, and 14 passed parser, common schema, Rego compilation and both OPA decisions.
2. Provider results are Qwen 0/4, GLM 2/4, Kimi 4/4, DeepSeek 4/4 and ChatGPT/Codex 4/4. These counts are technical-pipeline observations, not scientific model scores.
3. Historical parameter alignment is accepted for this smoke: Qwen `qwen3.5:9b` with output 1024; GLM `glm-5.2/high` with output 16384 after the authorized calibration; Kimi `kimi-k3/high` and DeepSeek `deepseek-v4-pro/high` with output 8192; ChatGPT/Codex `gpt-5.6-sol/high` with host-managed output in four fresh visible-only contexts.
4. Token gates passed with no truncation, empty output or wrapper retry. Four Qwen and two GLM failures are schema/protocol-layer generated-policy failures and are ineligible for scientific denominators; parameter freezing did not cause a token failure.
5. The earlier partial Stage 4 main/recovery audit remains historical interim evidence and is superseded for current Stage 4 status by the aligned rerun. Neither artifact may overwrite Revision 3 or be promoted as a formal ECAS/Direct-Rego result.
6. Actual paid cost remains `NOT_PROVIDER_REPORTED`; the preregistered ceiling was CNY 80. No monetary amount is inferred from token counts.

## Stage 3 No-Result Engineering Acceptance Decision

0. The user explicitly authorized planning and executing Stage 3 in goal mode until completion. The protocol was frozen before execution at 98 human-synthetic base fixtures and two repetitions: 196 local executions, with no denominator repair.
1. Stage 3 succeeded: both repetitions matched 98/98 expected outcomes, all 80 valid base fixtures compiled and evaluated on both repetitions, all 18 injected faults failed closed on both repetitions, and 98/98 normalized repeat pairs are byte-identical.
2. The nine frozen fault classes cover empty, truncated, schema-invalid, unauthorized, compile-invalid, undefined and ambiguous outputs on both blind routes. Real route/system/task/Oracle leakage is zero.
3. OPA 1.19.0 Windows amd64 was acquired from the official immutable release and matched SHA-256 `ED4EE673B2182352AF3A9D5F0DE4A74D23A063CBBB447723FB21AC5EAD8CD599`. The slow wrapper timeout was classified as transport/protocol, not scientific failure; the exact download completed. A removed version-format flag was repaired before full execution.
4. The final Stage 3 artifact manifest contains 2045 entries with zero failures and SHA-256 `DE1234431E11BA8CF627D78024092917EB408152A353AB41FCA6F1E20FA3204B`. Stage 2 and Revision 3 hashes remain unchanged.
5. These results establish only non-scientific pipeline acceptance. They provide no ECAS, Direct-Rego, model quality, superiority or generality evidence and may not be promoted into Revision 3.
6. The user stated that the five model families may be used when testing requires them. Before Stage 4 calls, the project must still freeze exact model IDs, providers, reasoning/effort, token budgets, call counts and costs under the external-model rules. Opus remains outside this authorization and requires per-call approval.

## Stage 2 Task-and-Oracle Freeze Entry Decision

0. On 2026-08-07 the user explicitly approved the Stage 2 plan and activated its goal. WP0--WP6 passed: 32 dual Oracles agree, Generation/Execution leakage is zero and the resealed 1104-entry final technical manifest has zero hash failures. Independent human reviewer `yi lv` inspected all ten checks, confirmed the single-file decision-log reseal delta and retained `PASS`; the fail-closed validator returned `PASS`. Stage 2 is therefore `SUCCESS` without lowering any denominator. The first failed human-validation attempt remains preserved. Stage 3 execution and all model/method calls still require a new plan and explicit authorization.
1. Stage 1 is complete at `SUCCESS / 4_OF_4_QUALIFIED`; TigerBeetle, Lago, OpenProject and Saleor are no longer pending T0/B3 candidates.
2. The next actual research stage is Stage 2: construct and freeze 32 business tasks, 8 evidence-deficient controls, 128 business requests, 32 structural negative controls, separate rule and execution Oracles, blinding maps and hash manifests across the fixed eight-system portfolio.
3. The Stage 2 execution contract is `working/exploration/20260807_stage2_task_oracle_freeze/STAGE2_TASK_ORACLE_FREEZE_GOAL_PLAN_20260807_CN.md`; the authoritative cross-conversation entry is `working/handoff/HANDOFF_20260807_STAGE2_TASK_ORACLE_FREEZE_ENTRY_CN.md`.
4. Existing T0/B3 evidence is a source for task construction but may not be copied into generation views as answers. No task, request or Oracle may be changed after observing any future ECAS or Direct-Rego output.
5. Stage 2 is complete only if all 8 systems, 32 business tasks, 8 controls, 128 business requests, 32 structural controls and 32 dual Oracles pass the freeze, leakage and hash gates with zero unresolved Oracle disagreements. The denominator may not be reduced to declare success.
6. This decision and plan authorize no Qwen, GLM, Kimi, DeepSeek, OpenAI, ECAS, Direct-Rego, paid API, GPU, formal comparison, automatic retry, Revision 3 mutation, manuscript promotion, submission or publication. Any Docker/WSL execution newly required for an execution Oracle remains subject to the experiment gate and the exact future goal authorization.

## Saleor Recovery and Stage 1 Completion Decision

1. The user explicitly authorized one bounded Saleor recovery attempt using a changed acquisition method, with alternatives to be considered only if it failed.
2. The exact frozen linux/amd64 manifest `sha256:46406d0f84e2b0c1a123e88dab85ccd640ccf513ac570c68950304ad4ba0b937` was acquired through `skopeo` OCI transport and verified byte-for-byte. No alternate version or image was used.
3. Direct `skopeo` daemon import failed only because its API 1.22 is incompatible with Docker 29.1.3's minimum API 1.44. The same verified OCI was exported as a Docker archive and loaded successfully. This is a resolved protocol compatibility failure and is not eligible as a scientific failure.
4. Saleor completed two independent clean-state native T0 runs. Both accepted the 50/100 valid refund and rejected the 500/100 semantic-invalid refund with `AMOUNT_GREATER_THAN_AVAILABLE`; normalized result files are byte-identical.
5. Saleor is therefore `QUALIFIED`, and the current Stage 1 status becomes `SUCCESS / 4_OF_4_QUALIFIED`. The original 3/4 closeout remains an immutable historical snapshot rather than being erased.
6. This completion is non-scientific engineering qualification. It does not authorize or establish ECAS superiority, Direct-Rego comparison, a five-model matrix, manuscript promotion, submission or publication. Revision 3 remains authoritative and unchanged.

## Stage 1 Four-System T0＋B3 Closeout Decision

1. The user explicitly authorized the bounded Stage 1 run for TigerBeetle 0.17.9, Lago v1.51.0, OpenProject 17.4.0 and Saleor 3.23.7, with no models, paid APIs, GPU, ECAS, Direct-Rego or Revision 3 mutation.
2. TigerBeetle, Lago and OpenProject each passed two independent clean-state T0＋B3 repetitions. Their result JSON files are hash-identical across repetitions and each native system rejected the frozen semantic-invalid input while B3 accepted it and rejected the structural control.
3. Saleor does not qualify. Its official source, GraphQL schema and remote linux/amd64 image digest were fixed, and B3 passed twice, but the exact image failed to finish downloading in two bounded 20-minute attempts. Native T0 was never run.
4. Apply the preregistered stop rule: after two identical acquisition blocks, stop without a third pull, alternate image, alternate version or substituted system. Classify the result as `NOT_QUALIFIED_ENGINEERING`, not as a business or scientific failure.
5. The overall four-system stage is therefore unsuccessful by its all-four criterion: `3_OF_4_QUALIFIED`. Preserve the successful three-system evidence and the Saleor failure boundary without denominator repair.
6. Any Saleor recovery requires a new user authorization and a changed acquisition method, preferably verified offline OCI import or another registry transport. Repeating the same pull is not implicitly authorized.
7. No five-model formal matrix may start from this decision. Exact model identities, call counts and cost ceilings remain separately approval-gated. Revision 3 remains authoritative and unchanged.

## Five-Model Coequal Comparison-Plan Revision Decision

1. The user approved revising the draft comparison plan so that Qwen, GLM, Kimi, DeepSeek and an exact OpenAI API model enter the same formal experiment as five coequal model blocks. The prior primary-model versus later-sensitivity split is removed from the draft.
2. Within each exact model block, Direct-Rego and ECAS receive the same frozen tasks, evidence, Evidence Inventory, prompt budget, configuration and three repetitions. The scientific comparison is the paired ECAS--Direct-Rego difference within model, not a model leaderboard.
3. Models and repetitions are moderators/blocks, not independent task samples. The task remains the inferential unit within systems; model-by-repetition rows may not be used as pseudo-replication.
4. The revised formal matrix contains 40 task packets, two generative routes, three repetitions and five models: at most 1200 formal calls. This cap includes no automatic retry authorization; any retry requires a failure audit and new explicit authorization.
5. A cross-model-stability claim requires the predeclared coverage, unsafe-allow, evidence-deficient-control and finance-subdomain gates to hold in at least four of the five model blocks. Any failing model remains an explicit boundary.
6. “ChatGPT” is not a reproducible model identifier. Before execution, the plan must freeze the exact OpenAI API model and exact Qwen/GLM/Kimi/DeepSeek model IDs, providers, versions, reasoning/effort, Token limits, call counts and cost ceilings.
7. This decision changes the plan only. It authorizes no model/API/GPU call, T0, Docker experiment, formal comparison, automatic retry, Revision 3 mutation, manuscript promotion, submission or publication.

## Finance B3 All-Ten Completion Decision

1. The user approved extending the frozen fair B3 definition from the three-case gate to the remaining seven finance-oriented cases without models, paid APIs, GPUs, ECAS, formal comparison or Revision 3 mutation.
2. Formance, Blnk, Freqtrade, LNbits, Midaz, openIMIS and Bigcapital completed the same valid, semantic-invalid and schema-invalid-control design twice. Combined with the frozen jPOS, LedgerSMB and BTCPay pilot evidence, the audit covers 10 cases and 60 decision files.
3. The all-ten audit passed: 40 accepts, 20 rejects, all 20 semantic-invalid executions accepted, all 20 structural controls rejected, 30/30 repeated decision pairs byte-identical and zero residual B3 containers.
4. B3 caught `0/10` target business-semantic cases. This means the tested pre-execution contract surfaces do not express those target rules; it does not establish ECAS superiority because ECAS was not executed.
5. Preserve the authority strata `4 HIGH / 5 MEDIUM / 1 LOW`. LedgerSMB remains `observer_ingress / LOW` and may not be presented as a product-published B3 surface.
6. The completion report is `working/exploration/20260806_finance_b3_all10/FINANCE_B3_ALL10_COMPLETION_20260806_CN.md`; the audit is `working/exploration/20260806_finance_b3_all10/runs/audit/ALL10_AUDIT.json`.
7. Revision 3 remains authoritative and unchanged. The next permissible step is protocol design for a separately authorized fair comparison; this decision authorizes no ECAS run, model/API/GPU call, formal comparison, manuscript promotion, submission or publication.

## Finance B3 Three-Case Gate Decision

1. The user approved the frozen ten-case B3 plan and a bounded three-case implementation gate without models, paid APIs, ECAS, formal comparison or Revision 3 mutation.
2. B3 is defined as the strongest complete pre-execution contract surface actually applicable to a case: published OpenAPI/JSON Schema, release DTO/enums/types/validation tags, or an explicitly downgraded observer-ingress schema. B3 may not call the business oracle, query business state or encode the known case answer.
3. The pre-run freeze is `working/exploration/20260806_finance_b3_pilot/PRE_RUN_FREEZE_MANIFEST_20260806.sha256`; the exact validator is `jsonschema==4.26.0` with format dependencies in image `sha256:4201fc5465401ccdd8dd26c09a1483ba5713f015c6626bdc11ce9b760f7d0580`.
4. jPOS, LedgerSMB and BTCPay each ran valid, semantic-invalid and schema-invalid-control inputs twice under network isolation and read-only runtime constraints. The audit passed: 18 decision files, 12 accepts, 6 rejects, all 6 semantic-invalid runs accepted, all 6 negative controls rejected, 9/9 cross-run outputs byte-identical and zero residual B3 containers.
5. The three target semantic rules are not represented by these pre-execution B3 surfaces. This is isolated baseline evidence, not an ECAS superiority result; ECAS was not executed.
6. The engineering gate is `GO_TO_ALL_10_B3_ADAPTATION_ONLY`. Expand in authority order and retain explicit authority labels. LedgerSMB remains `observer_ingress / LOW`; it must not be described as a complete product-published B3 unless a stronger native transport contract is found.
7. The gate report is `working/exploration/20260806_finance_b3_pilot/FINANCE_B3_THREE_CASE_GATE_REPORT_20260806_CN.md`. Revision 3 PDF and source ZIP hashes remain unchanged.
8. This decision does not authorize ECAS, a model, GPU, paid API, formal B3/ECAS/policy-as-code comparison, manuscript promotion, submission or publication.

## Finance T0 Ten-Case Authorization Decision

1. The user approved a bounded goal to obtain ten reproducible local finance-oriented test cases. The frozen protocol is `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_PROTOCOL_20260806_CN.md`.
2. A case qualifies only after exact source/image/API-contract identity is frozen, one valid and one structurally valid semantic-invalid request are sealed before execution, and both requests reproduce from clean state twice.
3. Use only Ubuntu WSL2 native Docker under `/root/ecas_finance_t0_20260806`; do not mix Docker Desktop state. Clean up only exact case-owned resources.
4. Primary queue: Formance Ledger, Blnk, Freqtrade, LedgerSMB, LNbits, BTCPay Server, Hyperswitch, Midaz, Open Bank Project, and openIMIS. Backups: Firefly III, Kill Bill, Lago, jPOS, Mojaloop, and Bigcapital.
5. The authorization covers repository download, local container execution, deterministic seeds and HTTP/API T0 only. It excludes models, paid APIs, GPUs, formal B3/ECAS/policy-as-code comparison, real funds, live trading, production bank links, manuscript changes, submission and publication.
6. Environment, path, dependency, transport and schema failures are engineering failures. They may trigger documented repair or substitution but never scientific conclusions.
7. Ten qualified systems are a bounded test portfolio, not proof of universal generality. Stop at ten and report the observed coverage and failure boundary.
8. Revision 3 remains authoritative and immutable; T0 evidence is explicitly mapped to no manuscript claim.
9. The bounded goal completed at `10/10 QUALIFIED`: Formance Ledger v2.4.12, Blnk v0.15.2, Freqtrade 2026.7, LedgerSMB 1.13.7, LNbits v1.5.6, BTCPay Server v2.4.1, Midaz v3.8.0, openIMIS 26.04, jPOS 2.1.10, and Bigcapital v0.25.25 each passed two clean repetitions. Hyperswitch and Open Bank Project were replaced by jPOS and Bigcapital under the pre-frozen backup rule because bounded deterministic runtime paths did not close; this is recorded only as an engineering scope boundary. The completion audit verified 190 evidence-manifest entries, zero pending cases, zero residual case containers, and unchanged Revision 3 PDF/source ZIP hashes. Completion report: `working/exploration/20260806_finance_t0_10cases/FINANCE_T0_10CASE_COMPLETION_20260806_CN.md`. These are isolated engineering evidence and change no manuscript claim.

## ASE Submission-Insurance Freeze and New Experiment Boundary

1. The user confirms Revision 3 as the current ASE submission-insurance version. It is the only authoritative manuscript and the immediate submission fallback; this decision does not record that portal submission has occurred.
2. Freeze the Revision 3 PDF, clean source, source ZIP, frozen results, figures, references, traceability, and reviewer artifacts. Experimental exploration may not edit them in place or backfill new evidence into the old primary study.
3. Supersede CBHG and the business/development/security three-Agent split as the active innovation route. They remain historical exploration/audit artifacts; renaming the existing Evidence/Inventory handoff or splitting roles is not accepted as independent novelty without a distinct mechanism and evidence.
4. Open a separately governed experiment-exploration route around strong baselines and genuinely unseen systems. The first decision gate is a complete OpenAPI 3.1/JSON Schema or native-framework validator B3 on the existing frozen requests.
5. Search for unseen systems in parallel with B3, but limit this parallel work to source/license/version/schema/business-constraint and execution-feasibility screening until the B3 gate is known. Do not invest in full annotation or model runs before that gate.
6. If B3 Pareto-dominates ECAS on legitimate coverage and unsafe allowance, stop the overall-performance route and revise the mechanism or claim. If ECAS trades additional semantic coverage for risk, report a predeclared Pareto/non-inferiority question rather than an overall win.
7. Formal confirmation, if justified, requires a common decision interface, equal raw-artifact access, an external policy-as-code method, an independent human ceiling, pre-output sealed oracle, and genuinely unseen systems. Multi-model runs are sensitivity analysis only and come last.
8. The detailed continuation contract is `working/handoff/HANDOFF_20260806_ASE_SUBMISSION_INSURANCE_FREEZE_AND_EXPERIMENT_EXPLORATION_CN.md`.
9. This decision authorizes no external-model call, Opus call, Ollama/GPU generation, paid API, formal experiment, manuscript promotion, submission, or publication. Each gated action requires its own current-task authorization.

## Unseen-System Source-Screening Decision

1. Exploration 1 stops after five systems pass the source screen: OpenProject 17.4.0, Saleor 3.23.7, Mattermost 11.7.2, Kill Bill 0.24.18, and Lago 1.51.0.
2. “Unseen” means not previously used as a studied system in the current ECAS project. Exact-name audit found no system use; the two Lago text hits are author-name occurrences (“Dal Lago”), not the Lago product. This is not a claim of global novelty.
3. Each candidate has a fixed version, auditable license, public business/developer evidence, an OpenAPI/GraphQL/Swagger or native validation surface, a non-structural business constraint, and an official local deployment route.
4. Prioritize OpenProject for the first pilot and Saleor for cross-domain confirmation. Mattermost is the first permissions-focused alternate; Kill Bill and Lago are billing-focused alternates with explicit T0 export/pinning conditions.
5. Source-screen `PASS` does not mean runtime qualification. Before any pilot, deterministic T0 must pin image digests, start the system locally, hash the API contract, test validator negative controls, and prove one positive and one negative seeded business case without model execution.
6. The complete B3 stop/go gate remains upstream of scientific comparison. No candidate selection may weaken the baseline, treat all-reject as success, or convert environment/schema failures into scientific results.
7. The authoritative record is `working/exploration/20260806_unseen_system_screening/UNSEEN_SYSTEM_SCREENING_20260806_CN.md`. This decision authorizes no runtime T0, formal experiment, model/API/GPU call, manuscript promotion, submission, or publication.

## Expanded Unseen-System Census Decision

1. Replace the five-system stopping target with a predeclared funnel: 50--100 systems in S0 census, 20--30 in S1 source screening, 8--12 in the deterministic T0 queue, 5--8 in any later formal comparison, and 3--5 in primary analysis. The original five systems remain seed records, not the full generality claim.
2. Freeze selection before runtime evidence using domain, API-contract type, semantic-constraint type, version, license, local execution path, and business-evidence gates. Candidate volume alone is not evidence of generality.
3. The first expanded checkpoint contains 75 unique systems across 12 domain strata. S1 contains 26 unique high-potential systems: 16 `SOURCE_PASS` and 10 `SOURCE_CONDITIONAL`.
4. The 12-system T0 queue is OpenProject, Saleor, Mattermost, Firefly III, authentik, OpenEMR, Cal.com, Directus, NetBox, Mayan EDMS, Twenty, and Kill Bill. It deliberately spans REST/OpenAPI, GraphQL, runtime schema export, permissions, workflow, lifecycle, finance, scheduling, relationship, and multitenancy constraints.
5. Freeze the saturation stop as: stop at 100 systems; or, after at least 50 candidates, stop when 10 consecutive eligible systems add no new domain x API x semantic-constraint cell; or stop after two documented no-progress expansion rounds. Saturation is not reached at 75 because important strata and coverage cells remain sparse.
6. Treat non-OSI or source-available terms and split core/enterprise features as explicit feasibility boundaries, not as passes. Invoice Ninja (Elastic-2.0) and NocoDB (Sustainable Use License 1.0) are recorded counterexamples rather than silently normalized as ordinary open-source candidates.
7. The authoritative artifacts are `working/exploration/20260806_unseen_system_screening/EXPANDED_CENSUS_PROTOCOL_20260806_CN.md`, `CANDIDATE_UNIVERSE_75_20260806.csv`, `S1_HIGH_POTENTIAL_SCREEN_26_20260806.csv`, and `EXPANDED_CENSUS_CHECKPOINT_20260806_CN.md`.
8. This decision authorizes source-level census work only. It authorizes no repository checkout, Docker/container startup, runtime T0, formal experiment, model/API/GPU call, manuscript promotion, submission, or publication.

## Finance and Banking Priority Decision

1. In response to the user's domain priority, weight unseen-system selection toward finance and banking while retaining a smaller cross-domain confirmation layer. Do not equate repeated accounting products with broader financial coverage.
2. Add 25 finance-focused candidates to the frozen 75-system census, reaching the predeclared S0 hard cap of 100. The resulting universe contains 31 explicitly finance-focused systems across core/open banking, payments/clearing/card interchange, ledgers/accounting, wealth/tax, trading/risk, and insurance claims.
3. Keep S1 within its frozen 20--30 range by reselecting 30 systems rather than appending all new candidates. The current S1 contains 19 finance/banking and 11 cross-domain systems, with 16 `SOURCE_PASS` and 14 `SOURCE_CONDITIONAL` overall.
4. The 15 newly screened finance systems contain 7 `SOURCE_PASS` and 8 `SOURCE_CONDITIONAL`. Conditional means version/component/schema/license/deployment or native-adapter qualification remains open; it is not a scientific failure.
5. Exclude Fineract and ERPNext from unseen-system primary selection because project records show that both were previously used as protected systems, evidence sources, development lanes, or runtime cases. They may appear only as separately labeled historical/secondary transfer evidence.
6. Weight the 12-system T0 queue toward eight financial systems: Formance Ledger, Blnk, Hyperswitch, Midaz, Open Bank Project, Freqtrade, LedgerSMB, and openIMIS. Retain OpenProject, Saleor, authentik, and OpenEMR as cross-domain confirmation. Queue order does not override each system's conditional blockers.
7. If formal comparison is later justified and separately authorized, target 4--6 finance systems plus 1--2 cross-domain confirmations among the 5--8 formal systems; select 3--5 primary finance systems from different financial subdomains. This can support a bounded finance-oriented applicability claim, not universal software generality.
8. Stop S0 expansion at 100 as predeclared. This is a hard-cap stop, not natural coverage saturation; further candidate expansion requires a new protocol decision rather than silently moving the cap.
9. Authoritative artifacts are `FINANCE_BANKING_DELTA_25_20260806.csv`, `CANDIDATE_UNIVERSE_FINANCE_PRIORITY_100_20260806.csv`, `FINANCE_BANKING_HIGH_POTENTIAL_15_20260806.csv`, `S1_FINANCE_PRIORITY_SCREEN_30_20260806.csv`, and `FINANCE_BANKING_PRIORITY_CHECKPOINT_20260806_CN.md` under `working/exploration/20260806_unseen_system_screening/`.
10. This decision authorizes no repository checkout, Docker/container startup, T0, formal experiment, model/API/GPU call, manuscript promotion, submission, or publication.

## Historical Revision 4 Independent-Handoff and Unified Five-Model Decision

The following 2026-08-05 decision is retained for provenance but is superseded as the active route by the 2026-08-06 decision above.

1. Open an isolated Revision 4 research-planning branch while preserving Revision 3 as the only authoritative manuscript and submission fallback.
2. Reject a simple rerun of the old 30 tasks across Qwen3.5 9B, DeepSeek, GLM, Kimi, and GPT. The old inputs are author-selected and contain task-specific `proposal_focus`; more model rows would not resolve the Inventory-independence novelty problem.
3. Define the candidate new mechanism as an answer-free claim--binding handoff graph (CBHG): source-linked business claims, developer/API bindings, mapping edges, and explicit `supported/conflicted/unresolved` states. The Security role may not encode a rule class, primitive, predicate, candidate, or admission answer.
4. Use a task-paired Raw/ECAS design. Both arms receive identical frozen raw evidence, target operation, full general catalog, and rule schema; only ECAS receives CBHG. The same model, parser, compiler, admission gate, and pre-sealed oracle evaluate both arms.
5. Treat the five exact models as fixed sensitivity moderators, not a leaderboard. Report within-model Raw--ECAS direction; task × model rows and repetitions are not independent tasks.
6. Require at least two genuinely new, never-studied systems for the primary analysis. Old Fineract/ERPNext and historical V3 systems cannot be relabeled unseen or pooled into the primary denominator; at most they are separately reported secondary transfer evidence.
7. Build and hash-seal a dual-evaluator oracle before any participant output or model call. Freeze allocation/randomization, role outputs, opaque arm IDs, candidate/admission records, and reveal the oracle only after all outputs are sealed.
8. The v0.2 protocol and smoke are approved only for Phase 1--4 development. Formal preregistration and any model call remain blocked until new-system, participant, oracle, sample/statistics, closest-work, runner, token/cost, authorization, reproduction, and traceability gates close.
9. No external-model call is authorized by this decision. Qwen service startup/GPU generation and every paid provider call require a separate explicit authorization after a declared model/config/budget/call count.
10. The current acceptance planning ranges remain historical planning judgments; this non-scientific plan/smoke does not raise the manuscript acceptance estimate.

## Revision 3 Opus Review and Innovation Decision

1. The 2026-08-05 authorized Opus call is usable only through the separately recorded, hash-identical offline reparse. The original `capture_incomplete` metadata remains a true parser-failure record and is not overwritten.
2. The wrapper now deduplicates Claude Code stream fragments by event UUID rather than `message.id`; the complete offline guard suite is `16/16 PASS`.
3. Revision 3 remains the only authoritative manuscript. This review changes no claim, formula, result, figure, artifact, PDF, or ZIP.
4. Adopt the review's core judgment: ASE and the trustworthy-LLM SI fit are strong, but scientific significance is only partially resolved; adding formulas or renamed contracts is not novelty.
5. Route priority is: nearest-neighbor/positive narrative tightening (`GO`); independent Inventory and cross-role handoff study (`CONDITIONAL_GO`, preferred new research); semantic-obligation monitor (`CONDITIONAL_GO`, only after closest-work and reduction audit).
6. Reject the Opus misuse of `ANNOTATION_CLOSURE_FAIL`, reclassify single-run variance as a P1 validity limit rather than reproducibility failure, and do not volunteer the CSI desk-rejection history in the ASE cover letter unless explicitly asked.
7. Codex planning ranges are current 13%–23%, route-1-only 17%–27%, and successful independent new mechanism/evidence 26%–43%. They are subjective planning intervals, not official ASE statistics.
8. No additional Opus call is authorized. Any new paid review, new experiment, or Revision 4 promotion requires a separate decision and applicable authorization.

## Opus 5 Review Failure Decision

1. The 2026-08-04 Revision 3 Opus call is invalid for review use because the production wrapper returned `secret_leak_detected` and failed the completeness gate. Process success and incurred cost do not convert it into an admissible review.
2. The redacted derivative may be used only to diagnose the generic `sk-` false positive; it must not be used to reconstruct or restore Opus content.
3. No retry is authorized. Any future Opus call requires a new explicit user authorization after an offline-tested wrapper repair.
4. Revision 3 remains the only authoritative manuscript. No finding from the failed call may change its claims, formulas, results, figures, or acceptance estimate.

## ASE Revision 1 Decisions

1. Target *Automated Software Engineering* and its trustworthy-LLM special issue with ECAS framed as a software-engineering workflow for turning business/development knowledge into executable field-level security rules.
2. Preserve the author's established language and paragraph rhythm. Revise surgically; do not perform a manuscript-wide AI rewrite.
3. Keep the original Figure 1--3 mechanism structures. Add data figures instead of replacing them.
4. Fix the contribution list at three items: field-policy reconstruction plus Evidence Contract; auditable end-to-end toolchain; frozen evaluation plus assurance boundary.
5. Treat formalization as an executable specification of the implemented boundary: four equations, one algorithm, and bounded invariants. Do not claim a new general theory merely because formulas were added.
6. Present primary and separately frozen post-hoc evidence in adjacent sections but never pool denominators or backfill the primary conclusion.
7. Report the B2-to-ECAS change as four additional safe-served tasks plus one over-permissive allowance, together with the two ECAS unsafe cases.
8. Keep limitations accurate but centralized. Foreground the positive engineering value in the abstract, introduction, discussion, and conclusion.
9. Do not rerun or alter the frozen experiment for this revision. Any new holdout or semantic-assurance study requires a separately frozen protocol.
10. Close author-review provenance by narrowing the manuscript to the supported aggregate process statement; do not fabricate a row-level author-review ledger.
11. Adopt external-review comments only when supported by official venue rules, implementation evidence, or frozen results. Reject invented page limits, forced population inference, and post-hoc B15/B22 patching on the same tasks.

## ASE Revision 3 Formula Typography Decision

1. Preserve Springer/Computer Modern's natural mathematical hierarchy: base symbols, subscripts, second-level scripts, and large operators are not forced to one visual size.
2. Use upright operator typography for named predicates and functions, upright roman typography for protocol states, and `\mathit` for multi-character field variables. Do not shrink formulas with `\small`, `\scriptsize`, or `\resizebox`.
3. Number every standalone formula that carries a theoretical definition, invariant, assurance boundary, or observed failure mechanism. Keep simple explanatory arithmetic inline. The current sequence is (1)--(14).
4. Use aligned structures and genuinely enclosing delimiter pairs for multi-line logic. Fix Algorithm 1 at its source position after Equation (6) so floats do not invert the explanatory order.
5. This decision supersedes only the Revision 1 presentation choice of numbering four core equations. It does not expand the formalization into a new general theory and does not change any formula meaning, experiment, frozen result, figure, table, or artifact.

## Innovation Exploration Branch Decision

1. Freeze Revision 3 as the authoritative fallback before any further novelty enhancement. Innovation work must occur in an isolated sandbox and cannot mutate or silently supersede the verified PDF, clean source, ZIP, results, or reviewer artifacts.
2. Treat novelty enhancement as a decision problem before treating it as a writing task. First test up to three mechanisms against closest work, implementation traceability, B15/B22, evidence requirements, and stop conditions.
3. Do not equate added formulas with added novelty. A new definition, proposition, algorithm, or guarantee is admissible only when it maps to implementation and evidence and resolves a real uncertainty.
4. New contradiction detection, semantic verification, correctness guarantees, or Inventory-independent claims require separately governed implementation and experiments; they cannot be backfilled into the frozen study.
5. Promote an innovation candidate to Revision 4 only after novelty, implementation, evidence, narrative, independent review, and submission-QA gates all pass. Otherwise preserve the failure audit and return to Revision 3.

## Paid Lower-AI Prose Merge Decision (2026-08-10)

1. For the Word candidate prepared for similarity and AI-style checking, the paid human-edited lower-AI manuscript is the primary prose authority.
2. Revision 3 supplies scientific facts, figures, tables, formulas, hyperlinks, references, and protected protocol wording; it is not the default wording source for this merge.
3. Preserve paid wording wherever it does not alter scientific meaning. Corrections are limited to material factual, protocol, or structural defects; do not perform a broad Codex rewrite.
4. The resulting DOCX is an isolated candidate and does not supersede or modify the authoritative Revision 3 PDF, source, ZIP, results, or reviewer artifact.
5. Promotion requires author review. No external model/API call, new experiment, submission, or publication is authorized by this merge.
