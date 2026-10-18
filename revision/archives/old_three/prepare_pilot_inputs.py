"""Prepare public-source inputs and separately frozen evaluation fixtures."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
EC=Path('/mnt/d/lunwen/ec')
TASKS=('FSV-B06','FSV-S02','FSV-S04')

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def main():
    if (ROOT/'INPUT_MANIFEST.json').exists():
        raise RuntimeError('Input freeze exists; do not overwrite.')
    records=[]
    for task in TASKS:
        source_path=EC/'ec_v2_field_security_materials_v4/visible'/task/'visible_input.json'
        original=json.loads(source_path.read_text(encoding='utf-8'))
        sources=[]; available=[]
        for item in original['visible_sources']:
            item=dict(item)
            if item['source_id']=='EC-V2-RUNTIME-INTERFACE-CATALOG-V1':
                available=item['content']['available_values']
                item['content']={key:item['content'][key] for key in ('available_values','target_operation','notice')}
            sources.append(item)
        packet={'task_window_id':task,'target':original['target'],'visible_sources':sources,
                'common_adapter':{'subject_role':'authenticated_api_caller','action':original['target']['operation'],
                                  'resource_system':original['target']['system'],'resource_version':original['target']['version'],
                                  'request_and_trusted_paths':available,
                                  'notice':'The adapter supplies identity/target constants only. It does not supply a policy condition, expected decision, test value, or evaluation label.'}}
        dest=ROOT/'generation_inputs'/task/'packet.json';dump(dest,packet)
        records.append({'path':str(dest.relative_to(ROOT)),'source_path':str(source_path),'source_sha256':sha(source_path),'sha256':sha(dest),'derivation':'retain original sources; remove ECAS primitive focus from runtime ABI; append neutral adapter constants'})
        org={'subject':['authenticated_api_caller'],'action':[original['target']['operation']],
             'resource':[original['target']['system']+':'+original['target']['version']],
             'condition_paths':[v['path'] for v in available]}
        dest=ROOT/'generation_inputs'/task/'organization_schema.json';dump(dest,org)
        records.append({'path':str(dest.relative_to(ROOT)),'sha256':sha(dest),'derivation':'common target and available paths; no business condition supplied'})
        for channel in ('O-L','O-I'):
            src=EC/'ec_v2_hidden_oracle_repository_v1/hidden'/task/f'{channel}.json'
            dest=ROOT/'sealed_evaluation'/task/f'{channel}.json'
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
            records.append({'path':str(dest.relative_to(ROOT)),'source_path':str(src),'sha256':sha(dest),'derivation':'byte identical archived synthetic fixture; generator must not read'})
    dump(ROOT/'INPUT_MANIFEST.json',records)
    statuses=[]
    for task in TASKS:
        for method in ('P2P_NATIVE','AUTOPAC_NATIVE','P2P_STYLE_PROPOSED','AUTOPAC_STYLE_PROPOSED','ECAS_MATCHED_PROPOSED'):
            statuses.append({'task':task,'method':method,'execution_status':'NOT_RUN','observed_legal_decision':None,'observed_invalid_decision':None})
    dump(ROOT/'RUN_STATUS.json',{'status':'PREPARED_PENDING_IMPLEMENTATION_CHOICE_AND_MODEL_AUTHORIZATION','rows':statuses,'model_calls':0})
    print(json.dumps({'tasks':list(TASKS),'frozen_files':len(records),'model_calls':0}))

if __name__=='__main__':main()
