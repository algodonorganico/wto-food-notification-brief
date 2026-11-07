"""주간 호 데이터 생성: sel.json(API 원자료) + curation.json(분류·국문 제목) → data/issue-YYYY-MM-DD.json"""
import json, sys, re, html
def plain(t): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))).strip()
WK, OUT = sys.argv[1], sys.argv[2]
S = json.load(open(f'{WK}/sel.json')); C = json.load(open(f'{WK}/curation.json'))
cur = C['items']
TYPE = {'Regular notification': '정규통보', 'Emergency notifications (SPS)': '긴급통보',
        'Addendum to Regular Notification': '추가통보', 'Addendum to Emergency Notification (SPS)': '추가통보(긴급)',
        'Corrigendum to Emergency Notification (SPS)': '정정통보(긴급)', 'Corrigendum to Regular Notification': '정정통보',
        'Revision to Regular Notification': '개정통보'}
ORDER = {'식품안전': 0, '식품 TBT': 1, '동물위생': 2, '식물검역': 3}
items = {}
for x in S['sps'] + S['tbt_all']:
    syms = [s.strip() for s in x['documentSymbol'].split(',')]
    k = syms[0]
    if k not in cur: continue
    c = cur[k]
    note = c.get('note', '')
    if len(syms) > 1: note = (note + ' / ' if note else '') + '공동 통보 번호: ' + ', '.join(syms)
    items[k] = {'sym': k, 'more': len(syms) - 1, 'area': x['area'], 'group': c['group'], 'date': x['distributionDate'][:10],
                'member': c['member'], 'type': TYPE.get(x['notificationType'], x['notificationType']), 'topic': c['topic'],
                'ko': c['ko'], 'orig': x['titlePlain'], 'products': (x.get('productsFreeTextPlain') or '')[:400],
                'hs': x.get('hsCodeText') or '', 'deadline': (x['commentDeadlineDate'] or '')[:10] or None,
                'link': x['linkToNotification'], 'note': note,
                'desc': (x.get('descriptionPlain') or '').strip()[:2500], 'adopt': plain(x.get('proposedAdoptionDateText')), 'eif': plain(x.get('proposedEntryIntoForceDateText'))}
assert len(items) == len(cur), (len(items), len(cur))
TOP = [('G/TBT/N/USA/2324', []), ('G/SPS/N/MAC/23/Rev.1', []), ('G/SPS/N/JPN/1435', ['G/SPS/N/JPN/1434', 'G/SPS/N/JPN/1436']),
       ('G/SPS/N/TUR/126/Add.1', []), ('G/SPS/N/UKR/284', []), ('G/SPS/N/THA/816', ['G/SPS/N/THA/817']),
       ('G/TBT/N/AUS/198/Rev.1', []), ('G/TBT/N/EU/1249', []), ('G/SPS/N/SAU/639', ['G/SPS/N/SAU/640', 'G/SPS/N/ARE/334/Corr.1']),
       ('G/SPS/N/KOR/212/Add.25', [])]
REASON = {
    'G/TBT/N/USA/2324': '의견 제출 기한이 이번 호에서 가장 이름(11.09)',
    'G/SPS/N/MAC/23/Rev.1': '중금속 기준 165개 중 92개를 한 번에 바꾸는 개정',
    'G/SPS/N/JPN/1435': '같은 주에 농약 기준 개정안 3건 통보',
    'G/SPS/N/TUR/126/Add.1': '아질산염·질산염 사용기준 강화 포함',
    'G/SPS/N/UKR/284': '축산 사용금지 물질 목록을 새로 정하는 명령안',
    'G/SPS/N/THA/816': '우유 제품명 표시 기준 변경, TBT로도 함께 통보',
    'G/TBT/N/AUS/198/Rev.1': '건강별점 표시를 의무로 바꾸는 제안의 2차 의견수렴',
    'G/TBT/N/EU/1249': '유효성분 재승인 거부, 잔류허용기준은 후속 통보 예정',
    'G/SPS/N/SAU/639': '긴급통보에 따른 가금 수입 일시 금지',
    'G/SPS/N/KOR/212/Add.25': '우리나라가 낸 통보',
}
NOTE = {
    'headline': '농약·중금속 기준 개정이 이어진 한 주',
    'subtitle': '10월 26일부터 11월 1일까지 배포된 WTO 통보 가운데 식품과 관련된 47건을 읽고, 꼭 알아야 할 흐름 네 가지를 골랐습니다.',
    'lead': '이번 주 식품 관련 통보 47건에서 눈여겨볼 흐름은 네 가지입니다.',
    'themes': [
        {'title': '농약·중금속 기준 개정이 이어졌습니다',
         'text': '일본이 티아디닐·펜아자퀸·1,3-디클로로프로펜 잔류허용기준 개정안 3건을, 호주가 생강 중 시아조파미드 기준 조정안을 통보했습니다. 마카오는 식품 중 중금속 최대기준 165개 가운데 92개를 신설·조정했고, 유럽연합은 펜메디팜 재승인 거부안을 내면서 잔류허용기준은 별도로 통보하겠다고 밝혔습니다.',
         'syms': ['G/SPS/N/JPN/1434', 'G/SPS/N/JPN/1435', 'G/SPS/N/JPN/1436', 'G/SPS/N/AUS/643', 'G/SPS/N/MAC/23/Rev.1', 'G/TBT/N/EU/1249']},
        {'title': '가금 수입 제한이 잇따라 바뀌었습니다',
         'text': '사우디아라비아가 뉴캐슬병을 이유로 폴란드 비엘코폴스카주와 브라질 산타카타리나주산 가금육·계란 수입을 일시 금지했습니다. 같은 내용의 걸프 7개국 공동 통보는 잘못 배포돼 무효 처리됐습니다. 태국은 네덜란드산 가금 수입·경유 중단을 해제했습니다.',
         'syms': ['G/SPS/N/SAU/639', 'G/SPS/N/SAU/640', 'G/SPS/N/ARE/334/Corr.1', 'G/SPS/N/THA/807/Add.1']},
        {'title': '세 나라에서 표시 규정 통보가 나왔습니다',
         'text': '미국 텍사스주는 새우 원산지 표시 규칙안을, 호주는 건강별점 표시 의무화 제안의 2차 의견수렴을, 태국은 우유·가향우유 제품명 표시 개정안을 통보했습니다. 텍사스주 건은 의견 제출 기한이 11월 9일입니다.',
         'syms': ['G/TBT/N/USA/2324', 'G/TBT/N/AUS/198/Rev.1', 'G/SPS/N/THA/816', 'G/SPS/N/THA/817']},
        {'title': '우리나라도 검역병해충을 추가했습니다',
         'text': '농림축산검역본부가 검역병해충 36종 추가를 통보했습니다. 의견 제출 기한은 12월 27일입니다.',
         'syms': ['G/SPS/N/KOR/212/Add.25']},
    ],
}
issue = {
    'id': '2026-11-w1', 'no': 1, 'label': '2026년 11월 1주', 'edition': '창간호', 'published': '2026-11-06',
    'note': NOTE,
    'from': '2026-10-26', 'to': '2026-11-01', 'fetched': '2026-11-03',
    'raw': {'spsRows': 48, 'tbtRows': 90, 'spsUnique': 36, 'tbtUnique': 62},
    'top': [{'sym': k, 'related': r, 'why': REASON[k]} for k, r in TOP],
    'items': sorted(items.values(), key=lambda r: (ORDER[r['group']], r['date'], r['sym'])),
    'criteria': [
        'WTO ePing API에서 배포일 기준으로 해당 주(월~일)의 SPS 통보 전체와 TBT 통보 전체를 수집',
        '여러 회원국이 같은 문서로 낸 공동 통보는 1건으로 병합',
        'TBT는 국제표준분류(ICS) 67번대(식품기술) 또는 ePing 키워드 "Food standards"인 건을 고른 뒤 담당자 검토로 가감'
    ] + [f'TBT 추가: {k} — 농약 유효성분 재승인 거부로 잔류허용기준에 영향' for k in C['added_tbt']]
      + [f'TBT 제외: {k} — {v}' for k, v in C['excluded_tbt'].items()],
}
json.dump([issue], open(OUT, 'w'), ensure_ascii=False, indent=1)
print('items', len(issue['items']), {g: sum(i['group'] == g for i in issue['items']) for g in ORDER})
