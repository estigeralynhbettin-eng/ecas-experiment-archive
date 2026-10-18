# 旧三案例：语义条件形成阶段核读

日期：2026-10-15。只读核对旧响应与政策，不调用模型、不重新执行政策。

**结论：旧表主要展示最终执行，确实遮住了“何时形成目标含义”。这可以补成单独维度，但本核读不是语义准确率或独立gold审查。**

|案例|所属项目|方法|首次实际政策内容|后续阶段|
|---|---|---|---|---|
|FSV-B06|Apache Fineract|P2P_STYLE|首次Rego已有latest == true；DSARCP已抽取该条件。|修复仅改缩进；不改变主约束。|
|FSV-B06|Apache Fineract|AUTOPAC_STYLE|首次Rego已有latest == true。|Judge指出仅适用于Re-Age；修复改为false时禁止，缺标志允许，未真正增加交易类型区分。|
|FSV-B06|Apache Fineract|ECAS_MATCHED|首次IR已有可信latest标志等于true；缺值deny。|已归档编译/准入与请求结果另列；此观察不等于通用undo完整语义正确。|
|FSV-S02|Apache Fineract|P2P_STYLE|入口OUT_OF_SCOPE；没有首次政策，不评语义错误。|提示限定显式访问政策，不强制把结构校验作为访问控制。|
|FSV-S02|Apache Fineract|AUTOPAC_STYLE|首次Rego只有documentKey/documentTypeId存在性；无白名单。|Judge ACCEPT；操作者未知键deny测试反馈后修复有allowed_keys和逐键成员检查，但is_integer导致编译失败。|
|FSV-S02|Apache Fineract|ECAS_MATCHED|首次IR已有allowed_fields及四字段清单。|来源仅列properties，没有additionalProperties=false；“闭集拒绝”只能归于既有任务约定，不能直接算原文唯一正确含义。|
|FSV-S04|ERPNext|P2P_STYLE|首次Rego只有身份/操作/资源，无邮箱格式条件。|DSARCP只提角色权限；开发修复加入is_string，没有邮箱格式校验。|
|FSV-S04|ERPNext|AUTOPAC_STYLE|首次Rego只有身份/操作/资源，无邮箱格式条件。|Judge ACCEPT且issues为空；操作者正负邮箱测试反馈后出现regex。原接口错误与事后统一接口复演须另列。|
|FSV-S04|ERPNext|ECAS_MATCHED|首次IR已有named_validator/email_basic_v1绑定email_id。|源字段options=Email；validator注册语义属于提供给模型的工具支持；不等于模型独立发明完整邮箱标准。|

## 解释边界

- P2P与AutoPAC同样做自然语言到政策；语义理解不是ECAS独有。
- 只核目标条件何时出现在实际政策，不用reason自述替代政策内容。
- B06三方目标条件已出现，但Re-Age与通用undo适用范围未闭合。
- S02封闭白名单约定未见于可见OpenAPI；不得直接当作理解正确性gold。
- 已有操作者反馈、原语目录、适用范围与编译错误均分列；不聚合语义准确率。
- S04中AutoPAC修复出现邮箱正则，能够证明目标条件已被尝试表达；不能据此直接判整个正则与源规范等价。
- 来源字段options=Email到注册validator的映射，以及四字段清单到闭集的映射，有不同来源强度，不能画同一种“语义全对”圆圈。
- P2P使用自动开发测试；AutoPAC接收操作者开发测试；ECAS有已定义原语及schema。该监督差异应随表保留。

## 逐项来源（SHA256与字段路径见同名JSON）

### FSV-B06 / P2P_STYLE

- [extraction.json/components/0/condition](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/P2P_STYLE/extraction.json)；SHA256 `8a9358ac601dd933f29173680be40e2a825a3c1f608585572a9e926212c4f08c`
- [generation.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/P2P_STYLE/generation.json)；SHA256 `a6fdb67e256fbbaa1f4f6bc2813f15894b879de6ad539e56cc5f0985a10675cf`
- [repair.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/P2P_STYLE/repair.json)；SHA256 `71eb9c9dff1958d8b95f6f4b8ce8b9c09e486c82315ecb000cad9c218617fd97`

### FSV-B06 / AUTOPAC_STYLE

- [generation.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/AUTOPAC_STYLE/generation.json)；SHA256 `7839f317484c6e97a3bf4b81bf1ae8545378cee143075ef1087bb06d12a9585f`
- [judge.json/issues/0](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/AUTOPAC_STYLE/judge.json)；SHA256 `04f209999292dd80e6379b4046fda98b58a6e1da190e56ce866de1ac2747159b`
- [repair.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/AUTOPAC_STYLE/repair.json)；SHA256 `f6fe3771a552f22547be4de54648f2aa05eb655adff78193caea3a951221ed52`

### FSV-B06 / ECAS_MATCHED

- [candidate.json/rules/0/params](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/ECAS_MATCHED/candidate.json)；SHA256 `ca4a80a844a1a50519a3c958b18d3530b5799e97c3147bf19aba2573dd7a95ff`
- [RESULT.json](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-B06/ECAS_MATCHED/RESULT.json)；SHA256 `7ce11d95dd90462618b63c697e2978132ad4250cd5d7831399272c6c6607cdb3`

### FSV-S02 / P2P_STYLE

- [detection.json](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S02/P2P_STYLE/detection.json)；SHA256 `d17c721cf1770dd1a29cc9bd28fc497c0135ef69f57e1dd99f5481295ea19b8e`
- [prompt.txt](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/calls/14_FSV-S02_p2p_detect/prompt.txt)；SHA256 `b27eea78185e7b7ff962a2f32455a864aa494a9bfd55fecf3f25f0af2e9f922b`

### FSV-S02 / AUTOPAC_STYLE

- [generation.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S02/AUTOPAC_STYLE/generation.json)；SHA256 `9bfa733511ea5a68a928770d207263748cf3da678c1bbaccf6b506ea8398b47e`
- [judge.json](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S02/AUTOPAC_STYLE/judge.json)；SHA256 `eddab795ac57a0be086f476d9d99cc9f07088806c604cbb29cdece4a23f54d5a`
- [prompt.txt](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/calls/17_FSV-S02_repair/prompt.txt)；SHA256 `8177f56e8f44089f5b4ef7866eadbd47059331ef1ac7dddbc59f9bb44ff1fcd0`
- [repair.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S02/AUTOPAC_STYLE/repair.json)；SHA256 `00fa3e18e6b0b72e8a553e5831bee753294f3cd793602a069574f5e057ed6753`
- [compile.stderr.txt](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S02/AUTOPAC_STYLE/repaired/compile.stderr.txt)；SHA256 `326b670fd453317fffa3a55e9b23aeb9d22af7e4c3d1d242fe392e8ac052a68f`

### FSV-S02 / ECAS_MATCHED

- [candidate.json/rules/0](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S02/ECAS_MATCHED/candidate.json)；SHA256 `e6f5a2af7dee84e067b1a81f4b3dd56483b2ba306983039d0112c28efbf49fe6`
- [packet.json/visible_sources/0/content/requestBody/content/application~1json/schema](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/generation_inputs/FSV-S02/packet.json)；SHA256 `5c8de100a097aa1cae1c236a1d9d7771e8c1e175d9c8601abc9d319dafca9611`

### FSV-S04 / P2P_STYLE

- [extraction.json/components](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/P2P_STYLE/extraction.json)；SHA256 `b6d2299ff2b3cb767bf5e6d5911f5e548e79ffeab83ee0e496a492dcb440dcc6`
- [generation.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/P2P_STYLE/generation.json)；SHA256 `06f7d66130515cacb25ee7b17461dd02c4cc7240ca16916bff29626ea878f102`
- [repair.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/P2P_STYLE/repair.json)；SHA256 `b60a7ed9458fc0a4f326541aba36cb26d0e7eace7167d871016bee4aeab9e749`

### FSV-S04 / AUTOPAC_STYLE

- [generation.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/AUTOPAC_STYLE/generation.json)；SHA256 `1bd409eb8ba263dea5c99b5248745d11cc0cd13e2429aa0e827fa6f620e08649`
- [judge.json](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/AUTOPAC_STYLE/judge.json)；SHA256 `2f2f4fa27ccd9c8d6477c226a6f9547975256455962da20867bed3f93f113092`
- [prompt.txt](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/calls/26_FSV-S04_repair/prompt.txt)；SHA256 `68790ca8bfdfb3353093adfd63037a0abdd9344b8cb7e7e81ebc302f916a28ca`
- [repair.json/rego](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/AUTOPAC_STYLE/repair.json)；SHA256 `a03ee4c2a6de6c07f6a1a870110cbc91490e6cb66abfa5195718b9ff7c1f12f7`
- [SUMMARY.json](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/binding_replay_resource_object/SUMMARY.json)；SHA256 `5345278278ae46c7054bbc6c023ff46505c866ac0872f115605aefe222e5dba3`

### FSV-S04 / ECAS_MATCHED

- [candidate.json/rules/0](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/effect_runs/FSV-S04/ECAS_MATCHED/candidate.json)；SHA256 `61100a221ee3fd6dca2ea31994cae0f377dbcf98e49c1c9963470917476dcf8d`
- [packet.json/visible_sources/1/content/fields/3](D:/lunwen/EC-CSI投稿/working/exploration/20261014_external_baseline_pilot/generation_inputs/FSV-S04/packet.json)；SHA256 `d37c94ec03d4901259ee058bd728fd0bc7736a3033a7b3347881626233bf5d49`

## 可见来源记录

|案例|evidence_id|source_id|locator|
|---|---|---|---|
|FSV-B06|VIS-FSV-B06-01|fineract-re-ageing.adoc|re-ageing.adoc:85-92;|
|FSV-B06|VIS-FSV-B06-02|fineract-re-ageing.adoc|re-ageing.adoc:95-110|
|FSV-B06|VIS-FSV-B06-RUNTIME-ABI|EC-V2-RUNTIME-INTERFACE-CATALOG-V1|tasks.FSV-B06|
|FSV-S02|VIS-FSV-S02-01|fineract-openapi-1.14.0.json|paths./v1/clients/{clientId}/identifiers.post|
|FSV-S02|VIS-FSV-S02-RUNTIME-ABI|EC-V2-RUNTIME-INTERFACE-CATALOG-V1|tasks.FSV-S02|
|FSV-S04|VIS-FSV-S04-01|frappe-rest-api.html|extracted/frappe-rest-api.md:article|
|FSV-S04|VIS-FSV-S04-02|erpnext-lead-doctype.json|erpnext-lead-doctype.json:complete-field-catalog|
|FSV-S04|VIS-FSV-S04-RUNTIME-ABI|EC-V2-RUNTIME-INTERFACE-CATALOG-V1|tasks.FSV-S04|

机械对账：43项全部通过；内容回溯到21个既有调用。B06与S04抽取状态EXTRACTED→READY为原run_pilot.py的既有别名恢复，业务字段相同。

原批次、原数据与原结论文件均未修改。
