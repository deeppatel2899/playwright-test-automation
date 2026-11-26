# Playwright Test Automation

[![tests](https://github.com/deeppatel2899/playwright-test-automation/actions/workflows/tests.yml/badge.svg)](https://github.com/deeppatel2899/playwright-test-automation/actions/workflows/tests.yml)

A UI and API test automation framework in **Python**, using **Playwright** and **pytest**.
It tests two public practice apps:

- **[Sauce Demo](https://www.saucedemo.com)**: an e-commerce store (login, catalog, cart, checkout)
- **[Restful Booker](https://restful-booker.herokuapp.com/apidoc/index.html)**: a hotel booking REST API (auth and full CRUD)

## What it shows

| Area | How |
|---|---|
| **Page Object Model** | Each screen is a class in `pages/`. Tests read like user stories and selectors live in one place. |
| **API client layer** | `api/booking_client.py` wraps the endpoints using Playwright's built-in `APIRequestContext`. No extra HTTP library is needed. |
| **Data-driven tests** | `pytest.mark.parametrize` covers login validation, checkout validation and all four sort orders. |
| **Fixtures and cleanup** | Fixtures log in, create bookings and delete them afterwards, so every test is independent. |
| **Contract tests** | JSON Schemas in `api/schemas.py` catch API changes such as a field changing type, going missing, or new fields appearing. |
| **Accessibility checks** | `tests/ui/test_accessibility.py` scans login, inventory, cart and checkout with axe-core (WCAG 2.1 A/AA). Known issues live in `a11y/baseline.json`, so the build fails only on a NEW serious or critical violation. |
| **Known-defect tracking** | A strict `xfail` records a real API bug (500 instead of 400). The suite flags it if the bug is ever fixed. |
| **Cross-browser** | CI runs the UI suite on Chromium and Firefox in parallel with `pytest-xdist`. |
| **Debuggability** | Failed UI tests keep a Playwright trace and a screenshot. Every run publishes an HTML report. |
| **Allure reporting** | CI merges the API job and both browser jobs into one Allure report. Tests are grouped by layer and feature, failed UI tests carry a screenshot and the URL, and failures are sorted into categories (product defect, a11y regression, contract break, timeout, known defect) by `reporting/categories.json`. |
| **CI/CD** | GitHub Actions runs lint, API and UI jobs on every push and PR, plus a daily scheduled run. |

## Project layout

```
pages/            Page objects (login, inventory, cart, checkout)
api/              Restful Booker API client
a11y/             axe-core scanner and the accessibility baseline
reporting/        Allure labels, environment info and failure categories
tests/ui/         Browser tests
tests/api/        API tests
config.py         URLs and credentials, all overridable with env vars
.github/workflows CI pipeline
```

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

pytest                      # everything
pytest -m smoke             # quick smoke subset
pytest -m api               # API tests only
pytest -m ui --headed       # watch the browser
pytest -m ui --browser firefox -n 4 --html=reports/report.html --self-contained-html
```

To build the Allure report locally (needs Java):

```bash
pytest --alluredir=allure-results
npx allure-commandline generate allure-results --clean --single-file -o allure-report
```

In CI, download the `allure-report` artifact and open `index.html`.

To point the suite at another environment, set `UI_BASE_URL` or `API_BASE_URL`.

To debug a failure, download the CI artifact and open the trace:

```bash
playwright show-trace test-results/<test-name>/trace.zip
```

## Roadmap

- [ ] Visual regression checks
- [x] Accessibility checks with axe-core, gated on a baseline (`tests/ui/test_accessibility.py`)
- [x] JSON schema validation for API responses (`api/schemas.py`)
- [x] Faulty-user tests: login time budget and tracked defects (`tests/ui/test_problem_users.py`)
- [x] Allure reporting with failure categories (`reporting/`)
