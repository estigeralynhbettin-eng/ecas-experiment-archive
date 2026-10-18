# 四例同行基线适配比较协议 v1

当前对象固定为S03/B13/B17/B19，先冻结输入与判断口径，不要求基线失败。

调用前输入长度修正（模型调用0）：通用Frappe REST说明统一保留介绍与完整Create小节，移除不属于本次POST操作的列表/读/改/删/上传部分。字段catalog按固定列转换为元组，仅统一移除Section Break、Column Break、Tab Break、Button、HTML、Fold布局控件，保留其余全部数据字段。业务条款全文保持。原稿、两次变换及移除清单单独保存。Model IR提示采用完整定义的分解表示，保留15种原语及其参数约束、根必需字段和单规则限制；完整原JSON Schema负责验证。

## 方法

P2P：检测政策→DSARCP抽取→组织schema落地→Rego生成→完整Regal/OPA检查→模型开发测试及共同开发测试→至多一次开发修复。

AutoPAC：Rego生成→Judge按源核读→OPA检查及共同开发测试→至多一次修复。其原CodeT5微调生成器不能复现，使用共同GLM模型替换，属于重大适配差异。

ECAS：完整Model IR schema生成→确定性编译→契约准入→共同开发测试→冻结后评价。保持本ECAS流程，无人工补规则。

三个方法输入相同的公开来源和中立ABI；ECAS另有其输出schema，P2P另有组织schema。移除ECAS专属primitive focus。结构性字段catalog可用固定字段白名单机械压缩（保留每个字段的名字、类型、选项、默认值、required、只读与链接约束）；保留完整条款文本，不按已知成功规则删选。原输入、派生输入和变换均有哈希。

共同OPA envelope完整说明：request/trusted逐字保留；subject={id,role}，两者为authenticated_api_caller；action为目标操作字符串；resource={id,system,version}，id为system:version。所有方法在生成前获知这一表示。组织schema中的字符串资源标识对应resource.id，不混用对象与字符串。中立身份常量不是新权限限制。

共同开发请求由公开条款预先冻结，对三方法同等评估；P2P还保留其自动开发测试。只向开发修复反馈源码、lint/编译、共同开发请求或方法自身Judge/测试，最终归档请求标签不反馈。布尔状态开发/最终条件有限，本轮不称盲测。

先报告首次生成约束、编译/准入及首次请求轨迹，再单列修复后结果。修复次数/监督不同是流程差异，不能归因为证据契约带来的因果收益。S03若P2P声明范围外，记范围外而非错判。

## 调用与门禁

GLM5.2 thinking enabled/high，input≤16384、completion≤16384（含推理）；最多40次，基础28+条件修复≤8+开发smoke≤4。不得自动付费重试；同prompt完整raw可以本地解析/复用。费用UNKNOWN。

串行执行；独立OPA/Regal进程无网络builtin、无时钟/随机/进程元数据builtin；超时25秒。Regal只关闭目录与包名匹配规则，保留其余规则。Windows仅执行批准GLM wrapper和安全凭据加载，政策编译、评价与编排在WSL。

T0、输入/脚本/工具/wrapper哈希和本轮scope门禁通过后才能小试；三流程完整输出token小试通过后才能方法批次。没有精确GLM本地tokenizer，调用前保守估计，调用后以提供方usage核验，不把估算称精确计数。

最终评价在候选冻结后执行原合法/违规对及预先冻结分支探针；原请求与工程扩展分列。原基线未执行与适配结果分列。没有请求输出的分支记—，不能由默认拒绝冒充识别。
