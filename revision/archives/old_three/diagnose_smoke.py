import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parent
schema=json.loads((ROOT/'execution_inputs/ecas_output_schema.json').read_text())
for rule in schema['$defs']['rule']['oneOf']:
    props=rule.get('properties',{})
    if props.get('op',{}).get('const') in ('strict_type','named_validator'):
        print(json.dumps({'op':props.get('op'),'primitive_id':props.get('primitive_id'),'params':props.get('params')},ensure_ascii=False))
folder=ROOT/'calls/03_FSV-S04_ecas_generate'
raw=json.loads((folder/'response.raw.json').read_text())
candidate=json.loads(raw['choices'][0]['message']['content'])['output']['candidate']
for r in candidate['rules']:print(json.dumps(r,ensure_ascii=False))
for e in Draft202012Validator(schema).iter_errors(candidate):
    for sub in e.context:
        if list(sub.path)[:1] not in [['rules']]:continue
        print('context',list(sub.path),sub.message[:200])
