import unittest
import parse_fix
from parse_fix import ParsedMsg

class TestFixValidator(unittest.TestCase):
    def test_empty_message(self):
        msg = ''
        self.assertEquals(
            ParsedMsg(-1, 'EMPTY MSG', {}, msg),
            parse_fix.parse_msg(msg)
        )

    def test_whitespace_message(self):
        msg = '  \t  '
        self.assertEquals(
            ParsedMsg(-1, 'EMPTY MSG', {}, msg),
            parse_fix.parse_msg(msg)
        )

    def test_no_duplicate_fields(self):
        msg = '8=FIX.4.2|9=0020|35=A|49=INCA|56=BATS|34=000000001|50=0028|57=PROD|108=30|10=084|'
        pmsg = parse_fix.parse_msg(msg)
        self.assertEquals(
            (0, 'GOOD'),
            (pmsg.parse_code, pmsg.parse_msg)
        )

    def test_duplicate_fields_parse(self):
        msg = '8=FIX.4.2|8=REPEATED|9=0020|35=A|49=INCA|56=BATS|34=000000001|50=0028|57=PROD|108=30|10=084|'
        pmsg = parse_fix.parse_msg(msg)
        self.assertEquals(
            (-2, f'DUPLICATE FIELD DETECTED: field_name=8'),
            (pmsg.parse_code, pmsg.parse_msg)
        )

    def test_duplicate_fields_report_empty_parsed_msgs(self):
        expected_output = [
            'NO DUPLICATE FIELDS MSGS DETECTED'
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_duplicate_fields_report([])
        )

    def test_duplicate_fields_report_no_errors(self):
        expected_output = [
            'NO DUPLICATE FIELDS MSGS DETECTED'
        ]
        parsed_msgs = [
            ParsedMsg(0, 'GOOD', {'8': 'FIX.4.2', '9': '0020'}, '8=FIX.4.2|9=0020'),
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_duplicate_fields_report(parsed_msgs)
        )

    def test_duplicate_fields_report_with_errors(self):
        orig_msg = '8=FIX.4.2|8=REPEATED'
        expected_output = [
            'DUPLICATE FIELDS MSGS REPORT:',
            f'DUPLICATE FIELD DETECTED: field_name=8, orig_msg={orig_msg}'
        ]
        parsed_msgs = [
            ParsedMsg(0, 'GOOD', {'8': 'FIX.4.2', '9': '0020'}, '8=FIX.4.2|9=0020'),
            ParsedMsg(-2, 'DUPLICATE FIELD DETECTED: field_name=8', {}, orig_msg)
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_duplicate_fields_report(parsed_msgs)
        )

    def test_high_low_prices_no_msgs(self):
        expected_output = [
            'NO NEW ORDER SINGLE MSGS FOUND'
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_high_low_new_order_single_prices([])
        )

    def test_high_low_prices_no_new_order_single_msgs(self):
        expected_output = [
            'NO NEW ORDER SINGLE MSGS FOUND'
        ]
        parsed_msgs = [
            ParsedMsg(0, 'GOOD', {'8': 'FIX.4.2', '9': '0020'}, '8=FIX.4.2|9=0020'),
            ParsedMsg(-2, 'DUPLICATE FIELD DETECTED: field_name=8', {}, '8=FIX.4.2|8=REPEATED')
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_high_low_new_order_single_prices(parsed_msgs)
        )

    def test_high_low_prices_one_order_only(self):
        expected_output = [
            'NEW ORDER SINGLE HIGH LOW PRICE REPORT:',
            'ACCOUNT=acct1, HIGH=100.0, LOW=100.0'
        ]
        parsed_msgs = [
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct1', '44': '100'}, '35=D|1=acct1|44=100')
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_high_low_new_order_single_prices(parsed_msgs)
        )

    def test_high_low_prices_two_accounts(self):
        expected_output = [
            'NEW ORDER SINGLE HIGH LOW PRICE REPORT:',
            'ACCOUNT=acct1, HIGH=100.0, LOW=91.1',
            'ACCOUNT=acct2, HIGH=101.5, LOW=98.6'
        ]
        parsed_msgs = [
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct1', '44': '100'}, '35=D|1=acct1|44=100'),
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct1', '44': '95'}, '35=D|1=acct1|44=95'),
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct1', '44': '91.1'}, '35=D|1=acct1|44=91.1'),
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct2', '44': '99.9'}, '35=D|1=acct1|44=99.9'),
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct2', '44': '98.6'}, '35=D|1=acct1|44=98.6'),
            ParsedMsg(0, 'GOOD', {'35': 'D', '1': 'acct2', '44': '101.5'}, '35=D|1=acct1|44=101.5')
        ]
        self.assertEquals(
            expected_output,
            parse_fix.get_high_low_new_order_single_prices(parsed_msgs)
        )