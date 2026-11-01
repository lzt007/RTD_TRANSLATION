"""Validate translated text against the bundled bitmap glyph inventory."""
import pathlib,json,csv
from export import read_mapping
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 mapping=read_mapping(ROOT/'translations.csv')
 codes={int(line.split('\t')[0]) for line in (ROOT/'sources/fonts/font.tsv').read_text(encoding='utf8').splitlines()[1:]}
 errors=[]
 for source,target in mapping.items():
  missing=sorted({c for c in target if not c.isspace() and ord(c) not in codes})
  if missing:errors.append({'source':source,'missing':missing})
 with (ROOT/'translations.csv').open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.reader(stream))[1:]
 print(json.dumps({'translated':len(mapping),'pending_rows':sum(not row[1].strip() for row in rows),'missing_glyph_entries':errors},ensure_ascii=True,indent=2))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
