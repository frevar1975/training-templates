import base64
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import socket
import threading
import time
import uuid
from urllib.parse import urlsplit

REPLICA = socket.gethostname()
STARTED = datetime.now(timezone.utc).isoformat()
PAGE = base64.b64decode(os.environ['HTML_BASE64'])
LOCK = threading.Lock()
COUNT = 0

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload, content_type='application/json'):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        global COUNT
        path = urlsplit(self.path).path
        if path == '/health':
            return self.reply(200, {'status': 'ok'})
        if path == '/':
            return self.reply(200, PAGE, 'text/html; charset=utf-8')
        if path == '/favicon.ico':
            return self.reply(204, b'')
        if path not in ('/api/info', '/api/oferta'):
            return self.reply(404, {'error': 'Ruta no encontrada'})
        with LOCK:
            COUNT += 1
            count = COUNT
        if path == '/api/oferta':
            time.sleep(1)  # Espera didactica, no consumo intenso de CPU.
        result = {'replica': REPLICA, 'revision': os.environ.get('CONTAINER_APP_REVISION', 'local'),
                  'request_id': uuid.uuid4().hex[:10], 'replica_requests': count,
                  'started_utc': STARTED, 'price': 240, 'currency': 'Bs'}
        if path == '/api/oferta':
            print(json.dumps({'event': 'oferta', **result}), flush=True)
        return self.reply(200, result)

    def log_message(self, fmt, *args):
        pass  # Health probes no llenan los logs.

if __name__ == '__main__':
    print(json.dumps({'event': 'inicio', 'replica': REPLICA, 'started_utc': STARTED}), flush=True)
    ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
