"""Packaging tests run without hardware, installed Plasma, or a real home directory."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build


class PackagingTests(unittest.TestCase):
    def test_reproducible_standalone_packages(self):
        for name, (ident, version, helper) in build.WIDGETS.items():
            with self.subTest(widget=name):
                path = build.build(name)
                first = path.read_bytes()
                build.build(name)
                self.assertEqual(first, path.read_bytes())
                with zipfile.ZipFile(path) as archive:
                    self.assertEqual(archive.read('contents/scripts/' + helper),
                                     (ROOT / 'widgets' / ('rog-' + name) / 'scripts' / helper).read_bytes())
                    self.assertEqual(json.loads(archive.read('metadata.json'))['KPlugin']['Id'], ident)
                    self.assertIn(b'Qt.resolvedUrl', archive.read('contents/ui/main.qml'))
                    self.assertNotIn(b'__HELPER', archive.read('contents/ui/main.qml'))
                    for icon in json.loads((ROOT / 'shared/assets.json').read_text())['icons']:
                        self.assertEqual(archive.read('contents/images/' + icon), (ROOT / 'shared/icons' / icon).read_bytes())

    @unittest.skipUnless(shutil.which('node'), 'Node.js needed to exercise exact QML JavaScript quoting')
    def test_qml_helper_command_quotes_unusual_paths(self):
        for name, (_, _, helper) in build.WIDGETS.items():
            qml = (ROOT / 'widgets' / ('rog-' + name) / 'package/contents/ui/main.qml').read_text()
            quote = next(line.strip() for line in qml.splitlines() if 'function shellQuote(' in line)
            expression = next(line.split('helper:', 1)[1].strip() for line in qml.splitlines() if 'property string helper:' in line)
            with tempfile.TemporaryDirectory(prefix="widget space '$; ") as directory:
                path = Path(directory) / helper
                path.write_text('print("safe-path")\n')
                js = quote + '\nconst Qt={resolvedUrl: () => ' + json.dumps(path.as_uri()) + '};\nconsole.log(' + expression + ');'
                command = subprocess.check_output(['node', '-e', js], text=True).strip()
                output = subprocess.check_output(['/bin/sh', '-c', command], text=True)
                self.assertEqual(output.strip(), 'safe-path')

    def test_installer_uses_isolated_home_and_retains_backup(self):
        build.build('gaming')
        with tempfile.TemporaryDirectory(prefix='rog installer ') as directory:
            home = Path(directory)
            binary = home / 'bin'; binary.mkdir()
            log = home / 'calls'
            mock = binary / 'kpackagetool6'
            mock.write_text('#!/bin/sh\nprintf "%s\\n" "$@" >> "$CALL_LOG"\n')
            mock.chmod(0o755)
            destination = home / 'data/plasma/plasmoids/io.rog.gaminghud'
            destination.mkdir(parents=True)
            (destination / 'sentinel').write_text('original')
            env = dict(os.environ, HOME=str(home), XDG_DATA_HOME=str(home / 'data'),
                       PATH=str(binary) + os.pathsep + os.environ['PATH'], CALL_LOG=str(log))
            subprocess.run(['bash', str(ROOT / 'tools/install.sh'), 'gaming'], env=env, check=True, capture_output=True)
            self.assertIn('--upgrade', log.read_text())
            backups = list((home / 'data/rog-flow-widget-backups/io.rog.gaminghud').glob('*/sentinel'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), 'original')
            self.assertEqual((destination / 'sentinel').read_text(), 'original')
            self.assertFalse((home / '.local/bin').exists())

    def test_upgrade_failure_restores_original(self):
        build.build('gaming')
        with tempfile.TemporaryDirectory(prefix='rog recovery ') as directory:
            home = Path(directory)
            binary = home / 'bin'; binary.mkdir()
            destination = home / 'data/plasma/plasmoids/io.rog.gaminghud'
            destination.mkdir(parents=True)
            (destination / 'sentinel').write_text('original')
            mock = binary / 'kpackagetool6'
            mock.write_text('#!/bin/sh\nrm -rf -- "$TEST_DESTINATION"\nmkdir -p -- "$TEST_DESTINATION"\nprintf partial > "$TEST_DESTINATION/partial"\nexit 7\n')
            mock.chmod(0o755)
            env = dict(os.environ, HOME=str(home), XDG_DATA_HOME=str(home / 'data'),
                       PATH=str(binary) + os.pathsep + os.environ['PATH'], TEST_DESTINATION=str(destination))
            result = subprocess.run(['bash', str(ROOT / 'tools/install.sh'), 'gaming'], env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('restored', result.stderr)
            self.assertEqual((destination / 'sentinel').read_text(), 'original')
            self.assertFalse((destination / 'partial').exists())
            self.assertEqual(len(list((home / 'data/rog-flow-widget-backups/io.rog.gaminghud').glob('*-failed/partial'))), 1)

    def test_uninstall_all_skips_absent_widgets(self):
        with tempfile.TemporaryDirectory(prefix='rog uninstall ') as directory:
            home = Path(directory)
            binary = home / 'bin'; binary.mkdir()
            log = home / 'calls'
            mock = binary / 'kpackagetool6'
            mock.write_text('#!/bin/sh\nprintf "%s\\n" "$@" >> "$CALL_LOG"\n')
            mock.chmod(0o755)
            (home / 'data/plasma/plasmoids/io.rog.gaminghud').mkdir(parents=True)
            env = dict(os.environ, HOME=str(home), XDG_DATA_HOME=str(home / 'data'),
                       PATH=str(binary) + os.pathsep + os.environ['PATH'], CALL_LOG=str(log))
            result = subprocess.run(['bash', str(ROOT / 'tools/uninstall.sh'), 'all'], env=env, check=True, capture_output=True, text=True)
            self.assertIn('Skipped io.rog.systemwidget', result.stdout)
            self.assertIn('io.rog.gaminghud', log.read_text())
            self.assertNotIn('io.rog.systemwidget', log.read_text())
