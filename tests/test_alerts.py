import unittest
from datetime import datetime
from unittest.mock import patch

from pagerduty_mcp.models import Alert, ListResponseModel
from pagerduty_mcp.tools.alerts import list_alerts


class TestAlertModelsAndTools(unittest.TestCase):
    """Tests for Alert model and alert tools, matching unittest style used elsewhere."""

    @classmethod
    def setUpClass(cls):
        cls.sample_alert_data = {
            "id": "A2",
            "summary": "CPU High",
            "status": "triggered",
            "severity": "critical",
            "created_at": "2024-01-02T03:04:05Z",
            "updated_at": "2024-01-02T04:05:06Z",
            "incident": {"id": "I123", "type": "incident_reference"},
            "service": {"id": "S456", "type": "service_reference"},
            "html_url": "https://pagerduty.example/alerts/A2",
            "alert_key": "dedupe-123",
            "source": "host-01",
            "component": "api",
            "group": "prod",
            "class": "threshold_breach",
            "body": {"cef": {"name": "CPU High"}},
            "details": {"cpu": 97},
            "integration": {"id": "int-1", "name": "CloudWatch"},
        }

    def test_alert_minimal(self):
        alert = Alert(id="A1")
        self.assertEqual(alert.id, "A1")
        self.assertEqual(alert.type, "alert")
        self.assertIsNone(alert.summary)
        self.assertIsNone(alert.status)
        self.assertIsNone(alert.severity)
        self.assertIsNone(alert.created_at)
        self.assertIsNone(alert.updated_at)

    def test_alert_full_payload_with_references_and_aliases(self):
        alert = Alert(**self.sample_alert_data)
        self.assertEqual(alert.id, "A2")
        self.assertEqual(alert.summary, "CPU High")
        self.assertEqual(alert.status, "triggered")
        self.assertEqual(alert.severity, "critical")
        self.assertIsInstance(alert.created_at, datetime)
        self.assertIsInstance(alert.updated_at, datetime)
        self.assertIsNotNone(alert.incident)
        self.assertEqual(alert.incident.id, "I123")
        self.assertIsNotNone(alert.service)
        self.assertEqual(alert.service.id, "S456")
        self.assertTrue(alert.html_url.endswith("/A2"))
        self.assertEqual(alert.alert_key, "dedupe-123")
        self.assertEqual(alert.source, "host-01")
        self.assertEqual(alert.component, "api")
        self.assertEqual(alert.group, "prod")
        self.assertEqual(alert.klass, "threshold_breach")
        self.assertIn("cef", alert.body or {})
        self.assertEqual((alert.details or {}).get("cpu"), 97)
        self.assertEqual((alert.integration or {}).get("name"), "CloudWatch")

    def test_alert_serialization_uses_alias_for_class(self):
        alert = Alert(id="A3", klass="network")
        dumped = alert.model_dump(by_alias=True)
        self.assertIn("class", dumped)
        self.assertEqual(dumped["class"], "network")
        self.assertNotIn("klass", dumped)

    @patch("pagerduty_mcp.tools.alerts.paginate")
    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_list_alerts_basic(self, mock_get_client, mock_paginate):
        mock_paginate.return_value = [self.sample_alert_data]
        result = list_alerts("I123")
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], Alert)
        # Verify paginate called with correct endpoint
        call_args = mock_paginate.call_args
        self.assertIn("entity", call_args.kwargs)
        self.assertEqual(call_args.kwargs["entity"], "incidents/I123/alerts")

    @patch("pagerduty_mcp.tools.alerts.paginate")
    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_list_alerts_with_limit(self, mock_get_client, mock_paginate):
        mock_paginate.return_value = [self.sample_alert_data]
        _ = list_alerts("I999", limit=25)
        call_args = mock_paginate.call_args
        self.assertEqual(call_args.kwargs["entity"], "incidents/I999/alerts")
        self.assertEqual(call_args.kwargs["maximum_records"], 25)
        # Params should include limit only when provided
        self.assertEqual(call_args.kwargs["params"], {"limit": 25})


if __name__ == "__main__":
    unittest.main()
