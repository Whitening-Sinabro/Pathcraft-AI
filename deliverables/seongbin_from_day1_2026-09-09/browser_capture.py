from playwright.sync_api import sync_playwright
from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parent
vid=sys.argv[1] if len(sys.argv)>1 else 'zKJQyBm4VnI'
times=list(map(float,sys.argv[2].split(','))) if len(sys.argv)>2 else [540]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,channel='msedge',args=['--autoplay-policy=no-user-gesture-required'])
    context=browser.new_context(viewport={'width':1600,'height':1000})
    page=context.new_page()
    page.goto('https://www.youtube.com/watch?v='+vid,wait_until='domcontentloaded',timeout=45000)
    page.wait_for_timeout(7000)
    print(page.title(),flush=True)
    print(page.locator('body').inner_text()[:1800],flush=True)
    (OUT/'frames'/vid).mkdir(parents=True,exist_ok=True)
    for t in times:
        try:
            page.evaluate('(t)=>{let v=document.querySelector("video");v.muted=true;v.currentTime=t;v.play().catch(()=>{});return true;}',t)
            page.wait_for_function('(t)=>{let v=document.querySelector("video");return v.readyState>=2 && Math.abs(v.currentTime-t)<5}',arg=t,timeout=25000)
            page.evaluate('document.querySelector("video").pause()')
        except Exception as e: print(type(e).__name__,str(e)[:250],flush=True)
        print(page.evaluate('Array.from(document.querySelectorAll("video")).map(v=>({time:v.currentTime,duration:v.duration,ready:v.readyState,error:v.error?.message}))'),flush=True)
        page.screenshot(path=str(OUT/'frames'/vid/f'browser_{t:09.2f}.png'))
    browser.close()
