#!/usr/bin/env node
// 把源 HTML 打包成「源码混淆 + 防窥」单文件
// 使用：node scripts/build-protected.js
//
// 注意：HTML 在浏览器中本质上无法 100% 加密，本脚本只能做轻度防窥（XOR + Base64）
// 专业人士仍可通过 DevTools / 内存反编译查看源码。

const fs = require('fs');
const path = require('path');

// ---------- 配置 ----------
const projectRoot = path.resolve(__dirname, '..');
const KEY = 'lifebeyond-2026-✦-stargate'; // 任意字符串作为 XOR 密钥

// 多个待打包文件
const TARGETS = [
  { src: 'experience.html', out: 'experience-protected.html', title: '数字彼岸' },
  { src: 'experience-pro.html', out: 'experience-pro-protected.html', title: '数字彼岸 · Pro' },
  { src: 'lifebeyond.byzmy.html', out: 'lifebeyond.byzmy.protected.html', title: '数字彼岸' },
  { src: 'lifebeyond.byzmy.pro.html', out: 'lifebeyond.byzmy.pro.protected.html', title: '数字彼岸 · Pro' },
];

// ---------- XOR + Base64 混淆 ----------
function xorEncrypt(text, key) {
  const buf = Buffer.from(text, 'utf-8');
  const keyBuf = Buffer.from(key, 'utf-8');
  const out = Buffer.alloc(buf.length);
  for (let i = 0; i < buf.length; i++) out[i] = buf[i] ^ keyBuf[i % keyBuf.length];
  return out.toString('base64');
}

// ---------- 处理依赖文件（civilization-galaxy.js）----------
function inlineExternalScripts(html, baseDir) {
  // 把 <script type="module" src="./civilization-galaxy.js"> 内联进去
  return html.replace(
    /<script([^>]*)\ssrc=["']\.?\/?(civilization-galaxy\.js)["']([^>]*)><\/script>/g,
    (_, before, fname, after) => {
      const full = path.join(baseDir, fname);
      if (!fs.existsSync(full)) return _;
      const code = fs.readFileSync(full, 'utf-8');
      return `<script${before}${after}>\n${code}\n</script>`;
    },
  );
}

// ---------- 模板 ----------
function buildLoaderHtml({ title, payload, keyJsLiteral }) {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0" />
<title>${title}</title>
<style>
  html,body{margin:0;padding:0;background:#03060e;color:#9ee9ff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;}
  .boot-stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:20px;}
  .boot-title{font-size:20px;letter-spacing:8px;color:#bfe9ff;text-shadow:0 0 20px rgba(110,200,255,.5);}
  .boot-sub{font-size:12px;color:#5b7da3;letter-spacing:3px;}
  .boot-orb{width:40px;height:40px;border-radius:50%;background:radial-gradient(circle,#8ce0ff 0%,#3a78c8 60%,transparent 100%);animation:orb 1.6s ease-in-out infinite;}
  @keyframes orb{0%,100%{transform:scale(0.8);opacity:.5;}50%{transform:scale(1.2);opacity:1;}}
</style>
</head>
<body>
<div class="boot-stage" id="__boot_stage">
  <div class="boot-orb"></div>
  <div class="boot-title">数字彼岸</div>
  <div class="boot-sub">CONNECTING TO THE OTHER SHORE…</div>
</div>
<script>
// === Anti-Snoop ===
(function(){
  try {
    document.addEventListener('contextmenu', function(e){ e.preventDefault(); }, { capture:true });
    document.addEventListener('keydown', function(e){
      var k=(e.key||'').toLowerCase();var c=e.ctrlKey||e.metaKey;var s=e.shiftKey;
      if(k==='f12'){e.preventDefault();return false;}
      if(c&&(k==='u'||k==='s')){e.preventDefault();return false;}
      if(c&&s&&(k==='i'||k==='j'||k==='c'||k==='k')){e.preventDefault();return false;}
    },{capture:true});
    var dev=false;setInterval(function(){
      var dh=(window.outerHeight-window.innerHeight)>200;var dw=(window.outerWidth-window.innerWidth)>200;
      if((dh||dw)&&!dev){dev=true;try{document.body.style.filter='blur(18px)';document.body.style.opacity='0.05';}catch(_){}}
      else if(!dh&&!dw&&dev){dev=false;try{document.body.style.filter='';document.body.style.opacity='';}catch(_){}}
    },1500);
  } catch(_){}
})();
// === Decrypt + Boot ===
(function(){
  var __k=${keyJsLiteral};
  var __p="${payload}";
  function dec(b64,key){
    var bin=atob(b64);
    var keyBytes=new TextEncoder().encode(key);
    var out=new Uint8Array(bin.length);
    for(var i=0;i<bin.length;i++){out[i]=bin.charCodeAt(i)^keyBytes[i%keyBytes.length];}
    return new TextDecoder('utf-8').decode(out);
  }
  setTimeout(function(){
    try {
      var html=dec(__p,__k);
      document.open();
      document.write(html);
      document.close();
    } catch(e) {
      var st=document.getElementById('__boot_stage');
      if(st){st.innerHTML='<div style="color:#ff8aa8">启动失败：'+ (e&&e.message||e) +'</div>';}
    }
  }, 600);
})();
</script>
</body>
</html>
`;
}

// ---------- 主流程 ----------
console.log('[build-protected] 启动打包流程');
TARGETS.forEach((t) => {
  const srcFull = path.join(projectRoot, t.src);
  const outFull = path.join(projectRoot, t.out);
  if (!fs.existsSync(srcFull)) {
    console.warn(`  跳过：找不到 ${t.src}`);
    return;
  }
  let html = fs.readFileSync(srcFull, 'utf-8');
  // 内联依赖
  html = inlineExternalScripts(html, projectRoot);
  // XOR + Base64
  const payload = xorEncrypt(html, KEY);
  // 把 KEY 也做轻度拆分混淆（不让 grep 直接拿到完整密钥）
  const keyChars = Array.from(KEY).map((c) => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0')).join('');
  const keyJsLiteral = '"' + keyChars + '"';
  const out = buildLoaderHtml({ title: t.title, payload, keyJsLiteral });
  fs.writeFileSync(outFull, out, 'utf-8');
  const srcKb = (Buffer.byteLength(html, 'utf-8') / 1024).toFixed(1);
  const outKb = (Buffer.byteLength(out, 'utf-8') / 1024).toFixed(1);
  console.log(`  ${t.src} (${srcKb}K) → ${t.out} (${outKb}K)`);
});
console.log('[build-protected] 完成');
