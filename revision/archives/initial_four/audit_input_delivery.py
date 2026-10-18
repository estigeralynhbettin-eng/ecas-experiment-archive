"""Source transformation reconciliation without model calls or result changes."""
import json
from pathlib import Path
from pilot_lib import ROOT,CONFIG,read,dump,sha,verify_inputs
verify_inputs();checks=[]
omit={'Section Break','Column Break','Tab Break','Button','HTML','Fold'}
keep={'fieldname','fieldtype','options','default','reqd','read_only','mandatory_depends_on','depends_on','fetch_from','allow_on_submit','unique','length','non_negative','precision'}
for task in CONFIG['tasks']:
    original=read(ROOT/'source_snapshots'/task/'visible_input.json');packet=read(ROOT/'generation_inputs'/task/'packet.json')
    checks.append({'check':task+'_identity','pass':original['target']==packet['target'] and packet['task_window_id']==task})
    for source in original['visible_sources']:
        actual=next(s for s in packet['visible_sources'] if s['evidence_id']==source['evidence_id'])
        checks.append({'check':task+'_'+source['evidence_id']+'_source_metadata','pass':source['source_id']==actual['source_id'] and source['source_sha256']==actual['source_sha256']})
        if source['source_id']=='EC-V2-RUNTIME-INTERFACE-CATALOG-V1':
            content={k:source['content'][k] for k in ('available_values','target_operation','notice')}
            checks.append({'check':task+'_neutral_abi','pass':actual['content']==content and 'proposal_focus' not in actual['content']})
        elif isinstance(source['content'],str):
            if source['source_id']=='frappe-rest-api.html':
                text=source['content'];a=text.index('### Create');b=text.index('### Read',a)
                expected=text[:text.index('## Authentication')].strip()+'\n\n'+text[a:b].strip()
            else:expected=source['content']
            checks.append({'check':task+'_'+source['evidence_id']+'_text','pass':actual['content']==expected})
        elif 'fields' in source['content']:
            fields=[f for f in source['content']['fields'] if f.get('fieldtype') not in omit]
            reconstructed=[]
            for row in actual['content']['field_catalog']:reconstructed.append({'fieldname':row[0],'fieldtype':row[1],**row[2]})
            expected=[{k:v for k,v in f.items() if k in keep} for f in fields]
            checks.append({'check':task+'_'+source['evidence_id']+'_complete_data_catalog','pass':reconstructed==expected,'field_count':len(expected)})
        else:checks.append({'check':task+'_'+source['evidence_id']+'_structured_source','pass':source['content']==actual['content']})
schema=read(ROOT/'execution_inputs/ecas_prompt_schema.json')
pre=read(ROOT/'setup_versions/pre_size_repair/PROMPT_TEMPLATES.json')['ecas_prompt_schema']
branches=pre['$defs']['rule']['oneOf'];actual=schema['rule_variants']
checks.append({'check':'all_15_schema_variants_equivalent','pass':len(actual)==len(branches)==15 and all(x==[v['properties']['op']['const'],v['properties']['primitive_id']['const'],v['properties']['params']] for x,v in zip(actual,branches))})
checks.append({'check':'root_constraints_retained','pass':all(schema['$defs'][k]==v for k,v in pre['$defs'].items() if k!='rule')})
receipt={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks,'model_calls':0,'note':'This script only checks delivery transformations; it does not initiate inference.'}
dump(ROOT/'INPUT_DELIVERY_QA.json',receipt)
print(json.dumps({'status':receipt['status'],'checks':len(checks),'failures':[x['check'] for x in checks if not x['pass']]}))
if receipt['status']!='PASS':raise SystemExit(2)
