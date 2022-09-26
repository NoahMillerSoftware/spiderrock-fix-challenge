# spiderrock-fix-challenge
```
usage: parse_fix.py [-h] file

Parse FIX messages

Read a file of pipe-delimeted FIX messages (one per line), and output two reports:
  - Duplicate Fields Report: list of messages with duplicated fields.
  - High Low Price Report: list high and low prices for "new order single" msgs, grouped by account

positional arguments:
  file        file containing pipe-delimited FIX messages (one per line)

optional arguments:
  -h, --help  show this help message and exit
```
