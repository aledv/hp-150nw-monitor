"""REST API for HP 150nw printer status and toner levels (run with: uvicorn main:app --port 5001)."""

from fastapi import FastAPI, HTTPException, Query

import printer

app = FastAPI(title="HP 150nw Printer Monitor")


@app.get("/printer/{host}")
def printer_status(host: str, full: bool = Query(False, description="Return every detail instead of the summary")):
    if not printer.valid_host(host):
        raise HTTPException(status_code=400, detail="Invalid printer address")
    return printer.read_printer(host, full)


@app.get("/health")
def health():
    return {"status": "ok"}
