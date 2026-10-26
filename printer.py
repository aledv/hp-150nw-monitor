"""Read status and toner levels from an HP Color Laser 150nw (and similar HP printers exposing the LEDM
`/DevMgmt/*.xml` pages). No web framework here: used by the API (main.py) and the CLI (main_standalone.py)."""

import ipaddress
import re
import subprocess
import xml.etree.ElementTree as ET

COLOR_NAMES = {"K": "Black", "C": "Cyan", "M": "Magenta", "Y": "Yellow"}
_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
_HOSTNAME = re.compile(rf"^(?=.{{1,253}}$){_LABEL}(?:\.{_LABEL})*$")


def valid_host(host: str) -> bool:
    """IPv4/IPv6 address or plain hostname: nothing that could change the URL handed to curl."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return bool(_HOSTNAME.match(host))


def xml_to_dict(element):
    """Recursively convert an XML element into a dict (repeated tags become lists)."""
    result = {}
    if element.attrib:
        result["@attributes"] = element.attrib

    children = list(element)
    if not children:
        text = element.text
        if text and text.strip():
            return text.strip()
        return result or None

    for child in children:
        child_data = xml_to_dict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    return result


def clean_namespace(root):
    """Drop XML namespaces from every tag."""
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]
    return root


def curl_get(url):
    """Fetch a page with curl: these printers only speak old TLS with weak DH keys, which Python's ssl rejects."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-k", "-L", "--max-time", "10", "--tls-max", "1.2", "--ciphers", "DEFAULT:@SECLEVEL=0", url],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"curl failed with exit code {e.returncode}") from e
    except FileNotFoundError:
        raise RuntimeError("curl not found: install it (e.g. apt-get install curl)") from None


def _children_as_dict(node):
    data = {}
    for child in node:
        data[child.tag] = xml_to_dict(child) if len(child) > 0 else (child.text or "")
    return data


def get_printer_status(host):
    """General printer status (StatusCategory, alerts...), or {"error": ...}."""
    try:
        root = clean_namespace(ET.fromstring(curl_get(f"http://{host}/DevMgmt/ProductStatusDyn.xml")))
        status_node = root.find(".//Status")
        status = _children_as_dict(status_node) if status_node is not None else {}
        alert_table = root.find(".//AlertTable")
        if alert_table is not None:
            alerts = [xml_to_dict(alert) for alert in alert_table.findall(".//Alert")]
            if alerts:
                status["alerts"] = alerts
        return status
    except Exception as e:
        return {"error": f"Status error: {e}"}


def get_consumables(host):
    """List of consumables (toner cartridges...), or {"error": ...}."""
    try:
        root = clean_namespace(ET.fromstring(curl_get(f"http://{host}/DevMgmt/ConsumableConfigDyn.xml")))
        return [_children_as_dict(c) for c in root.findall(".//ConsumableInfo")]
    except Exception as e:
        return {"error": f"Consumables error: {e}"}


def format_simple_status(status, consumables):
    """Compact view: overall status and level/product/state per toner colour."""
    simple = {"status": status.get("StatusCategory", "unknown"), "toner_levels": {}}
    if isinstance(consumables, list):
        for cons in consumables:
            label = cons.get("ConsumableLabelCode", "Unknown")
            life_state = cons.get("ConsumableLifeState", {})
            simple["toner_levels"][COLOR_NAMES.get(label, label)] = {
                "level": f"{cons.get('ConsumablePercentageLevelRemaining', 'N/A')}%",
                "product_number": cons.get("ProductNumber", "N/A"),
                "state": life_state.get("ConsumableState", "unknown") if isinstance(life_state, dict) else "unknown",
            }
    return simple


def read_printer(host, full=False):
    status = get_printer_status(host)
    consumables = get_consumables(host)
    if full:
        return {"status": status, "consumables": consumables}
    return format_simple_status(status, consumables)
