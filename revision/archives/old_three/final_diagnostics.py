"""One targeted missing-trusted-state diagnostic; not a new accuracy trial."""
import copy
import json
from pathlib import Path
from pilot_lib import ROOT,read,dump,rego_decision,evaluate_ecas,CONFIG
from run_binding_replay import envelope

def main():
    out=ROOT/'targeted_diagnostics';out.mkdir(exist_ok=False)
    original=read(ROOT/'sealed_evaluation/FSV-B06/O-L.json')['vectors'][0]['envelope']
    missing=copy.deepcopy(original);missing.setdefault('trusted',{}).pop('reAgeIsLatestTransaction',None)
    results=[]
    for method in ('P2P_STYLE','AUTOPAC_STYLE','ECAS_MATCHED'):
        folder=out/method;folder.mkdir()
        if method=='ECAS_MATCHED':
            policy=read(ROOT/'effect_runs/FSV-B06/ECAS_MATCHED/admitted_policy.json')
            contract=read(ROOT/'execution_inputs/FSV-B06/contract.json')
            actual=evaluate_ecas(policy,contract,envelope('FSV-B06',missing),admission_mode='semantic')
        else:
            row=read(ROOT/'binding_replay/FSV-B06'/method/'RESULT.json')
            actual=rego_decision(row['checks']['policy_path'],envelope('FSV-B06',missing),folder,'missing_trusted_flag')
        results.append({'method':method,'actual':actual})
    report={'classification':'POST_HOC_MISSING_TRUSTED_STATE_DIAGNOSTIC_NOT_ACCURACY_RESULT','case':'FSV-B06','mutation':'remove trusted.reAgeIsLatestTransaction only','input':missing,'results':results,'new_model_calls':0,'expected_class_not_assigned':True,'scope_limit':'Whether missing flag means non-Re-Age is not in provided ABI; do not extrapolate to all transaction types'}
    dump(out/'MISSING_TRUSTED_STATE.json',report)
    print(json.dumps({'classification':report['classification'],'observations':[{'method':x['method'],'decision':x['actual']['decision']} for x in results]}))

if __name__=='__main__':main()
