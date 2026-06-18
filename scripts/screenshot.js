/**
 * Capture full-page screenshots of LifeBeyond portfolio site
 * and split into individual poster images for upload to portfolio sites.
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT_DIR = path.join(__dirname, '..', 'public', 'posters');
fs.mkdirSync(OUT_DIR, { recursive: true });

const BASE = 'http://localhost:5000';
const DEVICE_SCALE = 2; // retina quality

async function run() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: DEVICE_SCALE,
  });

  // ── 1) Full-page long screenshot of portfolio (index.html) ──
  console.log('📸 Capturing portfolio page full-page...');
  const page1 = await ctx.newPage();
  await page1.goto(`${BASE}/`, { waitUntil: 'networkidle', timeout: 60000 });
  // Wait for canvas animation + fade-in
  await page1.waitForTimeout(3000);
  // Scroll to trigger all IntersectionObserver reveals
  await autoScroll(page1);
  await page1.waitForTimeout(2000);
  // Scroll back to top for clean shot
  await page1.evaluate(() => window.scrollTo(0, 0));
  await page1.waitForTimeout(1000);

  const fullPng = path.join(OUT_DIR, 'portfolio-full.png');
  await page1.screenshot({ path: fullPng, fullPage: true });
  const fullStat = fs.statSync(fullPng);
  console.log(`✅ Full page: ${fullPng} (${(fullStat.size/1024).toFixed(0)} KB)`);

  // ── 2) Section-by-section screenshots ──
  const sections = [
    { selector: 'section.hero',   name: '01-hero'         },
    { selector: '#story',         name: '02-vision'       },
    { selector: '#features',      name: '03-modules'      },
    { selector: '#design',        name: '04-philosophy'   },
    { selector: '#craft',         name: '05-showcase'     },
    { selector: 'section.final-cta', name: '06-cta'       },
  ];

  console.log('\n📸 Capturing individual sections...');
  for (const sec of sections) {
    const el = await page1.$(sec.selector);
    if (!el) {
      console.log(`⚠️  ${sec.selector} not found, skipping`);
      continue;
    }
    // Scroll section into view
    await el.scrollIntoViewIfNeeded();
    await page1.waitForTimeout(800);
    const filePath = path.join(OUT_DIR, `${sec.name}.png`);
    await el.screenshot({ path: filePath });
    const stat = fs.statSync(filePath);
    console.log(`✅ ${sec.name}: ${filePath} (${(stat.size/1024).toFixed(0)} KB)`);
  }

  // ── 3) Capture experience.html hero + key views ──
  console.log('\n📸 Capturing experience page views...');
  const page2 = await ctx.newPage();
  await page2.goto(`${BASE}/experience.html`, { waitUntil: 'networkidle', timeout: 60000 });
  await page2.waitForTimeout(4000); // wait for Three.js + canvas

  // Home view (default)
  const homeShot = path.join(OUT_DIR, '07-experience-home.png');
  await page2.screenshot({ path: homeShot });
  console.log(`✅ experience-home: ${homeShot} (${(fs.statSync(homeShot).size/1024).toFixed(0)} KB)`);

  // Click 彼岸动态 tab
  const dynBtn = await page2.$('[data-view="beyond"]');
  if (dynBtn) {
    await dynBtn.click();
    await page2.waitForTimeout(2000);
    const dynShot = path.join(OUT_DIR, '08-experience-dynamic.png');
    await page2.screenshot({ path: dynShot });
    console.log(`✅ experience-dynamic: ${dynShot} (${(fs.statSync(dynShot).size/1024).toFixed(0)} KB)`);
  }

  // Click 社区 tab
  const commBtn = await page2.$('[data-view="community"]');
  if (commBtn) {
    await commBtn.click();
    await page2.waitForTimeout(2000);
    const commShot = path.join(OUT_DIR, '09-experience-community.png');
    await page2.screenshot({ path: commShot });
    console.log(`✅ experience-community: ${commShot} (${(fs.statSync(commShot).size/1024).toFixed(0)} KB)`);
  }

  // Click 星图 tab
  const uniBtn = await page2.$('[data-view="universe"]');
  if (uniBtn) {
    await uniBtn.click();
    await page2.waitForTimeout(2000);
    const uniShot = path.join(OUT_DIR, '10-experience-universe.png');
    await page2.screenshot({ path: uniShot });
    console.log(`✅ experience-universe: ${uniShot} (${(fs.statSync(uniShot).size/1024).toFixed(0)} KB)`);
  }

  // Click 彼岸足迹 tab
  const footBtn = await page2.$('[data-view="footprint"]');
  if (footBtn) {
    await footBtn.click();
    await page2.waitForTimeout(1500);
    // Click 关系解码 zone
    const relBtn = await page2.$('[data-fzone="relation"]');
    if (relBtn) { await relBtn.click(); await page2.waitForTimeout(1000); }
    const footShot = path.join(OUT_DIR, '11-experience-footprint.png');
    await page2.screenshot({ path: footShot });
    console.log(`✅ experience-footprint: ${footShot} (${(fs.statSync(footShot).size/1024).toFixed(0)} KB)`);
  }

  await browser.close();
  console.log('\n🎉 All screenshots done!');
}

async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 300;
      const timer = setInterval(() => {
        window.scrollBy(0, distance);
        totalHeight += distance;
        if (totalHeight >= document.body.scrollHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 200);
    });
  });
}

run().catch((e) => { console.error(e); process.exit(1); });
