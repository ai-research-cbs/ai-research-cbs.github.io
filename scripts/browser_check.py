"""Check rendered pages and save desktop and phone screenshots of four key pages."""
import argparse
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright
from check import EXPECTED, rows


parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:4176')
parser.add_argument('--output', type=Path, default=Path('evidence'))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
sections = rows('sections.yml')
readings = rows('readings.yml')
counts = Counter((r['section'], r['page']) for r in readings)
pages = [('home', '', '/', 'Research in the Age of AI')]
for section in sections[1:]:
    pages.extend((section['slug'], p['slug'], f'/{section["slug"]}/{p["slug"]}/', p['title']) for p in section['pages'])
screens = {'/': 'home', '/tool/coding/': 'tool-coding', '/topic/economic-implications/': 'economic-implications', '/substitute/exposure/': 'exposure'}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: errors.append(f'{response.status}: {response.url}') if response.url.startswith(args.url) and response.status >= 400 else None)
    for width in [1280, 1024, 820, 390, 320]:
        page.set_viewport_size({'width': width, 'height': 900})
        header_height = None
        for section, slug, path, title in pages:
            response = page.goto(args.url + path, wait_until='networkidle')
            assert response.status == 200, path
            page.evaluate('document.fonts.ready')
            assert page.locator('h1').inner_text() == title, path
            assert page.locator('#topnav a').all_text_contents() == [s[0] for s in EXPECTED]
            assert page.locator('#topnav a[aria-current]').count() == 1
            assert page.locator('.material').count() == counts[(section, slug)], path
            for group in page.locator('.material-list').all():
                years = group.locator('.material').evaluate_all('(items) => items.map(item => Number(item.dataset.year))')
                assert years == sorted(years), (path, years)
            if section != 'home':
                expected_section = next(s for s in sections if s['slug'] == section)
                nav = '.subnav-inline' if width < 820 else '.subnav-top'
                assert page.locator(nav + ' a').all_text_contents() == [s['title'] for s in expected_section['pages']]
                assert page.locator(nav + ' a[aria-current]').inner_text() == title
                if expected_section.get('question'):
                    assert page.locator('.page-question').inner_text() == expected_section['question']
            size = page.locator('.topbar').bounding_box()['height']
            header_height = header_height or size
            assert size == header_height, (width, path, size, header_height)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, path, 'page overflow')
            clipped = page.locator('.topbar a').evaluate_all('''links => links.filter(a => {
                if (!a.getClientRects().length) return false;
                const r = a.getBoundingClientRect();
                const h = document.querySelector('.topbar').getBoundingClientRect();
                return r.right > innerWidth + 1 || r.left < -1 || r.bottom > h.bottom + 1;
            }).map(a => a.textContent)''')
            assert not clipped, (width, path, clipped)
            if width < 820:
                assert abs(page.locator('.content').bounding_box()['x'] - 16) < 1
                page.get_by_role('button', name='Menu').click()
                assert page.locator('#topnav').is_visible()
                assert page.get_by_role('button', name='Menu').get_attribute('aria-expanded') == 'true'
                page.keyboard.press('Escape')
                assert not page.locator('#topnav').is_visible()
                assert page.get_by_role('button', name='Menu').evaluate('(node) => node === document.activeElement')
            if path == '/substitute/exposure/':
                assert page.locator('.exposure-table tbody tr').count() == 7
                assert page.locator('.exposure-table thead th').count() == 5
            if path in screens and width in [1280, 390, 320]:
                page.get_by_role('heading', level=1).click()
                page.screenshot(path=str(args.output / f'{screens[path]}-{width}.png'), full_page=True)
                page.screenshot(path=str(args.output / f'{screens[path]}-{width}-viewport.png'))
        print(f'PASS: {len(pages)} pages at {width}px; ordered navigation, reading counts, year order, header, no overflow.')
    for section in sections[1:]:
        page.goto(args.url + section['url'], wait_until='networkidle')
        assert page.url.endswith(section['url'] + section['pages'][0]['slug'] + '/')
    page.set_viewport_size({'width': 390, 'height': 900})
    page.goto(args.url + '/', wait_until='networkidle')
    page.get_by_role('button', name='Menu').click()
    page.locator('#topnav').get_by_role('link', name='AI as a Topic', exact=True).click()
    page.wait_for_url('**/topic/information-extraction/')
    page.locator('.subnav-inline').get_by_role('link', name='Economic Implications', exact=True).click()
    page.wait_for_url('**/topic/economic-implications/')
    assert page.locator('h1').inner_text() == 'Economic Implications'
    assert page.locator('.material').count() == 41
    assert not errors, errors
    plain = browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 900})
    nojs = plain.new_page()
    nojs.goto(args.url + '/topic/economic-implications/')
    assert nojs.locator('#topnav').is_visible()
    assert nojs.locator('.material').count() == 41
    assert nojs.locator('main').bounding_box()['y'] >= nojs.locator('.topbar').bounding_box()['height']
    print('PASS: four redirects, mobile navigation, JavaScript-free content and navigation, zero script or local request errors.')
    browser.close()
