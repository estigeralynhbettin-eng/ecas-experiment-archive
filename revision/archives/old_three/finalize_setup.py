"""Fix runtime locator and freeze execution scripts before any call."""
import json
import shutil
from pathlib import Path
from pilot_lib import ROOT,LANE,read,dump,sha

def main():
    if (ROOT/'CALL_LEDGER.json').exists():raise RuntimeError('Calls already started')
    config=read(ROOT/'EXECUTION_CONFIG.json')
    shutil.copyfile(ROOT/'EXECUTION_CONFIG.json',ROOT/'EXECUTION_CONFIG_PRE_LOCATOR_FIX.json')
    config['pwsh']='/mnt/c/Users/PBCDCI/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
    assert Path(config['pwsh']).is_file()
    dump(ROOT/'EXECUTION_CONFIG.json',config)
    manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
    for item in manifest:
        if item['path']==str(ROOT/'EXECUTION_CONFIG.json'):item['sha256']=sha(ROOT/'EXECUTION_CONFIG.json')
    for file in ['pilot_lib.py','run_t0.py','run_pilot.py','finalize_setup.py','T0_RECEIPT.json']:
        p=ROOT/file;manifest.append({'path':str(p),'sha256':sha(p)})
    # Pin global approved wrapper identity, not credential contents.
    for p in [Path(config['model_wrapper']),Path('/mnt/d/lunwen/load_llm_api_keys.ps1')]:
        manifest.append({'path':str(p),'sha256':sha(p)})
    dump(ROOT/'EXECUTION_INPUT_MANIFEST.json',manifest)
    dump(ROOT/'EXECUTION_SETUP_RECEIPT.json',{'status':'FROZEN_BEFORE_CALLS','files':len(manifest),'config_locator_fix_only':True,'t0_status':read(ROOT/'T0_RECEIPT.json')['status'],'model_calls':0,'windows_exception':'Windows approved wrapper required for mandated Windows key loader; all policy compilation/lint/evaluation in WSL'})
    print(json.dumps({'status':'FROZEN','files':len(manifest)}))

if __name__=='__main__':main()
