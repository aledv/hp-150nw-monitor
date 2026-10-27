# hp-150nw-monitor

[![CI](https://github.com/aledv/hp-150nw-monitor/actions/workflows/image.yml/badge.svg)](https://github.com/aledv/hp-150nw-monitor/actions/workflows/image.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Image](https://img.shields.io/badge/ghcr.io-hp--150nw--monitor-2496ED?logo=docker&logoColor=white)](https://github.com/aledv/hp-150nw-monitor/pkgs/container/hp-150nw-monitor)

A tiny REST API that reads the status and toner levels of an **HP Color Laser 150nw** printer (and other HP printers
exposing the same LEDM `/DevMgmt/*.xml` pages) and returns them as JSON. Made for dashboard widgets such as
[Homepage](https://gethomepage.dev)'s custom API widget, Home Assistant REST sensors or monitoring scripts.

The printer only speaks old TLS with weak DH keys, which Python's `ssl` refuses, so the pages are fetched with `curl`.

## API

`GET /printer/<ip-or-hostname>`

```json
{
  "status": "inPowerSave",
  "toner_levels": {
    "Black": {"level": "70%", "product_number": "W2070A", "state": "ok"},
    "Cyan": {"level": "90%", "product_number": "W2071A", "state": "ok"}
  }
}
```

- `GET /printer/<ip-or-hostname>?full=true` returns every field of the status and consumables pages (alerts included).
- `GET /health` returns `{"status": "ok"}`.
- An invalid address returns 400. An unreachable printer still returns 200, with `"status": "unknown"` and empty
  `toner_levels` (or an `error` field with `?full=true`).

## Quick start

```bash
docker build -t hp-150nw-monitor .
docker run -d --name hp-150nw-monitor -p 5001:5001 hp-150nw-monitor
curl http://localhost:5001/printer/192.168.1.50
```

Or with Compose, using the image built by CI: `docker compose up -d`. The bind address, port and tag can be changed
with `HP_MONITOR_BIND`, `HP_MONITOR_PORT` and `HP_MONITOR_TAG` (see `.env.sample`).

Homepage example (`services.yaml`):

```yaml
- Printer:
    widget:
      type: customapi
      url: http://<host>:5001/printer/<printer-ip>
      mappings:
        - field: { toner_levels: { Black: level } }
          label: Black
        - field: status
          label: Status
```

## Command line

```bash
python main_standalone.py <printer-ip-or-hostname> [--full]
```

Prints the same JSON without starting a server. It only needs Python and `curl`, no FastAPI.

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m unittest discover -s tests -v        # tests (printer XML simulated, no network)
ruff check . && ruff format --check .          # Python linter (ruff.toml)
hadolint --config .hadolint.yaml Dockerfile    # Dockerfile linter
```

CI (`.github/workflows/image.yml`) runs the linters, then the tests. On `main` it also builds a multi-arch image
(`linux/arm64`, `linux/amd64`) and pushes it to `ghcr.io/aledv/hp-150nw-monitor`, tagged `<short sha>` and `latest`.

## Project structure

```
printer.py           reads and parses the printer's XML pages (no web framework)
main.py              FastAPI app: /printer/<host>, /health
main_standalone.py   command-line version
tests/               unit tests with simulated printer responses
```

## Contributing

Issues and pull requests are welcome. Please run the linters and tests (see [Development](#development)) before opening a pull request.

## License

MIT, see [LICENSE](LICENSE).
