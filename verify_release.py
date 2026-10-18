#!/usr/bin/env python3
"""Verify this archive without policy execution or network access."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
bad=[]
for item in manifest['files']:
 p=root/item['path']
 if not p.is_file() or p.stat().st_size!=item['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:bad.append(item['path'])
print(json.dumps({'status':'FAIL' if bad else 'PASS','checked_files':len(manifest['files']),'mismatched_files':bad,'policy_execution':False}))
sys.exit(bool(bad))
