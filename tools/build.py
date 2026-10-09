#!/usr/bin/env python3
"""Build deterministic, independently installable Plasma packages using stdlib only."""
import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WIDGETS = {
    'system': ('io.rog.systemwidget', '1.3.0', 'telemetry.py'),
    'control': ('io.rog.controlhud', '1.2.0', 'rog-control-helper.py'),
    'gaming': ('io.rog.gaminghud', '1.4.0', 'rog-gaming-helper.py'),
}


def package_files(name):
    source = ROOT / 'widgets' / ('rog-' + name)
    files = {p.relative_to(source / 'package').as_posix(): p.read_bytes()
             for p in (source / 'package').rglob('*') if p.is_file()}
    for p in (source / 'scripts').glob('*.py'):
        files['contents/scripts/' + p.name] = p.read_bytes()
    for icon in json.loads((ROOT / 'shared/assets.json').read_text())['icons']:
        if Path(icon).name != icon:
            raise ValueError('Shared asset must be a basename')
        files['contents/images/' + icon] = (ROOT / 'shared/icons' / icon).read_bytes()
    files['LICENSE'] = (ROOT / 'LICENSE').read_bytes()
    files['THIRD_PARTY_NOTICES.md'] = (ROOT / 'THIRD_PARTY_NOTICES.md').read_bytes()
    for p in source.glob('*ATTRIBUTION*'):
        files[p.name] = p.read_bytes()
    return files


def verify(name, files):
    ident, version, script = WIDGETS[name]
    meta = json.loads(files['metadata.json'])
    assert (meta['KPlugin']['Id'], meta['KPlugin']['Version']) == (ident, version)
    for required in ('contents/ui/main.qml', 'contents/config/main.xml',
                     'contents/config/config.qml', 'contents/scripts/' + script):
        assert required in files, required
    assert any(p.startswith('contents/images/') for p in files)
    for path, content in files.items():
        assert not path.startswith('/') and '..' not in Path(path).parts
        if path.endswith(('.qml', '.py', '.xml', '.json')):
            assert b'__HELPER' not in content, path
            assert b'/home/' not in content, path


def build(name):
    files = package_files(name)
    verify(name, files)
    out = ROOT / 'dist' / f'rog-{name}-{WIDGETS[name][1]}.plasmoid'
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, content in sorted(files.items()):
            info = zipfile.ZipInfo(path, date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content, compresslevel=9)
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
        verify(name, {p: archive.read(p) for p in archive.namelist()})
    print(out.relative_to(ROOT))
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('widget', choices=['all', *WIDGETS], nargs='?', default='all')
    args = parser.parse_args()
    for widget in WIDGETS if args.widget == 'all' else [args.widget]:
        build(widget)
