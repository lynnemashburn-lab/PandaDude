// Renders HTML pages to PNG and/or PDF with the bundled fonts.
// Usage: node render.js jobs.json
// Each job: { html, png?, pdf?, width, height, scale? }  (width/height in CSS px, or "8.5in" strings for PDF)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const job of jobs) {
    const page = await browser.newPage({
      viewport: { width: Math.ceil(job.vw || 800), height: Math.ceil(job.vh || 800) },
      deviceScaleFactor: job.scale || 1,
    });
    await page.goto('file://' + path.resolve(job.html));
    await page.evaluate(() => document.fonts.ready);
    if (job.png) {
      await page.screenshot({ path: job.png, clip: { x: 0, y: 0, width: job.vw, height: job.vh } });
    }
    if (job.pdf) {
      await page.pdf({ path: job.pdf, width: job.width, height: job.height, printBackground: true, pageRanges: '1' });
    }
    await page.close();
    console.log('rendered', job.png || '', job.pdf || '');
  }
  await browser.close();
})();
