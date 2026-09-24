const { chromium } = require('C:/Users/User/AppData/Local/npm-cache/_npx/9833c18b2d85bc59/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(path.join(__dirname, '05_06_남은항목_확인.html')).href);
    const results = [];
    for (const id of JSON.parse(fs.readFileSync(path.join(__dirname, 'replay_scenes.json'), 'utf8')).map(x => x.name)) {
      await page.waitForFunction(id => document.getElementById(id).readyState >= 2, id, { timeout: 20000 });
      const video = page.locator('#' + id);
      const wrapper = page.locator('.replay').filter({ has: video });
      await wrapper.locator('select').selectOption('0.5');
      await wrapper.locator('[data-action="forward"]').click();
      await page.waitForFunction(id => !document.getElementById(id).seeking, id);
      const half = await video.evaluate(v => ({ time: v.currentTime, rate: v.playbackRate }));
      if (Math.abs(half.time - 0.5) > 0.02 || half.rate !== 0.5) throw Error(id + ': seek/rate mismatch');
      await wrapper.locator('[data-action="back"]').click();
      await page.waitForFunction(id => !document.getElementById(id).seeking, id);
      await video.evaluate(v => { v.muted = true; });
      await wrapper.locator('[data-action="play"]').click();
      await page.waitForFunction(id => document.getElementById(id).currentTime > 0.2, id);
      await wrapper.locator('[data-action="play"]').click();
      const state = await video.evaluate(v => ({ id: v.id, duration: v.duration, width: v.videoWidth, height: v.videoHeight,
        currentTime: v.currentTime, paused: v.paused, decodedFrames: v.getVideoPlaybackQuality().totalVideoFrames,
        error: v.error?.message || null, posterLoaded: null }));
      state.posterLoaded = await video.evaluate(async v => { const i = new Image(); i.src = v.poster; await i.decode(); return i.naturalWidth > 0; });
      if (state.error || !state.paused || !state.decodedFrames || !state.posterLoaded) throw Error(JSON.stringify(state));
      results.push(state);
    }
    const missing = await page.locator('a[href]').evaluateAll(nodes => nodes.map(x => x.getAttribute('href'))
      .filter(x => x && !/^(https?:|#)/.test(x)));
    for (const href of missing) {
      if (href === 'review_page_validation.json') continue; // Created by this successful validation below.
      if (!fs.existsSync(path.resolve(__dirname, decodeURIComponent(href.split('#')[0])))) throw Error('Missing local target: ' + href);
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(__dirname, 'review_desktop.png') });
    await page.setViewportSize({ width: 390, height: 844 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    await page.screenshot({ path: path.join(__dirname, 'review_mobile.png') });
    if (overflow || errors.length) throw Error(JSON.stringify({ overflow, errors }));
    const record = { verified_at_utc: new Date().toISOString(), browser: 'headless Chrome', videos: results,
      local_links_checked: missing.length, page_errors: errors, mobile_horizontal_overflow: overflow };
    fs.writeFileSync(path.join(__dirname, 'review_page_validation.json'), JSON.stringify(record, null, 2) + '\n');
    if (!fs.existsSync(path.join(__dirname, 'review_page_validation.json'))) throw Error('Validation record was not written');
    const manifestPath = path.join(__dirname, 'review_manifest.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    manifest.browser_playback_verified = true;
    manifest.browser_validation_file = 'review_page_validation.json';
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
    console.log(JSON.stringify(record));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
