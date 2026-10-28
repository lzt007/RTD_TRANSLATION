import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def export(self, rows, expected=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (root / 'input.csv').open('w', encoding='utf-8-sig', newline='') as out:
                csv.writer(out).writerows([['源文本', '中文文本'], *rows])
            config = root / 'rtd.config.json'
            config.write_text(json.dumps({'paths': {'csv': str(root / 'input.csv'), 'output': str(root / 'output.json')}}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/export.py'), '--config', str(config)], cwd=tmp, capture_output=True)
            if expected is None:
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b'Export failed:', result.stderr)
                self.assertFalse((root / 'output.json').exists())
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads((root / 'output.json').read_text(encoding='utf-8')), expected)

    def test_multiline_quotes_and_exact_whitespace(self):
        self.export([[' a,"b"\r\nc ', ' 中文\r\n"译文" '], ['x', '  ']], {' a,"b"\r\nc ': ' 中文\r\n"译文" '})

    def test_identical_duplicates_and_empty_are_merged(self):
        self.export([['a', '甲'], ['a', ''], ['a', '甲'], [' a', '乙']], {'a': '甲', ' a': '乙'})

    def test_conflicting_duplicates_rejected(self):
        self.export([['a', '甲'], ['a', '乙']])

    def test_placeholders_and_tags_can_reorder(self):
        self.export([['[abcdef]{0} {1,3:N2}[-]', '[abcdef]{1,3:N2} {0}[-]']], {'[abcdef]{0} {1,3:N2}[-]': '[abcdef]{1,3:N2} {0}[-]'})

    def test_placeholder_change_rejected(self):
        self.export([['value {0:N2}', '数值 {0}']])

    def test_ngui_tag_change_rejected(self):
        self.export([['[abcdef]a[-]', '[ffffff]甲[-]']])

    def test_escaped_braces_and_malformed_template(self):
        self.export([['{{literal}} {0}', '{{文本}} {0}']], {'{{literal}} {0}': '{{文本}} {0}'})
        self.export([['{0}', '{0']])

    def test_wrong_column_count_rejected(self):
        self.export([['a', 'b', 'c']])

    def test_failure_preserves_previously_exported_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'old.json').write_text('{"old":"published"}', encoding='utf-8')
            with (root / 'bad.csv').open('w', encoding='utf-8', newline='') as stream:
                csv.writer(stream).writerows([['源文本', '中文文本'], ['a', '甲'], ['a', '乙']])
            (root / 'config.json').write_text(json.dumps({'paths': {'csv': str(root / 'bad.csv'), 'output': str(root / 'old.json')}}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/export.py'), '--config', str(root / 'config.json')], cwd=root, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b'conflicting duplicate', result.stderr)
            self.assertEqual((root / 'old.json').read_text(encoding='utf-8'), '{"old":"published"}')

    def test_real_source_inventory_and_blank_translation_state(self):
        with (ROOT / 'translations.csv').open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.reader(stream))
        self.assertEqual(rows[0], ['源文本', '中文文本'])
        self.assertTrue(all(len(row) == 2 and row[1] == '' for row in rows[1:]))
        sources = {row[0] for row in rows[1:]}
        textdb = json.loads((ROOT / 'sources/TextDatabase.json').read_text(encoding='utf-8'))
        parts = (ROOT / 'sources/TextDatabase.txt').read_bytes().decode('utf-8').split('\t')
        self.assertEqual(len(textdb), 819)
        self.assertEqual([{'key': parts[i], 'text': parts[i + 1]} for i in range(1, len(parts), 2)], textdb)
        self.assertTrue({row['text'] for row in textdb} <= sources)
        labels = json.loads((ROOT / 'sources/scene-labels.json').read_text(encoding='utf-8'))
        scene_texts = {row['mText'] for row in labels if row['mText'] != ''}
        self.assertEqual(len(scene_texts), 425)
        self.assertTrue(scene_texts <= sources)
        locations = json.loads((ROOT / 'metadata/locations.json').read_text(encoding='utf-8'))
        self.assertEqual(set(locations), sources)
        spec = importlib.util.spec_from_file_location('translation_export', ROOT / 'scripts/export.py')
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        self.assertEqual(exporter.read_mapping(ROOT / 'translations.csv'), {})


if __name__ == '__main__':
    unittest.main()
