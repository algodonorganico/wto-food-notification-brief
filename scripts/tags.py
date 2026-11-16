"""통보별 카테고리 태그(#첨가물, #잔류농약 등)를 정하는 규칙

세부 주제(topic)를 정해진 태그 목록으로 묶고, 국문 제목·원제에 나오는 핵심어로 보충한다.
한 통보에 태그가 여러 개 붙을 수 있다. 태그 목록을 바꾸려면 TAGS와 아래 규칙만 고치면 된다.
"""
import re

# 페이지의 태그 막대에 나오는 순서
TAGS = ['한국 관련', '식품법 전반', '잔류농약', '동물용의약품', '오염물질', '첨가물', '기구·용기', '신소재식품', '건강기능식품',
        '영유아·특수용도', '표시', 'GMO', '할랄', '유기식품', '품질규격', '위생·시설', '수입관리',
        '가축질병', '동물검역', '사료', '식물검역']

# 세부 주제(topic)에 이 글자가 들어 있으면 붙는 태그 (위에서부터 검사, 해당하는 것 모두)
TOPIC_RULES = [
    (r'식품안전 일반', '식품법 전반'),
    (r'농약', '잔류농약'),
    (r'동물용의약품', '동물용의약품'),
    (r'오염물질|미생물 기준', '오염물질'),
    (r'(?<!사료)첨가물|가공보조제|효소', '첨가물'),
    (r'기구|포장', '기구·용기'),
    (r'한시적 기준', '신소재식품'),
    (r'건강기능|보충성분|기능성 원료|영양강화', '건강기능식품'),
    (r'영유아|특수용도', '영유아·특수용도'),
    (r'표시|영양\(|소비기한', '표시'),
    (r'GMO', 'GMO'),
    (r'할랄', '할랄'),
    (r'유기식품', '유기식품'),
    (r'품질|규격|등급|표준|주류|먹는물|안전기준', '품질규격'),
    (r'(?<!수입)위생|시설기준|도축|GAP|급식', '위생·시설'),
    (r'수입(?!.*(제한|위생요건|검역))|국경검사|해외작업장|등록|시험·검사|허용국', '수입관리'),
    (r'HPAI|구제역|돼지열병|뉴캐슬|블루텅|스크래피|수생동물 질병|가금 수입제한|소 수입제한|BSE', '가축질병'),
    (r'사료', '사료'),
]
# 국문 제목·원제에 나오면 덧붙이는 태그 (세부 주제가 넓게 잡힌 통보 보완)
TEXT_RULES = [
    (r'농약|pesticide', '잔류농약'),
    (r'novel food|신규 ?식품|신소재', '신소재식품'),
    (r'식품첨가물|가공보조제|향료', '첨가물'),
    (r'오염물질|곰팡이독소|중금속|contaminant|mycotoxin', '오염물질'),
    (r'식품접촉|food contact', '기구·용기'),
    (r'조제분유|영아|infant formula', '영유아·특수용도'),
]
KOREA = r'\bKorea\b|한국산|한국'


def tags_for(x):
    topic, text = x.get('topic') or '', f"{x.get('ko', '')} {x.get('orig', '')}"
    out = []
    if x.get('member') == '한국' or re.search(KOREA, text):
        out.append('한국 관련')
    if not re.search(r'정정\(무효\)', topic):
        for pat, tag in TOPIC_RULES:
            if re.search(pat, topic) and tag not in out:
                out.append(tag)
        for pat, tag in TEXT_RULES:
            if re.search(pat, text, re.I) and tag not in out:
                out.append(tag)
    g = x.get('group')
    if g == '동물위생' and not any(t in out for t in ('가축질병', '사료', '동물용의약품')):
        out.append('동물검역')
    if g == '식물검역':
        out = [t for t in out if t in ('한국 관련',)] + ['식물검역']
    # 어느 태그에도 맞지 않는 통보(정정·무효 통보, 담배·살생물제처럼 식품 관련성이 낮은 통보)는 태그 없이 둔다
    return sorted(out, key=TAGS.index)


def apply(items):
    for x in items:
        x['tags'] = tags_for(x)
