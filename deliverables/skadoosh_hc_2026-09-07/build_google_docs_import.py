"""Prepare a self-contained Word import for native Google Docs conversion."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.docx_vendor'))
from bs4 import BeautifulSoup,NavigableString,Tag
import markdown
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=HERE.parents[1]
TITLE='Skadoosh 타락 함성·전사 토템 워브링어 — 하코 7단계 가이드 (0.5.5 · 2026-09-07)'
FOLDER='https://drive.google.com/drive/u/0/folders/1tMDcTQpR2GmWd21Xkcvh-YSsqZZ8X_IF'
ZIP='https://drive.google.com/file/d/1xTV5E_XrelGbWplDidZoVZ1RuU_9CAmw/view'
SOURCE=ROOT/'Docs/2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md'
OUT=HERE/'google_docs_import';OUT.mkdir(exist_ok=True)
text=SOURCE.read_text(encoding='utf-8')
# Cloud readers get the complete procedural appendices and Drive links.
text=re.sub(r'^\[브라우저용 가이드\].*$',f'[필터·플래너 ZIP]({ZIP}) · [가이드 자료 폴더]({FOLDER})',text,flags=re.M)
text=re.sub(r'^이전 0\.4 계보.*$', '개정 전 0.4 계보·패치·커뮤니티 리서치는 작업 폴더에 보존했다. 현재 플레이 순서는 이 문서를 따른다.',text,flags=re.M)
text=re.sub(r'^스킬·보조·장비 표는.*$', '스킬·보조·장비 표는 검증된 플래너와 대조했다. 아래 부록에 환불 순서·시뮬레이션·방송 근거를 함께 수록한다.',text,flags=re.M)
html_text=markdown.markdown(text,extensions=['tables','md_in_html'])
appendices=[('appendix-passives','부록 A · 노드별 패시브 환불·추가 순서','패시브전환.md'),('appendix-simulation','부록 B · 딜·회복 계산 입력과 한계','시뮬레이션결과.md'),('appendix-audit','부록 C · 방송 시각과 판정','방송대조보고서.md'),('appendix-checks','부록 D · 검증 결과','검증결과.md')]
for anchor,title,name in appendices:
    content=(HERE/'revision3'/name).read_text(encoding='utf-8').split('\n',1)[1]
    content=re.sub(r'^(#{1,5}) ',r'\1# ',content,flags=re.M)
    content=content.replace('새 파일의 게임 내 재로딩·실전 조작과 가속 희귀 다수 의식 생존은 직접 시험하지 않았다.','새 파일 7개의 정상 로드 로그와 실제 게임의 02 트리 표시를 확인했다. 실전 조작과 가속 희귀 다수 의식 생존은 직접 시험하지 않았다.')
    html_text+=f'<a id="{anchor}"></a><h2>{title}</h2>'+markdown.markdown(content,extensions=['tables'])
soup=BeautifulSoup(html_text,'html.parser')
targets={'패시브전환.md':'appendix-passives','시뮬레이션결과.md':'appendix-simulation','방송대조보고서.md':'appendix-audit','검증결과.md':'appendix-checks','무기세트와젬연결.md':'controls'}
for a in soup.find_all('a',href=True):
    href=a['href']
    if href.startswith(('https://','http://','#')):continue
    name=href.rsplit('/',1)[-1]
    if name in targets:a['href']='#'+targets[name]
    elif name.endswith(('.build','.zip')):a['href']=ZIP
    elif name=='시뮬레이션그래프.html':a['href']=ZIP;a.string='45개 조건 그래프 — ZIP 안의 시뮬레이션그래프.html'
    else:raise AssertionError(('unmapped local link',href))
for s in soup.find_all('summary'):s.string=s.get_text().replace(' 펼치기','')
assert all(a['href'].startswith(('https://','http://','#')) for a in soup.find_all('a',href=True))
(OUT/'cloud_guide.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><body>'+str(soup)+'</body></html>',encoding='utf-8')

doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
sec.top_margin=sec.bottom_margin=Inches(.65);sec.left_margin=sec.right_margin=Inches(.6)
normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10)
normal.element.rPr.rFonts.set(qn('w:eastAsia'),'맑은 고딕')
normal.paragraph_format.space_after=Pt(6)
for style,size in [('Title',23),('Heading 1',17),('Heading 2',13),('Heading 3',11)]:
    st=doc.styles[style];st.font.name='Arial';st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string('173B50')
    st.element.rPr.rFonts.set(qn('w:eastAsia'),'맑은 고딕')
doc.core_properties.title=TITLE;doc.core_properties.subject='POE2 0.5.5 하드코어 워브링어 7단계 가이드'
doc.core_properties.author='Pathcraft'
bookmarks={};links=[]
def mark(p,name):
    if name in bookmarks:return
    idx=len(bookmarks)+1;key=re.sub('[^a-zA-Z0-9_]','_',name)
    start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(idx));start.set(qn('w:name'),key)
    end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(idx))
    p._p.append(start);p._p.append(end);bookmarks[name]=key
def inline(p,node,bold=False,italic=False):
    if isinstance(node,NavigableString):
        run=p.add_run(str(node));run.bold=bold;run.italic=italic;return
    if not isinstance(node,Tag):return
    if node.name=='br':p.add_run().add_break();return
    if node.name=='a':
        if node.get('id'):mark(p,node['id'])
        if not node.get('href'):return
        href=node['href'];link=OxmlElement('w:hyperlink')
        if href.startswith('#'):link.set(qn('w:anchor'),re.sub('[^a-zA-Z0-9_]','_',href[1:]))
        else:link.set(qn('r:id'),p.part.relate_to(href,RT.HYPERLINK,is_external=True))
        run=OxmlElement('w:r');props=OxmlElement('w:rPr')
        color=OxmlElement('w:color');color.set(qn('w:val'),'176383');props.append(color)
        underline=OxmlElement('w:u');underline.set(qn('w:val'),'single');props.append(underline)
        run.append(props);t=OxmlElement('w:t');t.text=node.get_text();run.append(t);link.append(run);p._p.append(link)
        links.append(href);return
    for child in node.children:inline(p,child,bold or node.name in ['strong','b'],italic or node.name in ['em','i'])

counts={'tables':0,'table_rows':0,'headings':0}
first_title=True
def render(node,container=doc):
    global first_title
    if not isinstance(node,Tag):return
    if node.name in ['h1','h2','h3','h4','h5','h6']:
        level=int(node.name[1]);style='Title' if first_title and level==1 else 'Heading '+str(min(3,max(1,level-1)))
        first_title=False;p=container.add_paragraph(style=style);inline(p,node);counts['headings']+=1;return
    if node.name=='p':
        p=container.add_paragraph();inline(p,node);return
    if node.name=='a' and node.get('id'):mark(container.add_paragraph(),node['id']);return
    if node.name=='table':
        rows=node.find_all('tr');cols=max(len(r.find_all(['th','td'],recursive=False)) for r in rows)
        table=container.add_table(rows=0,cols=cols);table.style='Table Grid';table.autofit=False
        for ri,row in enumerate(rows):
            cells=table.add_row().cells
            for ci,source in enumerate(row.find_all(['th','td'],recursive=False)):
                p=cells[ci].paragraphs[0];inline(p,source,bold=ri==0)
                for run in p.runs:run.font.size=Pt(9)
                if ri==0 or ri%2==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCEAF3' if ri==0 else 'F4F7FA');cells[ci]._tc.get_or_add_tcPr().append(shade)
            if ri==0:
                repeat=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(repeat)
        counts['tables']+=1;counts['table_rows']+=len(rows)-1;container.add_paragraph();return
    if node.name in ['ul','ol']:
        for li in node.find_all('li',recursive=False):
            p=container.add_paragraph(style='List Bullet' if node.name=='ul' else 'List Number')
            for c in li.children:
                if isinstance(c,Tag) and c.name in ['ul','ol']:render(c,container)
                else:inline(p,c)
        return
    if node.name=='summary':
        p=container.add_paragraph(style='Heading 3');inline(p,node);return
    for child in node.children:render(child,container)
for child in soup.children:render(child)
for target in links:
    if target.startswith('#'):assert target[1:] in bookmarks,('missing bookmark',target)
path=OUT/(TITLE+'.docx');doc.save(path)
# Re-open the actual serialized import and count its table cells.
loaded=Document(path);assert len(loaded.tables)==counts['tables']
full_text='\n'.join([p.text for p in loaded.paragraphs]+[c.text for t in loaded.tables for r in t.rows for c in r.cells])
for code in range(1,8):assert any(p.text.startswith(f'{code:02} ') for p in loaded.paragraphs)
assert all(x in full_text for x in ['부록 A','부록 B','부록 C','부록 D','총 80점','지면 분쇄 [내부 액티브 젬]'])
record={'title':TITLE,'folder_url':FOLDER,'zip_url':ZIP,'zip_sha256':hashlib.sha256((HERE/'Skadoosh-HC-한국어-필터와플래너.zip').read_bytes()).hexdigest(),'import_file':str(path),'import_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'google_document_url':None,'tables':counts['tables'],'table_rows':counts['table_rows'],'paragraphs':len(loaded.paragraphs),'bookmarks':len(bookmarks),'hyperlinks':len(links),'local_links_remaining':0,'native_google_doc_verified':False}
(HERE/'google_docs_publication.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
