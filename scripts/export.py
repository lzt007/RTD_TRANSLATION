"""Validate a two-column translation CSV and atomically export a UTF-8 mapping."""
import argparse
import csv
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r'\{[0-9]+(?:,-?[0-9]+)?(?::[^{}]+)?\}')
TAG = re.compile(r'\[(?:[-/A-Za-z0-9_=:#.]+)\]')


def format_tokens(value):
    tokens = []
    offset = 0
    while offset < len(value):
        if value.startswith(('{{', '}}'), offset):
            tokens.append(value[offset:offset + 2])
            offset += 2
        elif value[offset] == '{':
            match = PLACEHOLDER.match(value, offset)
            if not match:
                raise ValueError('invalid string.Format placeholder')
            tokens.append(match.group())
            offset = match.end()
        elif value[offset] == '}':
            raise ValueError('unescaped closing brace')
        else:
            offset += 1
    return Counter(tokens)


def read_mapping(path):
    mapping = {}
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = csv.reader(stream, strict=True)
        if next(rows, None) != ['源文本', '中文文本']:
            raise ValueError('CSV header must be exactly 源文本,中文文本')
        for number, row in enumerate(rows, 2):
            if len(row) != 2:
                raise ValueError(f'CSV record {number}: expected exactly two columns')
            source, target = row
            if not target.strip():
                continue
            if not source:
                raise ValueError(f'CSV record {number}: empty source')
            try:
                if format_tokens(source) != format_tokens(target):
                    raise ValueError('string.Format placeholders differ')
                if Counter(TAG.findall(source)) != Counter(TAG.findall(target)):
                    raise ValueError('NGUI tags differ')
                if source in mapping and mapping[source] != target:
                    raise ValueError('conflicting duplicate source')
            except ValueError as error:
                raise ValueError(f'CSV record {number}: {error}') from error
            mapping[source] = target
    return mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'rtd.config.json')
    args = parser.parse_args()
    # All configured relative paths are rooted at this project, independent of cwd/config location.
    config = json.loads(args.config.read_text(encoding='utf-8-sig'))
    paths = config['paths']
    source = ROOT / Path(paths['csv'])
    destination = ROOT / Path(paths['output'])
    mapping = read_mapping(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(mapping, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, destination)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    print(f'Exported {len(mapping)} translations.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        print(f'Export failed: {error}', file=sys.stderr)
        sys.exit(1)
