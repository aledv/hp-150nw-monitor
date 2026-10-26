# CLAUDE.md — hp-150nw-monitor

FastAPI service reading status and toner levels of an HP Color Laser 150nw from its XML pages (fetched with `curl`,
because the printer only supports old TLS). `printer.py` holds the logic, `main.py` the API, `main_standalone.py` the CLI.

- The response format of `/printer/<host>` (`toner_levels.<Colour>.level`, `status`) is consumed by dashboard widgets:
  don't change it without a very good reason, and say so in the commit message.
- Keep `printer.py` free of FastAPI: the CLI must run with plain Python + curl.
- Every behaviour change gets a test (`tests/test_main.py`, printer XML simulated, no network).
- Before committing: `ruff check --fix . && ruff format .`, then the tests (commands in README). CI runs the same
  linters (ruff, hadolint) before the tests and blocks the image build if they fail.
- Production deployment is managed outside this repo: it pins the image built by CI (`tag@sha256`).
- English for code, comments, docs and commit messages.
