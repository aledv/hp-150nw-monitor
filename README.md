# HP 150nw Printer Monitor

API REST (FastAPI) che legge dalla stampante HP Color Laser 150nw lo stato e i livelli dei toner (pagine XML
`/DevMgmt/*.xml` della stampante, scaricate con `curl`). La usa il widget di homepage.

- `GET /printer/<ip>` → `{"status": ..., "toner_levels": {"Black": {"level": "70%", ...}, ...}}`
- `GET /printer/<ip>?full=true` → tutti i dettagli

## Test

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Senza rete: le risposte XML della stampante sono simulate.

## Immagine e deploy

- Ogni push su `main` esegue i test con GitHub Actions e, se passano, pubblica l'immagine multi-arch
  (`linux/arm64` per il Raspberry Pi, `linux/amd64`) su `ghcr.io/aledv/hp-150nw-monitor`, privata, con tag `<sha corto>` e `latest`.
- In produzione gira sul Raspberry Pi: il compose è in `my_rpi_scripts/hp-150nw-monitor/docker-compose.yml`, con
  l'immagine fissata (`:<sha>@sha256:...`). Aggiornare: push → Action verde → tag e digest nel compose →
  `docker compose pull && docker compose up -d` sul Pi → `curl http://192.168.1.30:5001/printer/<ip-stampante>`.
  Rollback: tag precedente.
- Il `docker-compose.yml` di questo repo serve per provarlo altrove (`HP_MONITOR_BIND`, `HP_MONITOR_PORT`, `HP_MONITOR_TAG`).

## Uso da riga di comando

`python main_standalone.py <ip-stampante> [--full]` stampa lo stesso JSON senza avviare il server.

