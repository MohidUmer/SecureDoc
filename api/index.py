import os
import sys
from pathlib import Path

# Add the project root's 'src' directory to the Python path
# Current file: api/index.py
# Parent: api/
# Parent.Parent: project_root/
ROOT = Path(__file__).resolve().parent.parent / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from securedoc import create_app

# Force production mode on Vercel
app = create_app(config_name="production")
