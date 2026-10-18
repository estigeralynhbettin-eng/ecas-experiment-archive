"""Add source-project labels to presentation tables without changing results."""
import csv
import datetime
import hashlib
import io
import json
import re
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=ROOT/'presentation_history'/('before_project_column_'+stamp)
backup.mkdir(parents=True,exist_ok=False)
names=['SEVEN_CASE_TABLE_CN.md','EXPERIMENT_SUMMARY_CN_R2.md','SEVEN_CASE_COMPARISON.csv','TABLE_SOURCES.json',
       'build_seven_case_table.py','R2_DELIVERY_QA.json','TABLE_INDEPENDENT_AUDIT.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
before={}
for name in names:
    p=ROOT/name;shutil.copyfile(p,backup/name);before[name]=sha(p)
expected={'FSV-B06':'Fineract','FSV-S02':'Fineract','FSV-S03':'Fineract',
          'FSV-S04':'ERPNext','FSV-B13':'ERPNext','FSV-B17':'ERPNext','FSV-B19':'ERPNext'}
with (ROOT/'SEVEN_CASE_COMPARISON.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;old_rows=list(reader)
assert len(old_rows)==21
for row in old_rows:assert row['system']==expected[row['task']]
projects={k:'Apache Fineract' if v=='Fineract' else v for k,v in expected.items()}
new_rows=[]
for row in old_rows:
    new=dict(row);new['project_name']=projects[row['task']];new_rows.append(new)
new_fields=list(fields);new_fields.insert(new_fields.index('system'),'project_name')
with (ROOT/'SEVEN_CASE_COMPARISON.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=new_fields);w.writeheader();w.writerows(new_rows)
assert [{k:v for k,v in r.items() if k!='project_name'} for r in new_rows]==old_rows

for name in ['SEVEN_CASE_TABLE_CN.md','EXPERIMENT_SUMMARY_CN_R2.md']:
    old=(ROOT/name).read_text(encoding='utf-8');lines=old.splitlines(keepends=True)
    start=next(i for i,line in enumerate(lines) if line.startswith('| 批次 | 案例'))
    for i in range(start,start+9):
        line=lines[i];end='\n' if line.endswith('\n') else ''
        cells=[x.strip() for x in line.strip().strip('|').split('|')]
        assert len(cells)==5
        value='所属项目' if i==start else ('---' if i==start+1 else projects['FSV-'+re.search(r'([BS]\d{2})',cells[1]).group(1)])
        cells.insert(2,value);lines[i]='| '+' | '.join(cells)+' |'+end
    revised=''.join(lines)
    # Removing just the new column must recover the exact original table/content.
    restored=revised.splitlines(keepends=True)
    for i in range(start,start+9):
        end='\n' if restored[i].endswith('\n') else ''
        cells=[x.strip() for x in restored[i].strip().strip('|').split('|')];del cells[2]
        restored[i]=('|'+ '|'.join(cells)+'|' if i==start+1 else '| '+' | '.join(cells)+' |')+end
    assert ''.join(restored)==old
    (ROOT/name).write_text(revised,encoding='utf-8')

source=json.loads((ROOT/'TABLE_SOURCES.json').read_text(encoding='utf-8-sig'))
for item in source['sources']:item['row']['project_name']=projects[item['task']]
(ROOT/'TABLE_SOURCES.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

p=ROOT/'build_seven_case_table.py';code=p.read_text(encoding='utf-8')
changes=[
('"system": "Fineract" if task in ("FSV-B06", "FSV-S02", "FSV-S03") else "ERPNext",',
 '"project_name": "Apache Fineract" if task in ("FSV-B06", "FSV-S02", "FSV-S03") else "ERPNext",\n            "system": "Fineract" if task in ("FSV-B06", "FSV-S02", "FSV-S03") else "ERPNext",'),
('"| 批次 | 案例与目标 | ECAS | P2P适配版 | AutoPAC适配版 |"','"| 批次 | 案例与目标 | 所属项目 | ECAS | P2P适配版 | AutoPAC适配版 |"'),
('"|---|---|---|---|---|"','"|---|---|---|---|---|---|"'),
('f"{task.replace(\'FSV-\', \'\')}：{labels[task]}", *cells]',
 'f"{task.replace(\'FSV-\', \'\')}：{labels[task]}", base["project_name"], *cells]')]
for old,new in changes:
    assert code.count(old)==1,(old,code.count(old));code=code.replace(old,new)
p.write_text(code,encoding='utf-8')
compile(code,str(p),'exec')
receipt={'status':'PASS_PRESENTATION_ONLY_AMENDMENT','new_model_calls':0,'new_policy_executions':0,
 'projects':projects,'method_rows':21,'case_rows_per_table':7,'prior_result_fields_unchanged':True,
 'prior_independent_scientific_audits_preserved_in':str(backup),
 'prior_QA_applies_to':'Original report bytes in backup; current amendment verifies project labels and no result-field changes.',
 'files':[{'file':name,'before_sha256':before[name],'after_sha256':sha(ROOT/name)} for name in names],
 'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(ROOT/'PROJECT_COLUMN_UPDATE_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':receipt['status'],'case_rows':7,'method_rows':21,'new_model_calls':0}))
