#!/usr/bin/env python3
"""Independent integrity and no-dispatch receipt for prepared Judge control."""
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LANE=Path('/root/ecas_semantic_judge_control_20261014')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
for item in read(ROOT/'SOURCE_MANIFEST.json'):
    checks.append({'check':'original_and_snapshot_unchanged','source':item['source'],'pass':sha(item['source'])==item['sha256']==sha(item['snapshot'])})
for item in read(ROOT/'INPUT_MANIFEST.json'):
    checks.append({'check':'frozen_input_unchanged','path':item['path'],'pass':sha(item['path'])==item['sha256']})
plans=read(ROOT/'CALL_PLAN.json');mapping=read(ROOT/'CANDIDATE_MAPPING.json')
checks.append({'check':'four_tasks_eight_unchanged_parent_candidates','pass':len(plans)==4 and len(mapping)==8 and len({x['task'] for x in mapping})==4})
checks.append({'check':'configuration_mapping_excluded_from_prompts','pass':all('four_case_v1' not in Path(p['prompt_path']).read_text(encoding='utf-8') and 'four_case_v2' not in Path(p['prompt_path']).read_text(encoding='utf-8') for p in plans)})
checks.append({'check':'no_model_attempts_during_preparation','pass':not (ROOT/'CALL_LEDGER.json').exists()})
checks.append({'check':'root_approval_not_written_by_preparer','pass':not (ROOT/'ROOT_DISPATCH_APPROVAL.json').exists()})
checks.append({'check':'offline_t0_pass_and_managed_success','pass':read(ROOT/'T0_RECEIPT.json')['status']=='PASS' and read(LANE/'managed_runs/typed-ir-judge-t0-v1/status.json')['state']=='SUCCEEDED'})
copies=[]
for p in sorted((LANE/'managed_runs/typed-ir-judge-t0-v1').rglob('*')):
    if not p.is_file():continue
    dest=ROOT/'t0_run_receipts'/p.relative_to(LANE/'managed_runs/typed-ir-judge-t0-v1');dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dest);copies.append({'source':str(p),'delivered':str(dest),'sha256':sha(p),'pass':sha(p)==sha(dest)})
checks.append({'check':'managed_t0_receipts_copied_exactly','pass':all(c['pass'] for c in copies)})
receipt={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','prepared_at':dt.datetime.now(dt.timezone.utc).isoformat(),
         'state':'PREPARED_NOT_DISPATCHED','model_calls':0,'checks':checks,'check_count':len(checks),'t0_receipt_copies':copies,
         'input_tokens_estimate_max':max(p['estimated_prompt_tokens'] for p in plans),'estimate_not_hard_bound':True,
         'planned_judge_calls':4,'shared_main_judge_cap':44,'future_dispatch_owner':'root'}
(ROOT/'PREPARATION_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ['status','state','model_calls','check_count','planned_judge_calls','shared_main_judge_cap']}))
if receipt['status']!='PASS':raise SystemExit(1)
