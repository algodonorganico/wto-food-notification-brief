"""시범 누적판 데이터: 9월호·10월호(월간) + 주간 1호 → data/archive.json

입력(작업 폴더 MO): raw_{09,10}_{sps,tbt}.json(API 원자료), cur_{09,10}_{sps,tbt}.py(건별 분류·국문 제목),
notes.json(호별 편집자 노트), ../wk/curation.json(주간 1호 큐레이션 — 10월 마지막 주와 겹치는 건에 재사용)
"""
import collections, html, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
MO = pathlib.Path(sys.argv[1])
OUT = ROOT / 'data' / 'archive.json'


def plain(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))).strip()


TYPE = {'Regular notification': '정규통보', 'Emergency notifications (SPS)': '긴급통보',
        'Addendum to Regular Notification': '추가통보', 'Addendum to Emergency Notification (SPS)': '추가통보(긴급)',
        'Corrigendum to Emergency Notification (SPS)': '정정통보(긴급)', 'Corrigendum to Regular Notification': '정정통보',
        'Revision to Regular Notification': '개정통보'}
ORDER = {'식품안전': 0, '식품 TBT': 1, '동물위생': 2, '식물검역': 3}
KO = {'Argentina': '아르헨티나', 'Australia': '호주', 'Bahrain, Kingdom of': '바레인', 'Belize': '벨리즈', 'Botswana': '보츠와나',
      'Brazil': '브라질', 'Burundi': '부룬디', 'Cambodia': '캄보디아', 'Canada': '캐나다', 'Chile': '칠레', 'China': '중국',
      'Chinese Taipei': '대만', 'Colombia': '콜롬비아', 'Costa Rica': '코스타리카', 'Czech Republic': '체코', 'Denmark': '덴마크',
      'Ecuador': '에콰도르', 'Egypt': '이집트', 'El Salvador': '엘살바도르', 'Eswatini': '에스와티니', 'European Union': '유럽연합',
      'Finland': '핀란드', 'Georgia': '조지아', 'Guyana': '가이아나', 'Hong Kong, China': '홍콩', 'India': '인도', 'Indonesia': '인도네시아',
      'Israel': '이스라엘', 'Jamaica': '자메이카', 'Japan': '일본', 'Jordan': '요르단', 'Kenya': '케냐', 'Korea, Republic of': '한국',
      'Kuwait, the State of': '쿠웨이트', 'Kyrgyz Republic': '키르기스스탄', 'Macao, China': '마카오', 'Malaysia': '말레이시아',
      'Mexico': '멕시코', 'Moldova, Republic of': '몰도바', 'New Zealand': '뉴질랜드', 'Nicaragua': '니카라과', 'Nigeria': '나이지리아',
      'Oman': '오만', 'Pakistan': '파키스탄', 'Panama': '파나마', 'Paraguay': '파라과이', 'Peru': '페루', 'Philippines': '필리핀',
      'Qatar': '카타르', 'Russian Federation': '러시아', 'Rwanda': '르완다', 'Saudi Arabia, Kingdom of': '사우디아라비아',
      'Singapore': '싱가포르', 'South Africa': '남아프리카공화국', 'Spain': '스페인', 'Sweden': '스웨덴', 'Switzerland': '스위스',
      'Tanzania': '탄자니아', 'Thailand': '태국', 'Türkiye': '튀르키예', 'Uganda': '우간다', 'Ukraine': '우크라이나',
      'United Arab Emirates': '아랍에미리트', 'United Kingdom': '영국', 'United States of America': '미국', 'Viet Nam': '베트남',
      'Yemen': '예멘', 'Zambia': '잠비아', 'Albania': '알바니아', 'Italy': '이탈리아', 'Kazakhstan': '카자흐스탄',
      'Malawi': '말라위', 'Poland': '폴란드', 'Sri Lanka': '스리랑카', 'Uruguay': '우루과이'}
GULF = {'ARE', 'BHR', 'KWT', 'OMN', 'QAT', 'SAU', 'YEM'}
EAC = {'BDI', 'KEN', 'RWA', 'TZA', 'UGA'}
W = json.load(open(MO.parent / 'wk' / 'curation.json'))['items']   # 주간 1호 큐레이션(전체 통보번호 키)
NOTES = json.load(open(MO / 'notes.json'))


def load(py):
    g = {}
    exec(open(py, encoding='utf-8').read(), g)
    return g


def member_label(rows):
    codes = {(r.get('documentSymbol') or '').split(',')[0].strip().split('/')[3][:3] for r in rows}
    n = len({r['notifyingMember'] for r in rows})
    first = KO.get(rows[0]['notifyingMember'], rows[0]['notifyingMember'])
    if n <= 1:
        return first
    allsyms = {s.strip().split('/')[3][:3] for r in rows for s in r['documentSymbol'].split(',')}
    if allsyms & GULF and len(allsyms - GULF) == 0:
        return f'걸프 {n}개국 공동'
    if allsyms <= EAC:
        return f'동아프리카 {n}개국 공동'
    return f'{first} 등 {n}개국 공동'


def build_month(m, label, f, t):
    sps, tbt = load(MO / f'cur_{m}_sps.py'), load(MO / f'cur_{m}_tbt.py')
    rows = {'sps': json.load(open(MO / f'raw_{m}_sps.json')), 'tbt': json.load(open(MO / f'raw_{m}_tbt.json'))}
    raw = {'spsRows': len(rows['sps']), 'tbtRows': len(rows['tbt'])}
    groups = {}
    for n in ('sps', 'tbt'):
        g = collections.OrderedDict()
        for x in rows[n]:
            k = x['documentSymbol'].split(',')[0].strip()
            g.setdefault(k, []).append(x)
        groups[n] = g
    raw['spsUnique'], raw['tbtUnique'] = len(groups['sps']), len(groups['tbt'])
    cur = {}
    for k, v in sps['CUR'].items():
        cur['G/SPS/N/' + k] = v
    for k, v in {**tbt['CUR'], **tbt.get('ADD', {})}.items():
        cur['G/TBT/N/' + k] = v
    sps_note = {'G/SPS/N/' + k: v for k, v in tbt.get('SPS_NOTE', {}).items()}
    items = []
    for n in ('sps', 'tbt'):
        for k, rs in groups[n].items():
            short = k.split('/N/')[1]
            if k in W:      # 주간 1호와 겹치는 건은 1호 판단을 그대로 씀
                c = W[k]; grp, topic, ko, note = c['group'], c['topic'], c['ko'], c.get('note', '')
                if n == 'tbt' and short in tbt['EXCL']:
                    continue
            elif k in cur:
                v = cur[k]; grp, topic, ko = v[0], v[1], v[2]; note = v[3] if len(v) > 3 else ''
            else:
                if n == 'tbt':
                    continue   # 식품 관련 아님(후보 신호 없음) 또는 제외 목록
                raise SystemExit(f'큐레이션 누락: {k}')
            x = rs[0]
            syms = [s.strip() for s in x['documentSymbol'].split(',')]
            if k in sps_note and sps_note[k] not in note:
                note = (note + ' / ' if note else '') + sps_note[k]
            if len(syms) > 1:
                note = (note + ' / ' if note else '') + '공동 통보 번호: ' + ', '.join(syms)
            items.append({'sym': k, 'more': len(syms) - 1, 'area': x['area'], 'group': grp, 'date': x['distributionDate'][:10],
                          'member': member_label(rs), 'type': TYPE.get(x['notificationType'], x['notificationType']), 'topic': topic,
                          'ko': ko, 'orig': plain(x['titlePlain'])[:600], 'products': plain(x.get('productsFreeTextPlain'))[:400],
                          'hs': x.get('hsCodeText') or '', 'deadline': (x['commentDeadlineDate'] or '')[:10] or None,
                          'link': x['linkToNotification'], 'note': note,
                          'desc': plain(x.get('descriptionPlain'))[:2500], 'adopt': plain(x.get('proposedAdoptionDateText')),
                          'eif': plain(x.get('proposedEntryIntoForceDateText'))})
    # 누락 점검: 큐레이션에 있는데 원자료에 없는 키
    have = {i['sym'] for i in items}
    miss = [k for k in cur if k not in have]
    assert not miss, miss
    excl = {('G/TBT/N/' + k): v for k, v in tbt['EXCL'].items() if ('G/TBT/N/' + k) in groups['tbt']}
    return {
        'id': f'2026-{m}', 'kind': 'monthly', 'badge': label, 'label': f'2026년 {int(m)}월호', 'edition': '시범 월간호',
        'published': NOTES[m]['published'], 'from': f, 'to': t, 'fetched': '2026-11-06', 'raw': raw, 'note': NOTES[m]['note'],
        'top': [], 'items': sorted(items, key=lambda r: (ORDER[r['group']], r['date'], r['sym'])),
        'criteria': ['WTO ePing API에서 배포일 기준으로 해당 월의 SPS 통보 전체와 TBT 통보 전체를 수집',
                     '여러 회원국이 같은 문서로 낸 공동 통보는 1건으로 병합',
                     'TBT는 ICS 67번대(식품기술), ePing 키워드 "Food standards", HS 1~24류(식품) 중 하나에 해당하는 건을 고른 뒤 Claude가 원문을 읽고 가감(담당자 검토 전 초안)',
                     'SPS와 같은 문서를 TBT로도 낸 경우 TBT 쪽을 빼고 SPS 건 비고에 표시',
                     '사료·사료첨가물은 동물위생으로 분류']
                    + [f'TBT 추가: {k} — 후보 신호는 없으나 식품 관련' for k in ['G/TBT/N/' + a for a in tbt.get('ADD', {})]]
                    + [f'TBT 제외: {k} — {v}' for k, v in excl.items()],
    }


if len(sys.argv) > 2 and sys.argv[2] == 'april':   # 4월 단독판
    x = build_month('04', '단독판', '2026-04-01', '2026-04-30')
    x.update({'id': '2026-04', 'label': '2026년 4월분', 'edition': '', 'seq': 1})
    (ROOT / 'data' / 'april.json').write_text(json.dumps([x], ensure_ascii=False, indent=1), encoding='utf-8')
    c = collections.Counter(i['group'] for i in x['items'])
    print(x['badge'], len(x['items']), dict(c), x['raw'])
    sys.exit()
issues = [build_month('09', '9월호', '2026-09-01', '2026-09-30'), build_month('10', '10월호', '2026-10-01', '2026-10-31')]
weekly = json.load(open(ROOT / 'data' / 'issues.json'))
for w in weekly:
    w.update({'kind': 'weekly', 'badge': f"주간 No. {w['no']:02d}"})
issues += weekly
for i, x in enumerate(sorted(issues, key=lambda x: x['from'])):
    x['seq'] = i + 1
    x['badge'] = f"No. {i + 1:02d}"
    x['label'] = f"2026년 {int(x['from'][5:7])}월분" if x['kind'] == 'monthly' else f"{x['from'][:4]}.{x['from'][5:7]}.{x['from'][8:]}~{x['to'][5:7]}.{x['to'][8:]}"
    x['edition'] = ''
OUT.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding='utf-8')
for x in issues:
    c = collections.Counter(i['group'] for i in x['items'])
    print(x['badge'], len(x['items']), dict(c), x['raw'])
