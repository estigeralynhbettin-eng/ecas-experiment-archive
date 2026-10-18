"""Read-only fixed-source gap investigation; no network, model, or policy execution."""
from pathlib import Path
import hashlib, json, subprocess

OUT=Path(__file__).resolve().parent
EXP=OUT.parent
SRC=Path(r'\\wsl.localhost\Ubuntu\root\ec\fineract-1.14.0-e1b')
LINUX='/root/ec/fineract-1.14.0-e1b'
PROVIDER='fineract-provider/src/main/java/org/apache/fineract/'
CORE='fineract-core/src/main/java/org/apache/fineract/'
def txt(p):return p.read_text(encoding='utf-8-sig')
def read(p):return json.loads(txt(p))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):
    r=subprocess.run(['wsl.exe','-d','Ubuntu','-e','git','-C',LINUX,*args],capture_output=True,text=True,encoding='utf-8',check=True)
    return r.stdout.strip()
identity={'source_tree_windows':str(SRC),'source_tree_linux':LINUX,'commit':git('rev-parse','HEAD'),'exact_tag':git('describe','--tags','--exact-match','HEAD'),'porcelain_status':git('status','--porcelain')}
assert identity['commit']=='7923d9e6cb67611c506b6c527b64497996acdc58'
assert identity['exact_tag']=='1.14.0' and not identity['porcelain_status']
refs={}
def ref(name, relative, spans):
    p=SRC/relative
    lines=txt(p).splitlines()
    value={'id':name,'path_windows':str(p),'path_linux':LINUX+'/'+relative,'sha256':sha(p),'line_excerpts':[{'start':a,'end':b,'text':'\n'.join(f'{i}:{lines[i-1]}' for i in range(a,b+1))} for a,b in spans]}
    refs[name]=value
    return value
ref('DOC_REAGE','fineract-doc/src/docs/en/chapters/features/re-ageing.adoc',[(85,92)])
ref('LOAN_API',PROVIDER+'portfolio/loanaccount/api/LoanTransactionsApiResource.java',[(85,98),(283,308),(347,361),(602,605),(722,745)])
ref('UNDO_BUILDER',CORE+'commands/service/CommandWrapperBuilder.java',[(3741,3748)])
ref('UNDO_HANDLER',PROVIDER+'portfolio/loanaccount/handler/loan/reaging/LoanUndoReAgingCommandHandler.java',[(30,48)])
ref('REAGE_SERVICE',PROVIDER+'portfolio/loanaccount/service/reaging/LoanReAgingService.java',[(161,180),(215,228)])
ref('REAGE_VALIDATOR',PROVIDER+'portfolio/loanaccount/service/reaging/LoanReAgingValidator.java',[(196,208)])
ref('GENERIC_ADJUST',PROVIDER+'portfolio/loanaccount/service/LoanWritePlatformServiceJpaRepositoryImpl.java',[(1180,1184),(1215,1245)])
ref('ADJUST_SERVICE',PROVIDER+'portfolio/loanaccount/service/adjustment/LoanAdjustmentServiceImpl.java',[(206,220)])
ref('UNDO_TEST_HELPER','integration-tests/src/test/java/org/apache/fineract/integrationtests/common/loans/LoanTransactionHelper.java',[(1095,1098)])
ref('IDENTIFIER_API',PROVIDER+'portfolio/client/api/ClientIdentifiersApiResource.java',[(113,127)])
ref('IDENTIFIER_DTO',PROVIDER+'portfolio/client/data/ClientIdentifierRequest.java',[(29,47)])
ref('HTTP_BODY_READER',PROVIDER+'infrastructure/core/jersey/JerseyJacksonObjectArgumentHandler.java',[(45,73)])
ref('JACKSON_CONFIG',PROVIDER+'infrastructure/core/jersey/JerseyJacksonConverterConfig.java',[(37,56)])
ref('IDENTIFIER_SERVICE',PROVIDER+'portfolio/client/service/ClientIdentifierWritePlatformServiceJpaRepositoryImpl.java',[(71,78)])
ref('IDENTIFIER_COMMAND_DESERIALIZER',PROVIDER+'portfolio/client/serialization/ClientIdentifierCommandFromApiJsonDeserializer.java',[(43,52),(60,77)])
ref('UNSUPPORTED_HELPER',CORE+'infrastructure/core/serialization/FromJsonHelper.java',[(86,102)])

manifest=EXP/'20261013_gateway_case_audit/selected_case_demo/sources/SOURCE_MANIFEST.json'
man=read(manifest)
declared={s['source_id']:s for s in man['sources']}
assert refs['DOC_REAGE']['sha256'].upper()==declared['fineract-re-ageing.adoc']['sha256']
assert refs['IDENTIFIER_API']['sha256'].upper()==declared['fineract-client-identifiers-api.java']['sha256']
prior=EXP/'20261014_external_baseline_pilot/generation_inputs'
packets={t:{'path':str(prior/t/'packet.json'),'sha256':sha(prior/t/'packet.json'),'target':read(prior/t/'packet.json')['target']} for t in ('FSV-B06','FSV-S02')}
s2=read(prior/'FSV-S02/packet.json')['visible_sources'][0]['content']['requestBody']['content']['application/json']['schema']
assert 'additionalProperties' not in s2

conclusions=[
 {'case':'FSV-B06','status':'SOURCE_OPERATION_SCOPE_NOT_CLOSED_SPECIFIC_COUNTEREVIDENCE_FOUND','confirmed':['同一1.14.0固定源码文档明确写Re-Age交易只能在为贷款账户最新交易时撤销。','该固定版本有独立POST /v1/loans/{loanId}/transactions?command=undoReAge，经独立handler进入undoReAge；不携带transactionId。','旧候选target POST /v1/loans/{loanId}/transactions/{transactionId}?command=undo进入Adjust a Transaction分支；该分支没有把undo映射为undoReAge。','专用undoReAge服务选择最新未撤销的Re-Age（不是直接比较账户所有类型交易的最新性）；其直接validator仅检查存在Re-Age。','通用调整另有CUMULATIVE schedule的LastTransactionDate检查，故不能概括为全项目没有最新交易检查。'],'implication':'保留历史文档目标抽取/可信布尔求值演示；暂不进入来源、真实API操作与状态获取完全闭合的主验证集。后续应另建固定专用操作任务，或证明通用adjust路径在明确交易类型与loan schedule范围内如何对应文档。不能追溯修改旧目标或把新源码当作旧模型已见材料。','unknown':['旧target的业务语义与Re-Age条款的完整等价关系未建立。','专用undoReAge和通用adjust在所有schedule、事件订阅及重处理路径下是否实施文档latest限制，本轮未运行后端或穷举调用链。','trusted/reAgeIsLatestTransaction在真实系统的认证、新鲜度与计算路径未核验。'],'evidence_ids':['DOC_REAGE','LOAN_API','UNDO_BUILDER','UNDO_HANDLER','REAGE_SERVICE','REAGE_VALIDATOR','GENERIC_ADJUST','ADJUST_SERVICE','UNDO_TEST_HELPER']},
 {'case':'FSV-S02','status':'INTERNAL_FOUR_KEY_CONTRACT_FOUND_HTTP_UNKNOWN_KEY_REJECTION_NOT_SUPPORTED','confirmed':['OpenAPI公开四字段但没有additionalProperties=false；旧模型可见材料未包含本轮查到的实现链。','内部ClientIdentifierCommand反序列化确有四字段SUPPORTED_PARAMETERS并调用checkForUnsupportedParameters；helper遇额外参数抛异常。','HTTP入口却先接收ClientIdentifierRequest typed DTO，再序列化DTO进入命令链。该DTO只有四字段，没有额外属性map或JsonAnySetter。','Jersey body reader对非String委托Jackson converter；固定源码ObjectMapper关闭FAIL_ON_UNKNOWN_PROPERTIES。因此现有静态HTTP链指向未知键被忽略/丢弃，而非被四字段内部checker拒绝。'],'implication':'可以把四字段作为受支持命令字段集的源码依据；不能把“原HTTP API必须拒绝未知键”声称已由源码证明。网关主动拒绝未知键可作为显式部署加固策略，但应另行制定、等量提供并标注为操作者策略；不得追溯改写旧例为原文唯一正确语义。','unknown':['未运行HTTP，故不声称已观察后端允许未知键，也不声称真实配置无额外拦截层。','没有找到该固定HTTP接口要求拒绝原始未知键的明确规定；没有在已检查测试范围内找到对应的unknown-key拒绝测试。'],'evidence_ids':['IDENTIFIER_API','IDENTIFIER_DTO','HTTP_BODY_READER','JACKSON_CONFIG','IDENTIFIER_SERVICE','IDENTIFIER_COMMAND_DESERIALIZER','UNSUPPORTED_HELPER']}
]
payload={'status':'COMPLETED_READ_ONLY_FIXED_SOURCE_INVESTIGATION','date':'2026-10-15','new_model_calls':0,'network_requests':0,'policy_or_backend_executions':0,'source_identity':identity,'source_manifest':{'path':str(manifest),'sha256':sha(manifest),'frozen_commit':man['fineract_commit'],'doc_and_identifier_api_hash_match':True},'prior_packets':packets,'search_scope':['已冻结source manifest与旧B06/S02 packet','/root/ec/fineract-1.14.0-e1b：指定Java入口、反序列化、service、builder、validator、Jersey converter及既有integration-tests和provider/src/test/java关键词搜索','D:/lunwen/ec/runtime仅做目录名定位（未发现Fineract目录）；未扩展到网络或其他版本'],'search_terms':['ClientIdentifier','checkForUnsupportedParameters','SUPPORTED_PARAMETERS','FAIL_ON_UNKNOWN_PROPERTIES','MappingJackson2HttpMessageConverter','undoReAge','UNDO_REAGE','adjustLoanTransaction','isReAge','latest transaction','unknown property/unsupported identifier test'],'negative_search_boundary':'无命中只对列出的本地范围有效；不解释为全世界无规范或无实现。WSL无rg，后续使用Windows rg读取WSL UNC与指定文件行段。','conclusions':conclusions,'evidence':list(refs.values()),'preservation':'原协议、模型输入/输出、标签、运行记录与R3均未修改。新增源码属于事后核读材料，不追溯补给历史模型。'}
(OUT/'SOURCE_GAP_CLOSURE.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# B06与S02来源缺口：固定实现源码核查','', '日期：2026-10-15。新增模型、网络、政策/后端执行均0。','', '**结论：查到了固定版本源码与具体反证，但两例仍不能被改标为“原业务语义与真实HTTP行为完全闭合”。B06存在专用undoReAge与旧通用target的差别；S02存在内部四字段检查，但HTTP先经过忽略未知属性的typed DTO。**','', '## 版本身份','', f"- 本地固定树：`{LINUX}`。",f"- HEAD=`{identity['commit']}`；exact tag=`{identity['exact_tag']}`；git porcelain为空。",'- 与冻结SOURCE_MANIFEST的commit相同；re-ageing.adoc与ClientIdentifiersApiResource的实际SHA256均精确匹配原manifest。','- 下列源码为本轮新核读，历史模型并未看到这些实现条款。','']
for c in conclusions:
    lines += ['## '+c['case'],'', '状态：`'+c['status']+'`。','', '已确认：','']+['- '+s for s in c['confirmed']]
    lines += ['', '**对实验使用的影响：** '+c['implication'],'','仍未知：','']+['- '+s for s in c['unknown']]
    lines += ['', '主要原件：','']
    for k in c['evidence_ids']:
        e=refs[k]
        line=','.join(str(x['start'])+'-'+str(x['end']) for x in e['line_excerpts'])
        lines.append(f"- `{e['path_linux']}`，行{line}；SHA256 `{e['sha256']}`。")
    lines += ['']
lines += ['## 有界搜索及停止边界','']+['- '+s for s in payload['search_scope']]+['- '+payload['negative_search_boundary'],'- 未执行HTTP或政策，不生成新的allow/deny观察；不据静态路径推断生产漏洞或生产成功。','- 逐行摘录、文件哈希和旧target见同名JSON；原协议和标签全部保留。']
(OUT/'SOURCE_GAP_CLOSURE_CN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':payload['status'],'source_files':len(refs),'version':identity['exact_tag'],'new_model_calls':0},ensure_ascii=False))
