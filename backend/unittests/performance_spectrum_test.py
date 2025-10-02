import unittest
from datetime import datetime
import shutil

from models import Eventlog
from test_setup import TestingSessionLocal, client


class TestMinedDataEndpoint(unittest.TestCase):
    def setUp(self):
        # Clear DB and add a valid event log
        self.db = TestingSessionLocal()
        self.db.query(Eventlog).delete()
        self.db.commit()

        shutil.copy("resources/advanced-log.xes", "uploads/advanced-log.xes")

        self.event_log = Eventlog(
            name="Test Log",
            path="advanced-log.xes",
            case_id="case:concept:name",
            activity="concept:name",
            timestamp="time:timestamp",
            entry_count=100,
            column_count=5,
        )
        self.db.add(self.event_log)
        self.db.commit()
        self.db.refresh(self.event_log)

    def tearDown(self):
        self.db.query(Eventlog).delete()
        self.db.commit()

    def test_sanity_check(self):
        filters = {
            "global_filters": {},
            "spectra": [
                {
                    "on": 0,
                    "batches": {
                        "batchType": "typeA",
                        "epsilon": 0.5,
                        "minSamples": 2
                    },
                    "quartile": 0.75
                }
            ]
        }

        response = client.post(
            f"/api/event-log/{self.event_log.id}/mined-data",
            json=filters
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['event_log']['id'], self.event_log.id)
        self.assertIn("column_count", data['event_log'])
        self.assertIn("entry_count", data['event_log'])

    def test_event_log_not_found(self):
        filters = {"global_filters": {}, "spectra": []}
        response = client.post("/api/mined-data/999999", json=filters)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_quartile_filter_advanced(self):
        def test_quartile(expected_length, spectra, variant=None):
            filters = {
                "global_filters": {
                    "variant": variant
                },
                "spectra": [
                    {
                        "on": spectrum['id'],
                        "quartile": spectrum['quartile']
                    } for spectrum in spectra
                ]
            }

            response = client.post(
                f"/api/event-log/{self.event_log.id}/mined-data",
                json=filters
            )

            data = response.json()['spectra'][0]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['records']), expected_length)
            self.assertEqual(data['empty'], expected_length == 0)
            if variant is not None:
                self.assertEqual(len(response.json()['spectra']), len(variant) - 1)

        test_quartile(3, [{'id': 0, 'quartile': 1}])
        test_quartile(2, [{'id': 0, 'quartile': 0.75}])
        test_quartile(1, [{'id': 0, 'quartile': 0.5}])
        test_quartile(3, [{'id': 0, 'quartile': 0.25}])

        test_quartile(
            1,
            [{'id': 0, 'quartile': 0.25}],
            variant=['Create Fine', 'Send Fine', 'Insert Fine Notification']
        )

        test_quartile(
            1,
            [{'id': 1, 'quartile': 0.5}],
            variant=['Create Fine', 'Send Fine', 'Insert Fine Notification']
        )

    def test_batch_advanced(self):
        def filter_batch(expected_length, spectra, variant=None):
            filters = {
                "global_filters": {
                    "variant": variant
                },
                "spectra": [
                    {
                        "on": spectrum['id'],
                        "batches": {
                            "batchType": spectrum['batchType'],
                            "epsilon": spectrum['epsilon'],
                            "minSamples": spectrum['minSamples']
                        }
                    } for spectrum in spectra
                ]
            }

            response = client.post(
                f"/api/event-log/{self.event_log.id}/mined-data",
                json=filters
            )

            data = response.json()['spectra'][0]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['records']), expected_length)
            if variant is not None:
                self.assertEqual(len(response.json()['spectra']), len(variant) - 1)

        filter_batch(7, [{'id': 0, 'batchType': 'start', 'epsilon': 0.5, 'minSamples': 2}])
        filter_batch(5, [{'id': 0, 'batchType': 'end', 'epsilon': 0.5, 'minSamples': 2}])
        filter_batch(2, [{'id': 0, 'batchType': 'both', 'epsilon': 0.5, 'minSamples': 2}])

        filter_batch(3, [{'id': 0, 'batchType': 'start', 'epsilon': 0.5, 'minSamples': 3}])
        filter_batch(3, [{'id': 0, 'batchType': 'start', 'epsilon': 10, 'minSamples': 3}])

        filter_batch(8,
                     [{'id': 1, 'batchType': 'start', 'epsilon': 2, 'minSamples': 8}],
                     variant=['Create Fine', 'Send Fine', 'Insert Fine Notification']
                     )

        filter_batch(6,
                     [{'id': 2, 'batchType': 'both', 'epsilon': 10, 'minSamples': 2}],
                     variant=['Create Fine', 'Send Fine', 'Insert Fine Notification', 'Add penalty', 'Payment']
                     )

    def test_time_filter_advanced(self):
        def filter_time(start, end, expected_length):
            filters = {
                "global_filters": {
                    "time": {
                        "time_start": start.isoformat(),
                        "time_end": end.isoformat()
                    }
                },
                "spectra": []
            }

            response = client.post(
                f"/api/event-log/{self.event_log.id}/mined-data",
                json=filters
            )

            data = response.json()['spectra'][0]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['records']), expected_length)

        start_time = datetime(2008, 6, 23, 0, 0)
        end_time = datetime(2008, 8, 31, 23, 59)

        filter_time(start_time, end_time, 10)

        start_time = datetime(2008, 6, 23, 0, 0)
        end_time = datetime(2008, 8, 1, 23, 59)
        filter_time(start_time, end_time, 3)

        start_time = datetime(2008, 6, 23, 0, 0)
        end_time = datetime(2008, 7, 30, 23, 59)
        filter_time(start_time, end_time, 0)

    def test_case_filter_advanced(self):
        def filter_cases(cases, expected_length):
            filters = {
                "global_filters": {
                    "cases": cases
                },
                "spectra": []
            }

            response = client.post(
                f"/api/event-log/{self.event_log.id}/mined-data",
                json=filters
            )

            data = response.json()['spectra'][0]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['records']), expected_length)

        filter_cases(['A33939', 'S126661'], 2)
        filter_cases(['A33939', 'S126661', 'A34131'], 3)
        filter_cases([], 10)

    def test_variant_filter(self):
        def filter_variant(variant, expected_length, variants_count):
            filters = {
                "global_filters": {
                    "variant": variant
                },
                "spectra": []
            }

            response = client.post(
                f"/api/event-log/{self.event_log.id}/mined-data",
                json=filters
            )

            data = response.json()['spectra'][0]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['records']), expected_length)
            self.assertEqual(data['statistics']['traces_count'], variants_count)
            self.assertEqual(len(response.json()['spectra']), len(variant) - 1)

        filter_variant(
            ['Create Fine', 'Send Fine', 'Insert Fine Notification', 'Add penalty', 'Payment'],
            8,
            variants_count=2  # We expect the same variant and the variant with 'Payment' appended
        )

        filter_variant(
            ['Create Fine', 'Send Fine', 'Insert Fine Notification', 'Add penalty', 'Payment', 'Payment'],
            1,
            variants_count=1
        )

    def test_segment_filter_advanced(self):
        def filter_segment(start_activity, end_activity, expected_length):
            filters = {
                "global_filters": {
                    "activities": {
                        'start_activity': start_activity,
                        'end_activity': end_activity
                    }
                },
                "spectra": []
            }

            response = client.post(
                f"/api/event-log/{self.event_log.id}/mined-data",
                json=filters
            )

            data = response.json()['spectra'][0]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['records']), expected_length)

        filter_segment('Create Fine', 'Send Fine', 10)
        filter_segment('Send Fine', 'Insert Fine Notification', 8)
        filter_segment('Send Fine', 'Payment', 1)
        filter_segment('Add penalty', 'Payment', 8)

    def test_basic_statistics(self):
        filters = {
            "global_filters": {},
            "spectra": []
        }

        response = client.post(
            f"/api/event-log/{self.event_log.id}/mined-data",
            json=filters
        )

        data = response.json()['spectra'][0]

        expected_histogram_counts = [
            1, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1
            , 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1
        ]

        self.assertEqual(data['statistics']['histogram']['counts'], expected_histogram_counts)

        expected_frequency_diagram_counts = [
            3, 1, 2, 0, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

        expected_frequency_end_diagram_counts = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1
        ]

        self.assertEqual(data['statistics']['frequency_end_diagram']['counts'], expected_frequency_end_diagram_counts)

        self.assertEqual(data['statistics']['case_count'], 10)
        self.assertEqual(data['statistics']['activities'], [
            "Create Fine",
            "Send Fine",
            "Insert Fine Notification",
            "Add penalty",
            "Payment",
            "Insert Date Appeal to Prefecture",
            "Send Appeal to Prefecture"
        ])

        self.assertEqual(len(data['statistics']['traces']), 4)
        self.assertEqual(data['statistics']['traces_count'], 4)
        self.assertEqual(data['statistics']['batches'], None)

        expected_metadata = {
            "min_timestamp": 1217548800.0,
            "max_timestamp": 1233792000.0,
            "quartiles": {
                "0.25": 12528000.0,
                "0.5": 14126400.0,
                "0.75": 15422400.0
            },
            "mean": 14057280.0,
            "variance": 2127588249600.0
        }

        self.assertEqual(data['metadata'], expected_metadata)