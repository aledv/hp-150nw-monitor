#!/usr/bin/env python3
"""Command-line version: python main_standalone.py <printer-ip-or-hostname> [--full]. Needs only curl, no FastAPI."""

import json
import sys

import printer


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    full = "--full" in args
    hosts = [a for a in args if not a.startswith("-")]
    if len(hosts) != 1 or not printer.valid_host(hosts[0]):
        print("usage: main_standalone.py <printer-ip-or-hostname> [--full]", file=sys.stderr)
        return 2
    print(json.dumps(printer.read_printer(hosts[0], full), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
