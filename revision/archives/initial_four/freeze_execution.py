"""Freeze actual inputs and approved wrapper; credentials are never manifest inputs."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
if (ROOT/'CALL_LEDGER.json').exists() or (ROOT/'EXECUTION_INPUT_MANIFEST.json').exists():raise RuntimeError('Already frozen or called')
config=read(ROOT/'EXECUTION_CONFIG.json');lane=Path(config['runtime_lane'])
files=[ROOT/f for f in ['AUTHORIZATION_CN.md','TASK_CONTRACT_CN.md','FROZEN_PROTOCOL_CN.md','PROMPT_TEMPLATES.json','EXECUTION_CONFIG.json','EXPERIMENT_SCOPE.json','INPUT_DERIVATIONS.json','SIZE_REPAIR_RECEIPT.json','LAYOUT_OMISSION_RECEIPT.json','pilot_lib.py','run_pilot.py','run_t0.py','managed_entry.py','prepare_scope.py','finalize_preparation.py','omit_presentation_fields.py','freeze_execution.py']]
scope=read(ROOT/'EXPERIMENT_SCOPE.json');scope['protocol_sha256']=sha(ROOT/'FROZEN_PROTOCOL_CN.md');(ROOT/'EXPERIMENT_SCOPE.json').write_text(json.dumps(scope,indent=2)+'\n',encoding='utf-8')
for dirname in ('generation_inputs','execution_inputs','sealed_evaluation','source_snapshots'):files.extend((ROOT/dirname).rglob('*.json'))
files.extend(p for p in (lane/'runtime').rglob('*') if p.suffix in ('.py','.json'))
files.extend((lane/'tools').iterdir());files.extend([Path(config['model_wrapper']),Path('/mnt/d/lunwen/load_llm_api_keys.ps1')])
manifest=[{'path':str(p),'sha256':sha(p)} for p in files]
(ROOT/'EXECUTION_INPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for p in (lane/'runtime').rglob('*'):
    if p.is_file():p.chmod(0o444)
print(json.dumps({'status':'FROZEN_BEFORE_CALLS','files':len(manifest)}))
