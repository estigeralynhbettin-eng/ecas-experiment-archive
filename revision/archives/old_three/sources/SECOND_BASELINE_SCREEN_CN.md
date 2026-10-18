# 第二外部基线候选核验：AutoPAC

核验时间：2026-10-13；范围：论文、作者官方项目页、固定提交的公开仓库树和关键源码静态阅读。没有安装依赖、加载权重、启动服务、调用模型、训练或运行实验。当前状态：`CANDIDATE_SCREENED / EXPERIMENT_PENDING`。

## 结论

建议两个主要候选为 **Prose2Policy (P2P)** 和 **AutoPAC**。AutoPAC 不是仅有论文名称的空候选：作者组官方项目页直接链接真实仓库，仓库包含生成服务、模型与训练代码、数据集、格式/语法校验脚本和测试材料。它和 P2P 都以 Rego 为输出，适合作为生成与校验流程的相关工作和后续比较对象。

**目前不具备声称完成原版 AutoPAC 复现的条件。** 固定仓库提交缺少 README 明确要求的微调 checkpoint，未检出许可证，公开校验脚本与生成服务还有静态可见的请求协议差异。若下一阶段按公开论文独立实现可比流程，应称 `AutoPAC-style adaptation (author implementation)`；不能简称为 reproduced AutoPAC，也不能引用作者成绩作为 ECAS 的实验结果。P2P 同样应先区分原论文方法、可获得原实现，以及作者自建适配实现。

## 来源与书目

- 作者组官方项目页：[UbiNet AutoPAC](https://ubinet-iitkgp.github.io/ubinet/pages/autopac.html)。页面的 AutoPAC Code / Dataset 链接分别指向 `NehaChowdhary/AutoPAC` 及其 DatasetOpaRules 目录。原 HTML 已保存为 `autopac_official_project.html`。
- 官方关联代码仓库：[NehaChowdhary/AutoPAC](https://github.com/NehaChowdhary/AutoPAC)。固定提交 `e31641a64d91d18574e338b8a38409d3f94391d7`；完整递归树返回 `truncated=false`，保存为 `autopac_tree_main.json`。
- 作者公开论文：[AutoPAC author PDF](https://subhrendu1987.github.io/pub/papers/2024.COMSNETS.Autopac.pdf)。获取到 234,660 字节、`%PDF-1.7` 文件；网页全文读取为 9 页，首页题名和四位作者与 Crossref 匹配。文件名含 2024 不改变正式发表年份。
- Crossref 注册元数据：题名 *AutoPAC: Exploring LLMs for Automating Policy to Code Conversion in Business Organizations*；Neha Chowdhary、Tanmoy Dutta、Subhrendu Chattopadhyay、Sandip Chakraborty；2025 17th International Conference on COMmunication Systems and NETworks (COMSNETS)，667–675；[DOI 10.1109/COMSNETS63942.2025.10885751](https://doi.org/10.1109/COMSNETS63942.2025.10885751)。原返回保存为 `autopac_crossref_metadata.json`。
- 本地索引：2026-10-13 的只读索引状态已核查；精确 `AutoPAC` 检索在 general/catalog/FTS 三层均为 0 条，见 `retrieval_pack_autopac_20261013.md/json`。这是有界本地检索结果，不是论文不存在。

所有实际获取均经 `D:\lunwen\download_with_direct_first.ps1`。`raw.githubusercontent.com` 的首次内容获取失败后，改用仓库树记录的同一对象 GitHub blob API 获取成功；失败记录为传输问题，没有计入科学结果。关键源码静态快照在 `autopac_source_snapshot`。

## 公开材料逐项核验

| 项目 | 已观察到的对象与结果 | 当前含义 |
|---|---|---|
| 官方归属 | 作者组项目页明确指向该仓库；题名、作者与论文一致 | 官方关联可确认 |
| 生成实现 | `PrivateGPT/Translator/privateGPT_server.py` 读取 `MODEL_NAME/MODEL_DIR`，调用 `T5Model.load_from_checkpoint` 和 tokenizer，生成回答；`t5model.py` 是 Lightning/T5 实现 | 是真实实现，非 README 空承诺 |
| 微调材料 | 树中有 `Code_t5_training.ipynb`、`t5dataset.py`、`t5model.py`、模型环境与依赖文件；论文 V-C/V-D 采用 fine-tuned CodeT5-small | 可研究其方法与训练流程；本次未重新训练 |
| 训练权重 | Translator README 要求拼接 `codet5_fine_tuned_split/*` 为 `.ckpt`；完整树没有该目录，也没有 `.ckpt/.bin/.safetensors` 权重或可见权重下载链接 | 原版生成服务不能仅靠当前仓库启动；checkpoint 待取得 |
| 校验材料 | `Test Setup/lint_opa.py`、`OpenAI_Judge.py`、unit-test CSV、测试/训练指标文件真实存在 | 可对照流程；预存成绩不是我们的复现实测 |
| 测试语义 | 原论文 IV 的 Local Verifier 使用用户提供的 unit tests；源码 README 同样如此 | 不写成 AutoPAC 自动生成独立测试；自动测试生成是 P2P 的能力 |
| 许可证 | GitHub repository API 返回 `license=null`；完整树没有 LICENSE、COPYING 或 NOTICE | 未获得可确认的代码再分发许可；正式 artifact 不应宣称其为已许可开源依赖 |
| 运行协议 | server 读 JSON 对象的 `question`；`lint_opa.py` 用 `json.dumps` 后把含 `query` 的字符串传给 `requests.post(..., json=...)` | 静态请求格式不匹配；须记录修复，再讨论复现 |
| 外部服务依赖 | `lint_opa.py` 调用公共 OPA playground 的 fmt/lint HTTP 接口 | 原脚本不是完整本地确定性流程；适配应冻结本地 OPA 版本并记录偏离 |
| 文本长度 | server 固定输入与输出长度 128，论文也以原数据集最高长度确定 128 | 直接送入长 ECAS artifact bundle 会改变适用范围或截断；必须先声明输入适配 |
| 实验状态 | 没有执行任何生成、校验、训练或性能比较 | 仅候选与接口核验；`EXPERIMENT_PENDING` |

## 与 ECAS 的可比范围及承接

| 工作 | 输入/输出与已完成能力 | ECAS 承接与需要适配的接口 |
|---|---|---|
| P2P | NLACP → DSARCP → Rego；组织 schema 检查、Regal lint、OPA 编译与正反测试生成/执行 | 承接结构化生成及确定性校验；其组织 schema 不等同于 ECAS 的源证据记录、API 版本/操作/字段准入契约。需明确 Rego/typed-policy 语义映射 |
| AutoPAC | 自然语言组织策略 → fine-tuned CodeT5-small → Rego；Judge LLM、格式处理、用户提供 unit tests | 承接生成器与规则校验器分离；授权策略到请求字段校验有任务差异，需声明业务材料/字段上下文如何进入模型，保持可比的输入与预算 |
| RAGent | 高层要求 + 组织实体检索 → decision/subject/action/resource/purpose/condition 规则；BART 语义错误分类反馈及迭代修正 | 适合结构化候选与校验反馈对照；输出不直接提供 ECAS 的版本化 API 目标与字段路径证据绑定，不能把组件 F1 与 ECAS 的请求裁决率混成同一指标 |
| ECAS | 业务/开发材料 + API 与有限规则目录 → 引用证据的 typed policy → Inventory/Contract 准入 → gateway 请求校验 | 新增明确的、可检查的“哪条冻结证据支持哪个 primitive、API 版本/操作及路径”义务；checkers 检查已登记支持关系，语义解释来自事先人工复核，不声称独立理解原文 |

比较应把 P2P 和 AutoPAC 分成两行；合并一行会掩盖自动测试与用户测试、prompting 与 fine-tuning 的差别。表格适合放 Related Work，报告能力和接口，不填待完成的性能数据。

ECAS 与前人之间的承接可直接表述为“沿用生成—结构化—校验的分解，把已有生成能力连接到证据准入问题”。原方法的 Rego 或一般访问控制规则不能直接充当 ECAS 的 typed field policy；中间还需要输出映射、字段执行语义以及证据引用。该接口差异说明集成需要怎样的适配；它本身不是 ECAS 更优的证据。

## RAGent / AGentVLM 备选核验

RAGent 论文原始页面：[arXiv 2409.07489v1](https://arxiv.org/html/2409.07489v1)，2024-09-08；作者为 Sakuna Harinda Jayasundara、Nalin Asanka Gamagedara Arachchilage、Giovanni Russello。论文两处把实现指向 `accessframework/RAGent`，该 URL 在本次网页访问返回 404。现存 [paperwave/RAGent](https://github.com/paperwave/RAGent) 有完整真实树、generation/evaluation/prompts.py、eval_ragentv.py、evaluator.py、BART verification 及数据/向量库，但 paperwave 主页自述为研究资料存档组织，不能把其现存镜像称为作者官方最新版。固定树为 `6f11a4bbb79c2b55ed15f2a2173b846bfcf7ac5e`，API license 仍为 null。

AGentVLM 与 RAGent 作者相同，现有稿件中的正式引文 DOI 为 `10.1016/j.jisa.2026.104379`；出版社发现页有 code/data 可得声明，但这不足以把 2024 的镜像视为 2026 的原版 artifact。本次未确立两者完整版本对应关系，不把 RAGent 的公开实现标为 AGentVLM 的复现。

Lawal et al. 的 [NIST 原始出版页](https://csrc.nist.gov/pubs/conference/2025/01/16/translating-natural-language-specifications/final) 可确认论文和 DOI；页面 Supplemental Material 为 None available。本次有界检索没有确立作者官方可运行仓库。AutoPAC 的官方来源链因此更适合第二优先候选。

## 后续比较的最小决定项

1. 先冻结比较名称：原实现复现，或论文方法启发的作者实现。分别记录论文版本、原代码提交、任何修复/适配及模型。不能用更换原 CodeT5 为现有 Qwen 后的流程代表 native AutoPAC 性能。
2. 冻结共同任务子集和输入；不把人工写出的 canonical policy/实验 oracle 或 sealed evaluation labels 注入外部生成器。授权任务与字段校验任务必须经过可审查的语义映射；不以长材料截断作为 baseline 科学失败。
3. 分开 native-system comparison 与固定模型的机制比较。前者含模型、微调、语言与预算差异；后者应叫 P2P/AutoPAC-style adaptation，并让共享模型/材料/预算成立。ECAS 契约不可被用于修补对照输出后仍称原始对照。
4. 判定编译、证据引用/绑定、field-policy 语义和独立请求行为，各自保留分母。作者报告的原数据集成绩留在相关工作，不能用于与当前 ECAS 数据直接排名。
5. AutoPAC native 复现闭合项：原微调 checkpoint 与校验值、明确代码/数据许可证、校验请求协议修复与本地 OPA 版本。P2P 原实现获取仍按父任务核验状态管理。取得前不启动运行，不回填结果。

## 可交付文字

`related_work_proposal.tex` 给出约 350 词的可选英文稿件片段。它明确各方法已经做了什么，说明 ECAS 的承接接口，并集中保留一句当前评估范围。`baseline_metadata.bib` 是已核验元数据候选；正式引用合并由主稿编辑者处理，不改根状态或 manuscript。`baseline_screen_qa.json` 记录了 15 个来源文件存在且与台账 SHA-256 一致，仓库完整树的许可证/权重匹配均为 0；这项 PASS 只覆盖静态材料，不是运行复现通过。
