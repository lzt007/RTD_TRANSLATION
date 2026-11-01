"""Apply reviewed skill templates; preserve existing translations exactly."""
import pathlib,json,re,csv,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
PATTERN=re.compile(r'\[[^\]]+\]|\d[\d,]*(?:\.\d+)?|物凄く|僅かに|僅か|少し|多く|凄く|超絶な|超絶|致命的な|絶大な|強力な|有利な|絶対的な|火|水|光|闇|無|剣|槍|弓|杖')
TERMS={'物凄く':'極大幅','僅かに':'微幅','僅か':'微幅','少し':'小幅','多く':'大幅','凄く':'大幅度','超絶':'超大幅','超絶な':'超強','致命的な':'致命','絶大な':'極強','強力な':'強力','有利な':'有利','絶対的な':'絕對','闇':'暗','剣':'劍'}
def normalize(source):
 values=[]
 def take(m):
  values.append(m[0]);return '@'+str(len(values)-1)+'@'
 return PATTERN.sub(take,source),values

def main():
 from export import read_mapping,format_tokens,TAG
 patterns=json.loads((ROOT/'metadata/skill-patterns.json').read_text(encoding='utf8'))
 templates={patterns[int(i)]:t for i,t in csv.reader((ROOT/'metadata/skill-pattern-translations.tsv').open(encoding='utf8'),delimiter='\t')}
 with (ROOT/'translations.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
 before={s:t for s,t in rows[1:] if t};added={};missing=collections.Counter()
 codes={int(line.split('\t')[0]) for line in (ROOT/'sources/fonts/font.tsv').read_text(encoding='utf8').splitlines()[1:]}
 for row in rows[1:]:
  s,t=row
  if t:continue
  key,values=normalize(s)
  if key not in templates:continue
  target=re.sub(r'@(\d+)@',lambda m:TERMS.get(values[int(m[1])],values[int(m[1])]),templates[key])
  assert format_tokens(s)==format_tokens(target),(s,target)
  assert collections.Counter(TAG.findall(s))==collections.Counter(TAG.findall(target)),(s,target)
  absent={c for c in target if not c.isspace() and ord(c) not in codes}
  if absent:missing.update(absent);continue
  row[1]=target;added[s]=target
 assert all(dict(rows[1:])[s]==t for s,t in before.items())
 with (ROOT/'translations.csv').open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(rows)
 print(json.dumps({'added':len(added),'missing_glyphs':dict(missing)},ensure_ascii=False))
if __name__=='__main__':main()
