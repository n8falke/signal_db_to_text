"""Formatter for signal messages to md."""

import io
import re
import sqlite3

from . import MsgFormatter
from ..msg_thread import MsgThread
from ..recipient import Recipient


class MsgMdFormatter(MsgFormatter):
    ext: str = '.md'

    def header(self, fh: io.TextIOWrapper, thread: MsgThread) -> None:
        print("# " + thread.recipient.name, file=fh)
        print(thread.recipient.phone, file=fh)
        print(file=fh)
        print("| Timestamp | From | Message", file=fh)
        print("|-----------|------|---------|", file=fh)

    def message(self, fh: io.TextIOWrapper,
                msg: tuple[int, str, int, str, int, str],
                recipient: Recipient) -> None:
        rows: list[str] = re.split(r'\r\n?|\n', msg[3])
        print(f"| {msg[1]} | {recipient.given_name} | {rows[0]} |", file=fh)
        for row in rows[1:]:
            if row:
                print(f"|  |  | {row} |", file=fh)

    def attachment(self, fh: io.TextIOWrapper, url: str, type: str, first: bool,
                   msg: tuple[int, str, int, str, int, str],
                   recipient: Recipient) -> None:
        inline = '!' if type in ('jpeg', 'png') else ''
        if first:
            print(f"| {msg[1]} | {recipient.given_name} | {inline}[{type}]({url}) |",
                  file=fh)
        else:
            print(f"|  |  | {inline}[{type}]({url}) |", file=fh)
