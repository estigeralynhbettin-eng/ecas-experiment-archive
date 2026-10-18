"""Isolate the literal generated regex on the frozen positive developer input."""
import json
import re
from pilot_lib import ROOT,LANE,read,dump,tool

generation=read(ROOT/'effect_runs/FSV-S04/AUTOPAC_STYLE/repair.json')
literal=re.search(r'regex\.match\(("(?:\\.|[^"\\])*")',generation['rego']).group(1)
folder=ROOT/'targeted_diagnostics/regex_literal';folder.mkdir(exist_ok=False)
policy=folder/'regex_diag.rego'
policy.write_text('package regex_diag\n\nvalue := regex.match('+literal+', input.email)\n',encoding='utf-8')
developer=read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks']['FSV-S04'][0]
dump(folder/'input.json',{'email':developer['input']['request']['body']['email_id']})
observed=tool([LANE/'tools/opa','eval','--format=json','--data',policy,'--input',folder/'input.json','data.regex_diag.value'],folder,'literal_eval')
if observed.returncode:raise RuntimeError('Literal regex diagnostic failed')
actual=json.loads(observed.stdout)['result'][0]['expressions'][0]['value']
dump(folder/'RESULT.json',{'classification':'ISOLATED_GENERATED_REGEX_DIAGNOSTIC_NOT_METHOD_RESULT','literal_rego_string':literal,'regex_runtime_string':json.loads(literal),'input_origin':'frozen positive operator developer test','observed_match':actual,'new_model_calls':0,'original_policy_changed':False})
print(json.dumps({'developer_positive_regex_match':actual,'new_model_calls':0}))
