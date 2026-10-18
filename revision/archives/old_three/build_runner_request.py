"""Bind one runner request with complete current input manifest."""
import argparse
import json
from pathlib import Path
from pilot_lib import ROOT,LANE,read,dump,sha,CONFIG

def main(mode):
    run_id='external-schema-smoke-v2' if mode=='recover_ecas_smoke' else 'external-three-case-effects-v3'
    output=ROOT/'SMOKE_RECORDS.json' if mode=='recover_ecas_smoke' else ROOT/'EXECUTION_STATE.json'
    inputs=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
    inputs+=[{'path':str(ROOT/'EXECUTION_INPUT_MANIFEST.json'),'sha256':sha(ROOT/'EXECUTION_INPUT_MANIFEST.json')}]
    if mode=='run':inputs+=[{'path':str(ROOT/'TOKEN_GATE_READY.json'),'sha256':sha(ROOT/'TOKEN_GATE_READY.json')}]
    request={'schema_version':1,'run_id':run_id,'run_root':str(LANE/'managed_runs'),
        'argv':['/usr/bin/python3',str(ROOT/'run_pilot.py'),mode],'cwd':str(ROOT),'inputs':inputs,
        'outputs':[{'path':str(output),'kind':'json','nonempty':True}],
        'timeout_seconds':900 if mode=='recover_ecas_smoke' else 14400,
        'authorization_ref':str(ROOT/'AUTHORIZATION_CN.md')+'; current user authorizes continuous execution within 30 calls'}
    # Managed runner requires outputs inside run_dir; a final snapshot is copied
    # by the entrypoint after successful execution, never treated as success early.
    request['argv']=['/usr/bin/python3',str(ROOT/'managed_entry.py'),mode,'{run_dir}/outputs/result.json']
    request['inputs']+=[{'path':str(ROOT/'managed_entry.py'),'sha256':sha(ROOT/'managed_entry.py')}]
    request['outputs']=[{'path':'outputs/result.json','kind':'json','nonempty':True}]
    dump(ROOT/(run_id+'.request.json'),request)
    print(json.dumps({'request':str(ROOT/(run_id+'.request.json')),'inputs':len(inputs)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['recover_ecas_smoke','run']);main(p.parse_args().mode)
