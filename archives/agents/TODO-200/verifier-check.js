const { chromium } = require('playwright');
const fs = require('fs');

const BASE = 'http://127.0.0.1:18765/';
const CONF = process.argv[2]; // path to conf.json

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.setViewportSize({ width: 390, height: 844 });

  let navCount = 0;
  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) navCount++;
  });

  await page.goto(BASE);
  navCount = 0; // reset after initial load

  // 1. mousedown/click on #todo_days should NOT trigger navigation
  const before = navCount;
  await page.locator('#todo_days').dispatchEvent('mousedown');
  await page.waitForTimeout(500);
  const afterMousedown = navCount;
  console.log('STEP1 nav_count_before=', before, 'after_mousedown=', afterMousedown, 'url=', page.url());

  // 2. selectOption 7 (1w) -> should submit
  const navPromise = page.waitForNavigation({ timeout: 5000 }).catch(() => null);
  await page.locator('#todo_days').selectOption('7');
  const nav = await navPromise;
  await page.waitForTimeout(300);
  const todoDaysValue = await page.locator('#todo_days').inputValue();
  console.log('STEP2 nav_happened=', !!nav, 'todo_days_value_after=', todoDaysValue, 'nav_count=', navCount);

  let confJson = null;
  try {
    confJson = fs.readFileSync(CONF, 'utf8');
  } catch (e) {
    confJson = 'ERROR: ' + e.message;
  }
  console.log('STEP2 conf.json=', confJson);

  // 3. filter icon mousedown -> should submit (navigation)
  const navCountBeforeFilter = navCount;
  const navPromise2 = page.waitForNavigation({ timeout: 5000 }).catch(() => null);
  await page.locator('svg[data-form-id="form_filter"]').first().dispatchEvent('mousedown');
  const nav2 = await navPromise2;
  await page.waitForTimeout(300);
  console.log('STEP3 nav_happened=', !!nav2, 'nav_count_before=', navCountBeforeFilter, 'nav_count_after=', navCount);

  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
