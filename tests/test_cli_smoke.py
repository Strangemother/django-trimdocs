from pathlib import Path
import subprocess
import sys


def test_cli_help(tmp_path: Path):
    proc = subprocess.run([sys.executable, '-m', 'trimdocs.cli', '--help'], capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'compile' in proc.stdout
