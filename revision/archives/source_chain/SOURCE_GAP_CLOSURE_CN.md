# B06与S02来源缺口：固定实现源码核查

日期：2026-10-15。新增模型、网络、政策/后端执行均0。

**结论：查到了固定版本源码与具体反证，但两例仍不能被改标为“原业务语义与真实HTTP行为完全闭合”。B06存在专用undoReAge与旧通用target的差别；S02存在内部四字段检查，但HTTP先经过忽略未知属性的typed DTO。**

## 版本身份

- 本地固定树：`/root/ec/fineract-1.14.0-e1b`。
- HEAD=`7923d9e6cb67611c506b6c527b64497996acdc58`；exact tag=`1.14.0`；git porcelain为空。
- 与冻结SOURCE_MANIFEST的commit相同；re-ageing.adoc与ClientIdentifiersApiResource的实际SHA256均精确匹配原manifest。
- 下列源码为本轮新核读，历史模型并未看到这些实现条款。

## FSV-B06

状态：`SOURCE_OPERATION_SCOPE_NOT_CLOSED_SPECIFIC_COUNTEREVIDENCE_FOUND`。

已确认：

- 同一1.14.0固定源码文档明确写Re-Age交易只能在为贷款账户最新交易时撤销。
- 该固定版本有独立POST /v1/loans/{loanId}/transactions?command=undoReAge，经独立handler进入undoReAge；不携带transactionId。
- 旧候选target POST /v1/loans/{loanId}/transactions/{transactionId}?command=undo进入Adjust a Transaction分支；该分支没有把undo映射为undoReAge。
- 专用undoReAge服务选择最新未撤销的Re-Age（不是直接比较账户所有类型交易的最新性）；其直接validator仅检查存在Re-Age。
- 通用调整另有CUMULATIVE schedule的LastTransactionDate检查，故不能概括为全项目没有最新交易检查。

**对实验使用的影响：** 保留历史文档目标抽取/可信布尔求值演示；暂不进入来源、真实API操作与状态获取完全闭合的主验证集。后续应另建固定专用操作任务，或证明通用adjust路径在明确交易类型与loan schedule范围内如何对应文档。不能追溯修改旧目标或把新源码当作旧模型已见材料。

仍未知：

- 旧target的业务语义与Re-Age条款的完整等价关系未建立。
- 专用undoReAge和通用adjust在所有schedule、事件订阅及重处理路径下是否实施文档latest限制，本轮未运行后端或穷举调用链。
- trusted/reAgeIsLatestTransaction在真实系统的认证、新鲜度与计算路径未核验。

主要原件：

- `/root/ec/fineract-1.14.0-e1b/fineract-doc/src/docs/en/chapters/features/re-ageing.adoc`，行85-92；SHA256 `95d99f4bee0b70b23487cbee14cc1c767ab4667240f297b6ece0de3545be5f16`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/api/LoanTransactionsApiResource.java`，行85-98,283-308,347-361,602-605,722-745；SHA256 `eb9a2312de08dec55a83b67e6c72ec754504d4d54f8b6b24027648ff8c0cddd2`。
- `/root/ec/fineract-1.14.0-e1b/fineract-core/src/main/java/org/apache/fineract/commands/service/CommandWrapperBuilder.java`，行3741-3748；SHA256 `ac2896769acc793b82f4abb5e4c8e57d1b3f10f0ef03980b047dbafbe9cc05fe`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/handler/loan/reaging/LoanUndoReAgingCommandHandler.java`，行30-48；SHA256 `b043ad0e7d2f956eb45eb271f717bc2c605381ed8bff81639c71b25675ec1e30`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/service/reaging/LoanReAgingService.java`，行161-180,215-228；SHA256 `33cc3575059b497dbc533e90c105aa1ce3420ac4885b2775b1661359066aff32`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/service/reaging/LoanReAgingValidator.java`，行196-208；SHA256 `1d635840c1164bef372007ba1d5c8b87f475301fa335de26f60febc0f58f9731`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/service/LoanWritePlatformServiceJpaRepositoryImpl.java`，行1180-1184,1215-1245；SHA256 `d10f4fc11ebb520a7def8d4424b4b4304938743ad13c9ef7f259f6e7d2746e7c`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/service/adjustment/LoanAdjustmentServiceImpl.java`，行206-220；SHA256 `d65ef8f42acb80e77f13481ddb9379b7f4c8bbaa1661fc8b89ad2bc35df70cb9`。
- `/root/ec/fineract-1.14.0-e1b/integration-tests/src/test/java/org/apache/fineract/integrationtests/common/loans/LoanTransactionHelper.java`，行1095-1098；SHA256 `face3c887a1e6e4d97c6b5a2940ab93fb4a8d67508b2e614498abc70cbf34ad5`。

## FSV-S02

状态：`INTERNAL_FOUR_KEY_CONTRACT_FOUND_HTTP_UNKNOWN_KEY_REJECTION_NOT_SUPPORTED`。

已确认：

- OpenAPI公开四字段但没有additionalProperties=false；旧模型可见材料未包含本轮查到的实现链。
- 内部ClientIdentifierCommand反序列化确有四字段SUPPORTED_PARAMETERS并调用checkForUnsupportedParameters；helper遇额外参数抛异常。
- HTTP入口却先接收ClientIdentifierRequest typed DTO，再序列化DTO进入命令链。该DTO只有四字段，没有额外属性map或JsonAnySetter。
- Jersey body reader对非String委托Jackson converter；固定源码ObjectMapper关闭FAIL_ON_UNKNOWN_PROPERTIES。因此现有静态HTTP链指向未知键被忽略/丢弃，而非被四字段内部checker拒绝。

**对实验使用的影响：** 可以把四字段作为受支持命令字段集的源码依据；不能把“原HTTP API必须拒绝未知键”声称已由源码证明。网关主动拒绝未知键可作为显式部署加固策略，但应另行制定、等量提供并标注为操作者策略；不得追溯改写旧例为原文唯一正确语义。

仍未知：

- 未运行HTTP，故不声称已观察后端允许未知键，也不声称真实配置无额外拦截层。
- 没有找到该固定HTTP接口要求拒绝原始未知键的明确规定；没有在已检查测试范围内找到对应的unknown-key拒绝测试。

主要原件：

- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/client/api/ClientIdentifiersApiResource.java`，行113-127；SHA256 `11212c7b4a65db3e57a5b9a08fa717e37cdf3b5c0c092f65633ba94b951a8a66`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/client/data/ClientIdentifierRequest.java`，行29-47；SHA256 `0df233e71e6e7a87ad07091922321e594bee54807a5020d77eef13ddfbf96df7`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/infrastructure/core/jersey/JerseyJacksonObjectArgumentHandler.java`，行45-73；SHA256 `5971f333e20b4465e58877adb16194d7cac81b2c98bba72a5392749bee350f75`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/infrastructure/core/jersey/JerseyJacksonConverterConfig.java`，行37-56；SHA256 `b10a993e6ab778544947b1124e658b16c2714eb6b8900090ce803627441f56d1`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/client/service/ClientIdentifierWritePlatformServiceJpaRepositoryImpl.java`，行71-78；SHA256 `57ece708d1a13559610eeeec25a5c261a67ee8477285d6f79d3c6a488e30cace`。
- `/root/ec/fineract-1.14.0-e1b/fineract-provider/src/main/java/org/apache/fineract/portfolio/client/serialization/ClientIdentifierCommandFromApiJsonDeserializer.java`，行43-52,60-77；SHA256 `72ad833393e08abb26a133db4ff2e0f032bb038b6a4522ca654a9a6dfe5ec06f`。
- `/root/ec/fineract-1.14.0-e1b/fineract-core/src/main/java/org/apache/fineract/infrastructure/core/serialization/FromJsonHelper.java`，行86-102；SHA256 `95ff0045cc207f64178bd77d64ac3a2de6849518815b93b5abc97630c0127ca9`。

## 有界搜索及停止边界

- 已冻结source manifest与旧B06/S02 packet
- /root/ec/fineract-1.14.0-e1b：指定Java入口、反序列化、service、builder、validator、Jersey converter及既有integration-tests和provider/src/test/java关键词搜索
- D:/lunwen/ec/runtime仅做目录名定位（未发现Fineract目录）；未扩展到网络或其他版本
- 无命中只对列出的本地范围有效；不解释为全世界无规范或无实现。WSL无rg，后续使用Windows rg读取WSL UNC与指定文件行段。
- 未执行HTTP或政策，不生成新的allow/deny观察；不据静态路径推断生产漏洞或生产成功。
- 逐行摘录、文件哈希和旧target见同名JSON；原协议和标签全部保留。
