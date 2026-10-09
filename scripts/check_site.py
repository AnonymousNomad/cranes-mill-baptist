import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {'.css', '.html', '.js', '.json', '.md', '.py', '.toml'}


def main():
    failures = []
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in TEXT_EXTENSIONS and '.site-git' not in path.parts:
            lines = len(path.read_text(encoding='utf-8').splitlines())
            if lines > 500:
                failures.append(f'{path.relative_to(ROOT)} exceeds 500 lines ({lines})')
    media = [path for path in (ROOT / 'church').iterdir() if path.is_file()]
    if len(media) != 74:
        failures.append(f'expected 74 supplied media files, found {len(media)}')
    seed = json.loads((ROOT / 'content' / 'seed.json').read_text(encoding='utf-8'))
    if not seed.get('sermons') or not seed.get('events'):
        failures.append('seed content must include sermons and events')
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    if not re.search(r'data-view="events"', html) or not re.search(r'id="calendar-grid"', html):
        failures.append('events calendar view is not wired')
    if not re.search(r'id="social-links"', html):
        failures.append('footer social links are not wired')
    if not re.search(r'class="floating-crosses"', html):
        failures.append('floating cross decoration is not wired')
    for route in ('sermons', 'contact', 'ministries'):
        if not re.search(rf'class="feature-link-card"[^>]*href="#{route}"', html):
            failures.append(f'home feature card for {route} is not wired')
    for document in (ROOT / 'index.html', ROOT / 'admin.html'):
        source = document.read_text(encoding='utf-8')
        for raw_path in re.findall(r'(?:src|href)="(/(?:styles|scripts|church)/[^"]+)"', source):
            asset = ROOT / unquote(raw_path.lstrip('/'))
            if not asset.is_file():
                failures.append(f'{document.name} references missing asset {raw_path}')
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print(f'PASS: {len(media)} supplied media files, seed content, routes, and 500-line cap')
    return 0


if __name__ == '__main__':
    sys.exit(main())
