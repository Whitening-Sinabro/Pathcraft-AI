import json,re
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
rows=json.loads((P/'cafe_article_index.json').read_text(encoding='utf-8'))
core={184,179,173,181,195,208,176,224,223,125,145,109}
covered=[]
pw={}
for pf in sorted((P/'cafe_playwright').glob('batch_*.json')):
 for pd in json.loads(pf.read_text(encoding='utf-8')):
  pd['evidence_file']=str(pf.relative_to(P));pw[pd['article_id']]=pd
for r in rows:
 aid=r['article_id'];f=P/'cafe_reads'/f'article_{aid}.json'
 r['topic']='kitava_build' if r['menu_id']==6 else 'build_research' if r['menu_id']==3 else 'common_tip' if r['menu_id']==7 else 'consultation_or_other'
 r['scope_reason']='Kitava board or research/common tips or directly related cross-board title' if r['scope']=='related_body' else 'Other build board without a Kitava/act dependency in the observed title' if r['scope']=='other_build_board_title_screened' else 'Nonmechanical/community or other topic title; not needed for this Kitava priority case'
 d=json.loads(f.read_text(encoding='utf-8')) if f.exists() else None
 t=d['content'] if d else ''
 n=len([x for x in t.splitlines() if '목록 항목 ' in x and '답글쓰기' in x])
 creator=[x for x in t.splitlines() if '목록 항목 탱커의정석' in x]
 body=t.split('제목 댓글')[0]
 image_rows=[x for x in body.splitlines() if re.search(r'\d+ 그래픽 ',x) and not any(v in x for v in ['객체','더보기'])]
 links=sorted(set(re.findall(r'https?://[^\s,]+',t)))
 links=[x for x in links if not any(h in x for h in ['cafe.naver.com','gfmarket.naver.com'])]
 title_ok=bool(re.search(r'\d+ 제목 '+re.escape(r['title']),t))
 c={'article_id':aid,'url':r['url'],'core':aid in core,'scope':r['scope'],'title_screened':True,'body_text':'read' if d and title_ok and '단추 URL 복사' in t else 'not_read','author_corrections':'read_'+str(len(creator))+'_creator_comment_rows' if d and n>=r['comments_list'] else 'not_complete' if d else 'not_read','comments_expected_list':r['comments_list'],'comment_rows_loaded':n,'comments_complete_against_list':bool(d and n>=r['comments_list']),'image_body':'not_present_in_accessibility_text' if d and not image_rows else 'not_visually_verified' if d else 'unknown','attachment_status':'linked_resources_separately_reviewed' if aid in [184,176,224] else 'executable_identified_not_downloaded_or_run' if aid==109 else 'links_discovered_not_all_opened' if links else 'none_identified_in_read_text' if d else 'unknown','external_links':links,'evidence_file':str(f.relative_to(P)) if d else None,'observed_at':d['observed_at'] if d else None,'published_date_list':r['date_list'],'edited_at':None,'edit_time_note':'No reliable separate edit timestamp captured; body may have been revised.'}
 pd=pw.get(aid)
 if pd and pd.get('title'):
  pn=len(pd.get('comments',[]));pc=sum(x.get('author')=='탱커의정석' for x in pd.get('comments',[]))
  c.update(body_text='read' if pd['title'].strip()==r['title'].strip() else 'title_mismatch',author_corrections='read_'+str(pc)+'_creator_comment_rows' if pn>=r['comments_list'] else 'not_complete',comment_rows_loaded=pn,comments_complete_against_list=pn>=r['comments_list'],image_body='not_visually_verified' if pd.get('images') else 'none_in_article_DOM',external_links=sorted(set(x['url'] for x in pd.get('links',[]) if x.get('url','').startswith('http') and 'cafe.naver.com' not in x['url'])),evidence_file=pd['evidence_file'],observed_at=pd['observed_at'],published_date_body=pd.get('date'),transport=pd['transport'])
 elif pd:
  c['playwright_attempt']={'status':'failed','error':pd.get('error'),'page_text':pd.get('page_text'),'evidence_file':pd['evidence_file']}
 covered.append(c)
counts={'listed_distinct_articles':len(rows),'target_body_articles':sum(r['scope']=='related_body' for r in rows),'body_text_read':sum(c['body_text']=='read' for c in covered),'target_body_read':sum(c['body_text']=='read' and c['scope']=='related_body' for c in covered),'target_comments_complete':sum(c['body_text']=='read' and c['scope']=='related_body' and c['comments_complete_against_list'] for c in covered),'core_body_read':sum(c['core'] and c['body_text']=='read' for c in covered),'core_total':len(core),'creator_comment_rows':sum(int(c['author_corrections'].split('_')[1]) for c in covered if c['author_corrections'].startswith('read_'))}
out={'as_of':datetime.now(timezone.utc).isoformat(),'status':'in_progress' if counts['target_body_read']<counts['target_body_articles'] or counts['target_comments_complete']<counts['target_body_articles'] else 'bounded_scope_review_complete','browser_identity':{'transport':'Orca computer UIA','app':'pid:30624','window_id':'1442544','login':'Visible logged-in cafe UI and article text; no profile/cookie export','separate_playwright':'Public linked resources only, not used as cafe login substitute'},'list_coverage':{'all_cafe':{'total_shown':217,'pages_read':[1,2,3,4,5],'page_size':50},'menu6':{'pages_read':[1,2],'page_size':50,'regular_articles':78,'pinned_distinct':2},'menu3':{'pages_read':[1,2],'regular_articles':16},'menu7':{'pages_read':[1],'regular_articles':1}},'counts':counts,'articles':covered,'linked_resource_reviews':[{'url':'https://www.youtube.com/watch?v=dcSWTFyF9TQ','method':'Public transcript 401 timestamp segments read; 22:45 video frame viewed','limit':'Not continuous full playback; ASR errors retained and not silently repaired'},{'url':'https://www.youtube.com/watch?v=zaft1U-7klQ','method':'Description, public transcript, linked build JSON, import XML','limit':'Not a Taengjeong video; commenter curiosity is not endorsement'},{'url':'https://pobb.in/5vFvXihk9x0q','method':'Rendered page and actual import code XML parsed; nine tree stages','limit':'Warbringer-to-Titan route, not Kitava'},{'url':'https://poe.ninja/poe2/pob/29d39','method':'Rendered page and actual import code XML parsed','limit':'Level97 snapshot and conditional calculations, not minimum level or gameplay proof'},{'url':'https://docs.google.com/spreadsheets/d/17ZMdCP_E_zFYe6RcPaO_FxEN6c01x1yCeopnXsAqTeA/edit','method':'Public original sheet and CSV read','limit':'Author opinion; no node-by-node game testing'}],'remaining_limits':['Personal screenshots were not all visually decoded; inaccessible-to-UIA image contents remain unverified.','Personal linked character sheets were discovered, not exhaustively cloned or re-tested.','No first-day Taengjeong full act VOD; referenced other creator route is explicitly separate.','No game validation or 1.0.0 viability approval.']}
out['browser_identity'].update(transport='Mixed: initial authenticated Orca UIA; later public Playwright MCP DOM',separate_playwright='Existing mcp-chrome-6f08191 profile visibly logged out; public article bodies/comments successfully read. Not the user logged-in Chrome.',user_chrome_extension='Installed Playwright Extension 0.4.0; real MCP initialized; connection consent pending. UIA queue stopped by user steering.')
(P/'cafe_coverage.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'cafe_article_index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(counts))
