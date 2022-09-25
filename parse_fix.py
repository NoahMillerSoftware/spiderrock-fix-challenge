import sys
import argparse
from collections import namedtuple

ParsedMsg = namedtuple('ParsedMsg', 'parse_code parse_msg field_dict orig_msg')


def parse_msg(msg: str):
    orig_msg = msg

    # trim leading and trailing whitespace
    msg = msg.strip()

    if msg == '':
        return ParsedMsg(-1, 'EMPTY MSG', {}, orig_msg)

    # split tag=value pairs by delimeter '|'
    fields = msg.split('|')
    # discard empty strings in fields list
    fields = [f for f in fields if f]

    # read fields into dictionary
    field_dict = {}
    for f in fields:
        tag, value = f.split('=', 1)

        # if field_name already exists, it's a duplicate field
        if tag in field_dict:
            return ParsedMsg(-2, f'DUPLICATE FIELD DETECTED: field_name={tag}', {}, orig_msg)

        field_dict[tag] = value

    return ParsedMsg(0, 'GOOD', field_dict, orig_msg)


def get_duplicate_fields_report(parsed_msgs):
    report_lines = []
    duplicate_fields_msgs = [p for p in parsed_msgs if p.parse_code == -2]
    if not duplicate_fields_msgs:
        report_lines.append('NO DUPLICATE FIELDS MSGS DETECTED')
        return report_lines

    report_lines.append('DUPLICATE FIELDS MSGS REPORT:')
    for m in duplicate_fields_msgs:
        report_lines.append(f'{m.parse_msg}, orig_msg={m.orig_msg}')

    return report_lines


def get_high_low_new_order_single_prices(parsed_msgs):
    report_lines = []
    new_order_single_msgs = [
        p for p in parsed_msgs
        if p.field_dict.get('35')=='D'
    ]

    if not new_order_single_msgs:
        report_lines.append('NO NEW ORDER SINGLE MSGS FOUND')
        return report_lines

    report_lines.append('NEW ORDER SINGLE HIGH LOW PRICE REPORT:')
    # group by account (field 1)
    high_low_by_account = {}
    for o in new_order_single_msgs:
        acct = o.field_dict['1']
        px = float(o.field_dict['44'])
        if acct not in high_low_by_account:
            high_low_by_account[acct] = {
                'high': float('-inf'),
                'low': float('inf')
            }
        high_low_by_account[acct]['high'] = max(
            high_low_by_account[acct]['high'],
            px
        )
        high_low_by_account[acct]['low'] = min(
            high_low_by_account[acct]['low'],
            px
        )

    for k, v in high_low_by_account.items():
        report_lines.append(f"ACCOUNT={k}, HIGH={v['high']}, LOW={v['low']}")

    return report_lines


def main(args):
    with open(args.file) as f:
        # get lines without trailing \n
        msgs = f.read().splitlines()

    parsed_msgs = []
    for m in msgs:
        parsed_msgs.append(parse_msg(m))

    # Print duplicate field report
    for l in get_duplicate_fields_report(parsed_msgs): print(l)
    
    # Print high/low pxs of New Order Singles by Account
    for l in get_high_low_new_order_single_prices(parsed_msgs): print(l)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate FIX messages')
    parser.add_argument('file', help='file containing FIX messages (one per line)')
    args = parser.parse_args()
    sys.exit(main(args))