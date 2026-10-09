#!/usr/bin/env python3
"""Static checks. Qt parser is optional locally and mandatory in CI."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from build import ROOT, WIDGETS, package_files, verify


def validate(require_qml=False):
    count = 0
    for directory in ('widgets', 'tools', 'tests', 'shared'):
        for p in (ROOT / directory).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:
                continue
            if p.suffix == '.py': ast.parse(p.read_text(), filename=str(p))
            elif p.suffix == '.json': json.loads(p.read_text())
            elif p.suffix in ('.xml', '.svg'): ET.parse(p)
            elif p.suffix == '.sh': subprocess.run(['bash', '-n', str(p)], check=True)
            count += 1
    for line in (ROOT / 'baselines/SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert hashlib.sha256((ROOT / 'baselines' / name).read_bytes()).hexdigest() == digest
    for name in WIDGETS:
        verify(name, package_files(name))
    qmlformat = os.environ.get('QMLFORMAT') or shutil.which('qmlformat')
    if qmlformat:
        for p in (ROOT / 'widgets').rglob('*.qml'):
            subprocess.run([qmlformat, str(p)], stdout=subprocess.DEVNULL, check=True)
        print('PASS: Qt QML syntax parsing (not Plasma type/runtime validation)')
    elif require_qml:
        raise RuntimeError('Qt 6 qmlformat required; set QMLFORMAT to its executable')
    else:
        print('SKIP: Qt QML syntax parsing; qmlformat unavailable. CI requires it.')
    print(f'PASS: {count} source files inspected; JSON/XML/SVG/Python/shell, archive layout, IDs, versions and baseline hashes validated')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--require-qml', action='store_true')
    validate(p.parse_args().require_qml)
