# 共同模型小试协议草案

状态：PROPOSED / NOT_AUTHORIZED / NOT_RUN。用户确定后冻结，修改须留版本。

## 1. 方法命名与可回答的问题

| 名称 | 实现 | 实质偏离 |
|---|---|---|
| P2P-style | 按论文构建检测分句、DSARCP、组织 schema、Rego、lint/编译、自动开发测试及有界反馈 | 自写提示；共同模型；业务约束接口适配；目前 Regal 尚不可用 |
| AutoPAC-style | 共同模型生成、Judge、确定性格式处理、操作者提供开发测试 | 微调 CodeT5-small 被替换，这是重大偏离；长输入/输出、OPA 版本及 Judge 接入改变 |
| ECAS-matched | 同模型、同可见来源生成原 V3 候选，经原证据契约及引擎 | 新生成结果独立记录；不替换历史结果 |

回答：上述适配流程在三例上的局部请求对表现、开发检查、调用数及成本差异。
不能回答：原 P2P/AutoPAC 的性能、总体准确率、ECAS 整体优越性。三个案例已有暴露，不是新增盲测。

## 2. 输入与输出接口

- 每例生成端只读 generation_inputs/<case>/packet.json 与 organization_schema.json。前者保留原文和来源元数据；仅删除 ECAS 专用 proposal_focus，添加中立身份/目标常量。
- 不手工把业务文档改写为答案政策，不交付原 ECAS 候选、历史决策、隐藏标签或 sealed_evaluation。
- P2P 检测输出政策句及引用，再提取 decision/subject/action/resource/condition/purpose；允许声明 OUT_OF_SCOPE 或 ABSTAIN。人工不得强行改为适用。
- 组织 schema 仅约束身份、目标和可用输入路径；条件的真值、关系和正确性须由模型从原文得出。
- Rego 输出 package external_pilot、import rego.v1、default allow := false；查询 data.external_pilot.allow，必须返回一个布尔值。
- 统一运行 envelope 为 request、trusted、subject、action、resource；身份/目标常量以中立适配器提供。原请求正文、可信状态和值不改。映射脚本须先用工程夹具验证并冻结。
- ECAS 保留原 V3 IR、契约和判定接口，以相同请求内容执行。向模型提供其方法所需输出 schema，不能从其他方法生成物中提取答案。
- 只做格式规范化和 schema 检查，不在人工作业中补充业务条件。语义性修复只能按本节预定调用处理并保留原候选。

## 3. 开发检查与最终评价分开

- P2P 自动开发测试由单独阶段基于政策原文/抽取结果生成；保留测试和原响应。测试通过仅是内部一致性证据。
- AutoPAC 原法依赖用户测试；本轮尚无用户提供的独立开发测试。若接受适配，由操作者按公开来源预先编写并冻结新开发测试，明确记录来源和新增条件；禁止复制最终请求对。不能伪装成原版自带测试。
- sealed_evaluation 的 O-L/O-I 仅在政策冻结后运行，标签不发模型，不供 Judge、自动测试生成或修复。
- 开发阶段每种外部方法每例最多一次修复；只反馈 lint、编译、schema 与开发测试，不能反馈最终评价标签。
- P2P 的 Regal lint 是必要流程组件：先恢复本地 Regal 或把该分支留作依赖阻塞，不静默删去后称完整流程。OPA 编译不能代替 Regal。

## 4. 拟议调用清单与预算

提供方：GLM / Z.AI，model=glm-5.2，thinking.type=enabled，reasoning_effort=high。只使用全局批准 wrapper；不读取未授权密钥。任务是业务政策推理，保留 high。

| 阶段 | 每例次数 | 三例合计 |
|---|---:|---:|
| P2P 检测、DSARCP、Rego、自动开发测试 | 4 | 12 |
| AutoPAC 生成、Judge | 2 | 6 |
| ECAS 同模型生成 | 1 | 3 |
| 基础调用 | 7 | 21 |
| P2P/AutoPAC 条件修复 | 最多各1 | 最多6 |
| 代表性 token smoke | 共最多3 | 最多3 |
| 总计 | | 最多30 |

单次最多16384完成tokens，包含推理；总完成tokens上限491520。每次还须限制输入在16384 tokens以内；实测计数器/模型上下文及 usage记录通过前不启动。总输入预算最多491520 tokens；该预算不代表人民币封顶。

先核验精确 endpoint、wrapper 原响应落盘与完整性保护，再做有界 smoke。历史 token 资格不能代替本轮最长输入与输出骨架检验；三次 smoke 无法建立完整输出资格则停止本轮，不追加调用。成功开发 smoke 不进入最终效果表。

人民币价格尚未核实，不宣称30元封顶；用户若要求金额上限，应先核实适用价目和调用前预算控制。不得在价格不明时把token上限换算成虚构费用。

发送内容仅限三例已准备的公开业务文档片段、版本/接口元数据、可用路径及本方法中间输出/开发测试；不发送论文全文、历史候选、最终请求对及标签。

## 5. 执行前门禁

1. 确定适配与具体调用配置；原版仍单独列 NOT_RUN。
2. 建立本轮范围冻结、输入/提示/代码清单及本地追溯表。
3. 优先 WSL 安装并核验 OPA/Regal；建立无网络 builtin 的隔离执行环境，限制资源与超时。
4. 验证请求映射、真假布尔、语法失败、undefined/非布尔、禁止 builtin 和完整单例路径；本次 T0 未通过则不得生成正式候选。
5. 完成 token smoke 和原响应落盘校验，然后按调用清单执行。

当前 Windows OPA 正反夹具仅为准备性验证，不能直接用作上述完整 T0。当前 gate为 block / T0_EVIDENCE_MISSING / scope=null。

## 6. 报告判定

- 同时满足合法 allow、违规 deny才称本例请求对识别正确；全拒绝不是正确识别。
- 生成/协议/工具失败、范围外、弃权、已执行判定分别报告，保留整体任务完成率；不把工具错误记成违规 deny，也不只挑成功候选报数。
- 原版与适配结果分开；ECAS 新结果与历史结果分开；记录源、候选、开发过程、总calls、input/completion/reasoning usage、latency和提供方实际费用字段。未返回费用记 UNKNOWN。
- 本轮只有三个事后案例、每例一对归档请求，最终只能提供局部证据；不得冻结整体优越性结论。
