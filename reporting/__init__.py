"""Allure reporting helpers.

pytest-html gives one flat page per CI job. Allure merges the API job and both
browser jobs into a single report, groups tests by layer and feature, and sorts
failures into categories (product bug, a11y regression, known defect, flaky
infrastructure), which is what a reviewer actually needs to triage a red build.

Everything here is a no-op unless pytest runs with `--alluredir`.
"""

import platform
import shutil
from pathlib import Path

import allure

import config

CATEGORIES_FILE = Path(__file__).parent / "categories.json"

LAYERS = {"ui": "UI - Sauce Demo", "api": "API - Restful Booker"}


def feature_name(module_name: str) -> str:
    """`test_problem_users` -> `Problem Users`."""
    return module_name.removeprefix("test_").replace("_", " ").title()


def label_test(item) -> None:
    """Group a test by layer (epic) and module (feature) and rate its severity."""
    parts = Path(str(item.fspath)).parts
    layer = next((LAYERS[p] for p in parts if p in LAYERS), None)
    if layer:
        allure.dynamic.epic(layer)
    allure.dynamic.feature(feature_name(Path(str(item.fspath)).stem))
    if item.get_closest_marker("smoke"):
        allure.dynamic.severity(allure.severity_level.CRITICAL)


def write_run_metadata(results_dir: Path) -> None:
    """Add the environment panel and failure categories to the results folder."""
    results_dir.mkdir(parents=True, exist_ok=True)
    env = {
        "UI_BASE_URL": config.UI_BASE_URL,
        "API_BASE_URL": config.API_BASE_URL,
        "Python": platform.python_version(),
        "OS": platform.platform(terse=True),
    }
    lines = [f"{key}={value}" for key, value in env.items()]
    (results_dir / "environment.properties").write_text("\n".join(lines) + "\n")
    shutil.copy(CATEGORIES_FILE, results_dir / "categories.json")
