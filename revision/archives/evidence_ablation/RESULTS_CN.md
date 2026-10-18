# 同候选证据准入消融：本地离线结果

**结论：证据契约能够阻止未绑定、版本错配及不充分证据的规则进入执行；它没有自动证明规则方向或目标覆盖正确，也未核验清单中的来源文件真实性。**

## 范围与公平控制

- 7个旧案例、11个父候选：前三例各1个，后四例v1/v2各保留1个；未逐例择优。全部来自已暴露的历史输出。
- 同一份候选先用原`compile_model_ir`编译；完整组用`compile_policy`及semantic执行，无契约组用引擎已有`compile_policy_shape_only`及shape_only执行。两组共用原语、schema和执行器。
- 无契约组不调用完整Inventory准入。完整组准入拒绝时不执行；无契约风险执行仅使用离线合成请求。
- 这是准入阶段的机制消融。两组候选生成时都看过证据，本轮没有检验“模型生成时不提供证据”，没有新模型调用，也没有AutoPAC Judge的新增对照。
- 配对扰动是人工构造的元数据/路径挑战；一个父候选的多个变体不是多个独立案例。未执行、schema失败、弃权均不算业务请求正确或错误。

## 完整准入与无契约编译

| 输入类别 | 父候选数 | 完整准入通过 | 完整准入拒绝 | schema/类型失败 | 无契约编译通过 |
|---|---:|---:|---:|---:|---:|
| 证据标记为不充分 | 11 | 0 | 11 | 0 | 11 |
| 引用的证据记录缺失 | 11 | 0 | 11 | 0 | 11 |
| 证据版本错配 | 11 | 0 | 11 | 0 | 11 |
| 历史原候选 | 11 | 11 | 0 | 0 | 11 |
| 必需绑定事实缺失 | 11 | 0 | 11 | 0 | 11 |
| schema控制：未知操作 | 11 | 0 | 0 | 11 | 0 |
| schema控制：hidden visibility | 11 | 0 | 0 | 11 | 11 |
| 来源locator/hash不可解析 | 11 | 11 | 0 | 0 | 11 |
| 可信路径换成未绑定客户端路径 | 7 | 0 | 7 | 0 | 7 |

完整准入拒绝表示规则不部署；合法业务覆盖同时降为未部署，不可把未执行算成合法允许或违规拒绝。由于元数据扰动不改变原规则，两组在原始清单上通过的合法覆盖相同；坏元数据下完整组宁可拒绝部署，无契约组仍执行。

## 原候选业务结果与语义漏检

| 案例 | 配置 | 完整准入 | 原合法请求 | 原违规请求 | 两条归档标签均命中 |
|---|---|---|---|---|---|
| FSV-B06 | three_case_v1 | ADMITTED | allow | deny | 是 |
| FSV-S02 | three_case_v1 | ADMITTED | allow | deny | 是 |
| FSV-S04 | three_case_v1 | ADMITTED | allow | deny | 是 |
| FSV-S03 | four_case_v1 | ADMITTED | allow | deny | 是 |
| FSV-S03 | four_case_v2 | ADMITTED | allow | allow | 否 |
| FSV-B13 | four_case_v1 | ADMITTED | allow | deny | 是 |
| FSV-B13 | four_case_v2 | ADMITTED | allow | deny | 是 |
| FSV-B17 | four_case_v1 | ADMITTED | deny | deny | 否 |
| FSV-B17 | four_case_v2 | ADMITTED | allow | deny | 是 |
| FSV-B19 | four_case_v1 | ADMITTED | deny | allow | 否 |
| FSV-B19 | four_case_v2 | ADMITTED | allow | deny | 是 |

表中“标签命中”只对归档请求对负责。B06的通用undo target与Re-Age条款范围、S02封闭字段约定的原出处仍未完全闭合，不能将归档标签作为独立语义gold。

B17 v1错误原语、B19 v1禁止条件反写为允许条件、S03 v2只生成字段白名单等历史错误仍保留在表中。完整准入没有自动把这些语义错误拒绝掉。不得用准入通过替代业务语义正确。

## 可信路径挑战的解释

将规则引用的`/trusted/...`改为未登记的`/request/body/ecasClientClaim/...`，完整组检查规则路径未绑定而拒绝，无契约组仍编译。另用历史合法状态值写入客户端字段，在真实trusted保持违规状态下离线重放。
该挑战检验注册路径绑定，不证明trusted字段在真实网关中真实性、来源认证、新鲜度或防伪；若操作者在清单中主动声明客户端路径可信，当前准入本身不验证声明真伪。

## 来源真实性挑战

所有证据记录的locator改为不存在的合成路径、sha256改为格式合法的全零值，其他绑定保持不变。引擎检查schema与清单声明，没有解析文件或比对源文件hash，11个父候选全部通过。原稿相对Inventory的保证假定清单已经结构化且可信；直接篡改清单来源真实性位于这一假设之外，因此这项结果不直接推翻该限定保证，也不能称为真实攻击或漏洞。它说明当前执行入口不负责源文件解析与清单真实性核验。

## 可下与不可下的结论

- 可下：在这7例的11个历史候选及配对构造挑战上，Inventory准入对已实现的证据绑定条件提供可观察的部署阻断。
- 不可下：ECAS整体优于AutoPAC；证据驱动提高生成语义正确率；证明普适性；极大降低人工劳动；证明源文档真实性或trusted值真实性。
- 后续同预算同行实验需要另比较生成时有/无证据、首次生成与等预算修复。用户已取消人工计时；本轮只登记生成方式与可观察工程工作量，不将代理量写成真实人时节省。

## 核验与复现

- 独立WSL lane，原引擎字节不改，T0工程正负夹具PASS，无Docker/GPU/服务/API。
- `SOURCE_MANIFEST.json`逐份绑定原件与只读快照；`FINAL_RECONCILIATION.json`核对原件未变、快照未变和11条原请求对重演。
- `COMPARISON_SUMMARY.json`保留逐行准入理由、离线执行观察及变体构造类别；`COMPARISON.csv`为索引。
- 运行入口：`T0_REQUEST.json`与`RUN_REQUEST.json`，用通用WSL managed runner validate/start。

## 扰动对象与执行资格

- 原候选未改变任何输入；可信路径替换和未知操作控制改变policy IR。其余证据缺失、版本、关系、绑定事实、locator/hash和visibility变体改变Inventory contract。
- 完整组被拒时是`INELIGIBLE_NOT_EXECUTED`，请求决策为`None`；没有造出deny，也不把这种拒绝算成业务全对。
- 仅contract变化的变体保留同一份compiled policy；独立QA核对无契约组执行观察与原候选逐项相同。
- schema控制不进入准入机制分母。元数据/路径构造挑战反映机制边界，不代表真实攻击发生率，也不用于声称优于AutoPAC。

## 客户端声明挑战观察

| 父候选 | 完整组 | 无契约组在合成伪造声明下 |
|---|---|---|
| FSV-B06__three_case_v1 | 无执行资格 | allow |
| FSV-B13__four_case_v1 | 无执行资格 | deny |
| FSV-B13__four_case_v2 | 无执行资格 | deny |
| FSV-B17__four_case_v1 | 无执行资格 | deny |
| FSV-B17__four_case_v2 | 无执行资格 | allow |
| FSV-B19__four_case_v1 | 无执行资格 | deny |
| FSV-B19__four_case_v2 | 无执行资格 | allow |

执行器对已有错误规则仍可能拒绝合法输入；合成声明被无契约组允许只说明该路径绑定挑战的风险，不表示所有规则或真实网关均有此漏洞。

## Windows交付与局部记录

- `COMPARISON_AUDITED.json/csv`增加扰动对象、执行资格、未执行的None和Windows证据路径。原始`COMPARISON_SUMMARY.json`保留。
- 本文档的后续建议按用户最新范围修订，取消人工计时；实际运行脚本与managed runner输入hash保持不变。
- `evidence_files/`交付只读输入、实际编译/请求/结果和两次managed run回执；`DELIVERY_MANIFEST.json`逐文件hash对账。
- `DELIVERY_QA.json`是局部交付核验；`RESULT_TRACEABILITY.csv`仅本实验局部账本，不写根科学ledger。
