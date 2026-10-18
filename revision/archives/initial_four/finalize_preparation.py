"""Bounded source and schema representation repair before model calls."""
import hashlib
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def c(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
if (ROOT/'CALL_LEDGER.json').exists() or (ROOT/'EXECUTION_INPUT_MANIFEST.json').exists():raise RuntimeError('Setup already frozen or called')
archive=ROOT/'setup_versions/pre_size_repair';archive.mkdir(parents=True,exist_ok=False)
shutil.copytree(ROOT/'generation_inputs',archive/'generation_inputs')
shutil.copyfile(ROOT/'PROMPT_TEMPLATES.json',archive/'PROMPT_TEMPLATES.json')
changes=[]
for p in (ROOT/'generation_inputs').rglob('packet.json'):
    packet=read(p)
    for s in packet['visible_sources']:
        if s['source_id']=='frappe-rest-api.html':
            original=s['content'];start=original.index('### Create');end=original.index('### Read',start)
            s['content']=original[:original.index('## Authentication')].strip()+'\n\n'+original[start:end].strip()
            s['locator']+=';operation-matched introduction and complete Create subsection'
            changes.append({'task':packet['task_window_id'],'source':s['source_id'],'derivation':'target POST create only; same excerpt rule across all ERPNext cases','start':start,'end':end})
        elif isinstance(s['content'],dict) and 'fields' in s['content']:
            fields=s['content'].pop('fields')
            s['content']['field_catalog_columns']=['fieldname','fieldtype','other_retained_properties']
            s['content']['field_catalog']=[[f.get('fieldname'),f.get('fieldtype'),{k:v for k,v in f.items() if k not in ('fieldname','fieldtype')}] for f in fields]
            changes.append({'task':packet['task_window_id'],'source':s['source_id'],'field_count':len(fields),'derivation':'lossless tuple representation of every retained field'})
    dump(p,packet)
templates=read(ROOT/'PROMPT_TEMPLATES.json');original_schema=templates['ecas_prompt_schema'];compact_schema=json.loads(json.dumps(original_schema))
variants=compact_schema['$defs'].pop('rule')['oneOf']
common={k:v for k,v in variants[0]['properties'].items() if k not in ('op','primitive_id','params')}
compact_schema['rule_common']={'type':'object','required':variants[0]['required'],'additionalProperties':False,'properties':common}
compact_schema['rule_variant_columns']=['op','primitive_id','params_schema']
compact_schema['rule_variants']=[[v['properties']['op']['const'],v['properties']['primitive_id']['const'],v['properties']['params']] for v in variants]
compact_schema['representation_notice']='This is a factored schema reference, not independently valid JSON Schema. Each rule has exactly the required rule_common fields; choose one row, use its op/primitive_id literals and its complete params_schema. The #/$defs/rule reference means one of these rows combined with rule_common. All root definitions, all 15 variants, all params constraints and minItems/maxItems are retained. Full original schema validates the output.'
templates['ecas_prompt_schema']=compact_schema
dump(ROOT/'execution_inputs/ecas_prompt_schema.json',compact_schema);dump(ROOT/'PROMPT_TEMPLATES.json',templates)
config=read(ROOT/'EXECUTION_CONFIG.json');sizes={p.parent.name:len(c(read(p)).encode()) for p in (ROOT/'generation_inputs').rglob('packet.json')};config['smoke_task']=max(sizes,key=sizes.get);dump(ROOT/'EXECUTION_CONFIG.json',config)
dump(ROOT/'SIZE_REPAIR_RECEIPT.json',{'model_calls':0,'changes':changes,'all_rule_variants':len(variants),'all_variants_retained':True,'packet_bytes':sizes,'prompt_schema_bytes':len(c(compact_schema).encode()),'full_schema_sha256':sha(ROOT/'execution_inputs/ecas_output_schema.json')})
# Fix smoke artifact identity and keep all shared developer checks visible.
p=ROOT/'run_pilot.py';text=p.read_text(encoding='utf-8')
text=text.replace("'FSV-S04_'+", "CONFIG['smoke_task']+'_'+")
old="admitted=compile_policy(compiled['policy'],contract);output['admission']='ADMITTED';dump(folder/'admitted_policy.json',admitted)"
new=old+"\n                devrows=[]\n                for test in read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]:\n                    actual=evaluate_ecas(admitted,contract,test['input'],admission_mode='semantic')\n                    devrows.append({'id':test['id'],'expected':test['expected'],'actual':actual,'pass':actual.get('decision')==test['expected'] and not actual.get('engine_error')})\n                output['common_developer_results']={'passed':all(t['pass'] for t in devrows),'rows':devrows}\n                dump(folder/'COMMON_DEVELOPER_RESULTS.json',output['common_developer_results'])\n                dump(folder/'CANDIDATE_FREEZE.json',{'policy_path':str(folder/'admitted_policy.json'),'policy_sha256':sha(folder/'admitted_policy.json'),'frozen_at':now(),'final_evaluation_not_yet_read':True})"
assert old in text;text=text.replace(old,new);p.write_text(text,encoding='utf-8')
print(json.dumps(read(ROOT/'SIZE_REPAIR_RECEIPT.json'),ensure_ascii=False))
