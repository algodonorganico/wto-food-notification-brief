"""원자료에서 공동 통보를 병합하고 식품 관련 후보를 골라 work/mo/cand_<tag>.json 으로 저장

사용: python3 scripts/candidates.py <tag>
SPS는 전부 후보. TBT는 ICS 67번대, ePing 키워드 "Food standards", HS 1~24류 중 하나라도 있으면 후보(_sig에 근거 기록).
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MO = ROOT / 'work' / 'mo'
tag = sys.argv[1]
out, stat = {}, {}
for n in ('sps', 'tbt'):
    rows = json.load(open(MO / f'raw_{tag}_{n}.json'))
    uniq = {}
    for x in rows:
        uniq.setdefault(x['documentSymbol'].split(',')[0].strip(), x)
    stat[n] = (len(rows), len(uniq))
    for k, x in uniq.items():
        if n == 'tbt':
            ics = [c['code'] for c in x.get('icsCodes') or []]
            kw = [c.get('name', '') if isinstance(c, dict) else str(c) for c in (x.get('keywords') or [])]
            hs = [c['code'] for c in x.get('hsCodes') or []]
            sig = []
            if any(c.startswith('67') for c in ics): sig.append('ICS67')
            if any('Food standards' in s for s in kw): sig.append('KW')
            if any(len(h) >= 2 and h[:2].isdigit() and 1 <= int(h[:2]) <= 24 for h in hs): sig.append('HS')
            if not sig:
                continue
            x['_sig'] = sig
        out[k] = x
(MO / f'cand_{tag}.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
print(stat, 'candidates', len(out), 'SPS', sum(x['area'] == 'SPS' for x in out.values()), 'TBT', sum(x['area'] == 'TBT' for x in out.values()))
