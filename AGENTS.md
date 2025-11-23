# Repository Guidelines

## Project Structure & Module Organization
Keep framework code in `quier_flask/`: `app_cfg.py` loads configuration, `route_ctrl.py` defines decorators and canonical routes, and `__init__.py` wires the Flask app instance. Business logic lives under `apps/` with `api/` exposing HTTP controllers, `service/` orchestrating domain workflows, and `utiles/` storing helpers; add `__init__.py` when creating new packages. Runtime artifacts belong in `logs/`, while `cfg.ini` and `cfg.ini.local` hold deployment-specific settings toggled via the `USE_LOCAL_CONFIG` environment variable. Entry points remain `run_server.py` plus the helper batch scripts.

## Build, Test, and Development Commands
`pip install -r requirements.txt` - install the pinned Flask, Gunicorn, and crypto stack.  
`set USE_LOCAL_CONFIG=true && python run_server.py` - run with local config using Flask's built-in server.  
`start_local.bat` / `start_server.bat` - Windows shortcuts for local versus production-style startups.  
`gunicorn -c gunicorn.conf.py quier_flask:app` - process-managed deployment (Linux or WSL) that logs to `logs/service.log`.

## Coding Style & Naming Conventions
Target Python 3.7+, four-space indentation, and UTF-8 headers as shown in `run_server.py`. Use `snake_case` for functions and endpoints (`example_api`), `PascalCase` for classes (`MCfg`), and keep module names lowercase. Favor single quotes except where f-strings improve clarity, return dictionaries that match the standard `{code, msg, data}` schema, and document new routes with concise docstrings. No formatter is enforced; follow PEP 8 and run `python -m compileall .` if you need a quick syntax check before pushing.

## Testing Guidelines
Place automated tests under `tests/` mirroring the module layout (for example, `tests/api/test_example.py`). Use Python's built-in `unittest` plus Flask's test client to avoid extra dependencies. Name files and methods `test_<behavior>` and run suites locally with `python -m unittest discover tests`. Cover both happy-path payloads (status, code, msg) and failure flows emitted by `ctrl_handler` so every response still matches the shared envelope.

## Commit & Pull Request Guidelines
History currently uses compact, lowercase summaries such as `inital project`; keep adopting that single-line, imperative style under 70 characters and place extra context in the body. Pull requests should describe the change, call out config edits (`cfg.ini*`, `gunicorn.conf.py`), attach test output (`python -m unittest ...`), and include sample curl commands or screenshots for new endpoints. Request at least one review before merge and link any tracking issue IDs in the description.

## Security & Configuration Tips
Never commit secrets; guard credentials via environment variables or encrypt with `MCfg.__encode`. Confirm `cfg.ini.local` stays off servers, and rotate `logs/` paths cautiously because `route_ctrl.init_service_log` and Gunicorn expect that directory to exist. When touching logging or config, mention the expected host and port values in the PR so operators can update their deployment manifests promptly.
