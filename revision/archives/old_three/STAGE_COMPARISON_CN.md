# 三例功能完成程度与差异出现阶段

日期：2026-10-14。材料：27次GLM5.2调用的既有原响应、初始生成、开发测试、修复及已归档请求执行轨迹；本次只读核对，不新增模型或实验。

## 1. 圆圈总览

圆圈表示目标约束的落实程度：**○ 未形成目标约束；◐ 部分形成或执行链未完成；● 已形成且通过原合法/违规请求对。** ◐不是50%准确率，●不是整个项目或所有请求都正确。

|案例与目标|P2P适配版|AutoPAC适配版|ECAS同模型|
|---|:---:|:---:|:---:|
|B06：最新Re-Age交易才允许撤销|●|●|●|
|S02：拒绝未声明请求字段|○¹|◐²|●|
|S04：拒绝格式错误的邮箱|◐³|●⁴|●|

1. P2P在政策检测阶段判定S02范围外，未执行请求；这里○表示目标未覆盖，不是判断错误。
2. AutoPAC修复后形成字段白名单，但调用不存在的is_integer，编译未通过；不是一半请求判对。
3. P2P只形成字符串类型检查，实际合法邮箱allow、错误格式邮箱也allow。
4. AutoPAC首次生成无邮箱格式检查；Judge接受了该候选。操作者开发测试反馈后才补出正则，资源接口统一后通过最终请求对。这与首次生成即形成格式规则是不同过程。

最终执行采用已说明的事后统一接口复演；原接口错配、格式问题及失败完整保留。P2P/AutoPAC为文献流程适配版，不能把此表作为原版性能排名。三个案例已经暴露且事后选取。

若论文表格只表示“最终请求判定”，建议另用：● 两条请求均对；◐ 一条对；○ 两条均错；— 未执行。此时S02的P2P和AutoPAC均须填—，不能填○或◐。不得把两种图例混用。

## 2. 首次形成目标规则的阶段

|案例|P2P适配版|AutoPAC适配版|ECAS同模型|
|---|---|---|---|
|B06|政策检测找出“仅最新Re-Age交易可撤销”；DSARCP抽取形成latest=true条件|首次Rego生成已经包含latest=true；Judge提出仅Re-Age适用的范围问题，修复改变缺失标志处理|首次候选生成形成bounded_guard_dnf，约束可信标志等于true；随后编译和证据准入通过|
|S02|政策检测判定只有API结构，没有显式访问政策，停止|首次生成只检查必需字段存在；Judge接受。开发测试反馈后的修复才增加allowed_keys白名单，但编译失败|首次候选生成形成allowed_fields，列出四个允许字段；随后编译和证据准入通过|
|S04|检测/抽取只覆盖身份和创建权限；首次Rego无格式检查，修复后仅加入is_string|首次Rego无格式检查，Judge接受；开发测试反馈后的修复阶段首次出现邮箱正则|首次候选生成选择named_validator/email_basic_v1；随后编译和证据准入通过|

“首次形成规则”和“首次判定具体请求”是两个时点。模型输出规则；具体请求的allow/deny由后续确定性执行器产生。

## 3. ECAS在哪一步判定请求

|案例|模型候选中的规则|证据准入检查的对象|具体请求判定发生在哪里|
|---|---|---|---|
|B06|可信状态等于true；on_missing=deny|原文引用、目标/版本与可信路径、允许原语的绑定|运行时bounded_guard_dnf求值：可信标志true允许，false拒绝|
|S02|allowed_fields字段白名单|可见API字段及支持原语的来源绑定|运行时比较请求键集合与白名单：出现未声明字段则拒绝|
|S04|email_id使用email_basic_v1；字段缺失时skip|Email字段类型、运行路径及注册校验器的来源绑定|运行时named_validator校验实际邮箱值：格式不通过则拒绝|

原执行日志对应：B06拒绝原因bounded_guard_rejected；S02为unexpected_fields，具体额外字段undeclared_script；S04为validator_rejected，具体校验器email_basic_v1。S02拒绝的是未声明字段，不是检测出了字段值中的脚本内容。

证据准入的作用是判断这条候选是否具备可执行资格。它不是直接发现请求中错误字段或错误邮箱的阶段；这些由运行时规则执行发现。此三例没有识别出证据契约相对于同候选无契约执行的因果增量。

## 4. 对论文表述的建议

- 可以写：本轮轨迹显示，ECAS在首次候选生成中形成三类目标约束；P2P主要提取显式访问政策；AutoPAC的S02白名单、S04邮箱格式在操作者测试反馈后的修复中出现。
- 应同时写清：AutoPAC获得操作者开发测试，P2P使用自动生成测试，ECAS使用原语/输出schema。这是监督与方法配置差异，不能将结果完全归因于证据契约。
- 不能写：本轮已证明ECAS整体优于两个原作，或证据准入直接发现三个请求的违规内容。需要匹配适用范围和监督条件的更广比较或消融才能证明这种主张。
- B06的通用undo接口与Re-Age规则适用范围、S02的封闭字段约定来源继续待核对，不因圆圈展示而省略。

## 5. 逐项来源

每行可回到以下文件核对（相对于本目录）：

- effect_runs/FSV-B06/P2P_STYLE/detection.json、extraction.json、generation.json；AUTOPAC_STYLE/generation.json、judge.json、repair.json；ECAS_MATCHED/candidate.json、RESULT.json。
- effect_runs/FSV-S02/P2P_STYLE/detection.json；AUTOPAC_STYLE/generation.json、judge.json、repair.json、repaired/CHECKS.json；ECAS_MATCHED/candidate.json、RESULT.json。
- effect_runs/FSV-S04/P2P_STYLE/detection.json、extraction.json、generation.json、repair.json；AUTOPAC_STYLE/generation.json、judge.json、repair.json；ECAS_MATCHED/candidate.json、RESULT.json。
- binding_replay_resource_object/SUMMARY.json：统一接口后的实际合法/违规决策；FINAL_OUTPUT_AUDIT.json：前序105项原始证据对账。

本表是作者核读用的局部轨迹归纳，未写入论文正文，也不是新增实验结果。
