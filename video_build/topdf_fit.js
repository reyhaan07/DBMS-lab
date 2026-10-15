// PDF with no header/footer; reports the font size each slide was fitted to.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const [[src, dst]] = JSON.parse(fs.readFileSync(process.argv[2]));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
  await p.goto('file://' + src); await p.waitForTimeout(300);
  console.log(await p.$$eval('.fit', fs => fs.map(f => f.dataset.size).join(' ')));
  await p.emulateMedia({ media: 'print' });
  await p.pdf({ path: dst, width: '1600px', height: '900px', printBackground: true, preferCSSPageSize: true });
  await b.close(); console.log(dst);
})();
