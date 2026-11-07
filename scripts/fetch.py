"""WTO ePing API에서 기간별 SPS·TBT 통보 원자료를 받아 work/mo/raw_<tag>_{sps,tbt}.json 으로 저장

사용: WTO_API_KEY=<키> python3 scripts/fetch.py <tag> <시작일> <종료일>
예:   WTO_API_KEY=... python3 scripts/fetch.py 11 2026-11-01 2026-11-30

키는 저장소에 넣지 않는다. 환경변수로만 전달한다.
"""
import json, os, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = os.environ.get('WTO_API_KEY')
if not KEY:
    sys.exit('WTO_API_KEY 환경변수가 없습니다.')
tag, date_from, date_to = sys.argv[1:4]
OUT = ROOT / 'work' / 'mo'
OUT.mkdir(parents=True, exist_ok=True)


def fetch(domain):
    items, page = [], 1
    while True:
        url = (f'https://api.wto.org/eping/notifications/search?language=1&domainIds={domain}'
               f'&distributionDateFrom={date_from}&distributionDateTo={date_to}&page={page}&pageSize=100')
        req = urllib.request.Request(url, headers={'Ocp-Apim-Subscription-Key': KEY})
        data = json.load(urllib.request.urlopen(req, timeout=60))
        items += data['items']
        if len(items) >= data['totalCount'] or not data['items']:
            return items, data['totalCount']
        page += 1


for domain, name in ((2, 'sps'), (1, 'tbt')):   # ePing domainIds: 2 = SPS, 1 = TBT
    items, total = fetch(domain)
    (OUT / f'raw_{tag}_{name}.json').write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')
    print(name, len(items), '/', total)
