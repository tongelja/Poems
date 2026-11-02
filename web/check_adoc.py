"""Check poems.adoc for edits that would break the site or the PDF.

Usage:  python check_adoc.py poems.adoc      (or - to read stdin)
Exits 1 and lists line numbers if anything is wrong. Plain Python, no packages.
"""

import re
import sys

OPEN = CLOSE = '____'


def check(lines):
    errors, warnings = [], []
    heading = None          # (line no, text) of the current ===== heading
    blocks_under_heading = 0
    block_start = None      # line no of the opening ____
    seen_headings = {}

    def end_heading():
        if heading and blocks_under_heading == 0:
            errors.append(f'{heading[0]}: "{heading[1]}" has no [verse] block under it')

    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()

        if block_start is not None:          # inside a block
            if line == CLOSE:
                block_start = None
            elif line in ('----', '....', '****', '===='):
                errors.append(f'{n}: "{line}" inside the block opened on line {block_start}; '
                              f'close it with {CLOSE}')
            elif re.match(r'^=+ \S', line):
                errors.append(f'{n}: heading inside the block opened on line {block_start} '
                              f'(missing {CLOSE} before it?)')
            continue

        if not line or line.startswith(':') or line.startswith('//'):
            continue
        if line == OPEN:
            if heading is None:
                errors.append(f'{n}: block before any ===== heading')
            prev = next((l.rstrip() for l in reversed(lines[:n - 1]) if l.strip()), '')
            if prev != '[verse]' and prev != CLOSE:
                warnings.append(f'{n}: block without [verse] above it (line breaks will be lost in the PDF)')
            block_start = n
            blocks_under_heading += 1
            continue
        if line == '[verse]':
            nxt = lines[n].rstrip() if n < len(lines) else ''
            if nxt != OPEN:
                errors.append(f'{n}: [verse] must be followed directly by {OPEN}')
            continue
        if m := re.match(r'^(=+) (.*\S)', line):
            level, text = len(m.group(1)), m.group(2)
            end_heading()
            if level == 5:
                heading, blocks_under_heading = (n, text), 0
                if text in seen_headings:
                    warnings.append(f'{n}: "{text}" is also on line {seen_headings[text]} (duplicate?)')
                seen_headings.setdefault(text, n)
            elif level == 4:
                heading = None
            else:
                errors.append(f'{n}: use ==== for a section or ===== for a poem, not {m.group(1)}')
            continue
        if re.match(r'^=+\S', line):
            errors.append(f'{n}: heading needs a space after the = signs')
            continue
        errors.append(f'{n}: text outside a block: "{line[:60]}"')

    if block_start is not None:
        errors.append(f'{block_start}: block opened here is never closed with {CLOSE}')
    end_heading()
    return errors, warnings


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    path = argv[1]
    text = sys.stdin.read() if path == '-' else open(path, encoding='utf-8').read()
    errors, warnings = check(text.splitlines())
    name = 'poems.adoc' if path == '-' else path
    for w in warnings:
        print(f'{name}:{w}  (warning)')
    for e in errors:
        print(f'{name}:{e}')
    if errors:
        print(f'\n{len(errors)} problem(s) in {name}.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
