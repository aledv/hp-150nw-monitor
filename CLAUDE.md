# CLAUDE.md — hp-150nw-monitor

API FastAPI (`main.py`) che legge stato e toner della stampante HP 150nw dalle sue pagine XML (via `curl`, perché la
stampante ha TLS vecchio). Il formato della risposta di `/printer/<ip>` è usato dal widget di homepage
(`toner_levels.<Colore>.level`): non cambiarlo senza aggiornare homepage.

## Flusso
- Lavora su `main`, commit piccoli, push subito (regole generali in ~/.claude/CLAUDE.md).
- Test: `pip install -r requirements.txt -r requirements-dev.txt && python -m unittest discover -s tests -v`
  (XML simulati, niente rete). Aggiungi un test per ogni modifica di comportamento.
- Push su `main` → `.github/workflows/image.yml` → `ghcr.io/aledv/hp-150nw-monitor:<sha corto>`.
- Deploy in produzione sul Raspberry Pi: tag e digest in `my_rpi_scripts/hp-150nw-monitor/docker-compose.yml`, poi
  `docker compose pull && docker compose up -d` e prova dell'endpoint.

## Linter
`ruff check . && ruff format --check .` (config `ruff.toml`) e hadolint sul Dockerfile (`.hadolint.yaml`): girano in CI prima dei test e sono bloccanti. Prima di ogni commit lancia `ruff check --fix . && ruff format .`.
