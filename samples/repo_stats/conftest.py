"""Make the package importable from the tree root when pytest runs here."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
