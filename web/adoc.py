"""Read poems.adoc into a list of entries.

The file is laid out as:

    ==== Poems                      <- section
    ===== Ulysses by Alfred Lord Tennyson   <- entry title (and author)
    [verse]
    ____
    lines...
    ____                            <- some blocks are closed with ---- instead

Under "Quotations" one heading often holds several separate quotes, so each
block there becomes its own entry. Under "Poems" the blocks stay together.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

DELIMITERS = {'____', '----'}
QUOTE_SECTIONS = {'quotations'}


@dataclass
class Entry:
    section: str
    heading: str
    title: str
    author: str | None
    blocks: list[str]
    slug: str = ''
    part: int | None = None        # 1, 2, ... when a quote heading was split
    parts: int | None = None
    kind: str = field(init=False)

    def __post_init__(self):
        self.kind = 'quote' if self.section.lower() in QUOTE_SECTIONS else 'poem'

    def as_dict(self):
        return {'slug': self.slug, 'section': self.section, 'kind': self.kind,
                'title': self.title, 'author': self.author, 'text': '\n\n'.join(self.blocks)}


def split_title(heading):
    """'Ulysses by Alfred Lord Tennyson' -> ('Ulysses', 'Alfred Lord Tennyson')."""
    if ' by ' in heading:
        title, author = heading.rsplit(' by ', 1)
        return title.strip().rstrip(','), author.strip()
    return heading, None


def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'untitled'


def _clean(lines):
    """Drop blank lines at either end and trailing spaces; keep indentation."""
    lines = [l.rstrip() for l in lines]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def parse(text):
    section = ''
    raw = []                    # (section, heading, [blocks])
    block = None

    for line in text.splitlines():
        stripped = line.strip()
        if block is not None:
            if stripped in DELIMITERS:
                if raw and (body := _clean(block)):
                    raw[-1][2].append(body)
                block = None
            else:
                block.append(line)
        elif stripped in DELIMITERS:
            block = []
        elif m := re.match(r'^(=+)\s+(.*\S)', line):
            level, title = len(m.group(1)), m.group(2)
            if level <= 4:
                section = title
            else:
                raw.append((section, title, []))
    if block is not None and raw and (body := _clean(block)):
        raw[-1][2].append(body)     # unclosed block at end of file

    entries = []
    for section, heading, blocks in raw:
        if not blocks:
            continue
        title, author = split_title(heading)
        if section.lower() in QUOTE_SECTIONS and len(blocks) > 1:
            for i, b in enumerate(blocks, 1):
                entries.append(Entry(section, heading, title, author, [b], part=i, parts=len(blocks)))
        else:
            entries.append(Entry(section, heading, title, author, blocks))

    used = set()
    for e in entries:
        base = slugify(e.heading) + (f'-{e.part}' if e.part else '')
        slug, n = base, 1
        while slug in used:         # the same poem pasted in twice
            n += 1
            slug = f'{base}-v{n}'
        used.add(slug)
        e.slug = slug
    return entries


class Library:
    """Entries from an .adoc file, re-read whenever the file changes."""

    def __init__(self, path):
        self.path = Path(path)
        self._mtime = None
        self._entries = []

    @property
    def entries(self):
        mtime = self.path.stat().st_mtime
        if mtime != self._mtime:
            self._entries = parse(self.path.read_text(encoding='utf-8'))
            self._by_slug = {e.slug: e for e in self._entries}
            self._mtime = mtime
        return self._entries

    def get(self, slug):
        self.entries
        return self._by_slug.get(slug)

    def sections(self):
        out = {}
        for e in self.entries:
            out.setdefault(e.section, []).append(e)
        return out
