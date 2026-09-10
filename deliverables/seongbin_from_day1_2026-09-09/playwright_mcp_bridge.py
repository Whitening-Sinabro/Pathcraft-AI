"""Keep the user's configured Playwright MCP Chrome server available to this task."""
from pathlib import Path
import asyncio,json,sys,datetime
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
Q=O/'mcp_session';Q.mkdir(exist_ok=True)
CLI=Path('C:/Users/User/AppData/Local/npm-cache/_npx/9833c18b2d85bc59/node_modules/@playwright/mcp/cli.js')
async def main():
    params=StdioServerParameters(command='C:/Program Files/nodejs/node.exe',args=[str(CLI),'--browser','chrome','--output-dir',str(Q)],cwd=str(O))
    with (Q/'server_stderr.log').open('a',encoding='utf-8') as log:
        async with stdio_client(params,errlog=log) as (read,write):
            async with ClientSession(read,write) as session:
                init=await session.initialize()
                ts=await session.list_tools()
                (Q/'tools.json').write_text(ts.model_dump_json(indent=2),encoding='utf-8')
                (Q/'server.json').write_text(init.model_dump_json(indent=2),encoding='utf-8')
                print('MCP initialized; tools saved',flush=True)
                while True:
                    for p in sorted(Q.glob('request_*.json')):
                        dest=p.with_name(p.name.replace('request_','response_'))
                        if dest.exists():continue
                        req=json.loads(p.read_text(encoding='utf-8'))
                        try:
                            result=await session.call_tool(req['name'],req.get('arguments',{}))
                            data=result.model_dump(mode='json')
                        except Exception as e:data={'isError':True,'exception_type':type(e).__name__,'message':str(e)}
                        dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
                        print(p.stem,req['name'],'done',data.get('isError',False),flush=True)
                    await asyncio.sleep(.25)
asyncio.run(main())
