# 冻结协议：缺值行为的机制识别

## 配置臂

每任务四个ECAS配置：原IR/full、原IR/shape-only、只将原IR的on_missing从deny改为skip/full、同一skip IR/shape-only。引擎与其他业务字段不改。full拒绝准入时不执行，decision为None。

每个同行适配版两个配置：原冻结Rego，原Rego+独立guard模块。后者查询data.ecas_mechanism_guard.allow，定义为原data.external_pilot.allow与guard均成立；不改原模块或声称这是原基线生成结果。

guard为人工确定性工程控制：B17要求customerDisabled是布尔值；B19要求supplierOnHold为false，或为true且holdType属于All/Invoices/Payments。onHold为false时不强制要求无关holdType，因此不拒绝原合法未冻结状态。guard来源和人工投入明确登记，不用于模型生成性能排名。

## 请求与读数

B17原合法/违规请求2条及历史分支4条；B19原请求2条、历史分支8条及新增部分缺值观察2条，共18输入，八配置臂合计144行。重复/相关输入不当独立样本。

新增两条：trusted仅supplierOnHold=false；trusted仅holdType=Payments。二者记录实际输出，不预设业务正确标签，不将部分信息下允许自动称为漏洞。原历史工程deny标签也是保守处理约定，不能当作公开业务规范已要求的gold。

读取阶段：Model IR编译、Inventory准入、运行缺值处理、正向允许条件、Rego negation和外围guard分别标注。与先前来源/版本/路径扰动消融分开解释：请求trusted缺值并不等同Inventory绑定记录缺失。

## 解释限制

本地反事实是手工干预既有候选，不是重新生成，不增加新案例/独立项目，不证明总体生成质量或泛化。安全guard能否闭合缺口用于检验该现象是否独有；不能把人工加固后的结果回填原基线。仍未验证真实上游状态认证、新鲜度或API转发。
