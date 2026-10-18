"""Remove only DocType layout widgets from compact payload catalogs; no calls."""
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if (ROOT/'EXECUTION_INPUT_MANIFEST.json').exists():raise RuntimeError('Frozen')
archive=ROOT/'setup_versions/pre_layout_omit';shutil.copytree(ROOT/'generation_inputs',archive/'generation_inputs')
excluded={'Section Break','Column Break','Tab Break','Button','HTML','Fold'};changes=[]
for p in (ROOT/'generation_inputs').rglob('packet.json'):
    packet=json.loads(p.read_text(encoding='utf-8'))
    for source in packet['visible_sources']:
        content=source['content']
        if isinstance(content,dict) and 'field_catalog' in content:
            old=content['field_catalog'];omit=[row for row in old if row[1] in excluded]
            content['field_catalog']=[row for row in old if row[1] not in excluded]
            content['omitted_layout_widget_types']=sorted(excluded)
            content['notice']='All retained data fields are represented; only presentation widget types are omitted by the same fixed type rule for every catalog.'
            changes.append({'task':packet['task_window_id'],'source':source['source_id'],'original_fields':len(old),'retained_data_fields':len(content['field_catalog']),'omitted_widgets':omit})
    p.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'LAYOUT_OMISSION_RECEIPT.json').write_text(json.dumps({'model_calls':0,'excluded_types':sorted(excluded),'changes':changes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'model_calls':0,'changes':[{k:v for k,v in x.items() if k!='omitted_widgets'} for x in changes]}))
