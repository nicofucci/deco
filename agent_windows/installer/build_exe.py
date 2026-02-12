import subprocess
import sys
from pathlib import Path

def main():
    here = Path(__file__).resolve().parent
    spec = here / 'agent_installer.spec'
    dist_dir = here / 'dist'

    cmd = [sys.executable, '-m', 'PyInstaller', str(spec)]
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd, cwd=here)

    out = dist_dir / 'agent_installer' / 'agent_installer.exe'
    if not out.exists():
        raise SystemExit("Build failed: agent_installer.exe not found")
    print(f"Build OK: {out}")

if __name__ == '__main__':
    main()
