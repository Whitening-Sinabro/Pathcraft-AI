"""Execute the unmodified PoB2 v0.23.1 calculation engine via its headless wrapper.

Only the graphical host/path functions and ASCII numeric display formatter are
adapted. No game data, damage/recovery equations or mods are patched.
"""
from pathlib import Path
import json, os, sys, time
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
ENGINE=REPO/'.tmp/skadoosh-simulation/pob2'
sys.path.insert(0,str(REPO/'.tmp/skadoosh-simulation/python-runtime'))
from lupa.luajit21 import LuaRuntime

class Pob:
    def __init__(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        os.chdir(ENGINE/'src')
        self.lua.execute("arg={}; package.path='../runtime/lua/?.lua;../runtime/lua/?/init.lua;'..package.path")
        # PoB uses this dependency for UI numeric strings. UI keyboard editing
        # isn't exercised. English PoB item/gem names are retained in input XML.
        self.lua.execute("package.preload['lua-utf8']=function() return string end")
        wrapper=(ENGINE/'src/HeadlessWrapper.lua').read_text(encoding='utf-8')
        wrapper=wrapper.split('\n',1)[1]
        isolated=(HERE/'pob-userdata').as_posix()
        (HERE/'pob-userdata').mkdir(exist_ok=True)
        hook=f'''
function GetScriptPath() return {json.dumps(isolated)} end
function GetRuntimePath() return {json.dumps(isolated)} end
function GetUserPath() return {json.dumps(isolated)} end
function GetWorkDir() return {json.dumps((ENGINE/'src').as_posix())} end
io.read=function() error('Headless initialization failed; see prompt above') end
dofile("Launch.lua")
'''
        wrapper=wrapper.replace('dofile("Launch.lua")',hook)
        self.lua.execute(wrapper)
        assert self.lua.globals().build is not None,'PoB build module unavailable'
    def load(self,path):
        self.lua.globals().loadBuildFromXML(Path(path).read_text(encoding='utf-8'),'Pathcraft Simulation')
        self.lua.execute("if launch.promptMsg then error(launch.promptMsg) end")
    def run(self,code):return self.lua.execute(code)
    def json(self,expression):
        return json.loads(self.lua.eval("require('dkjson').encode("+expression+")"))
    def scalars(self,expression):
        return json.loads(self.lua.execute("local out={} for k,v in pairs("+expression+") do if type(v)=='number' or type(v)=='string' or type(v)=='boolean' then out[k]=v end end return require('dkjson').encode(out)"))

if __name__=='__main__':
    start=time.time();p=Pob()
    if len(sys.argv)>1:p.load(sys.argv[1])
    output=p.scalars('build.calcsTab.mainOutput')
    print(json.dumps({'elapsed':time.time()-start,'selected':{k:output.get(k) for k in ['Life','LifeRegen','Mana','ManaRegen','Armour','FireResist','ColdResist','LightningResist','CombinedDPS','AverageDamage','ManaCost','LifeCost','TotalDPS']}},ensure_ascii=True))
