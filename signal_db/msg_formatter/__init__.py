"""Base class for signal message formatter."""

import io
import logging
from os import mkdir
from os.path import isdir, isfile
import shutil
from ..recipient import Recipient
from ..msg_thread import MsgThread

SPLIT_BY: dict[str, int] = {"year": 4, "month": 7, "day": 10}


class MsgFormatter:
    ext: str = '.???'  # extension set by child class

    def __init__(self, directory: str,
                 attachments_dir: str | None,
                 args) -> None:
        self.tgt_directory: str = directory
        self.max_msg_cnt: int | None = args.max
        self.split_by: int | None = SPLIT_BY[args.split] if args.split else None
        self.attachments_dir: str | None = attachments_dir
        self.tgt_attachments_dir: str | None = None
        self.curr_attachments_dir: str | None = None
        self.curr_attachments_url: str | None = None
        self.bom: bool = bool(args.bom)

    def header(self, fh: io.TextIOWrapper, thread: MsgThread) -> None:
        pass

    def close(self, fh: io.TextIOWrapper, thread: MsgThread) -> None:
        pass

    def message(self, fh: io.TextIOWrapper,
                msg: tuple[int, str, int, str, int, str],
                recipient: Recipient) -> None:
        pass

    def attachment(self, fh: io.TextIOWrapper, url: str, type: str, first: bool,
                   msg: tuple[int, str, int, str, int, str],
                   recipient: Recipient) -> None:
        pass

    def cp_attachment(self, msg, thread: MsgThread) -> tuple[str, str] | None:
        if not self.attachments_dir:
            return
        if not self.curr_attachments_dir:
            if not self.tgt_attachments_dir:
                self.tgt_attachments_dir = self.tgt_directory + 'attachments/'
                if not isdir(self.tgt_attachments_dir):
                    mkdir(self.tgt_attachments_dir)
            name: str = thread.recipient.cleaned_name
            self.curr_attachments_dir = self.tgt_attachments_dir + name + '/'
            self.curr_attachments_url = 'attachments/' + name + '/'
            if not isdir(self.curr_attachments_dir):
                mkdir(self.curr_attachments_dir)
        type: str = msg[5]  # mime type
        uid: str = str(msg[4])
        src: str = self.attachments_dir + uid + '.bin'
        if isfile(src):
            type = type[type.index('/') + 1:]
            file: str = uid + '.' + type
            tgt: str = self.curr_attachments_dir + file
            shutil.copy(src, tgt)
            return self.curr_attachments_url + file, type  # type: ignore
        logging.warning(f"Attachment {uid} of type {type} not found")
        return

    def export_thread(self, thread: MsgThread, cur) -> None:
        fh: io.TextIOWrapper | None = None
        lastId: int = 0
        lastTs: str = '0000-00'
        cnt: int = 0
        for msg, recipient in cur:
            ts: str = msg[1]
            # split into multiple files
            # if max messages reached (except do not split day)
            # or splitting by date
            if fh and (self.max_msg_cnt and cnt > self.max_msg_cnt and lastTs[:10] != ts[:10]
                       or self.split_by and lastTs[:self.split_by] != ts[:self.split_by]):
                self.close(fh, thread)
                fh.close()
                fh = None
                cnt = 0
            if not fh:
                filename: str = thread.recipient.cleaned_name + \
                    '_' + ts[:10] + self.__class__.ext
                # open file
                logging.info("Exporting into " + filename)
                fh = open(self.tgt_directory + filename, 'w', encoding="utf-8")
                if self.bom:
                    fh.write('\ufeff')
                self.header(fh, thread)
            if msg[3] and msg[0] != lastId:
                self.message(fh, msg, recipient)
            # attachment?
            if msg[4]:
                if attachment := self.cp_attachment(msg, thread):
                    self.attachment(fh, *attachment,
                                    msg[0] == lastId and msg[3],  # first?
                                    msg, recipient)
            lastId = msg[0]
            lastTs = ts
            cnt += 1
        # finished export
        if fh:
            self.close(fh, thread)  # allow formatter to write footer if needed
            fh.close()
