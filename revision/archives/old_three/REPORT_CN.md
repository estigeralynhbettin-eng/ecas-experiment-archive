# P2P / AutoPAC 三例外部比较准备报告

本文件保留为准备阶段历史记录。用户已授权并完成本轮适配实验（27次GLM调用）；当前结果入口：[RESULTS_CN.md](RESULTS_CN.md)。下文“未调用/待决定”描述准备阶段，不是当前状态。

日期：2026-10-14。**当前没有两个外部基线的识别结果。测试输入和判定器已准备；原版缺少运行材料，需要确定是否接受明确标注的适配实现。**

## 原版资格

| 基线 | 本次实查 | 当前缺口 |
|---|---|---|
| Prose2Policy | 作者 Apple 页面指向论文；GitHub精确仓库检索0条且结果完整 | 有界检索未找到可确认原代码及可直接复用完整提示；不能断言全网没有 |
| AutoPAC | 官方固定提交 e31641a64d91d18574e338b8a38409d3f94391d7，218项完整树；release空 | README所需 codet5_fine_tuned_split/checkpoint 未在该树或release找到；原微调CodeT5-small不能启动 |

AutoPAC 仓库许可证路径未匹配，不据此推断所有材料不可研究或不可用。Hugging Face 权重查询失败是网络问题，不能记为没有权重。

官方入口：[P2P](https://machinelearning.apple.com/research/prose2policy)、[P2P论文](https://arxiv.org/html/2603.15799v1)、[AutoPAC代码](https://github.com/NehaChowdhary/AutoPAC)、[AutoPAC作者公开论文](https://subhrendu1987.github.io/pub/papers/2024.COMSNETS.Autopac.pdf)。本次证据索引见 NATIVE_QUALIFICATION.json；旧资料来源索引 sources/baseline_sources.json 保留其2026-10-13日期，不冒充全数本日重新下载。

## 已完成的准备

- 固定 B06、S02、S04，共两原项目。生成输入、组织schema与最终请求对分离；INPUT_MANIFEST.json 记录12份文件及原来源。
- 原文与接口可用路径保留，删除ECAS专属primitive focus；不把正确策略/历史候选交给基线。
- 本地冻结 OPA 1.19.0 的人工 allow、deny、语法拒绝、禁止网络builtin拒绝四项工程检查通过。原日志位于 local_opa_conformance；这不是基线效果或本范围完整T0。
- Linux OPA/Regal下载在前序准备中失败，故仅判定器准备采用已说明的Windows原生例外；Regal尚未可用。相关网络失败不计入科学分母。
- 本日重新读取正式门禁仍为 block / T0_EVIDENCE_MISSING / experiment_scope=null，见 GATE_SNAPSHOT.json。历史追溯PASS不能使本轮具备正式运行资格。

本轮 model_calls=0、baseline_effect_results=0。RUN_STATUS.json 所有原版和拟适配行均 NOT_RUN，判定为空。

## 建议的具体方案

推荐先用共同 GLM5.2 做 P2P-style、AutoPAC-style、ECAS-matched 三例小试，比较生成、开发校验及最终allow/deny。最多30次、单次最多16384完成tokens；输入也设上限，详细阶段和停止条件见 ADAPTATION_PROTOCOL_CN.md。

这只能比较文献流程的适配实现。特别是AutoPAC更换微调生成器，不能把结果冠以原版AutoPAC性能；若返修要求原系统直接实测，仍需取得作者代码/权重或换用能确认复现资格的比较系统。尚未给作者发信。

用户已经授权“用他们测试一下”的目标。现在需要确定的新增事项是原版缺失后的替代实现，以及具体发送内容和付费配置。[论文探索SKILL](C:/Users/PBCDCI/.codex/skills/academic-research-suite/SKILL.md)明确要求：Before any upload, require current-task authorization that names the provider, exact model, call count, content class/scope, and budget. 本轮未读取密钥或调用模型。

待决定：是否接受上述适配版、GLM/Z.AI glm-5.2、thinking enabled/high、最多30次、每次最多16384输入及16384完成tokens，仅发送三例公开源片段/接口信息/中间产物及开发测试。人民币价格未核实，不承诺金额封顶。

## 下一步与完成边界

确定后先补本轮范围T0、Regal、wrapper原响应保护及token资格，再执行。不能将工程检查PASS填入基线识别表。

三个案例均已暴露且事后选取；即使全通过，也不是整体准确率或独立效果实验。P2P若判断结构性约束范围外，应报告范围外/弃权，而非强行改造成成功或当作执行失败。

本次准备未修改稿件、旧实验、根追溯账本或投稿状态。项目入口已更新，当前阶段停在具体适配与调用配置待决定。
