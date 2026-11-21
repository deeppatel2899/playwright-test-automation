import sys
from pathlib import Path

# Make `config`, `pages` and `api` importable from anywhere in the suite.
sys.path.insert(0, str(Path(__file__).parent))
