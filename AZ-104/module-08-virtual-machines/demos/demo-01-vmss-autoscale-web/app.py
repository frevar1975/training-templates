import hashlib,json,os,socket,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse
HOST=socket.gethostname()
GATE=threading.BoundedSemaphore(8)
PAGE=r'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Escalado en vivo AZ104</title><style>body{background:#101828;color:#fff;font:18px system-ui;max-width:760px;margin:60px auto;padding:24px}button{padding:16px;margin:8px;border:0;border-radius:10px;font-size:18px;background:#70e1c8}pre{white-space:pre-wrap;background:#24334b;padding:20px;border-radius:12px}small{color:#bcc9dd}</style><h1>Hagamos crecer nuestros servidores</h1><p>Cada solicitud realiza un cálculo real en el servidor.</p><button onclick="once()">Generar trabajo</button><button onclick="start()">Participar continuamente</button><button onclick="stop()">Detener mi participación</button><pre id="result">Listo para comenzar</pre><p id="count">Solicitudes completadas: 0</p><small>Detener pausa las siguientes solicitudes. La solicitud en curso puede terminar. Las respuestas pueden llegar del mismo servidor: el balanceador distribuye conexiones y no alterna estrictamente.</small><script>let active=false,n=0;async function once(){try{let r=await fetch('/work?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('Servidor ocupado '+r.status);let d=await r.json();document.getElementById('result').textContent='Servidor: '+d.server+'\nTiempo de cálculo: '+d.seconds+' s';document.getElementById('count').textContent='Solicitudes completadas: '+(++n);}catch(e){document.getElementById('result').textContent=e.message;}}async function start(){if(active)return;active=true;while(active){await once();await new Promise(r=>setTimeout(r,300));}}function stop(){active=false;}</script></html>'''
class Handler(BaseHTTPRequestHandler):
    def send(self,status,body,kind):
        body=body.encode();self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers()
        try:self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/health':return self.send(200,'ok','text/plain')
        if path=='/':return self.send(200,PAGE,'text/html; charset=utf-8')
        if path!='/work':return self.send(404,'No encontrado','text/plain')
        if not GATE.acquire(timeout=1):return self.send(429,'Ocupado','text/plain')
        try:
            started=time.monotonic()
            hashlib.pbkdf2_hmac('sha256',os.urandom(24),b'az104-demo',1000000)
            result=json.dumps({'server':HOST,'seconds':round(time.monotonic()-started,2)})
            self.send(200,result,'application/json')
        finally:GATE.release()
    def log_message(self,*args):pass
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8080'))),Handler).serve_forever()
