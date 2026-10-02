"""Test senza rete: le risposte XML della stampante sono simulate.
Run: pip install -r requirements.txt -r requirements-dev.txt && python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

STATUS_XML = """<?xml version="1.0"?>
<psdyn:ProductStatusDyn xmlns:psdyn="http://www.hp.com/schemas/imaging/con/ledm/productstatusdyn/2007/10/31"
  xmlns:pscat="http://www.hp.com/schemas/imaging/con/ledm/productstatuscategories/2007/10/31">
  <psdyn:Status><pscat:StatusCategory>inPowerSave</pscat:StatusCategory></psdyn:Status>
</psdyn:ProductStatusDyn>"""

CONS_XML = """<?xml version="1.0"?>
<ccdyn:ConsumableConfigDyn xmlns:ccdyn="http://www.hp.com/schemas/imaging/con/ledm/consumableconfigdyn/2007/11/19"
  xmlns:dd="http://www.hp.com/schemas/imaging/con/dictionaries/1.0/">
  <ccdyn:ConsumableInfo>
    <dd:ConsumableLabelCode>K</dd:ConsumableLabelCode>
    <dd:ConsumablePercentageLevelRemaining>70</dd:ConsumablePercentageLevelRemaining>
    <dd:ProductNumber>W2070A</dd:ProductNumber>
    <ccdyn:ConsumableLifeState><dd:ConsumableState>ok</dd:ConsumableState></ccdyn:ConsumableLifeState>
  </ccdyn:ConsumableInfo>
  <ccdyn:ConsumableInfo>
    <dd:ConsumableLabelCode>C</dd:ConsumableLabelCode>
    <dd:ConsumablePercentageLevelRemaining>90</dd:ConsumablePercentageLevelRemaining>
    <dd:ProductNumber>W2071A</dd:ProductNumber>
    <ccdyn:ConsumableLifeState><dd:ConsumableState>ok</dd:ConsumableState></ccdyn:ConsumableLifeState>
  </ccdyn:ConsumableInfo>
</ccdyn:ConsumableConfigDyn>"""


def fake_curl(url):
    return STATUS_XML if "ProductStatusDyn" in url else CONS_XML


class PrinterApiTest(unittest.TestCase):
    def setUp(self):
        mock.patch.object(main, "curl_get", side_effect=fake_curl).start()
        self.client = TestClient(main.app)

    def tearDown(self):
        mock.patch.stopall()

    def test_simple_status(self):
        r = self.client.get("/printer/192.0.2.1")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "inPowerSave")
        self.assertEqual(body["toner_levels"]["Black"], {"level": "70%", "product_number": "W2070A", "state": "ok"})
        self.assertEqual(body["toner_levels"]["Cyan"]["level"], "90%")

    def test_full_details(self):
        body = self.client.get("/printer/192.0.2.1?full=true").json()
        self.assertEqual(len(body["consumables"]), 2)

    def test_printer_unreachable_is_reported_not_raised(self):
        mock.patch.stopall()
        with mock.patch.object(main, "curl_get", side_effect=Exception("Curl failed")):
            body = self.client.get("/printer/192.0.2.1").json()
        self.assertEqual(body["status"], "unknown")
        self.assertEqual(body["toner_levels"], {})


if __name__ == "__main__":
    unittest.main()
