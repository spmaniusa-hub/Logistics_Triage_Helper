import unittest
from intake import Complaint, normalize_text, can_auto_route, build_record

class TestIntake(unittest.TestCase):
    def test_normalize_text(self):
        raw = "  Parcel   arrived    late\n  and damaged. \t "
        self.assertEqual(normalize_text(raw), "Parcel arrived late and damaged.")

    def test_can_auto_route_standard_eligible(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "Shipment delayed by two days.",
            "needs_human": False
        }
        self.assertTrue(can_auto_route(triage))

    def test_can_auto_route_bug_ticket_reproduction(self):
        """Requirement 5: Any record with needs_human=true must have auto_route=false"""
        triage = {
            "category": "damaged",
            "priority": "P1",
            "summary": "Screen cracked on monitor.",
            "needs_human": True
        }
        # THIS SHOULD FAIL ON UNFIXED CODE
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_missing_key(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "Delayed"
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_extra_key(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "Delayed",
            "needs_human": False,
            "extra_field": "unexpected"
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_invalid_category(self):
        triage = {
            "category": "lost_forever",
            "priority": "P2",
            "summary": "Item lost",
            "needs_human": False
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_invalid_priority(self):
        triage = {
            "category": "delay",
            "priority": "URGENT",
            "summary": "Delayed",
            "needs_human": False
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_empty_summary(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "",
            "needs_human": False
        }
        self.assertFalse(can_auto_route(triage))

    def test_build_record_integration(self):
        c = Complaint(complaint_id="NGL-002", text="The monitor box was crushed.")
        triage = {
            "category": "damaged",
            "priority": "P1",
            "summary": "Monitor crushed.",
            "needs_human": True
        }
        rec = build_record(c, triage)
        self.assertEqual(rec["complaint_id"], "NGL-002")
        self.assertEqual(rec["original_text"], "The monitor box was crushed.")
        self.assertEqual(rec["category"], "damaged")
        self.assertEqual(rec["priority"], "P1")
        self.assertTrue(rec["needs_human"])
        self.assertFalse(rec["auto_route"])

if __name__ == "__main__":
    unittest.main()
