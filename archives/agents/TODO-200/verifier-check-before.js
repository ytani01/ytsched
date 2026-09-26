const { chromium } = require('playwright');

const BASE = 'http://127.0.0.1:18765/';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.setViewportSize({ width: 390, height: 844 });

  let navCount = 0;
  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) navCount++;
  });

  await page.goto(BASE);
  navCount = 0;

  const navPromise = page.waitForNavigation({ timeout: 3000 }).catch(() => null);
  await page.locator('#todo_days').dispatchEvent('mousedown');
  const nav = await navPromise;
  await page.waitForTimeout(500);
  console.log('STEP1(before-fix) nav_happened=', !!nav, 'nav_count=', navCount, 'url=', page.url());

  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
