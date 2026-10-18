"""Bind parser-only status alias repair, retaining old raw and stopped state."""
import json
from pathlib import Path
from pilot_lib import ROOT,read,dump,sha

def main():
    p=ROOT/'FROZEN_PROTOCOL_CN.md'
    p.write_text(p.read_text(encoding='utf-8')+'\n执行修正v3：P2P抽取第6次调用返回完整DSARCP，但status=EXTRACTED，旧解析器只接受READY。p2p_extract原提示仅写status，未明确枚举。统一已完成非空抽取的等价状态词EXTRACTED→READY，不修改DSARCP、引用、政策条件或最终标签；原失败/原raw保留，保存派生输出和本地修复回执。按精确prompt SHA和raw SHA复用第5/6次原响应，不重计费。后续同类状态作相同确定性格式处理。新的v3执行入口重新绑定，禁止重复提交旧runner。总调用及模型配置不变。\n',encoding='utf-8')
    scope=read(ROOT/'EXPERIMENT_SCOPE.json');scope['protocol_sha256']=sha(p);scope['execution_revision']='v3-parser-status-alias-idempotent-resume';dump(ROOT/'EXPERIMENT_SCOPE.json',scope)
    manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
    for item in manifest:item['sha256']=sha(item['path'])
    manifest.append({'path':str(ROOT/'freeze_resume_v3.py'),'sha256':sha(ROOT/'freeze_resume_v3.py')})
    dump(ROOT/'EXECUTION_INPUT_MANIFEST.json',manifest)
    dump(ROOT/'STATUS_ALIAS_REPAIR.json',{'failed_call':6,'raw_status_preserved':'STOPPED_PROTOCOL_OR_TRANSPORT','equivalent_status_alias':'EXTRACTED -> READY','business_conditions_changed':False,'new_model_calls_for_repair':0,'resumed_from_exact_prompt_and_raw':True})
    print(json.dumps({'status':'FROZEN_PARSER_ONLY_RESUME','new_model_calls':0}))

if __name__=='__main__':main()
