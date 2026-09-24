const {chromium} = require('C:/Users/User/AppData/Local/npm-cache/_npx/9833c18b2d85bc59/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');

(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(path.join(__dirname, '빌드핵심_추가확인.html')).href);
    await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0));
    const replays = [];
    for (let i = 0; i < await page.locator('video').count(); i++) {
      const item = page.locator('.replay').nth(i);
      await item.locator('video').evaluate(v => {v.preload = 'metadata'; v.load();});
      await page.waitForFunction(index => {
        const v = document.querySelectorAll('video')[index];
        return v.readyState >= 1 && Number.isFinite(v.duration);
      }, i);
      await item.locator('video').evaluate(v => {v.currentTime = 2;});
      await page.waitForFunction(index => !document.querySelectorAll('video')[index].seeking, i);
      await item.locator('button[data-seek="0.5"]').click();
      await item.locator('select').selectOption('0.5');
      const data = await item.locator('video').evaluate(v => ({src: v.getAttribute('src'), width: v.videoWidth, duration: v.duration, time: v.currentTime, speed: v.playbackRate}));
      if (data.width !== 1280 || Math.abs(data.time - 2.5) > .1 || data.speed !== .5) throw new Error(JSON.stringify(data));
      replays.push(data);
    }
    await page.screenshot({path: path.join(__dirname, 'desktop_review.png')});
    await page.setViewportSize({width: 390, height: 844});
    await page.evaluate(() => window.scrollTo(0, 0));
    const mobile = await page.evaluate(() => ({viewport: innerWidth, page: document.documentElement.scrollWidth}));
    if (mobile.page > mobile.viewport) throw new Error('Mobile overflow: ' + JSON.stringify(mobile));
    await page.screenshot({path: path.join(__dirname, 'mobile_review.png')});
    if (errors.length) throw new Error(errors.join('\n'));
    const result = {checkedUtc: new Date().toISOString(), replays, mobile, pageErrors: errors, allImagesLoaded: true};
    fs.writeFileSync(path.join(__dirname, 'browser_validation.json'), JSON.stringify(result, null, 2));
    const filename = path.join(__dirname, 'report_validation.json');
    const validation = JSON.parse(fs.readFileSync(filename));
    validation.browser = result;
    fs.writeFileSync(filename, JSON.stringify(validation, null, 2));
    process.stdout.write(JSON.stringify(result));
  } finally {
    await browser.close();
  }
})().catch(e => {process.stderr.write(String(e)); process.exitCode = 1;});
