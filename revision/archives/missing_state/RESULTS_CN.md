# 缺可信状态行为的本地机制对照

## 结论

本地对照已完成，无新增模型调用。当前缺状态/未知类型差异有实际意义，但本轮不能把它认定为证据准入带来的独有保证。

1. ECAS只改变on_missing=skip，仍通过原Inventory准入，B17/B19的全缺trusted输入均从deny变为allow。
2. 同一候选full与shape-only的运行观察逐项相同；因此本组请求上的差异来自候选参数和规则逻辑，而非准入开关。
3. 给两同行的原Rego叠加人工编写的最小typed状态guard后，原先四类allow观察均可变为deny，并保留两例各自原合法/违规请求对。不能把这种手工控制回填成同行原生成结果。

## 核心对照

| 配置 | B17 trusted={} | B19 trusted={} | B19冻结且类型为空/未知 | 两例原请求对 |
|---|---|---|---|---|
| ECAS原候选/full | deny | deny | deny | 各2/2匹配 |
| ECAS原候选/shape-only | deny | deny | deny | 各2/2匹配 |
| ECAS只改on_missing=skip/full | allow | allow | deny | 各2/2匹配 |
| ECAS只改on_missing=skip/shape-only | allow | allow | deny | 各2/2匹配 |
| P2P适配版原候选 | allow | allow | allow | 各2/2匹配 |
| P2P原候选+人工guard | deny | deny | deny | 各2/2匹配 |
| AutoPAC适配版原候选 | allow | allow | allow | 各2/2匹配 |
| AutoPAC原候选+人工guard | deny | deny | deny | 各2/2匹配 |

B19的空/未知类型拒绝来自正向允许条件：supplierOnHold=false或holdType=Payments。只改缺值参数不改变这两种有值但未命中条件的结果。

## 部分缺值不能混称全缺

| B19输入trusted | ECAS原/full及shape | 两同行原政策 | 两同行+人工guard |
|---|---|---|---|
| 只有supplierOnHold=false | allow | allow | allow |
| 只有holdType=Payments | allow | allow | deny |

这两项只有观察值，没有预设业务正确标签。一个允许分支已经能成立时，另一字段缺失未必构成业务违规；也不能把人工guard更保守的结果自动算作更正确。此前“缺少可信供应商状态时拒绝”须精确限定为原trusted={}探针，不能泛化为任意部分信息缺失都拒绝。

## 两种缺失发生在不同阶段

- Inventory证据记录、版本或绑定事实失效：规则准入阶段判断是否可部署，已有配对消融证明被测硬检查会拒绝候选。
- 请求trusted运行值缺失：执行阶段由候选运算语义和on_missing参数决定；当前准入没有对本组规则强制on_missing=deny。

源语义Judge是第三种检查：核读目标和允许/禁止方向，不负责证明来源或运行状态真实。先前Judge指出三个主语义问题的结果继续有效，但不能据此自动补全上述硬运行保证。

## 对继续研究的影响

应该继续研究证据约束下的安全执行。下一步需要把所需可信输入、条件依赖、类型和失效处理明确成为可核验契约，检验能否在模型漏写安全默认值时仍保证一致执行；并把已加入安全guard的同行作为强对照。当前的缺值拒绝现象本身不能单独充当独特性证据。

本轮18个相关输入、八配置臂、144行是机制干预观察，不是144个独立案例。四类allow→deny控制涉及两个旧任务和两个同行配置；原合法覆盖只对已测试请求负责。没有新增生成任务、独立系统、真实攻击或生产状态认证验证。

## 复现与证据

运行missing-state-mechanism-v1实际SUCCEEDED；INPUT_MANIFEST/SOURCE_MANIFEST绑定不变引擎、OPA、原候选和快照。RESULTS.json、OBSERVATIONS.csv保留全部行，FINAL_RECONCILIATION.json保留逐项对账。人工guard独立放在guards/，两同行原Rego未修改。旧原件、论文和根科学账本不改。
