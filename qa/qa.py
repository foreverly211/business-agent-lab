"""MYkrokosmos browser QA: drives the app like a first-time user and reports ok / !! lines.
usage: python qa.py <app.html> <label>"""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

APP = 'file://' + str(pathlib.Path(sys.argv[1]).resolve())
LABEL = sys.argv[2] if len(sys.argv) > 2 else 'run'
HERE = pathlib.Path(__file__).parent
OUT = HERE / 'shots' / LABEL; OUT.mkdir(parents=True, exist_ok=True)
issues, oks = [], []
def bug(m): issues.append(m); print('  !! ' + m)
def ok(m): oks.append(m); print('  ok ' + m)
def shot(pg, n): pg.screenshot(path=str(OUT / f'{n}.png'))
EXP = "[...document.querySelectorAll('#graph-svg .node')].filter(g => (g.getAttribute('aria-label') || '').startsWith('경험'))"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1366, 'height': 900}, locale='ko-KR')
    errors = []
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errors.append(f'console.{m.type}: {m.text}') if m.type == 'error' else None)

    print('1. 첫 방문')
    pg.goto(APP); pg.wait_for_timeout(1500)
    ok('이름 입력 창이 먼저 뜸') if pg.locator('.welcome').count() else bug('이름 입력 창이 뜨지 않음')
    ok('이름 없이는 시작 버튼 비활성') if pg.locator('#wl-ok').is_disabled() else bug('이름 없이도 시작 가능')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok('Esc로 닫히지 않음') if pg.locator('.welcome').count() else bug('Esc로 필수 창이 닫힘')
    pg.fill('#wl-name', '테스터'); pg.fill('#wl-m1', '디지털경영'); pg.fill('#wl-m2', '산업경영공학')
    pg.click('#wl-ok'); pg.wait_for_timeout(1500)

    print('2. 튜토리얼')
    ok('튜토리얼 시작') if pg.locator('#tour-card').count() else bug('튜토리얼이 시작되지 않음')
    for i in range(1, 11):
        if i == 2:
            pg.mouse.move(3, 3); pg.wait_for_timeout(1500)
            shot(pg, 'tutorial_step2')
            n = pg.evaluate(EXP + '.length')
            if n: ok(f'튜토리얼 2단계: 예시 별 {n}개 표시')
            else: bug('튜토리얼 2단계: 예시 별자리 대신 빈 하늘이 보임')
            if n:
                box = pg.evaluate("(() => { const n = " + EXP + "[0]; const r = n.getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; })()")
                before = pg.evaluate("(" + EXP + ")[0].getAttribute('transform')")
                pg.mouse.move(*box); pg.mouse.down(); pg.mouse.move(box[0] + 80, box[1] + 40, steps=6); pg.mouse.up(); pg.wait_for_timeout(500)
                after = pg.evaluate("(" + EXP + ")[0].getAttribute('transform')")
                ok('튜토리얼 중 별 끌기 가능') if before != after else bug('튜토리얼 중 별을 끌 수 없음')
        pg.click('#t-next'); pg.wait_for_timeout(700)
    ok('튜토리얼 종료') if not pg.locator('#tour-card').count() else bug('튜토리얼이 끝나지 않음')
    st = json.loads(pg.evaluate("localStorage.getItem('byeoljari.v1')"))
    ok('튜토리얼 후 예시 데이터가 남지 않음') if not st['experiences'] else bug('예시 데이터가 저장됨')

    print('3. 경험 기록')
    pg.click('#btn-record'); pg.wait_for_timeout(400)
    pg.fill('#ed-title', '데이터 분석 공모전 참가')
    pg.fill('#ed-body', '팀장으로 파이썬과 SQL로 데이터를 분석하고 시각화 대시보드를 만들었다. 발표도 했다.')
    pg.wait_for_timeout(500)
    sugg = pg.locator('#ed-sugg [data-add]').count()
    ok(f'태그 추천 {sugg}개') if sugg >= 3 else bug(f'태그 추천이 너무 적음 ({sugg})')
    for _ in range(3):
        if pg.locator('#ed-sugg [data-add]').count(): pg.locator('#ed-sugg [data-add]').first.click(); pg.wait_for_timeout(150)
    s5 = pg.locator('#ed-imp .star').nth(4).bounding_box(); pg.mouse.click(s5['x'] + s5['width'] * .8, s5['y'] + s5['height'] / 2)
    g4 = pg.locator('#ed-growth .star').nth(3).bounding_box(); pg.mouse.click(g4['x'] + g4['width'] * .2, g4['y'] + g4['height'] / 2)
    v = (pg.locator('#ed-imp').get_attribute('data-v'), pg.locator('#ed-growth').get_attribute('data-v'))
    ok('0.5 단위 별점 (5 / 3.5)') if v == ('5', '3.5') else bug(f'별점 오류 {v}')
    pg.click('#ed-save'); pg.wait_for_timeout(1500)
    ok('기록 저장 후 하늘에 새 별') if pg.evaluate(EXP + '.length') == 1 else bug('저장 후 별이 없음')

    print('4. 백업 불러오기')
    pg.click('[data-go="me"]'); pg.wait_for_timeout(400)
    sample = json.load(open(HERE / 'sample_state.json', encoding='utf-8'))
    pg.set_input_files('#me-import', str(HERE / 'sample_state.json')); pg.wait_for_timeout(400)
    if pg.locator('#confirm-root [data-a="1"]').count(): pg.click('#confirm-root [data-a="1"]'); pg.wait_for_timeout(1200)
    n = len(json.loads(pg.evaluate("localStorage.getItem('byeoljari.v1')"))['experiences'])
    ok(f'경험 {n}개 불러옴') if n == len(sample['experiences']) else bug('불러오기 실패')

    print('5. 별자리')
    pg.click('[data-go="graph"]'); pg.wait_for_timeout(3000)
    shot(pg, 'sky')
    n = pg.evaluate(EXP + '.length')
    ok(f'경험 별 {n}개 그려짐') if n == len(sample['experiences']) else bug(f'별 개수 불일치 {n}')
    out = pg.evaluate("""(() => { const s = document.querySelector('#graph').getBoundingClientRect(); return [...document.querySelectorAll('#graph-svg .node')].filter(n => { const r = n.getBoundingClientRect(); const cx = r.x + r.width/2, cy = r.y + r.height/2; return cx < s.left || cx > s.right || cy < s.top || cy > s.bottom; }).map(n => n.getAttribute('aria-label')); })()""")
    bug(f'하늘 밖에 그려진 별 {len(out)}개: {out}') if out else ok('모든 별이 하늘 안에 있음')
    pos = pg.evaluate("(() => { const n = [...document.querySelectorAll('#graph-svg .node')].find(g => g.getAttribute('aria-label').includes('Haybit')); const r = n.getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; })()")
    pg.mouse.move(*pos); pg.wait_for_timeout(300)
    ok('마우스를 올리면 말풍선') if pg.locator('#graph-tip').is_visible() else bug('말풍선이 뜨지 않음')
    pg.mouse.click(*pos); pg.wait_for_timeout(500)
    if pg.locator('#graph-panel').is_visible():
        ok('별을 누르면 정보 카드')
        pg.mouse.move(*pos); pg.wait_for_timeout(300)
        bug('말풍선이 열린 정보 카드를 덮음') if pg.locator('#graph-tip').is_visible() else ok('카드가 열린 별에는 말풍선이 뜨지 않음')
    else: bug('정보 카드가 열리지 않음')
    pg.fill('#g-search', '데이터'); pg.wait_for_timeout(300)
    f = pg.locator('#graph-svg .node.found').count()
    ok(f'키워드 검색 {f}개') if f else bug('검색 결과 없음')
    pg.press('#g-search', 'Escape')
    pg.click('#g-view'); pg.wait_for_timeout(1200)
    vb = pg.locator('#graph').bounding_box()
    ok('감상 모드가 창 전체를 채움') if vb['width'] >= 1365 else bug(f'감상 모드 오른쪽에 빈 줄 ({1366 - round(vb["width"])}px)')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(500)
    ok('Esc로 감상 모드 종료') if not pg.locator('#graph.viewing').count() else bug('Esc로 감상 모드가 끝나지 않음')

    print('6. 다른 화면')
    for v in ['records', 'ability', 'timeline', 'goal', 'summary', 'me']:
        pg.click(f'[data-go="{v}"]'); pg.wait_for_timeout(800)
        bug(f'{v}: 가로 스크롤 생김') if pg.evaluate('document.documentElement.scrollWidth > innerWidth') else ok(f'{v} 화면 정상')

    print('7. 새로고침')
    pg.reload(); pg.wait_for_timeout(2000)
    ok('기록 유지, 튜토리얼 다시 안 뜸') if not pg.locator('#tour-card').count() and not pg.locator('.welcome').count() else bug('새로고침 후 튜토리얼이 다시 뜸')

    print('\n브라우저 오류:', len(errors))
    for e in sorted(set(errors)): print('  ', e)
    b.close()

print(f'\n결과: 통과 {len(oks)}개 · 문제 {len(issues)}개')
for i in issues: print(' -', i)
