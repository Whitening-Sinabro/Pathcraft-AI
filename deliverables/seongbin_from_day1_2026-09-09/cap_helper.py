"""Write a Playwright MCP capture request into the existing bridge file queue.

Keeps the response object in the validator's expected shape
(time/width/height/ready/paused/url) and names files by the real currentTime.

The preamble pins 720p and scrolls the player into view first: right after a
navigation the <video> box is not laid out yet and locator.screenshot() grabs
page chrome instead of the frame.
"""
import json
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent / 'mcp_session'

TMPL = (
    "async(page)=>{if(!page.url().includes('v=%(vid)s'))throw new Error('Wrong video');"
    "await page.waitForFunction(()=>{const v=document.querySelector('video');return v&&v.readyState>=2},null,{timeout:60000});"
    "await page.evaluate(()=>{const mp=document.querySelector('#movie_player');"
    "try{if(mp&&mp.setPlaybackQualityRange)mp.setPlaybackQualityRange('hd720','hd720');}catch(e){}"
    "const v=document.querySelector('video');v.pause();v.scrollIntoView({block:'center'});});"
    "await page.waitForFunction(()=>{const v=document.querySelector('video');const r=v.getBoundingClientRect();"
    "return v.videoHeight>=720&&r.width>1000&&r.height>500},null,{timeout:60000});"
    "const out=[];"
    "for(const t of %(times)s){try{"
    "await page.evaluate(t=>{const v=document.querySelector('video');v.pause();v.currentTime=t;},t);"
    "await page.waitForFunction(t=>{const v=document.querySelector('video');"
    "return v.readyState>=2&&!v.seeking&&Math.abs(v.currentTime-t)<1.5},t,{timeout:30000});"
    "await page.waitForFunction(()=>{const v=document.querySelector('video');return v.videoHeight>=720},null,{timeout:30000});"
    "await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));"
    "const st=await page.evaluate(()=>{const v=document.querySelector('video');"
    "return {time:v.currentTime,width:v.videoWidth,height:v.videoHeight,ready:v.readyState,paused:v.paused,url:location.href}});"
    "const name=String(Math.round(st.time*100)/100).padStart(5,'0');"
    "await page.locator('video').screenshot({path:'%(dir)s/%(tag)s_'+name+'.png'});"
    "st.file=name;out.push(st);}"
    "catch(e){out.push({requested:t,error:String(e)})}}return out}"
)

OUT_DIR = Q.as_posix()


def write(num, vid, tag, times):
    code = TMPL % {'vid': vid, 'times': json.dumps(times), 'dir': OUT_DIR, 'tag': tag}
    payload = {"name": "browser_run_code_unsafe", "arguments": {"code": code}}
    (Q / ('request_%s.json' % num)).write_text(
        json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return num


if __name__ == '__main__':
    num, vid, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    times = [float(x) for x in sys.argv[4].split(',')]
    print(write(num, vid, tag, times))
