import shutil
import unittest

from test_setup import client, TestingSessionLocal
from models import Eventlog


class TestEventLogUpload(unittest.TestCase):

    def setUp(self) -> None:
        # Clear the database before each test
        self.db = TestingSessionLocal()
        self.db.query(Eventlog).delete()
        self.db.commit()

    def setup_log(self):
        shutil.copy("resources/simple-log.xes", "uploads/simple-log.xes")

        # Insert fake event log
        self.event_log = Eventlog(
            name="Fake Log",
            path="simple-log.xes",
            case_id="case:concept:name",
            activity="concept:name",
            timestamp="time:timestamp",
            entry_count=100,
            column_count=5,
        )
        self.db.add(self.event_log)
        self.db.commit()
        self.db.refresh(self.event_log)

    def test_can_delete_event_log(self):
        self.setup_log()
        event_log_id = self.event_log.id
        response = client.delete(f"/api/delete-event-log/{event_log_id}")
        self.assertEqual(response.status_code, 200)
        missing_log = self.db.query(Eventlog).filter_by(id=self.event_log.id).first()
        self.assertIsNone(missing_log)

    def test_get_event_logs(self):
        log_count = 5
        for _ in range(log_count):
            self.setup_log()

        response = client.get("/api/event-logs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), log_count)
        for _ in range(log_count):
            self.assertIn("id", data[0])
