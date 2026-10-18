#!/usr/bin/env python3
"""Freeze the approved zero-call dispatch-interface repair; preserve v1 history."""
import copy
from pathlib import Path
import judge_control as j

root=j.ROOT
prior=root/'setup_history/preparation_v1'
if (root/'CALL_LEDGER.json').exists() or (root/'ROOT_DISPATCH_APPROVAL.json').exists():
    raise RuntimeError('no refreeze after approval or dispatch')
old=j.read(prior/'INPUT_MANIFEST.json')
allowed={str(root/'judge_control.py'),str(root/'verify_preparation.py')}
for row in old:
    if row['path'] not in allowed and j.sha(row['path'])!=row['sha256']:
        raise RuntimeError('unexpected prepared input drift: '+row['path'])
j.dump(root/'ROOT_DISPATCH_APPROVAL_TEMPLATE.json',j.approval_template())
paths={row['path'] for row in old}|{str(root/'verify_preparation.py'),str(root/'PROTOCOL_CN.md'),
        str(root/'ROOT_DISPATCH_APPROVAL_TEMPLATE.json'),str(Path(__file__).resolve())}
items=[{'path':p,'sha256':j.sha(p)} for p in sorted(paths)]
j.dump(root/'INPUT_MANIFEST.json',items)
req=j.read(prior/'T0_REQUEST.json')
req['run_id']='typed-ir-judge-t0-v2'
req['inputs']=items+[{'path':str(root/'INPUT_MANIFEST.json'),'sha256':j.sha(root/'INPUT_MANIFEST.json')}]
j.dump(root/'T0_REQUEST.json',req)
run=j.read(prior/'RUN_REQUEST_BASE.json')
run['run_id']='typed-ir-judge-control-v2'
run['inputs']=copy.deepcopy(req['inputs'])
j.dump(root/'RUN_REQUEST_BASE.json',run)
print(j.compact({'status':'REFROZEN_FOR_ZERO_CALL_T0','input_count':len(items),'t0_run_id':req['run_id'],
                 'planned_judge_run_id':run['run_id'],'all_four_original_prompt_hashes_unchanged':True,'model_calls':0}))
