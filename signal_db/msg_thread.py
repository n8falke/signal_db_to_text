'''Store thread information.'''

import re
from sqlite3 import Timestamp
import sqlite3
from .recipient import Recipient

L_SKIP = 0
L_STD = 1
L_ONLY = 2
INDICATOR = ('-', ' ', '*')


class MsgThread:
    def __init__(self, row) -> None:
        self.exp_level: int = L_STD
        self.id: int
        self.recipient_id: int
        self.cnt: int
        self.cnt_sent: int
        self.first_ts: Timestamp
        self.last_ts: Timestamp
        self.id, self.recipient_id, self.cnt, self.cnt_sent, self.first_ts, self.last_ts = row

    def setRecipient(self, recipient: Recipient,
                     exp_only_re: re.Pattern | None,
                     skip_re: re.Pattern | None) -> None:
        self.recipient: Recipient = recipient
        if exp_only_re and exp_only_re.search(recipient.name):
            self.exp_level = L_ONLY
        if skip_re and skip_re.search(recipient.name):
            self.exp_level = L_SKIP

    def __str__(self):
        return (f"{INDICATOR[self.exp_level]} {self.recipient.name or str(id):27}"
                f"|{self.cnt - self.cnt_sent:-9} |{self.cnt_sent:-8} "
                f"| {self.first_ts} | {self.last_ts}")

    def select_messages(self, cur: sqlite3.Cursor, reversed: bool) -> sqlite3.Cursor:
        # limit messages to in/out and from signal
        # see https://github.com/signalapp/Signal-Android/blob/main/app/src/main/java/org/thoughtcrime/securesms/database/MessageTypes.java
        return cur.execute(
            """SELECT m._id,
                       DATETIME(m.date_sent / 1000, 'unixepoch') AS Zeitpunkt,
                       from_recipient_id,
                       m.body,
                       p.unique_id, p.ct
                  FROM message m
                  LEFT JOIN part p ON p.mid = m._id
                 WHERE thread_id = ?
                   AND type IN ( 10485780, 10485783, 8388628 )
                 ORDER BY m.date_sent""" + (" DESC" if reversed else ""),
            (self.id,))
