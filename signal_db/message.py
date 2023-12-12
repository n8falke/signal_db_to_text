"""Hold message information.

Currently unuse. Instead tuple is directly used."""

from signal_db.recipient import Recipient


class Message:
    def __init__(self, msg: tuple[int, str, int, str, int, str], recipient: Recipient) -> None:
        self.id: int
        self.timestamp: str
        self.recipient_id: int
        self.body: str
        self.attachment_id: int
        self.attachment_type: str
        self.id, self.timestamp, self.recipient_id, self.body, self.attachment_id, self.attachment_type = msg
        self.recipient: Recipient = recipient
