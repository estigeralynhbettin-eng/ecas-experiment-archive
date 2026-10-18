"""Read archived artifacts only; do not invoke models, OPA, or policy execution."""
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parents[1] / '20261014_external_baseline_pilot'
OUT = Path(__file__).resolve().parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
refs = {}
checks = []
def ref(relative, pointer=''):
    p = BASE / relative
    refs[relative] = {'path': str(p), 'sha256': sha(p)}
    return {'path': str(p), 'sha256': refs[relative]['sha256'], 'json_pointer': pointer}
def effect(task, method, filename, pointer=''):
    return ref(f'effect_runs/{task}/{method}/{filename}', pointer)
def stage(call, task, method, filename, nested=False):
    call_path = BASE / 'calls' / call
    raw = read(call_path / 'response.raw.json')
    content = read(call_path / 'content.json')
    checks.append({'check': f'{call}:raw_content_equal', 'pass': json.loads(raw['choices'][0]['message']['content']) == content})
    expected = content['output']['candidate'] if nested else content['output']
    actual = read(BASE / 'effect_runs' / task / method / filename)
    if call.startswith(('06_', '20_')):
        expected = dict(expected)
        assert expected['status'] == 'EXTRACTED'
        expected['status'] = 'READY'
    checks.append({'check': f'{call}:effect_equal', 'pass': expected == actual})
    for name in ('response.raw.json', 'content.json', 'prompt.txt'):
        ref(f'calls/{call}/{name}')
    return actual

mapping = [
 ('05_FSV-B06_p2p_detect','FSV-B06','P2P_STYLE','detection.json',False),
 ('06_FSV-B06_p2p_extract','FSV-B06','P2P_STYLE','extraction.json',False),
 ('07_FSV-B06_p2p_rego','FSV-B06','P2P_STYLE','generation.json',False),
 ('09_FSV-B06_repair','FSV-B06','P2P_STYLE','repair.json',False),
 ('10_FSV-B06_autopac_generate','FSV-B06','AUTOPAC_STYLE','generation.json',False),
 ('11_FSV-B06_autopac_judge','FSV-B06','AUTOPAC_STYLE','judge.json',False),
 ('12_FSV-B06_repair','FSV-B06','AUTOPAC_STYLE','repair.json',False),
 ('13_FSV-B06_ecas_generate','FSV-B06','ECAS_MATCHED','candidate.json',True),
 ('14_FSV-S02_p2p_detect','FSV-S02','P2P_STYLE','detection.json',False),
 ('15_FSV-S02_autopac_generate','FSV-S02','AUTOPAC_STYLE','generation.json',False),
 ('16_FSV-S02_autopac_judge','FSV-S02','AUTOPAC_STYLE','judge.json',False),
 ('17_FSV-S02_repair','FSV-S02','AUTOPAC_STYLE','repair.json',False),
 ('18_FSV-S02_ecas_generate','FSV-S02','ECAS_MATCHED','candidate.json',True),
 ('19_FSV-S04_p2p_detect','FSV-S04','P2P_STYLE','detection.json',False),
 ('20_FSV-S04_p2p_extract','FSV-S04','P2P_STYLE','extraction.json',False),
 ('21_FSV-S04_p2p_rego','FSV-S04','P2P_STYLE','generation.json',False),
 ('23_FSV-S04_repair','FSV-S04','P2P_STYLE','repair.json',False),
 ('24_FSV-S04_autopac_generate','FSV-S04','AUTOPAC_STYLE','generation.json',False),
 ('25_FSV-S04_autopac_judge','FSV-S04','AUTOPAC_STYLE','judge.json',False),
 ('26_FSV-S04_repair','FSV-S04','AUTOPAC_STYLE','repair.json',False),
 ('27_FSV-S04_ecas_generate','FSV-S04','ECAS_MATCHED','candidate.json',True),
]
for args in mapping:
    stage(*args)
ref('run_pilot.py')
ref('calls/06_FSV-B06_p2p_extract/LOCAL_RECOVERY_RECEIPT.json')
rows = []
def row(task, method, first, later, evidence):
    rows.append({'case': task, 'project': 'Apache Fineract' if task != 'FSV-S04' else 'ERPNext', 'method': method, 'first_generated_policy_semantic_observation': first, 'later_stage_observation': later, 'evidence': evidence})
row('FSV-B06','P2P_STYLE','首次Rego已有latest == true；DSARCP已抽取该条件。','修复仅改缩进；不改变主约束。',[
 effect('FSV-B06','P2P_STYLE','extraction.json','/components/0/condition'),effect('FSV-B06','P2P_STYLE','generation.json','/rego'),effect('FSV-B06','P2P_STYLE','repair.json','/rego')])
row('FSV-B06','AUTOPAC_STYLE','首次Rego已有latest == true。','Judge指出仅适用于Re-Age；修复改为false时禁止，缺标志允许，未真正增加交易类型区分。',[
 effect('FSV-B06','AUTOPAC_STYLE','generation.json','/rego'),effect('FSV-B06','AUTOPAC_STYLE','judge.json','/issues/0'),effect('FSV-B06','AUTOPAC_STYLE','repair.json','/rego')])
row('FSV-B06','ECAS_MATCHED','首次IR已有可信latest标志等于true；缺值deny。','已归档编译/准入与请求结果另列；此观察不等于通用undo完整语义正确。',[
 effect('FSV-B06','ECAS_MATCHED','candidate.json','/rules/0/params'),effect('FSV-B06','ECAS_MATCHED','RESULT.json')])
row('FSV-S02','P2P_STYLE','入口OUT_OF_SCOPE；没有首次政策，不评语义错误。','提示限定显式访问政策，不强制把结构校验作为访问控制。',[
 effect('FSV-S02','P2P_STYLE','detection.json'),ref('calls/14_FSV-S02_p2p_detect/prompt.txt')])
row('FSV-S02','AUTOPAC_STYLE','首次Rego只有documentKey/documentTypeId存在性；无白名单。','Judge ACCEPT；操作者未知键deny测试反馈后修复有allowed_keys和逐键成员检查，但is_integer导致编译失败。',[
 effect('FSV-S02','AUTOPAC_STYLE','generation.json','/rego'),effect('FSV-S02','AUTOPAC_STYLE','judge.json'),ref('calls/17_FSV-S02_repair/prompt.txt'),effect('FSV-S02','AUTOPAC_STYLE','repair.json','/rego'),effect('FSV-S02','AUTOPAC_STYLE','repaired/compile.stderr.txt')])
row('FSV-S02','ECAS_MATCHED','首次IR已有allowed_fields及四字段清单。','来源仅列properties，没有additionalProperties=false；“闭集拒绝”只能归于既有任务约定，不能直接算原文唯一正确含义。',[
 effect('FSV-S02','ECAS_MATCHED','candidate.json','/rules/0'),ref('generation_inputs/FSV-S02/packet.json','/visible_sources/0/content/requestBody/content/application~1json/schema')])
row('FSV-S04','P2P_STYLE','首次Rego只有身份/操作/资源，无邮箱格式条件。','DSARCP只提角色权限；开发修复加入is_string，没有邮箱格式校验。',[
 effect('FSV-S04','P2P_STYLE','extraction.json','/components'),effect('FSV-S04','P2P_STYLE','generation.json','/rego'),effect('FSV-S04','P2P_STYLE','repair.json','/rego')])
row('FSV-S04','AUTOPAC_STYLE','首次Rego只有身份/操作/资源，无邮箱格式条件。','Judge ACCEPT且issues为空；操作者正负邮箱测试反馈后出现regex。原接口错误与事后统一接口复演须另列。',[
 effect('FSV-S04','AUTOPAC_STYLE','generation.json','/rego'),effect('FSV-S04','AUTOPAC_STYLE','judge.json'),ref('calls/26_FSV-S04_repair/prompt.txt'),effect('FSV-S04','AUTOPAC_STYLE','repair.json','/rego'),ref('binding_replay_resource_object/SUMMARY.json')])
row('FSV-S04','ECAS_MATCHED','首次IR已有named_validator/email_basic_v1绑定email_id。','源字段options=Email；validator注册语义属于提供给模型的工具支持；不等于模型独立发明完整邮箱标准。',[
 effect('FSV-S04','ECAS_MATCHED','candidate.json','/rules/0'),ref('generation_inputs/FSV-S04/packet.json','/visible_sources/1/content/fields/3')])

source_observations = []
for task in ('FSV-B06','FSV-S02','FSV-S04'):
    p = BASE / 'generation_inputs' / task / 'packet.json'
    packet = read(p)
    ref(f'generation_inputs/{task}/packet.json')
    for i,s in enumerate(packet['visible_sources']):
        source_observations.append({'case':task,'packet_path':str(p),'packet_sha256':sha(p),'json_pointer':f'/visible_sources/{i}','evidence_id':s['evidence_id'],'source_id':s['source_id'],'source_sha256_as_recorded_in_packet':s['source_sha256'],'locator':s['locator']})
schema = read(BASE/'generation_inputs/FSV-S02/packet.json')['visible_sources'][0]['content']['requestBody']['content']['application/json']['schema']
checks.append({'check':'S02_openapi_additionalProperties_absent','pass':'additionalProperties' not in schema})
assert all(c['pass'] for c in checks), checks
payload = {'classification':'READ_ONLY_POST_HOC_STAGE_CONTENT_AUDIT_NOT_NEW_MODEL_EXPERIMENT_OR_INDEPENDENT_GOLD_REVIEW','new_model_calls':0,'new_policy_executions':0,'rows':rows,'source_observations':source_observations,'source_files':list(refs.values()),'checks':checks,'all_checks_pass':True,'boundaries':['P2P与AutoPAC同样做自然语言到政策；语义理解不是ECAS独有。','只核目标条件何时出现在实际政策，不用reason自述替代政策内容。','B06三方目标条件已出现，但Re-Age与通用undo适用范围未闭合。','S02封闭白名单约定未见于可见OpenAPI；不得直接当作理解正确性gold。','已有操作者反馈、原语目录、适用范围与编译错误均分列；不聚合语义准确率。']}
(OUT/'OLD_THREE_SEMANTIC_AUDIT.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines = ['# 旧三案例：语义条件形成阶段核读','', '日期：2026-10-15。只读核对旧响应与政策，不调用模型、不重新执行政策。','', '**结论：旧表主要展示最终执行，确实遮住了“何时形成目标含义”。这可以补成单独维度，但本核读不是语义准确率或独立gold审查。**','', '|案例|所属项目|方法|首次实际政策内容|后续阶段|','|---|---|---|---|---|']
for r in rows:
    lines.append('|'+ '|'.join(r[k] for k in ('case','project','method','first_generated_policy_semantic_observation','later_stage_observation'))+'|')
lines += ['', '## 解释边界', ''] + ['- '+x for x in payload['boundaries']] + [ '- S04中AutoPAC修复出现邮箱正则，能够证明目标条件已被尝试表达；不能据此直接判整个正则与源规范等价。','- 来源字段options=Email到注册validator的映射，以及四字段清单到闭集的映射，有不同来源强度，不能画同一种“语义全对”圆圈。','- P2P使用自动开发测试；AutoPAC接收操作者开发测试；ECAS有已定义原语及schema。该监督差异应随表保留。','', '## 逐项来源（SHA256与字段路径见同名JSON）','']
for r in rows:
    lines += [f"### {r['case']} / {r['method']}", '']
    for e in r['evidence']:
        label = Path(e['path']).name + (e['json_pointer'] or '')
        lines.append(f"- [{label}]({e['path'].replace(chr(92),'/')})；SHA256 `{e['sha256']}`")
    lines += ['']
lines += ['## 可见来源记录', '', '|案例|evidence_id|source_id|locator|', '|---|---|---|---|']
for s in source_observations:
    lines.append('|'+ '|'.join(s[k] for k in ('case','evidence_id','source_id','locator'))+'|')
lines += ['', f"机械对账：{len(checks)}项全部通过；内容回溯到21个既有调用。B06与S04抽取状态EXTRACTED→READY为原run_pilot.py的既有别名恢复，业务字段相同。", '', '原批次、原数据与原结论文件均未修改。']
(OUT/'OLD_THREE_SEMANTIC_AUDIT_CN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(checks),'rows':len(rows),'source_files':len(refs),'report':str(OUT/'OLD_THREE_SEMANTIC_AUDIT_CN.md')},ensure_ascii=False))
