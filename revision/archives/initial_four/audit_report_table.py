"""Bind the user-facing circle matrix to raw per-request decisions, including both ECAS configs."""
from pilot_lib import ROOT,CONFIG,read,dump
def symbol(result):
    if result['status']!='EVALUATED' or len(result.get('requests',[]))!=2:return '—'
    count=sum(x['actual'].get('decision')==x['expected'] and not x['actual'].get('engine_error') for x in result['requests'])
    return {0:'○',1:'◐',2:'●'}[count]
summary=read(ROOT/'COMPARISON_SUMMARY.json');latest={(r['task'],r['method']):r for r in summary['rows']}
report=(ROOT/'RESULTS_CN.md').read_text(encoding='utf-8')
section=report[report.index('## 2.'):report.index('## 3.')]
checks=[]
for task in CONFIG['tasks']:
    cells=[line for line in section.splitlines() if line.startswith('| '+task.removeprefix('FSV-')+'：')]
    assert len(cells)==1
    actual=[x.strip()[0] for x in cells[0].split('|')[2:-1]]
    expected=[symbol(latest[(task,'P2P_STYLE')]),symbol(latest[(task,'AUTOPAC_STYLE')]),symbol(read(ROOT/'effect_runs'/task/'ECAS_MATCHED/RESULT.json')),symbol(read(ROOT/'documented_ecas'/task/'ECAS_MATCHED/RESULT.json'))]
    checks.append({'case':task,'expected':expected,'rendered':actual,'pass':actual==expected})
v1=read(ROOT/'V1_ECAS_DIAGNOSTICS.json')
for record in v1['rows']:
    result=read(ROOT/'effect_runs'/record['task']/'ECAS_MATCHED/RESULT.json')
    checks.append({'case':record['task'],'check':'v1_original_requests_match','pass':record['requests']==result['requests']})
ok=all(x['pass'] for x in checks)
dump(ROOT/'REPORT_TABLE_QA.json',{'status':'PASS' if ok else 'FAIL','checks':checks,'note':'Circle cells computed from raw per-request decisions; source and engineering controls remain separate.'})
import json
print(json.dumps({'status':'PASS' if ok else 'FAIL','checks':len(checks),'cells':16}))
if not ok:raise SystemExit(2)
