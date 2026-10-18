# 适配比较中的语义核对事项

日期：2026-10-14。本文件记录可复核的核对事项，不把Judge意见自动当作科学事实。

## B06 文档条件与通用目标操作

AutoPAC-style 第11次Judge实际返回REVISE，指出生成政策对所有撤销强制trusted.reAgeIsLatestTransaction=true，而VIS-FSV-B06-01的原句是“Re-Age transactions can be reversed only if they are the latest transaction”。

当前共同target为POST /v1/loans/{loanId}/transactions/{transactionId}?command=undo；运行ABI只列reAgeIsLatestTransaction布尔值，未列目标交易是否Re-Age的单独字段。

因此需要核实：该适配器是否只向本政策送入Re-Age撤销，或者在通用接口上另有可靠交易类型条件。仅对原布尔正反请求判定正确，不能证明对所有交易类型的行为正确。不得为了让AutoPAC通过而添加不可见isReAge字段或反馈最终标签。

这是从实际Judge回执得到的待核对点，与原案例报告“生产undo绑定仍待核实”一致。Judge不是独立专家：本轮生成器与Judge共用GLM5.2。原文和实际程序接口才是决定性证据。

证据：calls/11_FSV-B06_autopac_judge/response.raw.json、effect_runs/FSV-B06/AUTOPAC_STYLE/judge.json、generation_inputs/FSV-B06/packet.json。

## S02 的封闭字段解释

原可见OpenAPI请求schema列举properties，未显式写additionalProperties=false。本轮原任务把未知字段当作违规；操作者开发测试沿用这一封闭字段约定。这不是OpenAPI默认语义的自动推论。

若要把比较写成正式安全效果，应明确说明封闭字段约定的权威来源，并让各方法同等获得该约定。当前仅按已归档任务标签报告局部请求对，不据未知字段被拒绝直接宣称标准层面违规被检出。AutoPAC收到操作者开发测试，其额外监督须记录。
