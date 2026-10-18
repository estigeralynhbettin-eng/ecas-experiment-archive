# 三例外部基线适配实测结果

日期：2026-10-14；执行状态：COMPLETED；原始证据对账：PASS。

## 先看结论

**B06也能被两个外部流程的适配版识别，不能把这个例子说成ECAS独有能力。S04中P2P的最终候选只检查邮箱是字符串，没有检查邮箱格式；AutoPAC能提取格式要求，统一资源接口后也能正确拦截。** 三例ECAS同模型候选均通过原合法/违规请求对。

以下是对所有方法统一做OPA格式化、中立身份常量映射及资源对象表示后的事后本地复演。资源对象仅含原已声明的id/system/version；字符串表示的另一套复演结果同时保留。没有重写业务规则、没有再次调用模型，不作为新正式效果试验；原生成流程的失败另列在下表和原始记录中。

|案例|P2P适配版|AutoPAC适配版|ECAS同模型|
|---|---|---|---|
|B06 撤销条件|合法allow、违规deny|合法allow、违规deny；需中立接口字段映射修正|合法allow、违规deny|
|S02 字段白名单|判为显式访问政策范围外|已提取字段约束；最终Rego调用不存在的is_integer，编译失败|合法allow、违规deny|
|S04 邮箱格式|合法allow、错误邮箱也allow；仅检查string类型|合法allow、错误邮箱deny；资源对象映射修正后跑通|合法allow、违规deny|

这里的“违规”是原归档任务的预期标签。每例只有一对请求；不表示整体识别率。P2P适用范围与ECAS不同，AutoPAC更换生成器是重大偏离，不能把这张表写成原版性能排名。

### 对改稿的意见

1. 保留B06作共同能力展示，不用它单独证明ECAS优于P2P/AutoPAC。
2. S04可说明显式访问政策、普通字符串类型检查与结构化格式校验的差别；仍需更广任务和公平输入证明方法收益。
3. AutoPAC的编译/接口错误说明本适配实现的执行可靠性，不能改写成“原AutoPAC看不懂业务规则”。
4. B06必须核实政策只应用于Re-Age撤销，或补可靠交易类型绑定。通用undo接口比文档限制的范围更广，AutoPAC Judge实际指出了这个问题。
5. S02的OpenAPI只列properties，未显式additionalProperties=false；未知字段拒绝是原任务的封闭字段约定。正式比较应补该约定来源并同等提供，不能称OpenAPI默认语义。

### 一个与可信状态有关的观察

删去B06的trusted.reAgeIsLatestTransaction后，事后诊断实际返回：P2P deny、ECAS deny、AutoPAC allow。AutoPAC修复候选把“标志缺失”解释为限制不适用；当前ABI没有提供这个解释。这个观察供核对缺失状态与接口范围，不并入原准确率分母。

证据入口：binding_replay_resource_object/SUMMARY.json（资源对象表示）、binding_replay/SUMMARY.json（资源字符串表示）、targeted_diagnostics/MISSING_TRUSTED_STATE.json、targeted_diagnostics/regex_literal/RESULT.json、SEMANTIC_REVIEW_FINDINGS_CN.md。统一映射只使用原common_adapter已声明的中立身份/目标元数据，request和trusted逐份保持；各政策格式化前后AST一致。AutoPAC S04正则的单独诊断实际匹配合法开发邮箱；初期正则转义怀疑已被证伪，不列为代码错误。

模型批次、格式恢复及两套资源表示均独立保存。不能只摘录修正后成功行而隐去接口故障；也不能将修正前的Harness错配当作基线识别失败。最终105项原始证据对账PASS（FINAL_OUTPUT_AUDIT.json），只证明这些文件和观察一致，不是全文科学验收。

## 原生成流程与纯格式恢复后的记录

|案例|方法|合法请求|违规请求|执行状态|请求对正确|
|---|---|---|---|---|---|
|FSV-B06|P2P适配版|allow|deny|EVALUATED|是|
|FSV-B06|AutoPAC适配版|未执行|未执行|DEVELOPMENT_REJECTED|不适用|
|FSV-B06|ECAS同模型|allow|deny|EVALUATED|是|
|FSV-S02|P2P适配版|未执行|未执行|OUT_OF_SCOPE|不适用|
|FSV-S02|AutoPAC适配版|未执行|未执行|DEVELOPMENT_REJECTED|不适用|
|FSV-S02|ECAS同模型|allow|deny|EVALUATED|是|
|FSV-S04|P2P适配版|未执行|未执行|DEVELOPMENT_REJECTED|不适用|
|FSV-S04|AutoPAC适配版|未执行|未执行|DEVELOPMENT_REJECTED|不适用|
|FSV-S04|ECAS同模型|allow|deny|EVALUATED|是|

合法allow与违规deny同时成立才是本请求对识别正确。全拒绝、范围外、弃权、开发检查拒绝与协议故障单列；未执行不冒充违规deny。

## 过程与预算

- GLM/Z.AI glm-5.2，thinking enabled/high，共27次：开发smoke 4次，方法调用23次，其中修复5次；无自动重试。
- 提供方实际input tokens合计104975，完成tokens合计66728。每次原响应、返回模型、finish_reason及usage见CALL_LEDGER.json与calls/。完成预算包含推理；未收到人民币费用字段，实际金额未知。
- 本机没有精确GLM5.2 tokenizer。调用前采用已披露长度估计，smoke及每次调用以提供方prompt_tokens核验实际16384上限；不把估算数称精确token数。
- 第3次开发smoke输出3条规则，因我精简提示schema遗漏原maxItems=1而失败；原响应与失败状态保留。恢复原结构限制，挪用一次预留调用作新提示smoke（共4次），条件修复总预算降为5次，总调用上限仍30次。没有删除候选规则来制造PASS。
- 第6次P2P抽取的原status=EXTRACTED与解析器READY不一致，发生阶段暂停；只统一已完成抽取的等价状态词，保留原失败与原响应，DSARCP和业务条件未改。精确prompt/raw哈希复用第5/6次响应，本地恢复没有追加API调用。
- Linux OPA/Regal与本范围11项T0检查通过，模型输出小试独立计入调用预算且不进入效果结果。编排、lint、编译、评价在WSL；Windows只承担全局批准wrapper的凭据加载与API调用。
- P2P使用完整Regal规则集，唯目录与包名匹配规则因逐例保存目录关闭；记录完整lint输出。AutoPAC开发测试由操作者按公开来源预先冻结，并非原作者测试。
- 最终归档请求对仅在候选冻结后用于评价，未作为Judge或修复反馈。Boolean状态只有两个真值，开发与最终测试不可避免共享条件值；本轮不能称新盲测。

## 原版与适配的边界

- P2P原代码尚未找到；AutoPAC原微调CodeT5权重尚缺，两个原版均未运行。本文报告按论文流程构建的适配实现。AutoPAC生成器替换是重大偏离，不能据此报告原版AutoPAC性能。
- B06/S02来自原Apache Fineract，S04来自原ERPNext，仍只有两个项目。三例已暴露且事后选取，每例一对归档请求；不是总体准确率，也不能证明ECAS整体优越。
- 业务请求上的共同正确与证据准入机制分开解释；P2P/AutoPAC的Rego执行不具有ECAS原契约准入接口，不把“没有这个接口”计作它们识别失败。
- 参数和提示见FROZEN_PROTOCOL_CN.md、PROMPT_TEMPLATES.json、calls/*/prompt.txt；实际政策与开发/最终轨迹见effect_runs/。原版资格证据见NATIVE_QUALIFICATION.json。

## 未执行或被拒绝的分支

- FSV-B06 / AutoPAC适配版：DEVELOPMENT_REJECTED；详见逐例RESULT.json及开发检查。
- FSV-S02 / P2P适配版：OUT_OF_SCOPE；The visible sources contain only API schema definitions (mandatory fields, request body structure) and adapter metadata. There are no explicit access control or policy statements present.。
- FSV-S02 / AutoPAC适配版：DEVELOPMENT_REJECTED；详见逐例RESULT.json及开发检查。
- FSV-S04 / P2P适配版：DEVELOPMENT_REJECTED；详见逐例RESULT.json及开发检查。
- FSV-S04 / AutoPAC适配版：DEVELOPMENT_REJECTED；详见逐例RESULT.json及开发检查。

## 文件入口

- FINAL_SUMMARY.json、ADAPTED_COMPARISON.csv：逐例结果与实际调用/usage。
- RESULT_RECONCILIATION.json：原响应、政策冻结与OPA实际输出的确定性对账。
- RESULT_TRACEABILITY.csv：本范围结果追溯；不修改根历史账本。
- EXECUTION_INPUT_MANIFEST.json：冻结输入、代码、工具及wrapper的哈希绑定。

本轮未改论文、旧实验或投稿状态；该结果供作者选择案例及设计进一步比较。
