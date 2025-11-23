# Repository Guidelines

## Project Structure & Module Organization
Core framework code stays in `quier_flask/`: `app_cfg.py` loads configuration, `route_ctrl.py` hosts decorators plus canonical routes, and `__init__.py` builds the Flask app instance. Business logic belongs in `apps/` where `api/` exposes controllers, `service/` coordinates workflows, and `utiles/` stores helpers; create `__init__.py` files for any new packages. Runtime artifacts go to `logs/`, while `cfg.ini` and `cfg.ini.local` toggle via the `USE_LOCAL_CONFIG` environment variable. Entry points remain `run_server.py` and the helper batch scripts, so avoid adding parallel launchers.

## Build, Test, and Development Commands
Use `pip install -r requirements.txt` to get the pinned Flask, Gunicorn, and crypto stack. Start locally with `set USE_LOCAL_CONFIG=true && python run_server.py` or run the shortcut `start_local.bat`. For production-like testing, use `start_server.bat` or `gunicorn -c gunicorn.conf.py quier_flask:app`, which logs to `logs/service.log`. Before pushing, `python -m compileall .` offers a fast syntax check.

## Coding Style & Naming Conventions
Target Python 3.7+, four-space indentation, and the UTF-8 header pattern seen in `run_server.py`. Keep module names lowercase, functions and endpoints in `snake_case` (e.g., `example_api`), and classes in `PascalCase` (e.g., `MCfg`). Favor single quotes unless f-strings improve clarity. HTTP responses should use the `{code, msg, data}` envelope, and new routes need short docstrings describing the behavior.

## Testing Guidelines
Place automated tests in `tests/` mirroring the module layout (`tests/api/test_example.py`). Use `unittest` with Flask’s test client, name files and methods `test_<behavior>`, and cover both successful payloads and failure flows emitted by `ctrl_handler`. Run the suite via `python -m unittest discover tests`; include output in PRs when new code paths are covered.

## Commit & Pull Request Guidelines
Commits follow one-line, lowercase, imperative summaries under 70 characters (e.g., `add user auth`). Pull requests should describe the change, mention config edits (`cfg.ini*`, `gunicorn.conf.py`), attach `python -m unittest ...` results, and provide sample curl commands or screenshots for new endpoints. Request at least one review and link tracking issues where applicable.

## Security & Configuration Tips
Never commit secrets; prefer environment variables or `MCfg.__encode`. Keep `cfg.ini.local` off servers. When adjusting logging or config defaults, call out the expected host and port so operators can update deployment manifests. Ensure the `logs/` directory exists since `route_ctrl.init_service_log` and Gunicorn depend on it.
