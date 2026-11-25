"""Accessibility scanning with axe-core, gated against a recorded baseline.

Sauce Demo already has a few accessibility issues. Failing on all of them
would make the check permanently red and therefore useless, so known issues
are recorded in `baseline.json`. A test fails only when a page gains a NEW
serious or critical violation, which is how teams adopt a11y checks on an
existing product without blocking every build.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

BASELINE_FILE = Path(__file__).parent / "baseline.json"

# WCAG 2.1 A/AA plus axe's best-practice rules.
AXE_OPTIONS = {
    "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"]},
    "resultTypes": ["violations"],
}

# Impacts that block the build when they are new. Moderate and minor
# findings are still reported in the failure message, but don't fail on their own.
BLOCKING_IMPACTS = {"serious", "critical"}

_axe = Axe()


@dataclass(frozen=True)
class Violation:
    rule: str
    impact: str
    help: str
    targets: tuple[str, ...]

    def __str__(self) -> str:
        return f"[{self.impact}] {self.rule}: {self.help} -> {', '.join(self.targets[:3])}"


def scan(page: Page) -> list[Violation]:
    """Run axe-core on the current page and return its violations."""
    result = _axe.run(page, options=AXE_OPTIONS)
    return [
        Violation(
            rule=v["id"],
            impact=v.get("impact") or "minor",
            help=v["help"],
            targets=tuple(str(n["target"][0]) for n in v["nodes"]),
        )
        for v in result.response["violations"]
    ]


def load_baseline() -> dict[str, list[str]]:
    """Page name -> rule ids already known to fail on that page."""
    return json.loads(BASELINE_FILE.read_text())


def new_violations(found: list[Violation], known_rules: list[str]) -> list[Violation]:
    """Violations whose rule is not in the baseline for this page."""
    return [v for v in found if v.rule not in known_rules]


def fixed_rules(found: list[Violation], known_rules: list[str]) -> list[str]:
    """Baseline rules that no longer fail, so the baseline can be tightened."""
    still_failing = {v.rule for v in found}
    return [rule for rule in known_rules if rule not in still_failing]
