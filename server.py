"""Local-only dashboard and triage demo; no external API calls."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, argparse
from analyze import run,clean_text,ROOT

class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  paths={'/process':('web/process.html','text/html'),'/':('web/index.html','text/html'),'/analysis.json':('output/analysis.json','application/json')}
  if self.path not in paths:self.send_error(404);return
  name,mime=paths[self.path];data=(ROOT/name).read_bytes();self.send_response(200);self.send_header('Content-Type',mime+'; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if self.path!='/classify':self.send_error(404);return
  try:
   length=int(self.headers.get('Content-Length',0))
   if not 0<length<=20000:raise ValueError('Message is too long or empty')
   body=json.loads(self.rfile.read(length))
   if not isinstance(body,dict):raise ValueError('Expected a JSON object')
   text=body.get('message','')
   if not isinstance(text,str) or not text.strip():raise ValueError('Enter a customer message')
   p=MODEL.predict_proba([clean_text(text)])[0];idx=p.argsort()[::-1][:3]
   result={'category':MODEL.classes_[idx[0]],'score':round(float(p[idx[0]]),3),'review':bool(p[idx[0]]<.70),'alternatives':[{'category':MODEL.classes_[i],'score':round(float(p[i]),3)} for i in idx]}
   data=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
  except (ValueError,TypeError,json.JSONDecodeError) as e:self.send_error(400,str(e))
 def log_message(self,*args):pass # Do not log private messages.

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8765);ap.add_argument('--data-dir',type=Path,default=ROOT/'data/raw');a=ap.parse_args()
 MODEL,_,_=run(a.data_dir)
 print(f'Open http://127.0.0.1:{a.port} (Ctrl-C to stop)',flush=True)
 ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
