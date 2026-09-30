#!/usr/bin/env python3
"""Verify delivery integrity only; this is not a mathematical proof check."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
try:
    entries=json.loads((root/'FILE_MANIFEST.json').read_text())['sha256']
    failures=[]
    for name,wanted in entries.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root): failures.append('Unsafe path: '+name)
        elif not path.is_file(): failures.append('Missing: '+name)
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=wanted: failures.append('Changed: '+name)
    if failures: print('FAIL\n'+'\n'.join(failures));sys.exit(1)
    print(json.dumps({'status':'PASS','verified_files':len(entries)},indent=2))
except (OSError,ValueError,KeyError,TypeError) as e:
    print('Verification failed: '+str(e));sys.exit(2)
