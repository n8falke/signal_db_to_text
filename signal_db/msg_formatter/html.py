"""Formatter for signal messages to md."""

import html
import io
import re
from . import MsgFormatter
from ..msg_thread import MsgThread
from ..recipient import Recipient


class MsgHtmlFormatter(MsgFormatter):
    ext: str = '.html'

    def header(self, fh: io.TextIOWrapper, thread: MsgThread) -> None:
        name: str = html.escape(thread.recipient.name)
        print(f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8" />
<title>{name}</title>
<style>
img {{ max-height: 30vh; max-width: 30vw; }}
table {{ border-spacing: 0; }}
td {{ border-top: 1px solid gray; vertical-align: top; }}
</style>
</head>
<body>
<h1>{thread.recipient.name}</h1>
<p>{thread.recipient.phone}</p>
<table>
<tr><th>Timestamp<th>From<th>Message</tr>""",
              file=fh)

    def close(self, fh, thread: MsgThread) -> None:
        print("</table></body></html>", file=fh)

    def message(self, fh: io.TextIOWrapper,
                msg: tuple[int, str, int, str, int, str],
                recipient: Recipient) -> None:
        body: str = re.sub(r'\r\n?|\n', '<br>', html.escape(msg[3]))
        print(f"<tr><td>{msg[1]}<td>{recipient.given_name}<td>{body}",
              file=fh)

    def attachment(self, fh: io.TextIOWrapper, url: str, type: str, first: bool,
                   msg: tuple[int, str, int, str, int, str],
                   recipient: Recipient) -> None:
        content: str = f'<img src="{url}">' if type in (
            'jpeg', 'png') else type
        html: str = f' <a href="{url}">{content}</a>'
        if first:
            print(
                f"<tr><td>{msg[1]}<td>{recipient.given_name}<td>{html}", file=fh)
        else:
            print(html, file=fh)
