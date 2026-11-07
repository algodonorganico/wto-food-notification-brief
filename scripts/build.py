"""src/<page>.html + data/issues.json + 글꼴 → dist/<out>.html

글꼴 폴더 두 가지를 받음
- Pretendard woff2-subset 폴더: Pretendard 400/500/600을 통째로 넣음
- @fontsource/noto-sans-kr 패키지 폴더(400.css 등이 있는 곳): 페이지에 실제 쓰인 글자만 남겨 Noto Sans KR 400/500/700/800을 넣음
"""
import base64, io, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_DIR = pathlib.Path(sys.argv[1])
SRC = sys.argv[2] if len(sys.argv) > 2 else 'page.html'
OUT = sys.argv[3] if len(sys.argv) > 3 else 'wto-weekly.html'
page = (ROOT / 'src' / SRC).read_text(encoding='utf-8')
import os
data = json.loads((ROOT / os.environ.get('WTO_DATA', 'data/issues.json')).read_text(encoding='utf-8'))
data.sort(key=lambda x: x['from'], reverse=True)  # 최신 호가 앞
DATA = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')


def b64(raw):
    return base64.b64encode(raw).decode()


def pretendard():
    faces = []
    for w, n in [(400, 'Regular'), (500, 'Medium'), (600, 'SemiBold')]:
        faces.append(f"@font-face{{font-family:'Pretendard';font-weight:{w};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,{b64((FONT_DIR / f'Pretendard-{n}.subset.woff2').read_bytes())}) format('woff2');}}")
    return faces


def ranges(spec):
    out = []
    for part in spec.split(','):
        a, _, b = part.strip()[2:].partition('-')
        out.append((int(a, 16), int(b or a, 16)))
    return out


def noto(weights=(400, 500, 700, 800)):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    # 페이지 문구 + 데이터에 쓰인 글자 + 기본 문장부호·숫자·영문(검색창 입력 대비)
    used = set(page) | set(DATA) | set(chr(c) for c in range(0x20, 0x7F)) | set('·…—–‘’“”→←↑↓★☆')
    used = {ord(c) for c in used}
    faces = []
    for w in weights:
        css = (FONT_DIR / f'{w}.css').read_text()
        for m in re.finditer(r"url\(\./files/([^)]+?\.woff2)\).*?unicode-range: ([^;]+);", css, re.S):
            rs = ranges(m.group(2))
            need = sorted(c for c in used if any(a <= c <= b for a, b in rs))
            if not need:
                continue
            f = TTFont(str(FONT_DIR / 'files' / m.group(1)))
            opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']; opt.name_IDs = ['*']
            sub = subset.Subsetter(opt); sub.populate(unicodes=need); sub.subset(f)
            buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
            ur = m.group(2).strip()
            faces.append(f"@font-face{{font-family:'Noto Sans KR';font-weight:{w};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,{b64(buf.getvalue())}) format('woff2');unicode-range:{ur};}}")
    # 가운뎃점·대시·따옴표는 Noto Sans KR에서 전각처럼 넓게 나오므로 같은 계열 Noto Sans(라틴) 글리프로 덮음
    if LATIN_DIR:
        punct = [0xB7, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026]
        for w in weights:
            f = TTFont(str(LATIN_DIR / 'files' / f'noto-sans-latin-{w}-normal.woff2'))
            have = [c for c in punct if c in f.getBestCmap()]
            opt = subset.Options(); opt.flavor = 'woff2'
            sub = subset.Subsetter(opt); sub.populate(unicodes=have); sub.subset(f)
            buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
            ur = ','.join(f'U+{c:x}' for c in have)
            faces.append(f"@font-face{{font-family:'Noto Sans KR';font-weight:{w};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,{b64(buf.getvalue())}) format('woff2');unicode-range:{ur};}}")
    return faces


LATIN_DIR = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else None
faces = noto() if (FONT_DIR / '400.css').exists() else pretendard()
out = page.replace('/*FONTS*/', '\n'.join(faces)).replace('/*DATA*/', DATA)
(ROOT / 'site').mkdir(exist_ok=True)
(ROOT / 'site' / OUT).write_text(out, encoding='utf-8')
print(f'site/{OUT} {len(out.encode())/1024:.0f} KB, issues {len(data)}, font faces {len(faces)}')
