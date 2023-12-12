#!env python

import argparse
from os.path import isdir, isfile, dirname
import sys
from typing import NoReturn
import logging
from signal_db import SignalDb
from signal_db.msg_formatter import MsgFormatter


def die(msg) -> NoReturn:
    print(msg)
    sys.exit(1)


parser = argparse.ArgumentParser(
    prog='signal_db_to_md',
    description='Convert signal db from backup to md/csv/html-file')

parser.add_argument('db_file', help="Signal sqlite db")
parser.add_argument('out', help="Output directory", nargs='?')
parser.add_argument('--max', type=int,
                    help="Maximum number of messages in a file")
parser.add_argument('--split',
                    help="Split conversation files by month/year/day")
parser.add_argument('--log', help="Set log level", default="info")
parser.add_argument('--only', help="Export only matching regex")
parser.add_argument('--skip', help="Do not export matching regex")
parser.add_argument('-f', '--format',
                    help="Output as md/csv/html", default='html')
parser.add_argument('--attachments', help="Directory with attachments from backup",
                    default="attachments")
parser.add_argument('-r', '--reversed', help="Start with last message",
                    action=argparse.BooleanOptionalAction)
parser.add_argument('--bom', help="Write bom into file",
                    action=argparse.BooleanOptionalAction)

args = parser.parse_args()

logging.basicConfig(level=args.log.upper())

# check parameter
splitBy: str = args.split
if splitBy is not None and splitBy not in ('month', 'year', 'day'):
    die("Please provide month or year as --split option")

db_file = args.db_file
if not isfile(db_file):
    die("Could not find sqlite file " + db_file)

formatter: MsgFormatter | None = None
outDir = args.out
if outDir:
    if not isdir(outDir):
        die(f"Please create directory {outDir} first")
    # prepare outdir for concatenation
    if outDir[-1] != '/' and outDir[-1] != '\\':
        outDir += '/'
    attachmentDir = args.attachments
    if attachmentDir:
        if attachmentDir[-1] != '/' and attachmentDir[-1] != '\\':
            attachmentDir += '/'
        attachmentDir: str = dirname(db_file) + '/' + attachmentDir
        if not isdir(attachmentDir):
            die(f'Attachments dir not found in {attachmentDir} use '
                '--attachments "" to disable attachments')

    match args.format:
        case 'html':
            from signal_db.msg_formatter.html import MsgHtmlFormatter
            formatter = MsgHtmlFormatter(outDir, attachmentDir, args)
        case 'md':
            from signal_db.msg_formatter.md import MsgMdFormatter
            formatter = MsgMdFormatter(outDir, attachmentDir, args)
        case 'csv':
            from signal_db.msg_formatter.csv import MsgCsvFormatter
            formatter = MsgCsvFormatter(outDir, attachmentDir, args)
        case _:
            die("Pleas use md/csv/html as --format")

# main
db = SignalDb(db_file)
db.get_message_threads(args.only, args.skip)
db.print_stats()
if formatter:
    db.export(formatter, 2 if args.only else 1, bool(args.reversed))
db.close()
