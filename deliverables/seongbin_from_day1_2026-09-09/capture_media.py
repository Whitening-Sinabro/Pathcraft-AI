from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import threading,requests,json,sys,subprocess,re,time
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parent
vid=sys.argv[1];times=list(map(float,sys.argv[2].split(',')));fid=sys.argv[3] if len(sys.argv)>3 else '298'
d=json.loads((OUT/'sources'/f'{vid}.info.json').read_text(encoding='utf-8'))
fmt=next(f for f in d['formats'] if f['format_id']==fid)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        start=int(re.search(r'bytes=(\d+)',self.headers.get('Range','bytes=0-')).group(1))
        try:
            r=requests.get(fmt['url'],headers={**fmt.get('http_headers',{}),'Range':f'bytes={start}-{start+2097151}'},timeout=40)
            total=int(r.headers['Content-Range'].split('/')[-1])
            self.send_response(206)
            self.send_header('Content-Type','video/mp4')
            self.send_header('Accept-Ranges','bytes')
            self.send_header('Content-Range',f'bytes {start}-{total-1}/{total}')
            self.send_header('Content-Length',str(total-start))
            self.end_headers()
            while True:
                self.wfile.write(r.content); self.wfile.flush()
                start+=len(r.content)
                if start>=total:break
                r=requests.get(fmt['url'],headers={**fmt.get('http_headers',{}),'Range':f'bytes={start}-{min(start+2097151,total-1)}'},timeout=40)
                if r.status_code!=206:break
        except Exception: 
            try:self.send_error(502)
            except Exception:pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
folder=OUT/'frames'/vid;folder.mkdir(parents=True,exist_ok=True)
log=[]
for t in times:
    dest=folder/f'{t:09.2f}.jpg'
    if dest.exists():continue
    try:
        r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',f'http://127.0.0.1:{server.server_port}/video','-frames:v','1','-pix_fmt','yuvj420p','-q:v','2',str(dest)],capture_output=True,timeout=100)
        result={'video_id':vid,'requested_seconds':t,'returncode':r.returncode,'file_exists':dest.exists(),'format_id':fid,'file':str(dest.relative_to(OUT)),'error':r.stderr.decode('utf-8',errors='replace')}
    except subprocess.TimeoutExpired: result={'video_id':vid,'requested_seconds':t,'error':'ffmpeg timed out after 100 seconds'}
    log.append(result);print(result,flush=True)
    (folder/f'capture_{times[0]}.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
server.shutdown()
