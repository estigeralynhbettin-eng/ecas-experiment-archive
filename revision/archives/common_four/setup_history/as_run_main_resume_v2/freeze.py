"""Freeze owned script/input/tool identity and build managed runner requests."""
import json
from pathlib import Path
from pilot_lib import ROOT, LANE, CONFIG, read, dump, sha

def manifest():
    paths=[]
    for name in ['AUTHORIZATION_CN.md','TASK_CONTRACT.md','USER_PROTOCOL_CN.md','FROZEN_PROTOCOL_CN.md','EXECUTION_CONFIG.json',
                 'EXPERIMENT_SCOPE.json','PROMPT_TEMPLATES.json','DOCUMENTED_OPERATOR_SEMANTICS.json','INPUT_DERIVATIONS.json','SOURCE_COPY_RECEIPT.json','TOKEN_ESTIMATOR_CALIBRATION.json','SCHEMA_FACTORIZATION_QA.json',
                 'pilot_lib.py','run_matched.py','managed_entry.py','run_t0.py','prepare.py','freeze.py','recover_wrapper_v2.py',
                 'prepare_main_resume_v2.py','MAIN_RESUME_AUTHORIZATION_V2.json','SOURCE_REFERENCE_ACCEPTANCE_V2.json']:
        paths.append(ROOT/name)
    for sub in ['generation_inputs','execution_inputs','sealed_evaluation','source_snapshots','t0_fixtures']:
        paths.extend(p for p in (ROOT/sub).rglob('*') if p.is_file())
    for sub in ['runtime','tools']:
        paths.extend(p for p in (LANE/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend([Path(CONFIG['model_wrapper']),Path('/mnt/d/lunwen/load_llm_api_keys.ps1')])
    values=[{'path':str(p),'sha256':sha(p)} for p in sorted(set(paths))]
    dump(ROOT/'EXECUTION_INPUT_MANIFEST.json',values)
    return values

def requests(wrapper_recovery=False,main_resume=False):
    values=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
    base=values+[{'path':str(ROOT/name),'sha256':sha(ROOT/name)} for name in ['EXECUTION_INPUT_MANIFEST.json','T0_RECEIPT.json','T0_EVIDENCE.json','PROMPT_SIZE_PLAN.json']]
    for mode in (['resume'] if main_resume else ['smoke','run']):
        names=['SCOPED_GATE_READY.json','DISPATCH_AUTHORIZATION.json']+(['TOKEN_GATE_READY.json'] if mode in ['run','resume'] else [])
        missing=[n for n in names if not (ROOT/n).exists()]
        values=base+[{'path':str(ROOT/n),'sha256':sha(ROOT/n)} for n in names if (ROOT/n).exists()]
        run_id='matched-generation-main-resume-v2' if main_resume else ('matched-generation-smoke-wrapper-recovery-v2' if mode=='smoke' and wrapper_recovery else 'matched-generation-'+mode+'-v1')
        request={'schema_version':1,'run_id':run_id,'run_root':str(LANE/'managed_runs'),
                 'argv':['/usr/bin/python3',str(ROOT/'managed_entry.py'),mode,'{run_dir}/outputs/result.json'],'cwd':str(ROOT),
                 'inputs':values,'outputs':[{'path':'outputs/result.json','kind':'json','required_keys':[] if mode=='smoke' else ['status','scope_id','rows'],'nonempty':True}],
                 'timeout_seconds':3600 if mode=='smoke' else 28800,
                 'authorization_ref':str(ROOT/'AUTHORIZATION_CN.md')+'; current matched comparison; cumulative <=44; root dispatch only'}
        dump(ROOT/(run_id+'.request.json'),request)
        dump(ROOT/('REQUEST_'+mode.upper()+'_READINESS.json'),{'status':'WAITING_ROOT_GATES' if missing else 'FILES_READY_REQUIRES_RUNNER_VALIDATE','missing':missing,'scope_id':CONFIG['scope_id'],'actual_model_calls':0 if not (ROOT/'CALL_LEDGER.json').exists() else len(read(ROOT/'CALL_LEDGER.json'))})
    print(json.dumps({'request_files':2,'gate_files_still_required':True}))

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='requests':requests(wrapper_recovery=len(sys.argv)>2 and sys.argv[2]=='wrapper-recovery',main_resume=len(sys.argv)>2 and sys.argv[2]=='main-resume')
    else:print(json.dumps({'frozen_files':len(manifest()),'model_calls':0}))
