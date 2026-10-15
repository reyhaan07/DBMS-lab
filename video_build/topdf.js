const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2]));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [src, dst] of jobs) {
    await page.goto('file://' + src);
    await page.pdf({ path: dst, preferCSSPageSize: true, printBackground: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:7px;color:#94a3b8;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
    console.log(dst);
  }
  await browser.close();
})();
