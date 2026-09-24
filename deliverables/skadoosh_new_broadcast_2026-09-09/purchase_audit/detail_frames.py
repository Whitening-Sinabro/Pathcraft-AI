from pathlib import Path
import cv2
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
GROUPS = {
    'fear_first': range(2330,2348,2),
    'amulet_buy': range(2450,2492,3),
    'desecrate': range(2512,2548,2),
    'omen_buy': range(2670,2700,2),
    'well_choice': range(2710,2762,4),
    'prefix_slam': range(2852,2864),
    'fear_second': range(2968,2979,2),
    'instil': range(3044,3069,2),
}
out=HERE/'frames';out.mkdir(exist_ok=True)
caps={2220:cv2.VideoCapture(str(HERE/'purchase_37_42.mp4')),2520:cv2.VideoCapture(str(HERE/'purchase_42_47.mp4')),2820:cv2.VideoCapture(str(HERE/'purchase_47_52.mp4'))}
for label,seconds in GROUPS.items():
    shots=[]
    for sec in seconds:
        base=max(s for s in caps if s<=sec);cap=caps[base]
        cap.set(cv2.CAP_PROP_POS_MSEC,(sec-base)*1000);ok,frame=cap.read();assert ok,sec
        im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        im.save(out/f'vod_{sec}.jpg');shots.append((sec,im))
    for page in range((len(shots)+9)//10):
        part=shots[page*10:page*10+10];board=Image.new('RGB',(1280,385*((len(part)+1)//2)),(12,18,25));draw=ImageDraw.Draw(board)
        for i,(sec,im) in enumerate(part):
            im.thumbnail((640,360));x=i%2*640;y=i//2*385;board.paste(im,(x,y+25));draw.text((x+8,y+4),f'{sec//60:02}:{sec%60:02}',fill='white')
        board.save(out/f'{label}_{page}.jpg')
    print(label, 'complete',flush=True)
for cap in caps.values():cap.release()
