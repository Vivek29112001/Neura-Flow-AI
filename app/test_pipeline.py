import sys
import io

# Fix Windows encoding without closing stderr
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from core.orchestrator import NeuraCore

core = NeuraCore()
results = core.run()
print("Pipeline done!")