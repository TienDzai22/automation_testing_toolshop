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

CI checks out the official [Toolshop repository](https://github.com/testsmith-io/practice-software-testing) at release 2.5 (`9e7736c3841ec2bbb9a6822c9e6602353b7b9a65`) into a separate directory. Its license permits private, internal, non-commercial use and restricts public redistribution; review the upstream LICENSE before use. Do not commit or publish the upstream checkout. The development Compose files provide Angular, Laravel, nginx, MariaDB, Composer, MailCatcher, cron and phpMyAdmin. `docker/compose.ci.yml` mounts the same API source into nginx, so it can serve Laravel's public directory.

Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) and start its Linux container engine. From the project directory, a local disposable deployment can be prepared in PowerShell:

```powershell
git clone --branch 2.5 https://github.com/testsmith-io/practice-software-testing.git .toolshop-upstream
$toolshopDir = (Resolve-Path .toolshop-upstream).Path
$env:SPRINT = 'sprint5'
$env:COMPOSE_PROJECT_NAME = 'toolshop-local'
$env:COMPOSE_FILE = "$toolshopDir\docker-compose.yml;$toolshopDir\docker-compose.override.yml;$PWD\docker\compose.ci.yml"
docker compose --project-directory $toolshopDir config
docker compose --project-directory $toolshopDir up -d --build
docker wait (docker compose --project-directory $toolshopDir ps -a -q composer)
# Once MariaDB is ready, initialize its disposable database:
docker compose --project-directory $toolshopDir exec -T laravel-api php artisan migrate --seed --force
$env:BASE_URL = 'http://localhost:4200'
$env:API_URL = 'http://localhost:8091'
python -m pytest --browser chromium
docker compose --project-directory $toolshopDir down
```

Wait until the UI and `$env:API_URL/brands` respond before testing. The first build and Angular dependency installation can take several minutes. The upstream seed creates brands, users, categories, images, products, specifications, favorites, invoices and payments. The UI is at `http://localhost:4200`, the API at `http://localhost:8091`, MailCatcher at `http://localhost:1080` and MariaDB at port `3306`. These are local test services and upstream default credentials must not be used for production. `down` does not delete named volumes. Use a fresh isolated Docker project for a clean seed.

The workflow runs the full suite for Chromium, Firefox and WebKit with two workers per job and one retry. Two workers limit runner and Docker load; one retry helps identify intermittent failures but a rerun is not proof of stability. Investigate `RERUN` results. Local `-n 4` remains available. Reports and failure artifacts are uploaded even on failure. The workflow has not been run on GitHub Actions.

Neither the Docker setup nor the three browser jobs have been executed here. The suite includes a `buggy` hash-route navigation test, while this stack starts Sprint 5 PROD; the test forces BUGGY route settings and may fail against PROD. The GitHub footer test also needs access to GitHub. Verify these constraints, current API contracts, seed data, failure traces and all three browser jobs against the actual deployment without weakening assertions. Docker logs can contain test data and are uploaded on failure; review artifact access and contents.

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
