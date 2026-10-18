import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def c(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':'))
s=read(ROOT/'execution_inputs/ecas_prompt_schema.json')
print('schema',len(c(s).encode()), 'defs',list(s['$defs']))
for p in (ROOT/'generation_inputs').rglob('packet.json'):
    print(p.parent.name,len(c(read(p)).encode()),'combined',len(c(s).encode())+len(c(read(p)).encode()))
