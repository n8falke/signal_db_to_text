'''Store signal recipient information in Recipient
and get and cache entries from database in RecipientCache.'''

import re
import sqlite3


class Recipient:
    def __init__(self, row):
        self.phone: str
        self.given_name: str
        self.name: str
        self.group_id: int
        self.phone, self.given_name, self.name, self.group_id = row
        self.cleaned_name: str = re.sub(
            r'''[_ :#<>|*?"'/\\]+''', '_', self.name)


class RecipientCache:
    def __init__(self, con) -> None:
        self.cur: sqlite3.Cursor = con.cursor()
        self.recipients: dict[int, Recipient] = {}

    def get(self, recipient_id: int) -> Recipient:
        # recipient already looked up?
        if recipient_id in self.recipients:
            return self.recipients[recipient_id]
        recipient = Recipient(self.cur.execute(
            'SELECT e164,'
            '       COALESCE(system_given_name, profile_given_name) AS first,'
            '       COALESCE(system_joined_name, profile_joined_name, title) AS name,'
            '       g._id'
            '  FROM recipient r'
            '  LEFT JOIN groups g ON r.type = 3 AND g.recipient_id = r._id'
            ' WHERE r._id = ?', (recipient_id,)).fetchone())
        self.recipients[recipient_id] = recipient
        return recipient

    def close(self) -> None:
        self.cur.close()
