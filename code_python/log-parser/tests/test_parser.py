import unittest
import os
import json
import tempfile
from datetime import datetime
from src.parser import parse_line, process_log_file
from src.models import LogEntry, LogSeverity

class TestLogParser(unittest.TestCase):

    def test_parse_valid_line(self):
        line = "[2023-10-27 10:00:01] {INFO} [AUTH_SERVICE] - U1001: LOGIN_SUCCESS | User logged in."
        entry, error = parse_line(line, 1)

        self.assertIsNone(error)
        self.assertIsNotNone(entry)
        self.assertIsInstance(entry, LogEntry)
        self.assertEqual(entry.timestamp, datetime(2023, 10, 27, 10, 0, 1))
        self.assertEqual(entry.severity, LogSeverity.INFO)
        self.assertEqual(entry.module, 'AUTH_SERVICE')
        self.assertEqual(entry.user_id, 'U1001')
        self.assertEqual(entry.action, 'LOGIN_SUCCESS')
        self.assertEqual(entry.message, 'User logged in.')

    def test_parse_invalid_timestamp(self):
        line = "[2023-10-27 10:00:99] {INFO} [MOD] - U1001: ACT | Msg"
        entry, error = parse_line(line, 1)
        self.assertIsNone(entry)
        self.assertIsNotNone(error)
        self.assertIn("Invalid timestamp", error.error_message)

    def test_parse_invalid_severity(self):
        line = "[2023-10-27 10:00:01] {WTF} [MOD] - U1001: ACT | Msg"
        entry, error = parse_line(line, 1)
        self.assertIsNone(entry)
        self.assertIsNotNone(error)
        self.assertIn("severity", error.error_message) # Pydantic enum error

    def test_parse_invalid_user_id(self):
        line = "[2023-10-27 10:00:01] {INFO} [MOD] - X100: ACT | Msg"
        entry, error = parse_line(line, 1)
        self.assertIsNone(entry)
        self.assertIsNotNone(error)
        self.assertIn("user_id", error.error_message)

    def test_malformed_line(self):
        line = "Just some random text"
        entry, error = parse_line(line, 1)
        self.assertIsNone(entry)
        self.assertIsNotNone(error)
        self.assertEqual(error.error_message, "Invalid log format")

    def test_process_logs_integration(self):
        # Create a temporary file with logs
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tf:
            tf.write("[2023-10-27 10:00:01] {INFO} [MOD] - U1001: ACT | Msg\n")
            tf.write("Invalid Line\n")
            temp_path = tf.name

        try:
            result = process_log_file(temp_path)

            self.assertEqual(result.metadata.total_processed, 2)
            self.assertEqual(result.metadata.valid_count, 1)
            self.assertEqual(result.metadata.invalid_count, 1)
            self.assertEqual(result.logs[0].message, "Msg")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
