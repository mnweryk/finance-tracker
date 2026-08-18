import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if __name__ == "__main__":
    print("Starting tests with coverage")
    # Coverage options: measure src, show missing lines, generate HTML report
    coverage_args = [
        "tests",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]
    # Pass any additional arguments to pytest
    sys.exit(pytest.main(coverage_args + sys.argv[1:]))