# Automation Testing Toolshop

Python/Playwright automation test suite for the Toolshop practice application.

The suite covers UI, API, route mocking and BDD scenarios.

## Quick start (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install
pytest -m smoke --browser chromium
```

Copy `.env.example` to `.env` only for local reference. Test configuration is read from environment variables, for example:

```powershell
$env:TEST_ENV = "buggy"
pytest -m smoke --browser chromium
```

Tests create isolated accounts and anonymous carts on the selected deployment; the contact test submits a message. Never commit credentials, tokens, reports, or browser artifacts.

## Browsers, parallel runs and reports

```powershell
python -m pytest --browser chromium
python -m pytest --browser firefox
python -m pytest --browser webkit
python -m pytest --browser chromium -n 4
python -m pytest -m api
python -m pytest tests/bdd --browser chromium
python -m pytest --browser chromium --html=report.html --self-contained-html --tracing=retain-on-failure --screenshot=only-on-failure
python -m playwright show-trace path/to/trace.zip
```

Open `report.html` in a browser. Failure screenshots and traces are stored in `test-results/`. In GitHub Actions, open a workflow run and download the browser-specific artifact under **Artifacts**; retention is seven days.

## Docker and CI status

The verified Toolshop source and Compose configuration are not present in this repository. Docker cannot currently be started from this project. Supply the official Toolshop deployment source and a verified `docker-compose.toolshop.yml` with its required configuration and seed data; do not add secrets. Inspect services and ports with `docker compose -f docker-compose.toolshop.yml config`, start with `docker compose -f docker-compose.toolshop.yml up -d`, and stop with `docker compose -f docker-compose.toolshop.yml down`.

Set repository Actions variables `TOOLSHOP_BASE_URL` and `TOOLSHOP_API_URL` to the actual UI and API URLs exposed on `localhost` or `127.0.0.1` on the runner. The workflow validates these URLs and waits for the UI and `/brands` API. Browser-facing API configuration and CORS must match the deployment. Ports and service names must be verified from the supplied source.

The workflow runs the full suite for Chromium, Firefox and WebKit with two workers per job and one retry. Two workers limit runner and Docker load; one retry helps identify intermittent failures but a rerun is not proof of stability. Investigate `RERUN` results. Local `-n 4` remains available. Reports and failure artifacts are uploaded even on failure. The workflow has not been run on GitHub Actions.

The suite includes a `buggy` hash-route navigation test and a GitHub footer navigation test. Verify the supplied deployment supports that route and the footer test can reach GitHub. PROD API assertions also assume current response types and seed data. Run all three browsers against the actual deployment and address evidenced contract differences without weakening assertions.

## GitHub setup and pull requests

1. Create a public GitHub repository and review staged files for secrets before making the first real commit.
2. Rename the initial branch to `main` if needed and connect the repository with `git remote add origin <repository-url>`. Push only when authorized.
3. Create a branch with `git switch -c feature/<name>`, commit actual work, and push it when authorized.
4. Open a pull request into `main`, describe the change and include real CI results. Have a reviewer review and merge it after checks pass.
5. In repository settings configure a branch protection rule or ruleset for `main` requiring pull requests, review, and the actual browser CI checks after the workflow has run.

Suggested PR description:

```markdown
## Change
Describe the problem and implemented behavior.

## Verification
List commands and actual results, including CI run links and failures.

## Risks
Describe deployment, data or browser limitations.
```

At least three genuinely reviewed and merged PRs and actual commits from every team member must be created by the team. These requirements cannot be established from the current local repository.
