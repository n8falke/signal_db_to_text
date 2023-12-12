# Make signal messenger database from backup readable

Just a personal project to make old messages available after change to Apple
iPhone. It is not possible to migrate Signal conversations from Android to iOS.

Python 3.10 required.

Use https://github.com/mossblaser/signal_for_android_decryption to decrypt
signal backup into a folder.

Use this script to make database and attachments viewable.

Example usage:
```bash
git clone https://github.com/n8falke/signal_db_to_text.git
cd signal_db_to_text
# first check content
python signal_db_to_text.py ../decrypted_backup/database.sqlite
mkdir ../out # target directory for "text"-files
python signal_db_to_text.py ../decrypted_backup/database.sqlite ../out
```


## Select conversions to export

With (python) [regular expressions](https://docs.python.org/3/library/re.html)
you can limit conversations to export.
Without specifying the output directory you can preview the message selection.

With i.e. `--skip "Name|Other|Signal"` you can exclude all full names matching
the expression case sensitive. Use quotes with `|` or ` `.
Matches are marked with `-` in message overview.

With i.e. `--only Familyname` you can limit the exports to only matches.
Matches are marked with `*` in message overview.

Combine `--skip` to exclude from `--only` matches.


## Output formats and limit file size

Supported `--format`s are:
- html (default)
- md i.e. for Nextcloud (gets slow on longer conversations and no images in app)
- csv `;`-separated utf-8 file (use `--bom` on Windows) attachments only as link

For each conversation a file (or more with `--max` and/or `--split`) is written
with full name of contact and start (or end of conversation with --reversed).

When attachments are in the conversation, they are copied into a folder
`attachments/contact_name` in the output directory.
Disable attachments with `--attachments ""`.

With i.e. `--max 100` limits the messages in one file. After 100 messages a new
file will be created after finishing the current day. So one day is not borken
into more than one file.

The option `--split year` creates a new file each year.

Both options can be combined.


### Specifics to md

Becaus nextcloud does not support line breaks insiede a table cell,
one message is broken into multiple rows on line breaks.
This lines do not have an extra timestamp and contact name.


## Options overview

| Option               | Description
|----------------------|-------------------------------------------
| --max _MAX_          | Maximum number of messages in a file
| --split _SPLIT_      | Split conversation files by month/year/day
| --log _LEVEL_        | Set log level
| --only _ONLY_        | Export only matching regex
| --skip _SKIP_        | Do not export matching regex
| -f/--format _format_ | Output as md/csv/html
| --attachments _dir_  | Directory with attachments from backup
| -r, --reversed       | Start with last message
| --bom                | Write bom into file
