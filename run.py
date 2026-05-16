"""
SecureDoc entrypoint. Run from this directory:
  python run.py
Or:
  set PYTHONPATH=src
  flask --app securedoc run
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from securedoc import create_app

app = create_app(
    config_name=os.getenv("FLASK_ENV", "development"),
)

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
