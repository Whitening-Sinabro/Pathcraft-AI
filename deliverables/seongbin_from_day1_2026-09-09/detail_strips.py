from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path(__file__).resolve().parent
SPECS=[('zKJQyBm4VnI',1080,1250,'day1_ritual'),('GtC5-b4QXec',710,820,'crossbow_reveal'),('GtC5-b4QXec',6300,6540,'ascendancy'),('C_tkSubXWDk',1420,1630,'mutable_star'),('C_tkSubXWDk',5670,5840,'weapon_assignment'),('C_tkSubXWDk',8970,9210,'helmet_trade')]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for vid,start,end,name in SPECS:
    secs=list(range(start,end+1,10)); im=Image.new('RGB',(1280,207*((len(secs)+3)//4)),'white');draw=ImageDraw.Draw(im)
    for n,t in enumerate(secs):
        index=t//10;cell=index%9;src=Image.open(O/'storyboards'/vid/f'{index//9:03}.jpg')
        x=n%4*320;y=n//4*207;im.paste(src.crop((cell%3*320,cell//3*180,cell%3*320+320,cell//3*180+180)),(x,y))
        draw.text((x+3,y+182),f'{vid} ~{t//3600:02}:{t//60%60:02}:{t%60:02}',font=font,fill='black')
    p=O/'frames'/f'{name}.jpg';im.save(p,quality=94)
    print(p)
