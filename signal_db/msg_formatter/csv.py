"""Formatter for signal messages to csv."""

import io
import re

from . import MsgFormatter
from ..msg_thread import MsgThread
from ..recipient import Recipient


class MsgCsvFormatter(MsgFormatter):
    ext: str = '.csv'

    def header(self, fh: io.TextIOWrapper, thread: MsgThread) -> None:
        print("Timestamp;From;Message", file=fh)

    def message(self, fh: io.TextIOWrapper,
                msg: tuple[int, str, int, str, int, str],
                recipient: Recipient) -> None:
        # in lines use CR only
        (body, cnt_breaks) = re.subn(r'\r\n?|\n', '\r', msg[3])
        if body[0] == '"' or cnt_breaks > 0 or ';' in body:
            body = '"' + body.replace('"', '""') + '"'
        print(f"{msg[1]};{recipient.given_name};{body}", file=fh)

    def attachment(self, fh: io.TextIOWrapper, url: str, type: str, first: bool,
                   msg: tuple[int, str, int, str, int, str],
                   recipient: Recipient) -> None:
        if first:
            print(f"{msg[1]};{recipient.given_name};{type}: file://{url}",
                  file=fh)
        else:
            print(f";;{type}: file://{url}", file=fh)
