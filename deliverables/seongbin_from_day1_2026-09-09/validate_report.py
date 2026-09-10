from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
import datetime, hashlib, json, sys
from playwright.sync_api import sync_playwright
from planner_crosscheck import without_notes
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
ROOT=O.parents[1]
manifest=json.loads((O/'report_manifest.json').read_text(encoding='utf-8'))
ledger=json.loads((O/'확인대장.json').read_text(encoding='utf-8'))
metadata=json.loads((O/'방송목록.json').read_text(encoding='utf-8'))
durations={v['id']:v['duration'] for v in metadata['videos']}
errors=[];links=[];screens=[];browser_checks=[]
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='a' and 'href' in a:self.refs.append(a['href'])
        if tag in ['img','script'] and 'src' in a:self.refs.append(a['src'])
parsers={}
for row in manifest['documents']:
    path=O/row['html'];p=Parser();p.feed(path.read_text(encoding='utf-8'));parsers[path]=p
    if '{timeline}' in path.read_text(encoding='utf-8') or '{status}' in path.read_text(encoding='utf-8'):errors.append('unexpanded template '+path.name)
for path,p in parsers.items():
    for ref in p.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        dest=(path.parent/unquote(u.path)).resolve() if u.path else path
        exists=dest.is_file();links.append({'from':path.name,'target':ref,'exists':exists})
        if not exists:errors.append('missing '+path.name+' -> '+ref)
        if u.fragment and dest in parsers and unquote(u.fragment) not in parsers[dest].ids:errors.append('missing fragment '+ref)
for r in ledger['observations']:
    v=r['video_id'];u=urlsplit(r['url']);q=parse_qs(u.query)
    if q.get('v')!=[v] or q.get('t')!=[str(r['start_seconds'])+'s']:errors.append('timestamp mismatch '+r['id'])
    if not 0<=r['start_seconds']<=r['end_seconds']<=durations[v]+2:errors.append('out of duration '+r['id'])
    if r['execution_verified']:errors.append('unsupported execution flag '+r['id'])
    if not r['caption_segment_indices']:errors.append('missing caption evidence '+r['id'])
for r in ledger['visual_reviews']:
    if hashlib.sha256((O/r['file']).read_bytes()).hexdigest()!=r['sha256']:errors.append('changed visual '+r['id'])
receipts=[]
for path in sorted((O/'mcp_session').glob('response_*.json')):
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('isError'):continue
    for block in data.get('content',[]):
        if block.get('type')!='text':continue
        text=block['text']
        if not text.startswith('### Result\n'):continue
        try:
            result=json.loads(text.split('\n',2)[1])
        except (ValueError,IndexError):continue
        for item in result if isinstance(result,list) else [result]:
            if isinstance(item,dict) and 'time' in item and item.get('ready',item.get('readyState',0))>=2:
                # Earlier receipts have the page URL in the MCP footer; later captures return it per frame.
                import re
                footer_url=re.search(r'Page URL: (https://[^\s]+)',text)
                item['evidence_url']=item.get('url') or (footer_url[1] if footer_url else '')
                receipts.append((item,path.name))
for r in ledger.get('original_video_frame_reviews',[]):
    if hashlib.sha256((O/r['file']).read_bytes()).hexdigest()!=r['sha256']:errors.append('changed original frame '+r['id'])
    if not 0<=r['start_seconds']<=durations[r['video_id']]:errors.append('original frame timestamp outside duration '+r['id'])
    if not any(abs(item['time']-r['start_seconds'])<0.1 and item.get('width')==1280 and item.get('height')==720 and parse_qs(urlsplit(item['evidence_url']).query).get('v')==[r['video_id']] for item,path in receipts):errors.append('no MCP video/timestamp/resolution receipt '+r['id'])
for r in json.loads((O/'planner_source_validation.json').read_text(encoding='utf-8'))['files']:
    if hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest()!=r['sha256']:errors.append('changed planner '+r['source'])

# Cross-session preservation and semantic deduplication: same frame is never counted twice.
frames=ledger.get('original_video_frame_reviews',[])
frame_keys=[(r['video_id'],r['start_seconds']) for r in frames]
if len(frame_keys)!=len(set(frame_keys)):errors.append('duplicate original frame identity')
old=O/'session_backups/resume_20260909T164134Z'
inherited=json.loads((old/'원본_화면대장.json').read_text(encoding='utf-8'))['frames']
current={r['id']:r for r in frames}
for r in inherited:
    if r['id'] not in current or current[r['id']]['sha256']!=r['sha256']:errors.append('lost inherited frame '+r['id'])
    if current.get(r['id'],{}).get('reviewed_utc')!=r['reviewed_utc']:errors.append('changed inherited review date '+r['id'])
if (O/'stash_notes.py').read_bytes()!=(old/'stash_notes.py').read_bytes():errors.append('changed inherited stash source')
if (O/'보관함_정리방식.md').read_bytes()!=(old/'보관함_정리방식.md').read_bytes():errors.append('changed inherited stash report')
history=json.loads((O/'교차검증_이력.json').read_text(encoding='utf-8'))
for event in history['events']:
    for ref in event['frames']:
        if ref['id'] not in current:errors.append('event points to absent frame '+ref['id'])
audit=json.loads((O/'planner_crosscheck.json').read_text(encoding='utf-8'))
for r in audit['files']:
    for path,key in [(ROOT/r['repository_file'],'repository_sha256'),(ROOT/r['original_file'],'original_sha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=r[key]:errors.append('changed crosscheck source '+str(path))
    installed=r['installed_original']
    if installed['exists'] and hashlib.sha256(Path(installed['path']).read_bytes()).hexdigest()!=installed['sha256']:errors.append('changed installed planner '+installed['path'])
for r in audit['research_copies']:
    path=O/r['file'];source=ROOT/r['source']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=r['sha256']:errors.append('changed research copy '+r['file'])
    a=json.loads(path.read_text(encoding='utf-8'));b=json.loads(source.read_text(encoding='utf-8'))
    if without_notes(a)!=without_notes(b):errors.append('research copy changes more than name/notes '+r['file'])

shots=O/'validation';shots.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,channel='msedge')
    for width,height in [(1440,1000),(390,844)]:
        context=browser.new_context(viewport={'width':width,'height':height})
        page=context.new_page();page_errors=[]
        page.on('pageerror',lambda e:page_errors.append(str(e)))
        for row in manifest['documents']:
            path=O/row['html'];page.goto(path.as_uri(),wait_until='load')
            metrics=page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,images:[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0})),h1:document.querySelector('h1')?.textContent,tableCount:document.querySelectorAll('table').length})''')
            result={'page':row['html'],'viewport':width,**metrics};browser_checks.append(result)
            if metrics['scrollWidth']>width:errors.append(f'page overflow {width} '+row['html'])
            if not metrics['h1']:errors.append('missing title '+row['html'])
            if any(not i['loaded'] for i in metrics['images']):errors.append('unloaded image '+row['html'])
            if row['html'] in ['index.html','첫날_상세분석.html']:
                dest=shots/f'{path.stem}_{width}.png';page.screenshot(path=str(dest),full_page=False);screens.append(dest.relative_to(O).as_posix())
        page.goto((O/'첫날_상세분석.html').as_uri(),wait_until='load')
        count=page.locator('tbody tr').count();page.locator('#filter').fill('세케마')
        visible=page.locator('tbody tr:visible').count()
        if not 0<visible<count:errors.append(f'filter failed {width}')
        page.locator('#filter').fill('')
        if page.locator('tbody tr:visible').count()!=count:errors.append(f'filter reset failed {width}')
        browser_checks.append({'viewport':width,'filter_total':count,'filter_matching':visible,'filter_reset':True})
        errors.extend(page_errors);context.close()
    browser.close()
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'documents':len(manifest['documents']),
        'local_links_checked':len(links),'caption_observations_checked':len(ledger['observations']),
        'original_video_frame_hashes_and_mcp_times_checked':len(ledger.get('original_video_frame_reviews',[])),
        'planner_sources_hash_checked':5,'inherited_frames_preserved':len(inherited),
        'repository_planners_compared':len(audit['files']),'installed_planners_hash_checked':sum(r['installed_original']['exists'] for r in audit['files']),
        'research_planner_copies_parsed':len(audit['research_copies']),'duplicate_frames':len(frame_keys)-len(set(frame_keys)),
        'errors':errors,'passed':not errors,'browser_checks':browser_checks,'screenshots':screens,
        'scope':'Document rendering, local links, caption references, immutable source hashes. Not original video playback or in-game validation.'}
(O/'report_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['documents','local_links_checked','caption_observations_checked','passed','errors']},ensure_ascii=False))
sys.exit(bool(errors))
