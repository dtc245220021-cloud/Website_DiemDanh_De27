"""Use the same Compose project and explicit stage files on every invocation."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
stage=int(sys.argv[1])
if stage not in [1,2,3]: raise SystemExit('stage must be 1, 2 or 3')
args=['docker','compose','-f','compose.yaml']
if stage>=2:args+=['-f','compose.monitoring.yaml']
if stage>=3:args+=['-f','compose.logging.yaml']
raise SystemExit(subprocess.call(args+sys.argv[2:],cwd=root))
