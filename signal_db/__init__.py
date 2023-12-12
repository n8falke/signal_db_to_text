'''Access to signal database.'''

import re
import sqlite3
import logging
from .msg_thread import MsgThread
from .recipient import Recipient, RecipientCache
from .msg_formatter import MsgFormatter


class SignalDb:

    def __init__(self, filename: str) -> None:
        self.con = sqlite3.connect(filename)
        self.recipient_cache = RecipientCache(self.con)

    def close(self) -> None:
        self.recipient_cache.close()
        self.con.close()

    def get_message_threads(self, exp_only=None, skip=None) -> None:
        exp_only_re = re.compile(exp_only) if exp_only else None
        skip_re = re.compile(skip) if skip else None

        cur: sqlite3.Cursor = self.con.cursor()
        logging.info("Counting messages")
        self.threads: list[MsgThread] = [MsgThread(row) for row in cur.execute(
            "SELECT t._id, t.recipient_id, COUNT(*) AS cnt,"
            "       SUM(m.from_recipient_id = 1) AS sent,"
            "       DATETIME(MIN(m.date_sent) / 1000, 'unixepoch') AS first_ts,"
            "       DATETIME(MAX(m.date_sent) / 1000, 'unixepoch') AS last_ts"
            "  FROM thread t"
            "  JOIN message m"
            "    ON m.thread_id = t._id"
            "   AND m.type IN ( 10485780, 10485783, 8388628 )"
            " GROUP BY t._id, t.date, t.recipient_id").fetchall()]

        logging.info("Getting user infos")
        recipients: dict[int, Recipient] = {}
        for thread in self.threads:
            thread.setRecipient(self.recipient_cache.get(thread.recipient_id),
                                exp_only_re, skip_re)

        cur.close()

    def print_stats(self) -> None:
        print("  Name                       | received | sent    | first msg           | last msg")
        print("-" * 93)
        for stat in self.threads:
            print(stat)

    def export(self, formatter: MsgFormatter, from_level, reversed: bool) -> None:
        cur: sqlite3.Cursor = self.con.cursor()
        for thread in self.threads:
            if thread.exp_level >= from_level:
                formatter.export_thread(thread,
                                        ((msg, self.recipient_cache.get(msg[2]))
                                         for msg in thread.select_messages(cur, reversed)))
        cur.close()
