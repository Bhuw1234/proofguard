import sys
from pathlib import Path
import pytest

# Add the backend directory to sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))



