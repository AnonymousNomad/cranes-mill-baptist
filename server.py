import hashlib
import hmac
import json
import mimetypes
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import db

ROOT = Path(__file__).resolve().parent
MAX_BODY_BYTES = 64 * 1024
ADMIN_TOKEN = os.environ.get('CHURCH_ADMIN_TOKEN', '').strip()
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
EMAIL_PATTERN = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_ROUTES = {'about', 'contact', 'events', 'give', 'ministries', 'sermons'}
SITE_TEXT_LIMITS = {
    'address': 160,
    'phone': 40,
    'worship_time': 120,
    'welcome_heading': 160,
    'welcome_body': 1000,
    'giving_body': 1000,
}
SITE_URL_FIELDS = {'facebook_url', 'instagram_url', 'youtube_url'}


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    handler.end_headers()
    handler.wfile.write(body)


def error_response(handler, status, code, message):
    json_response(handler, status, {'error': code, 'message': message})


def request_body(handler):
    try:
        length = int(handler.headers.get('Content-Length', '0'))
    except ValueError as error:
        raise ValueError('invalid_content_length') from error
    if length < 0 or length > MAX_BODY_BYTES:
        raise ValueError('request_too_large')
    raw = handler.rfile.read(length)
    if len(raw) != length:
        raise ValueError('incomplete_request')
    try:
        value = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('invalid_json') from error
    if not isinstance(value, dict):
        raise ValueError('object_required')
    return value


def text_field(payload, key, maximum, required=True):
    value = payload.get(key, '')
    if not isinstance(value, str):
        raise ValueError(f'{key}_must_be_text')
    value = value.strip()
    if required and not value:
        raise ValueError(f'{key}_required')
    if len(value) > maximum:
        raise ValueError(f'{key}_too_long')
    return value


def date_field(payload, key):
    value = text_field(payload, key, 10)
    if not DATE_PATTERN.fullmatch(value):
        raise ValueError(f'{key}_must_be_iso_date')
    return value


def email_field(payload):
    value = text_field(payload, 'email', 160, required=False)
    if value and not EMAIL_PATTERN.fullmatch(value):
        raise ValueError('email_invalid')
    return value


def route_field(payload):
    value = text_field(payload, 'action_route', 40, required=False) or 'contact'
    if value not in ALLOWED_ROUTES:
        raise ValueError('action_route_invalid')
    return value


def int_field(payload, key, minimum, maximum):
    value = payload.get(key, minimum)
    try:
        parsed = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f'{key}_must_be_integer') from error
    if parsed < minimum or parsed > maximum:
        raise ValueError(f'{key}_out_of_range')
    return parsed


def media_field(payload, key):
    value = text_field(payload, key, 500, required=False)
    if value and (value.startswith('//') or (not value.startswith('/') and urlparse(value).scheme not in {'http', 'https'})):
        raise ValueError(f'{key}_invalid')
    return value


def external_url_field(payload, key):
    value = text_field(payload, key, 500, required=False)
    if value and (value.startswith('//') or urlparse(value).scheme not in {'http', 'https'}):
        raise ValueError(f'{key}_invalid')
    return value


def safe_static_path(request_path):
    relative = unquote(request_path).lstrip('/') or 'index.html'
    parts = Path(relative).parts
    if any(part.startswith('.') for part in parts) or 'data' in parts or Path(relative).suffix.lower() in {'.py', '.sqlite3', '.db'}:
        raise PermissionError('private_path')
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as error:
        raise PermissionError('path_outside_site') from error
    if not candidate.is_file():
        raise FileNotFoundError(relative)
    return candidate


def gallery_items():
    items = []
    for candidate in sorted((ROOT / 'church').iterdir(), key=lambda path: path.name.lower()):
        if candidate.is_file() and candidate.suffix.lower() in IMAGE_EXTENSIONS:
            items.append({'name': candidate.name, 'url': f'/church/{quote(candidate.name)}'})
    return items


def admin_is_authorized(handler):
    provided = handler.headers.get('Authorization', '')
    if not ADMIN_TOKEN or not provided.startswith('Bearer '):
        return False
    supplied_token = provided[7:].strip().encode('utf-8')
    expected_token = ADMIN_TOKEN.encode('utf-8')
    return hmac.compare_digest(hashlib.sha256(supplied_token).digest(), hashlib.sha256(expected_token).digest())


class ChurchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/gallery':
            try:
                items = gallery_items()
            except OSError:
                error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'media_unavailable', 'The gallery is temporarily unavailable.')
                return
            json_response(self, HTTPStatus.OK, {'items': items})
            return
        if parsed.path == '/api/site':
            try:
                payload = {'site': db.list_site_content(), 'ministries': db.list_ministries()}
            except OSError:
                error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'storage_unavailable', 'Site content is temporarily unavailable.')
                return
            json_response(self, HTTPStatus.OK, payload)
            return
        if parsed.path == '/api/sermons':
            try:
                items = db.list_sermons()
            except OSError:
                error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'storage_unavailable', 'The sermon archive is temporarily unavailable.')
                return
            json_response(self, HTTPStatus.OK, {'items': items})
            return
        if parsed.path == '/api/events':
            try:
                items = db.list_events()
            except OSError:
                error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'storage_unavailable', 'The event calendar is temporarily unavailable.')
                return
            json_response(self, HTTPStatus.OK, {'items': items, 'query': parse_qs(parsed.query)})
            return
        if parsed.path == '/api/music':
            try:
                items = db.list_music_tracks()
            except OSError:
                error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'storage_unavailable', 'The music player is temporarily unavailable.')
                return
            json_response(self, HTTPStatus.OK, {'items': items})
            return
        if parsed.path == '/api/health':
            json_response(self, HTTPStatus.OK, {'status': 'ok'})
            return
        if parsed.path == '/api/admin/health':
            if not admin_is_authorized(self):
                error_response(self, HTTPStatus.UNAUTHORIZED, 'admin_required', 'A valid administrator token is required.')
                return
            json_response(self, HTTPStatus.OK, {'status': 'authorized'})
            return
        if parsed.path == '/api/admin/prayer-requests':
            if not admin_is_authorized(self):
                error_response(self, HTTPStatus.UNAUTHORIZED, 'admin_required', 'A valid administrator token is required.')
                return
            try:
                items = db.list_prayer_requests()
            except OSError:
                error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'storage_unavailable', 'Prayer requests are temporarily unavailable.')
                return
            json_response(self, HTTPStatus.OK, {'items': items})
            return
        self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = request_body(self)
            if parsed.path == '/api/prayer-requests':
                record = (text_field(payload, 'name', 80), email_field(payload), text_field(payload, 'message', 2000))
                identifier = db.create_prayer_request(record)
                json_response(self, HTTPStatus.CREATED, {'id': identifier, 'status': 'received'})
                return
            if parsed.path == '/api/admin/sermons':
                self.require_admin()
                record = (text_field(payload, 'title', 160), text_field(payload, 'speaker', 120), date_field(payload, 'published_on'), text_field(payload, 'scripture', 120, False), text_field(payload, 'summary', 1000, False), media_field(payload, 'video_url'), media_field(payload, 'image_url'))
                identifier = db.create_sermon(record)
                json_response(self, HTTPStatus.CREATED, {'id': identifier})
                return
            if parsed.path == '/api/admin/site':
                self.require_admin()
                limits = {**SITE_TEXT_LIMITS, **{key: 500 for key in SITE_URL_FIELDS}}
                record = [(key, external_url_field(payload, key) if key in SITE_URL_FIELDS else text_field(payload, key, limit)) for key, limit in limits.items()]
                record.append(('email', email_field(payload)))
                db.set_site_content(record)
                json_response(self, HTTPStatus.CREATED, {'status': 'saved'})
                return
            if parsed.path == '/api/admin/events':
                self.require_admin()
                record = (text_field(payload, 'title', 160), date_field(payload, 'event_date'), text_field(payload, 'event_time', 80, False), text_field(payload, 'location', 160, False), text_field(payload, 'description', 1000, False))
                identifier = db.create_event(record)
                json_response(self, HTTPStatus.CREATED, {'id': identifier})
                return
            if parsed.path == '/api/admin/ministries':
                self.require_admin()
                record = (text_field(payload, 'title', 120), text_field(payload, 'summary', 600), text_field(payload, 'action_label', 80, False), route_field(payload), media_field(payload, 'image_url'), int_field(payload, 'sort_order', 0, 999))
                identifier = db.create_ministry(record)
                json_response(self, HTTPStatus.CREATED, {'id': identifier})
                return
            if parsed.path == '/api/admin/music':
                self.require_admin()
                audio_url = media_field(payload, 'audio_url')
                if not audio_url:
                    raise ValueError('audio_url_required')
                record = (text_field(payload, 'title', 160), text_field(payload, 'artist', 120, False), audio_url, int_field(payload, 'sort_order', 0, 999))
                identifier = db.create_music_track(record)
                json_response(self, HTTPStatus.CREATED, {'id': identifier})
                return
            error_response(self, HTTPStatus.NOT_FOUND, 'route_not_found', 'The requested API route does not exist.')
        except PermissionError:
            error_response(self, HTTPStatus.UNAUTHORIZED, 'admin_required', 'A valid administrator token is required.')
        except ValueError as error:
            error_response(self, HTTPStatus.BAD_REQUEST, 'invalid_request', str(error))
        except OSError:
            error_response(self, HTTPStatus.SERVICE_UNAVAILABLE, 'storage_unavailable', 'The request could not be stored.')

    def require_admin(self):
        if not admin_is_authorized(self):
            raise PermissionError('admin_required')

    def serve_static(self, request_path):
        try:
            target = safe_static_path(request_path)
        except PermissionError:
            error_response(self, HTTPStatus.FORBIDDEN, 'path_forbidden', 'That path is not available.')
            return
        except FileNotFoundError:
            error_response(self, HTTPStatus.NOT_FOUND, 'not_found', 'That page was not found.')
            return
        content_type = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(target.stat().st_size))
        self.end_headers()
        with target.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                self.wfile.write(chunk)

    def log_message(self, _format, *_args):
        return


def run():
    db.initialize_database()
    host = os.environ.get('CHURCH_HOST', '127.0.0.1')
    port = int(os.environ.get('CHURCH_PORT', '4173'))
    server = ThreadingHTTPServer((host, port), ChurchHandler)
    print(f'Cranes Mill site listening on http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    run()
