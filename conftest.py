import sys
from pathlib import Path

import pytest

# Make `config`, `pages`, `api` and `reporting` importable from anywhere in the suite.
sys.path.insert(0, str(Path(__file__).parent))

import reporting  # noqa: E402


@pytest.fixture(autouse=True)
def _allure_labels(request):
    reporting.label_test(request.node)


def pytest_sessionfinish(session):
    results_dir = session.config.getoption("--alluredir", default=None)
    # With pytest-xdist only the controller writes, not every worker.
    if results_dir and not hasattr(session.config, "workerinput"):
        reporting.write_run_metadata(Path(results_dir))
