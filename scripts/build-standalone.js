#!/usr/bin/env node
/**
 * 把 civilization-galaxy.js 内联到 experience.html 中，
 * 生成一份完全自包含、可 file:// 双击打开的 experience-standalone.html。
 *
 * 用法：node scripts/build-standalone.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const HTML_IN = path.join(ROOT, 'experience.html');
const JS_IN = path.join(ROOT, 'civilization-galaxy.js');
const OUT = path.join(ROOT, 'experience-standalone.html');

const html = fs.readFileSync(HTML_IN, 'utf8');
const js = fs.readFileSync(JS_IN, 'utf8');

const tag = '<script type="module" src="./civilization-galaxy.js"></script>';
if (!html.includes(tag)) {
  console.error('[build-standalone] 未在 experience.html 中找到外链脚本标签：', tag);
  process.exit(1);
}

// 注意：< / > 字符在 module 内部代码中不会让 HTML 解析器误判结束，
// 但保险起见，把脚本内容里所有 </script 都打散，避免极端情况下提前终止 <script> 块。
const safeJs = js.replace(/<\/script/gi, '<\\/script');

const banner =
  '<!-- ✦ inlined civilization-galaxy.js (build-standalone.js) ✦ -->\n' +
  '<script type="module">\n' +
  safeJs +
  '\n</script>';

const out = html.replace(tag, banner);

fs.writeFileSync(OUT, out, 'utf8');
const stat = fs.statSync(OUT);
console.log('[build-standalone] ok ->', OUT);
console.log('  size:', (stat.size / 1024).toFixed(1) + ' KB');
console.log('  inlined js bytes:', js.length);
