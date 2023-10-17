import unittest
from pysyslog_server.validator import Validator


class TestValidator(unittest.TestCase):

    def test_valid_message(self):
        syntax = "<100>Jan 10 00:00:00 myapphost MyApp: Something went wrong!"
        date = "<100>Dec  1 16:21:59 myapphost MyApp: User 'myuser' locked out for invalid credentials!"

        syntax_validator = Validator(syntax, "192.168.0.10")
        date_validator = Validator(date, "192.168.0.10")

        self.assertEqual(syntax_validator.validate_message(), syntax)
        self.assertEqual(date_validator.validate_message(), date)

    
    def test_invalid_timestamp(self):
        # can't reliably compare time since timestamp is inserted
        invalid_month = "<100>July 10 01:02:03 localhost hello:world" 
        invalid_day = "<100>Jul 01 01:02:03 localhost hello:world"
        invalid_time = "<100>Jul 01 01:02:03 localhost hello:world"

        invalid_month_validator = Validator(invalid_month, "localhost")
        invalid_day_validator = Validator(invalid_day, "localhost")
        invalid_time_validator = Validator(invalid_time, "localhost")

        self.assertNotEqual(invalid_month_validator.validate_message(), invalid_month)
        self.assertNotEqual(invalid_day_validator.validate_message(), invalid_day)
        self.assertNotEqual(invalid_time_validator.validate_message(), invalid_time)


    def test_invalid_priority(self):
        too_large = "<192>Jan 10 01:02:03 localhost hello:world"
        too_many_chars = "<191p>Jan 10 01:02:03 localhost hello:world"
        leading_zero = "<00>Jan 10 01:02:03 localhost hello:world"
        too_many_angle_brackets1 = "<9>>>Jan 10 01:02:03 localhost hello:world"
        too_many_angle_brackets2 = "<9>>Jan 10 01:02:03 localhost hello:world"
        contains_special_chars = "<9!>Jan 10 01:02:03 localhost hello:world"

        too_large_validator = Validator(too_large, "127.0.0.1")
        too_many_chars_validator = Validator(too_many_chars, "127.0.0.1")
        leading_zero_validator = Validator(leading_zero, "127.0.0.1")
        too_many_angle_brackets_validator1 = Validator(too_many_angle_brackets1, "127.0.0.1")
        too_many_angle_brackets_validator2 = Validator(too_many_angle_brackets2, "127.0.0.1")
        contains_special_chars_validator = Validator(contains_special_chars, "127.0.0.1")

        self.assertNotEqual(too_large_validator.validate_message(), too_large)
        self.assertNotEqual(too_many_chars_validator.validate_message(), too_many_chars)
        self.assertNotEqual(leading_zero_validator.validate_message(), leading_zero)
        self.assertNotEqual(too_many_angle_brackets_validator1.validate_message(), too_many_angle_brackets1)
        self.assertNotEqual(too_many_angle_brackets_validator2.validate_message(), too_many_angle_brackets2)
        self.assertNotEqual(contains_special_chars_validator.validate_message(), contains_special_chars)