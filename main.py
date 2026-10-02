#!/usr/bin/env python3

import json
import subprocess
import xml.etree.ElementTree as ET

from fastapi import FastAPI, Query

app = FastAPI(title="Printer API")

# ==========================
# Funzioni originali
# ==========================


def xml_to_dict(element):
    """Converte ricorsivamente un elemento XML in dizionario"""
    result = {}
    if element.attrib:
        result["@attributes"] = element.attrib

    children = list(element)
    if children:
        for child in children:
            tag = child.tag
            child_data = xml_to_dict(child)
            if tag in result:
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_data)
            else:
                result[tag] = child_data
    else:
        text = element.text
        if text and text.strip():
            return text.strip()
        else:
            return result if result else None

    return result


def clean_namespace(root):
    """Rimuove i namespace dall'XML"""
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    return root


def curl_get(url):
    """Usa curl per ottenere l'XML (bypassa problemi SSL di Python)"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-k", "-L", "--max-time", "10", "--tls-max", "1.2", "--ciphers", "DEFAULT:@SECLEVEL=0", url],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout

    except subprocess.CalledProcessError as e:
        raise Exception(f"Curl failed: {e}") from e
    except FileNotFoundError:
        raise Exception("curl non trovato. Installalo con: sudo apt-get install curl") from None


def get_printer_status(ip):
    """Ottiene lo status generale della stampante"""
    url = f"http://{ip}/DevMgmt/ProductStatusDyn.xml"

    try:
        xml_content = curl_get(url)
        root = clean_namespace(ET.fromstring(xml_content))

        status = {}
        status_node = root.find(".//Status")
        if status_node:
            for child in status_node:
                tag = child.tag
                if len(child) > 0:
                    status[tag] = xml_to_dict(child)
                else:
                    status[tag] = child.text if child.text else ""

        alerts = []
        alert_table = root.find(".//AlertTable")
        if alert_table:
            for alert in alert_table.findall(".//Alert"):
                alerts.append(xml_to_dict(alert))

        if alerts:
            status["alerts"] = alerts

        return status

    except Exception as e:
        return {"error": f"Status error: {str(e)}"}


def get_consumables(ip):
    """Ottiene i livelli dei consumabili"""
    url = f"http://{ip}/DevMgmt/ConsumableConfigDyn.xml"

    try:
        xml_content = curl_get(url)
        root = clean_namespace(ET.fromstring(xml_content))
        consumables = []

        for consumable in root.findall(".//ConsumableInfo"):
            cons_data = {}
            for child in consumable:
                tag = child.tag
                if len(child) > 0:
                    cons_data[tag] = xml_to_dict(child)
                else:
                    text = child.text
                    cons_data[tag] = text if text else ""

            consumables.append(cons_data)

        return consumables

    except Exception as e:
        return {"error": f"Consumables error: {str(e)}"}


def format_simple_status(status, consumables):
    """Formatta uno status semplificato e leggibile"""
    simple = {"status": status.get("StatusCategory", "unknown"), "toner_levels": {}}

    if isinstance(consumables, list):
        for cons in consumables:
            label = cons.get("ConsumableLabelCode", "Unknown")
            level = cons.get("ConsumablePercentageLevelRemaining", "N/A")
            product = cons.get("ProductNumber", "N/A")
            life_state = cons.get("ConsumableLifeState", {})
            if isinstance(life_state, dict):
                state = life_state.get("ConsumableState", "unknown")
            else:
                state = "unknown"

            color_map = {"K": "Black", "C": "Cyan", "M": "Magenta", "Y": "Yellow"}
            color_name = color_map.get(label, label)

            simple["toner_levels"][color_name] = {"level": f"{level}%", "product_number": product, "state": state}

    return simple


# ==========================
# FastAPI endpoints
# ==========================


@app.get("/printer/{ip}")
def printer_status(ip: str, full: bool = Query(False, description="Mostra tutti i dettagli se True")):
    status = get_printer_status(ip)
    consumables = get_consumables(ip)

    if full:
        return {"status": status, "consumables": consumables}
    else:
        return format_simple_status(status, consumables)


# ==========================
# Script execution
# ==========================

if __name__ == "__main__":
    import sys

    printer_ip = "192.168.1.39"
    full_output = False

    for arg in sys.argv[1:]:
        if arg == "--full":
            full_output = True
        elif not arg.startswith("-"):
            printer_ip = arg

    status = get_printer_status(printer_ip)
    consumables = get_consumables(printer_ip)

    if full_output:
        result = {"status": status, "consumables": consumables}
    else:
        result = format_simple_status(status, consumables)

    print(json.dumps(result, indent=2, ensure_ascii=False))
