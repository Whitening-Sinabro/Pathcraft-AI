# 기존 Playwright MCP 연결 사용

새 브라우저나 두 번째 Playwright MCP 서버를 띄우지 않는다. 아래 브리지는 조정자가 이미 사용하던 실제 Playwright MCP 서버에 요청을 전달한다. 브라우저 연결은 하나이며 작업자가 사용하는 동안 조정자는 페이지를 조작하지 않는다.

연결 파일: `D:/Pathcraft-AI/.tmp/tangjung_055_mcp_bridge.json`
이 파일의 토큰은 출력하거나 보고서/커밋에 복사하지 않는다. 연결이 실패하면 조정자에게 알려서 기존 연결을 복구한다.

Node REPL 예시:

```js
var fs = await import('node:fs/promises');
var bridge = JSON.parse(await fs.readFile('D:/Pathcraft-AI/.tmp/tangjung_055_mcp_bridge.json', 'utf8'));
var mcp = async (method, params = {}) => {
  var r = await fetch(bridge.url, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-task-token': bridge.token },
    body: JSON.stringify({method, params})
  });
  if (!r.ok) throw new Error('Playwright bridge HTTP ' + r.status);
  return await r.json();
};
var resultOf = r => {
  if (r.isError) throw new Error(r.content?.filter(c=>c.type==='text').map(c=>c.text).join('\n'));
  var t = r.content.filter(c=>c.type==='text').map(c=>c.text).join('\n');
  return JSON.parse(t.split('### Result\n')[1].split('\n###')[0]);
};
console.log((await mcp('tools/list')).tools.map(t=>({name:t.name,description:t.description,inputSchema:t.inputSchema})));
```

페이지 확인 예시(탭 번호를 고정하지 말고 URL을 확인한다):

```js
var r = await mcp('tools/call', {
  name: 'browser_run_code_unsafe',
  arguments: {code: "async(page)=>page.context().pages().map((p,i)=>({i,url:p.url()}))"}
});
console.log(resultOf(r));
```

현재 연구용 탭은 0번 치지직 검색 페이지다. Google Docs, 사용자 유튜브, Mobalytics, poe.ninja 탭은 사용자 소유로 취급한다. 탭 순서는 바뀔 수 있으므로 실제 URL로 재확인한다.

스크린샷은 MCP의 이미지 콘텐츠를 emitImage하거나 `browser_run_code_unsafe`에서 영상 요소 screenshot 버퍼를 base64로 반환해 Node REPL의 `nodeRepl.emitImage(Buffer.from(frame,'base64'))`로 본다. 이미지 파일은 worker/ 아래에만 저장한다.

브라우저 전체 닫기/설치 도구는 이 브리지에서 허용하지 않는다. 코드 실행으로 우회해서 브라우저를 종료하거나 다른 탭을 조작하지 않는다. 계정 정보·쿠키·토큰을 수집하거나 출력하지 않는다.
