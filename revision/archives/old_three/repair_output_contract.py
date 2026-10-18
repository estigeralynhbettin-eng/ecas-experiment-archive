"""Restore omitted structural constraints; no candidate semantic rewriting."""
import json
import shutil
from pathlib import Path
from pilot_lib import ROOT,LANE,read,dump,sha

def main():
    archive=ROOT/'setup_versions/v1';archive.mkdir(parents=True,exist_ok=False)
    for name in ('EXECUTION_CONFIG.json','PROMPT_TEMPLATES.json','FROZEN_PROTOCOL_CN.md','EXPERIMENT_SCOPE.json','EXECUTION_INPUT_MANIFEST.json'):
        shutil.copyfile(ROOT/name,archive/name)
    shutil.copyfile(ROOT/'execution_inputs/ecas_prompt_schema.json',archive/'ecas_prompt_schema.json')
    original=read(ROOT/'execution_inputs/ecas_output_schema.json')
    def slim(value):
        if isinstance(value,dict):return {k:slim(v) for k,v in value.items() if k not in ('description','title','$schema','$id','maxLength','minLength','uniqueItems','pattern')}
        if isinstance(value,list):return [slim(v) for v in value]
        return value
    fixed=slim(original)
    templates=read(ROOT/'PROMPT_TEMPLATES.json');templates['ecas_prompt_schema']=fixed
    templates['stages']['ecas_generate']+=' The original runtime permits EXACTLY ONE rule for propose (rules minItems=1 and maxItems=1). Never return multiple rules. Abstain uses empty rules. Preserve every schema parameter name; select one grounded rule without adding other constraints.'
    dump(ROOT/'PROMPT_TEMPLATES.json',templates);dump(ROOT/'execution_inputs/ecas_prompt_schema.json',fixed)
    config=read(ROOT/'EXECUTION_CONFIG.json');config['max_smoke_calls']=4;config['max_total_external_repair_calls']=5
    dump(ROOT/'EXECUTION_CONFIG.json',config)
    p=ROOT/'FROZEN_PROTOCOL_CN.md';text=p.read_text(encoding='utf-8')
    text+='\n执行修正v2（仍在30次总调用授权内）：第3次开发smoke完整返回，但生成3条规则，原schema只允许1条。原因是准备脚本对提示schema删除了maxItems/minItems；恢复结构限制，不删减或改写候选业务条件。原失败保留并不进入效果；采用一次预留调用做新提示资格检查，开发smoke上限4次、条件修复总上限5次，基础调用上限21次，总上限仍30次。由用户“继续实验、不用一直问、一直开展”的当前授权覆盖必要接口修复，不增加提供方、模型、发送内容或总token预算。原v1冻结存档setup_versions/v1。\n'
    p.write_text(text,encoding='utf-8')
    scope=read(ROOT/'EXPERIMENT_SCOPE.json');scope['protocol_sha256']=sha(p);scope['execution_revision']='v2-output-shape-constraint-restoration';dump(ROOT/'EXPERIMENT_SCOPE.json',scope)
    manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
    for item in manifest:
        item['sha256']=sha(item['path'])
    manifest.append({'path':str(ROOT/'repair_output_contract.py'),'sha256':sha(ROOT/'repair_output_contract.py')})
    dump(ROOT/'EXECUTION_INPUT_MANIFEST.json',manifest)
    dump(ROOT/'OUTPUT_CONTRACT_REPAIR.json',{'classification':'DEVELOPMENT_SCHEMA_INTERFACE_REPAIR','original_failed_call':3,'failure':'3 rules violate original maxItems=1','root_cause':'Slim prompt schema omitted structural item limits','candidate_semantics_modified':False,'additional_smoke_limit':1,'total_call_limit_unchanged':30,'old_version_archive':'setup_versions/v1','no_auto_same_prompt_retry':True,'smoke_records_original_failure_retained':True})
    print(json.dumps({'status':'INTERFACE_REPAIRED','smoke_limit':4,'total_call_limit':30}))

if __name__=='__main__':main()
