"""Verify the factory's frozen local sources without contacting any repository."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def check_reference():
    spec=json.loads((ROOT/'REFERENCE_MANIFEST.json').read_text())
    base=ROOT/'reference'
    actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual != set(spec['files']):
        raise ValueError('Frozen reference file set changed; review and update the reference manifest')
    for name,expected in spec['files'].items():
        if hashlib.sha256((base/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Frozen source changed: '+name)
    return len(actual)


if __name__=='__main__':
    print('Verified local reference files:',check_reference())
