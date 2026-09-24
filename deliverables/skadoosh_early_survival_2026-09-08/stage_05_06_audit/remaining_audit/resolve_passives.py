"""Reconstruct the two VOD states and prepare per-node visual audit crops.

The candidates remain unpublished until the atlas has been inspected.
"""
from pathlib import Path
import json,sys,copy,math
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent
sys.path.insert(0,str(AUDIT.parents[1]/'skadoosh_hc_2026-09-07'))
import progression_core as p
POS=json.loads((AUDIT/'tree_positions.json').read_text(encoding='utf-8'))
def save(name,x):(HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

old=p.state(json.loads((AUDIT/'tree54_candidate.json').read_text(encoding='utf-8')))
s54=dict(old)
for n in ['warcries24','warcries19_','warcries23','warcries28']:del s54[n]
s54.update(dict.fromkeys(['shield15','shield16','shield1','shield5'],1))
raw=json.loads((AUDIT/'ninja_day-2.json').read_text(encoding='utf-8'))
s74={p.NUM[n]:0 for n in raw['passiveSelection']}
s74.update({p.NUM[n]:1 for n in raw['passiveSelectionSet1']})
s74.update({p.NUM[n]:2 for n in raw['passiveSelectionSet2']})
later=['physical28','physical29','physical26','physical37','strength45_',
       'criticals33','criticals35','criticals31','criticals40','jewel_slot1974',
       'AscendancyWarrior2Notable7','AscendancyWarrior2Small7_']
s65={n:w for n,w in s74.items() if n not in later}
assert p.legal(s54) and p.costs(s54)=={'ordinary':71,'sets':[14,14],'ascendancy':4}
assert p.legal(s65) and p.costs(s65)=={'ordinary':87,'sets':[22,22],'ascendancy':4}
assert all(s65[n]==w for n,w in s54.items())
for level,state in [(54,s54),(65,s65)]:
    save(f'candidate_{level}.json',{'level':level,'costs':p.costs(state),'passives':p.entries(state),
        'published':False,'visual_audit_pending':True})
print('ADD 54 -> 65',[(n,w,p.NS[n]['name']) for n,w in s65.items() if n not in s54])

# Screen positions from two visible, horizontally aligned travel nodes.
# These are approximate crop centres, not a claim of pixel-perfect tree geometry.
scale=.07177
references={
 '54_centre':(AUDIT/'tree54_1796.jpg',[scale,933.6,155.5]),
 '54_north':(HERE/'54_1812.jpg',[scale,993.1,877.9]),
 '54_south':(HERE/'54_1752.jpg',[scale,1073.6,-38.5]),
}
targets={
 '54_middle':(HERE/'54_1813.3.jpg','54_north'),
 '65_north':(AUDIT/'tree65_14100.jpg','54_north'),
 '65_middle':(AUDIT/'tree65_14110.jpg','54_centre'),
 '65_centre':(AUDIT/'tree65_14144.jpg','54_centre'),
 '65_south':(HERE/'65_14130.jpg','54_south'),
}
def register(refpath,targetpath):
    im1=cv2.imread(str(refpath),0);im2=cv2.imread(str(targetpath),0)
    mask=np.zeros_like(im1);mask[45:610,20:1090]=255
    sift=cv2.SIFT_create(nfeatures=6000)
    k1,d1=sift.detectAndCompute(im1,mask);k2,d2=sift.detectAndCompute(im2,mask)
    good=[a for a,b in cv2.BFMatcher().knnMatch(d1,d2,k=2) if a.distance<.68*b.distance]
    a=np.float32([k1[x.queryIdx].pt for x in good]);b=np.float32([k2[x.trainIdx].pt for x in good])
    matrix,inliers=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=2)
    assert matrix is not None and int(inliers.sum())>=12,(targetpath,len(good))
    assert abs(matrix[0,1])<.002 and abs(matrix[1,0])<.002,matrix
    return matrix,int(inliers.sum())
registration=[]
for key,(path,ref) in targets.items():
    m,n=register(references[ref][0],path)
    s,tx,ty=references[ref][1]
    references[key]=(path,[s*m[0,0],*(m@np.array([tx,ty,1])).tolist()])
    registration.append({'frame':key,'reference':ref,'matrix':m.tolist(),'inlier_feature_matches':n})
save('image_registration.json',registration)

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
fontsmall=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
manifest=[]
for level,state in [(54,s54),(65,s65)]:
    # Include rejected/missing alternatives as negative controls.
    ids=set(state)|set(later)|{'warcries24','warcries19_','warcries23','warcries28','warcries39','wolf14','totems8'}
    ids={n for n in ids if not p.NS[n].get('ascendancyName')}
    records=[]
    for n in sorted(ids,key=lambda n:(state.get(n,9),POS[n][1],POS[n][0])):
        options=[]
        for key,(path,(s,tx,ty)) in references.items():
            if not key.startswith(str(level)):continue
            if level==54 and n in ('armour_break28','armour_break29') and key!='54_centre':continue
            x,y=np.array(POS[n])*s+np.array([tx,ty])
            max_y=680 if 370<x<880 else 600
            if 55<x<1060 and 60<y<max_y:
                edge=min(x-55,1060-x,y-60,max_y-y)
                options.append((edge,key,path,x,y))
        if not options:
            records.append({'id':n,'set':state.get(n),'name':p.NS[n]['name'],'missing_frame':True});continue
        _,key,path,x,y=max(options)
        records.append({'id':n,'set':state.get(n),'name':p.NS[n]['name'],'frame':key,'source':str(path),'centre':[x,y]})
    for start in range(0,len(records),20):
        out=Image.new('RGB',(1200,1100),'#101820');draw=ImageDraw.Draw(out)
        for j,row in enumerate(records[start:start+20]):
            x0=(j%5)*240;y0=(j//5)*275
            draw.text((x0+8,y0+4),row['id'],fill='#ffffff',font=font)
            draw.text((x0+8,y0+25),('UNALLOCATED' if row['set'] is None else 'COMMON' if row['set']==0 else 'SET '+str(row['set'])),fill='#ffd58b',font=fontsmall)
            draw.text((x0+8,y0+45),row['name'][:29],fill='#bedcfa',font=fontsmall)
            if 'missing_frame' in row:
                draw.text((x0+8,y0+90),'NO VIEW',fill='red',font=font);continue
            x,y=row['centre'];im=Image.open(row['source']).crop((round(x)-40,round(y)-40,round(x)+40,round(y)+40)).resize((192,192))
            out.paste(im,(x0+8,y0+70))
        name=f'atlas_{level}_{start//20:02}.jpg';out.save(HERE/name,quality=94)
        manifest.append({'image':name,'records':records[start:start+20]})
save('node_atlas_manifest.json',manifest)
print('MISSING',[(m['image'],r['id']) for m in manifest for r in m['records'] if r.get('missing_frame')])
print('atlases',len(manifest))
