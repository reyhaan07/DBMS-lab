// Screenshot every slide HTML in manifest.json to PNG.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const manifest = JSON.parse(fs.readFileSync(process.argv[2]));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const s of manifest) {
    await page.goto('file://' + s.html);
    await page.screenshot({ path: s.html.replace('.html', '.png') });
  }
  await browser.close();
  console.log('shot', manifest.length);
})();
