"""Local MLflow tracking for the LifeGuard-RL research benchmarks."""

import os
from pathlib import Path
import sys


def use_local_dependencies():
    """Expose optional compatibility packages to the CLI and its server worker."""
    dependencies = Path(__file__).resolve().parent.parent / ".mlflow" / "dependencies"
    if dependencies.is_dir():
        directory = str(dependencies)
        sys.path.insert(0, directory)
        existing = os.environ.get("PYTHONPATH")
        os.environ["PYTHONPATH"] = directory + (os.pathsep + existing if existing else "")
