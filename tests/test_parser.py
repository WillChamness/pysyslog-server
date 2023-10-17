import unittest
from pysyslog_server.parser import Parser


class TestCollector(unittest.TestCase):
    # parser assumes validation/correction
    
    def test_parsing(self):
        parser = Parser(f"<{8*16+4}>Jan 10 01:02:03 localhost hello: world")
        expected_output = {
            "facility": 16,
            "severity": 4,
            "date": "Jan 10",
            "time": "01:02:03",
            "hostname": "localhost",
            "tag": "hello:",
            "content": " world"
        }

        self.assertEqual(parser.parse(), expected_output) 


    def test_day_less_than_10(self):
        parser = Parser(f"<{8*16+4}>Jan  1 01:02:03 localhost hello: world")  
        expected_output = {
            "facility": 16,
            "severity": 4,
            "date": "Jan  1",
            "time": "01:02:03",
            "hostname": "localhost",
            "tag": "hello:",
            "content": " world"
        }
        self.assertEqual(parser.parse(), expected_output) 

        parser = Parser(f"<{8*16+4}>Jan  9 01:02:03 localhost hello: world")  
        expected_output = {
            "facility": 16,
            "severity": 4,
            "date": "Jan  9",
            "time": "01:02:03",
            "hostname": "localhost",
            "tag": "hello:",
            "content": " world"
        }
        self.assertEqual(parser.parse(), expected_output) 

    
    def test_bad_hostname(self):
        parser = Parser(f"<{8*16+4}>Jan 11 01:02:03 myinstance.example.com hello: world")  
        expected_output = {
            "facility": 16,
            "severity": 4,
            "date": "Jan 11",
            "time": "01:02:03",
            "hostname": "myinstance.example.com",
            "tag": "hello:",
            "content": " world"
        }

        self.assertEqual(parser.parse(), expected_output) 


    def test_bad_msg(self):
        parser = Parser(f"<{8*16+4}>Jan 11 01:02:03 localhost [hello]: world")  
        expected_output = {
            "facility": 16,
            "severity": 4,
            "date": "Jan 11",
            "time": "01:02:03",
            "hostname": "localhost",
            "tag": "[",
            "content": "hello]: world"
        }

        self.assertEqual(parser.parse(), expected_output) 


    def test_tag_and_content_not_separated(self):
        parser = Parser(f"<{8*16+4}>Jan  1 01:02:03 localhost hello[world]")  
        expected_output = {
            "facility": 16,
            "severity": 4,
            "date": "Jan  1",
            "time": "01:02:03",
            "hostname": "localhost",
            "tag": "hello[",
            "content": "world]"
        }

        self.assertEqual(parser.parse(), expected_output) 


    def test_message_corrected(self):
        parser = Parser(f"<{13}>Jan 11 01:02:03 127.0.0.1 <00>Jan 11 01:02:00 localhost hello:world")  
        expected_output = {
            "facility": 13//8,
            "severity": 13%8,
            "date": "Jan 11",
            "time": "01:02:03",
            "hostname": "127.0.0.1",
            "tag": "<",
            "content": "00>Jan 11 01:02:00 localhost hello:world"
        }

        self.assertEqual(parser.parse(), expected_output) 