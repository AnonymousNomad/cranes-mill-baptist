import unittest
from pathlib import Path
from urllib.parse import unquote

import server


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {'.css', '.html', '.js', '.json', '.md', '.py', '.toml'}


class StaticContractTests(unittest.TestCase):
    def test_supplied_media_inventory_is_preserved(self):
        files = [path for path in (ROOT / 'church').iterdir() if path.is_file()]
        images = [path for path in files if path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic'}]
        videos = [path for path in files if path.suffix.lower() == '.mp4']
        documents = [path for path in files if path.suffix.lower() == '.pdf']
        self.assertEqual(len(files), 74)
        self.assertEqual(len(images), 67)
        self.assertEqual(len(videos), 6)
        self.assertEqual(len(documents), 1)

    def test_source_files_obey_line_cap(self):
        over_limit = []
        for path in ROOT.rglob('*'):
            if path.is_file() and path.suffix in TEXT_EXTENSIONS and '.site-git' not in path.parts:
                line_count = len(path.read_text(encoding='utf-8').splitlines())
                if line_count > 500:
                    over_limit.append((str(path.relative_to(ROOT)), line_count))
        self.assertEqual(over_limit, [])

    def test_routes_and_styles_are_wired(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        for route in ('home', 'about', 'ministries', 'sermons', 'events', 'give', 'contact'):
            self.assertIn(f'data-route="{route}"', html)
            self.assertIn(f'data-view="{route}"', html)
        for stylesheet in ('tokens.css', 'layout.css', 'components.css', 'views.css'):
            self.assertIn(f'/styles/{stylesheet}', html)
        self.assertEqual(html.count('<section'), html.count('</section>'))
        self.assertIn('id="gallery-dialog"', html)
        self.assertIn('id="ministry-list"', html)
        self.assertEqual(html.count('class="feature-link-card"'), 3)
        self.assertIn('id="hero-slideshow"', html)
        self.assertIn('class="hero-location"', html)
        self.assertIn('hero-cinematic', html)
        self.assertIn('/assets/hero/sunrise-hero.jpg', html)
        self.assertIn('id="hero-title"', html)
        self.assertIn('A church that feels like home.', html)
        self.assertIn('class="banner-title display-3d"', html)
        self.assertRegex(html, r'class="[^"]*\bdisplay-3d\b[^"]*"')
        self.assertIn('class="band-copy"', html)
        self.assertIn('class="floating-crosses"', html)
        self.assertIn('id="social-links"', html)
        self.assertIn('facebook_url', (ROOT / 'scripts' / 'app.js').read_text(encoding='utf-8'))
        self.assertIn('class="event-card-image"', (ROOT / 'scripts' / 'app.js').read_text(encoding='utf-8'))
        tokens = (ROOT / 'styles' / 'tokens.css').read_text(encoding='utf-8')
        self.assertIn('--paper: #123443', tokens)
        self.assertIn('--cream: #0b202d', tokens)
        self.assertIn('id="site-form"', (ROOT / 'admin.html').read_text(encoding='utf-8'))
        self.assertIn('id="music-form"', (ROOT / 'admin.html').read_text(encoding='utf-8'))
        self.assertIn('id="site-player"', html)
        for raw_path in ('/styles/tokens.css', '/styles/layout.css', '/styles/components.css', '/styles/views.css', '/scripts/app.js'):
            self.assertTrue((ROOT / unquote(raw_path.lstrip('/'))).is_file())
        self.assertEqual(len(server.gallery_items()), 66)


if __name__ == '__main__':
    unittest.main()
