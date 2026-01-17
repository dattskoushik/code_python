import unittest
import os
import json
import tempfile
from parser import parse_line, process_logs

class TestLogParser(unittest.TestCase):

    def test_parse_valid_line(self):
        line = "[2023-10-27 10:00:01] {INFO} [AUTH_SERVICE] - U1001: LOGIN_SUCCESS | User logged in."
        result = parse_line(line, 1)
        self.assertTrue(result['valid'])
        self.assertEqual(result['timestamp'], '2023-10-27T10:00:01')
        self.assertEqual(result['severity'], 'INFO')
        self.assertEqual(result['module'], 'AUTH_SERVICE')
        self.assertEqual(result['user_id'], 'U1001')
        self.assertEqual(result['action'], 'LOGIN_SUCCESS')
        self.assertEqual(result['message'], 'User logged in.')

    def test_parse_invalid_timestamp(self):
        line = "[2023-10-27 10:00:99] {INFO} [MOD] - U1: ACT | Msg"
        result = parse_line(line, 1)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid timestamp", result['error'])

    def test_parse_invalid_severity(self):
        line = "[2023-10-27 10:00:01] {WTF} [MOD] - U1: ACT | Msg"
        result = parse_line(line, 1)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid severity", result['error'])

    def test_parse_invalid_user_id(self):
        line = "[2023-10-27 10:00:01] {INFO} [MOD] - X100: ACT | Msg"
        result = parse_line(line, 1)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid User ID format", result['error'])

    def test_malformed_line(self):
        line = "Just some random text"
        result = parse_line(line, 1)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid format", result['error'])

    def test_process_logs_integration(self):
        # Create a temporary file with logs
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tf:
            tf.write("[2023-10-27 10:00:01] {INFO} [MOD] - U1: ACT | Msg\n")
            tf.write("Invalid Line\n")
            temp_path = tf.name

        output_path = temp_path + ".json"

        try:
            process_logs(temp_path, output_path, quiet=True)

            with open(output_path, 'r') as f:
                data = json.load(f)

            self.assertEqual(data['metadata']['total_processed'], 2)
            self.assertEqual(data['metadata']['valid_count'], 1)
            self.assertEqual(data['metadata']['invalid_count'], 1)
            self.assertEqual(data['logs'][0]['message'], "Msg")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(output_path):
                os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
