import sys,json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1366,'height':900},locale='ko-KR'); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1000)
    pg.fill('#wl-name','t'); pg.click('#wl-ok'); pg.wait_for_timeout(600); pg.click('#t-skip'); pg.wait_for_timeout(600)
    n=lambda: len(json.loads(pg.evaluate("localStorage.getItem('byeoljari.v1')"))['experiences'])
    for i in range(2):
        pg.click('#btn-record'); pg.fill('#ed-title',f'경험{i}'); pg.click('#ed-save'); pg.wait_for_timeout(500)
    print('saved',n())
    pg.click('[data-go="records"]'); pg.wait_for_timeout(300); pg.click('.rcard >> nth=0'); pg.wait_for_timeout(300)
    pg.click('#dt-del'); pg.click('#confirm-root [data-a="1"]'); pg.wait_for_timeout(400); print('after detail delete',n())
    pg.click('.rcard >> nth=0'); pg.click('#dt-edit'); pg.wait_for_timeout(300); pg.click('#ed-del'); print('confirm text:',pg.inner_text('#confirm-root p')); pg.click('#confirm-root [data-a="1"]'); pg.wait_for_timeout(400); print('after editor delete',n())
    pg.click('[data-go="ability"]'); pg.wait_for_timeout(300)
    print('night bg:', pg.evaluate("getComputedStyle(document.querySelector('.night')).backgroundImage.slice(0,40)"))
    print('errors',errs); b.close()
