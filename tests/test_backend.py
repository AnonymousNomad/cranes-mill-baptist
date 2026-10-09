import io
import json
import os
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db
import server


class HandlerHarness(server.ChurchHandler):
    def __init__(self, path, payload=b'', headers=None):
        self.path = path
        self.rfile = io.BytesIO(payload)
        self.wfile = io.BytesIO()
        self.headers = {'Content-Length': str(len(payload)), 'Accept': 'application/json', **(headers or {})}
        self.status = None
        self.response_headers = {}

    def send_response(self, status):
        self.status = status

    def send_header(self, name, value):
        self.response_headers[name] = value

    def end_headers(self):
        return

    def result(self):
        body = self.wfile.getvalue()
        if self.response_headers.get('Content-Type', '').startswith('application/json'):
            return json.loads(body.decode('utf-8'))
        return body


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temp_dir.name) / 'church.sqlite3'
        server.db.DB_PATH = db.DB_PATH
        server.ADMIN_TOKEN = 'test-token'
        db.initialize_database()

    def tearDown(self):
        self.temp_dir.cleanup()

    def call(self, method, path, payload=None, token=None, headers=None):
        body = b'' if payload is None else json.dumps(payload).encode('utf-8')
        request_headers = dict(headers or {})
        if token:
            request_headers['Authorization'] = f'Bearer {token}'
        handler = HandlerHarness(path, body, request_headers)
        getattr(server.ChurchHandler, f'do_{method}')(handler)
        return handler.status, handler.result()

    def test_seed_records_and_crud(self):
        self.assertEqual(len(db.list_sermons()), 1)
        self.assertEqual(len(db.list_events()), 4)
        self.assertEqual(db.list_site_content()['phone'], '(830) 899-7936')
        self.assertEqual(db.list_site_content()['facebook_url'], 'https://www.facebook.com/CMBCCL/')
        self.assertEqual(db.list_site_content()['instagram_url'], '')
        self.assertEqual(len(db.list_ministries()), 4)
        with db.connect() as connection:
            db.seed_if_empty(connection)
            indexes = {row['name'] for row in connection.execute("SELECT name FROM sqlite_schema WHERE type = 'index'")}
        self.assertTrue({'idx_sermons_published', 'idx_events_schedule', 'idx_ministries_order', 'idx_prayer_created', 'idx_music_order'} <= indexes)
        self.assertEqual(db.create_music_track(('Welcome song', 'Cranes Mill', '/assets/music/welcome.mp3', 1)), 1)
        self.assertEqual(len(db.list_music_tracks()), 1)
        db.set_site_content([('phone', '(830) 555-0100')])
        self.assertEqual(db.list_site_content()['phone'], '(830) 555-0100')
        db.create_prayer_request(('Odinn', 'odinn@example.test', 'Please pray.'))
        self.assertEqual(len(db.list_prayer_requests()), 1)
        self.assertEqual(db.create_sermon(('New message', 'Speaker', '2026-10-20', '', '', '', '')), 2)
        self.assertEqual(db.create_event(('New event', '2026-10-21', '', '', '')), 5)
        self.assertEqual(db.create_ministry(('New ministry', 'Summary', 'Learn more', 'contact', '', 10)), 5)

    def test_validation_and_request_boundaries(self):
        with self.assertRaises(ValueError): server.text_field({'name': 4}, 'name', 10)
        with self.assertRaises(ValueError): server.text_field({'name': 'x' * 11}, 'name', 10)
        with self.assertRaises(ValueError): server.date_field({'date': '10/20/2026'}, 'date')
        with self.assertRaises(ValueError): server.email_field({'email': 'not-an-email'})
        with self.assertRaises(ValueError): server.route_field({'action_route': 'private'})
        with self.assertRaises(ValueError): server.int_field({'sort_order': 'bad'}, 'sort_order', 0, 9)
        with self.assertRaises(ValueError): server.int_field({'sort_order': 10}, 'sort_order', 0, 9)
        with self.assertRaises(ValueError): server.media_field({'video_url': 'javascript:alert(1)'}, 'video_url')
        with self.assertRaises(ValueError): server.external_url_field({'facebook_url': 'javascript:alert(1)'}, 'facebook_url')
        self.assertEqual(server.external_url_field({'facebook_url': 'https://example.test/church'}, 'facebook_url'), 'https://example.test/church')
        self.assertEqual(server.media_field({'image_url': '/church/photo.jpg'}, 'image_url'), '/church/photo.jpg')
        for payload in (b'[]', b'not-json', 'é'.encode('latin1')):
            with self.assertRaises(ValueError): server.request_body(HandlerHarness('/api/test', payload))
        with self.assertRaises(ValueError): server.request_body(HandlerHarness('/api/test', b'{}', {'Content-Length': '0'}))
        with self.assertRaises(ValueError): server.request_body(HandlerHarness('/api/test', b'{}', {'Content-Length': 'bad'}))
        with self.assertRaises(ValueError): server.request_body(HandlerHarness('/api/test', b'{}', {'Content-Length': str(server.MAX_BODY_BYTES + 1)}))
        with self.assertRaises(ValueError): server.request_body(HandlerHarness('/api/test', b'{}', {'Content-Length': '3'}))
        self.assertEqual(server.text_field({}, 'optional', 4, False), '')

    def test_static_and_auth_boundaries(self):
        for path in ('/../server.py', '/server.py', '/.site-git/config', '/data/church.sqlite3'):
            with self.assertRaises(PermissionError): server.safe_static_path(path)
        with self.assertRaises(FileNotFoundError): server.safe_static_path('/missing.html')
        self.assertEqual(server.safe_static_path('/index.html').name, 'index.html')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'inside'
            outside_dir = Path(temporary) / 'outside'
            root.mkdir()
            outside_dir.mkdir()
            outside = outside_dir / 'outside.txt'
            outside.write_text('outside', encoding='utf-8')
            (root / 'link').symlink_to(outside)
            with patch.object(server, 'ROOT', root):
                with self.assertRaises(PermissionError): server.safe_static_path('/link')
        no_token = HandlerHarness('/api/admin/health')
        self.assertFalse(server.admin_is_authorized(no_token))
        self.assertFalse(server.admin_is_authorized(HandlerHarness('/api/admin/health', headers={'Authorization': 'Basic x'})))
        self.assertFalse(server.admin_is_authorized(HandlerHarness('/api/admin/health', headers={'Authorization': 'Bearer wrong'})))
        self.assertTrue(server.admin_is_authorized(HandlerHarness('/api/admin/health', headers={'Authorization': 'Bearer test-token'})))
        original = server.ADMIN_TOKEN
        server.ADMIN_TOKEN = ''
        self.assertFalse(server.admin_is_authorized(HandlerHarness('/api/admin/health', headers={'Authorization': 'Bearer test-token'})))
        server.ADMIN_TOKEN = original

    def test_public_and_admin_routes(self):
        status, health = self.call('GET', '/api/health')
        self.assertEqual((status, health['status']), (200, 'ok'))
        status, gallery = self.call('GET', '/api/gallery')
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(gallery['items']), 1)
        status, site = self.call('GET', '/api/site')
        self.assertEqual((status, len(site['ministries'])), (200, 4))
        status, events = self.call('GET', '/api/events?month=2026-10')
        self.assertEqual((status, len(events['items'])), (200, 4))
        status, sermons = self.call('GET', '/api/sermons')
        self.assertEqual((status, len(sermons['items'])), (200, 1))
        status, _ = self.call('GET', '/api/admin/health')
        self.assertEqual(status, 401)
        status, _ = self.call('GET', '/api/admin/health', headers={'Authorization': 'Bearer test-token'})
        self.assertEqual(status, 200)
        status, _ = self.call('GET', '/api/admin/prayer-requests')
        self.assertEqual(status, 401)
        status, _ = self.call('POST', '/api/prayer-requests', {'name': 'Visitor', 'email': '', 'message': 'Hello'})
        self.assertEqual(status, 201)
        status, requests = self.call('GET', '/api/admin/prayer-requests', headers={'Authorization': 'Bearer test-token'})
        self.assertEqual((status, len(requests['items'])), (200, 1))
        status, _ = self.call('POST', '/api/prayer-requests', {'name': 'Visitor'})
        self.assertEqual(status, 400)
        status, _ = self.call('POST', '/api/admin/sermons', {'title': 'No token', 'speaker': 'x', 'published_on': '2026-10-20'})
        self.assertEqual(status, 401)
        status, _ = self.call('POST', '/api/admin/sermons', {'title': 'Admin message', 'speaker': 'Speaker', 'published_on': '2026-10-20'}, 'test-token')
        self.assertEqual(status, 201)
        site_payload = {'address': '10215 FM 2673', 'phone': '(830) 555-0100', 'email': 'office@example.test', 'facebook_url': 'https://facebook.example/church', 'instagram_url': '', 'youtube_url': '', 'worship_time': 'Sunday at 11:00 AM', 'welcome_heading': 'Welcome home.', 'welcome_body': 'Come worship with us.', 'giving_body': 'Give with purpose.'}
        status, _ = self.call('POST', '/api/admin/site', site_payload, 'test-token')
        self.assertEqual(status, 201)
        self.assertEqual(db.list_site_content()['email'], 'office@example.test')
        self.assertEqual(db.list_site_content()['facebook_url'], 'https://facebook.example/church')
        status, _ = self.call('POST', '/api/admin/events', {'title': 'Admin event', 'event_date': '2026-10-21'}, 'test-token')
        self.assertEqual(status, 201)
        status, _ = self.call('POST', '/api/admin/ministries', {'title': 'Admin ministry', 'summary': 'Summary', 'action_route': 'contact', 'sort_order': '5'}, 'test-token')
        self.assertEqual(status, 201)
        status, music = self.call('GET', '/api/music')
        self.assertEqual((status, len(music['items'])), (200, 0))
        status, _ = self.call('POST', '/api/admin/music', {'title': 'No token', 'audio_url': '/assets/music/welcome.mp3'})
        self.assertEqual(status, 401)
        status, _ = self.call('POST', '/api/admin/music', {'title': 'Praise song', 'artist': 'Choir', 'audio_url': '/assets/music/welcome.mp3', 'sort_order': '2'}, 'test-token')
        self.assertEqual(status, 201)
        status, music = self.call('GET', '/api/music')
        self.assertEqual((status, len(music['items'])), (200, 1))
        status, _ = self.call('POST', '/api/admin/music', {'title': 'Missing audio'}, 'test-token')
        self.assertEqual(status, 400)
        status, _ = self.call('POST', '/api/no-route', {})
        self.assertEqual(status, 404)
        status, _ = self.call('GET', '/missing.html')
        self.assertEqual(status, 404)
        status, _ = self.call('GET', '/server.py')
        self.assertEqual(status, 403)
        status, body = self.call('GET', '/index.html')
        self.assertEqual(status, 200)
        self.assertIn(b'Cranes Mill Baptist Church', body)
        HandlerHarness('/index.html').log_message('ignored')

    def test_storage_and_server_fail_closed(self):
        for route, target in (('/api/gallery', 'gallery_items'), ('/api/site', 'list_site_content'), ('/api/sermons', 'list_sermons'), ('/api/events', 'list_events'), ('/api/music', 'list_music_tracks')):
            owner = server if target == 'gallery_items' else server.db
            with patch.object(owner, target, side_effect=OSError):
                status, _ = self.call('GET', route)
                self.assertEqual(status, 503)
        with patch.object(server.db, 'list_prayer_requests', side_effect=OSError):
            status, _ = self.call('GET', '/api/admin/prayer-requests', headers={'Authorization': 'Bearer test-token'})
            self.assertEqual(status, 503)
        with patch.object(server.db, 'create_prayer_request', side_effect=OSError):
            status, _ = self.call('POST', '/api/prayer-requests', {'name': 'Visitor', 'message': 'Hello'})
            self.assertEqual(status, 503)
        site_payload = {'address': '10215 FM 2673', 'phone': '(830) 555-0100', 'email': 'office@example.test', 'facebook_url': '', 'instagram_url': '', 'youtube_url': '', 'worship_time': 'Sunday at 11:00 AM', 'welcome_heading': 'Welcome home.', 'welcome_body': 'Come worship with us.', 'giving_body': 'Give with purpose.'}
        with patch.object(server.db, 'set_site_content', side_effect=OSError):
            status, _ = self.call('POST', '/api/admin/site', site_payload, 'test-token')
            self.assertEqual(status, 503)
        with patch.object(server, 'ThreadingHTTPServer') as factory, patch.object(server.db, 'initialize_database'):
            fake_server = factory.return_value
            fake_server.server_address = ('127.0.0.1', 4173)
            fake_server.serve_forever.side_effect = KeyboardInterrupt
            with patch.dict(os.environ, {'CHURCH_HOST': '127.0.0.1', 'CHURCH_PORT': '4173'}):
                server.run()
            fake_server.server_close.assert_called_once()

        class MainServer:
            server_address = ('127.0.0.1', 4173)

            def __init__(self, _address, _handler):
                return

            def serve_forever(self):
                raise KeyboardInterrupt

            def server_close(self):
                return

        with patch('http.server.ThreadingHTTPServer', MainServer), patch.object(server.db, 'initialize_database'):
            with patch.dict(os.environ, {'CHURCH_HOST': '127.0.0.1', 'CHURCH_PORT': '4173'}):
                runpy.run_path(str(Path(server.__file__)), run_name='__main__')


if __name__ == '__main__':
    unittest.main()
