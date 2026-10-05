"""Exercise the real shell entrypoint without ESP-IDF, firmware or hardware."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'buildFirmware.sh'

class BuildFailureTests(unittest.TestCase):
    def run_build(self, fail=False, configuration=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('bin', 'build', 'build-scripts'):
                (root / name).mkdir()
            if configuration:
                (root / 'build-scripts/I2S-4MFlash-sdkconfig.defaults').write_text('synthetic')
            compiler = root / 'bin/idf.py'
            compiler.write_text('#!/bin/sh\necho "$1" >> "$TEST_LOG"\n'
                                + ('if [ "$1" = build ]; then exit 7; fi\n' if fail else '')
                                + 'exit 0\n')
            compiler.chmod(0o700)
            archiver = root / 'bin/zip'
            archiver.write_text('#!/bin/sh\necho zip >> "$TEST_LOG"\nexit 0\n')
            archiver.chmod(0o700)
            env = dict(os.environ, PATH=str(root / 'bin') + ':' + os.environ['PATH'],
                       TEST_LOG=str(root / 'calls'), tag='synthetic',
                       TARGET_BUILD_NAME='I2S-4MFlash', BUILD_NUMBER='1', DEPTH='16',
                       artifact_file_name='synthetic.zip')
            result = subprocess.run(['/bin/bash', str(SCRIPT)], cwd=root, env=env,
                                    capture_output=True, text=True, timeout=10)
            calls = (root / 'calls').read_text().splitlines() if (root / 'calls').exists() else []
            return result.returncode, calls

    def test_failed_compiler_stops_reporting(self):
        self.assertEqual(self.run_build(fail=True), (7, ['build']))

    def test_success_runs_reports(self):
        self.assertEqual(self.run_build(), (0, ['build', 'size-components', 'size-components-squeezelite', 'zip', 'zip']))

    def test_missing_configuration_stops_before_compiler(self):
        code, calls = self.run_build(configuration=False)
        self.assertNotEqual(code, 0)
        self.assertEqual(calls, [])

if __name__ == '__main__':
    unittest.main()
