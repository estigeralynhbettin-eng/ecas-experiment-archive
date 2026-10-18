"""Recover pre-patch source exactly and verify against the saved original hash."""
from pathlib import Path
import json
import hashlib
ROOT=Path(__file__).resolve().parent
text=(ROOT/'run_pilot.py').read_text(encoding='utf-8')
text=text.replace("if stage!='ecas_generate':payload['additional_public_case']=read(ROOT/'generation_inputs/FSV-S02/packet.json')","payload['additional_public_case']=read(ROOT/'generation_inputs/FSV-S02/packet.json')")
text=text.replace("        error_message=str(exc).split('\\n')[0][:2000]\n        item.update({'status':'STOPPED_PROTOCOL_OR_TRANSPORT','error_type':type(exc).__name__,'error':error_message,'completed_at':now()})","        item.update({'status':'STOPPED_PROTOCOL_OR_TRANSPORT','error_type':type(exc).__name__,'error':str(exc),'completed_at':now()})")
start=text.index('\ndef recover_ecas_smoke():')
end=text.index('\ndef final_rego(',start)
text=text[:start]+text[end:]
start=text.index("    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['stats','smoke','recover_ecas_smoke','run'])")
text=text[:start]+"    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['stats','smoke','run']);args=parser.parse_args()\n    {'stats':prompt_stats,'smoke':smoke,'run':run}[args.mode]()\n"
expected=next(x['sha256'] for x in json.loads((ROOT/'setup_versions/v1/EXECUTION_INPUT_MANIFEST.json').read_text(encoding='utf-8')) if x['path']==str(ROOT/'run_pilot.py'))
actual=hashlib.sha256(text.encode('utf-8')).hexdigest()
if actual!=expected:raise RuntimeError('Original source reconstruction digest mismatch')
(ROOT/'setup_versions/v1/run_pilot.py').write_text(text,encoding='utf-8')
print(json.dumps({'status':'ORIGINAL_SCRIPT_RECONSTRUCTED_BYTE_EXACT','sha256':actual}))
