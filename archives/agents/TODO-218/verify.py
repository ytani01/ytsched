from playwright.sync_api import sync_playwright
JS = """() => {
 const o = {};
 document.querySelectorAll('.my-mini-cal, table').forEach(()=>{});
 const cells = [...document.querySelectorAll('td[data-date]')];
 o.cells = cells.map(td => {
  const cs = getComputedStyle(td);
  const tbl = td.closest('table');
  const cap = (tbl.previousElementSibling||tbl.parentElement).textContent.trim().slice(0,30);
  return {d: td.dataset.date, cap, cls: td.className, bg: cs.backgroundColor, fg: cs.color,
          dot: !!td.querySelector('.my-mini-cal-dot')};
 }).filter(c => ['2027-04-29','2027-04-30','2027-05-01','2027-05-02','2027-04-16'].includes(c.d));
 return o;
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width':412,'height':915})
    pg.goto('http://localhost:10999/ytsched/?date=2027-04-26')
    pg.wait_for_timeout(1500)
    for c in pg.evaluate(JS)['cells']: print(c)
    pg.screenshot(path='archives/agents/TODO-218/mini-cal.png')
    b.close()
