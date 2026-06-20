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
<html lang="zh-CN" style="background:#03060e !important;">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0" />
<meta name="theme-color" content="#03060e" />
<meta name="color-scheme" content="dark" />
<title>${title}</title>
<style>
  :root{color-scheme:dark;background:#03060e;}
  html{background:#03060e !important;}
  html,body{margin:0;padding:0;background:#03060e;color:#9ee9ff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;overflow:hidden;}
  .boot-stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:22px;background:#03060e;}
  .boot-stage::before,.boot-stage::after{content:"";position:absolute;inset:-20%;background:
    radial-gradient(circle at 20% 30%, rgba(120,180,255,0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(180,140,255,0.06) 0%, transparent 55%);
    pointer-events:none;}
  .boot-stage::after{background:
    radial-gradient(1px 1px at 12% 22%, rgba(220,235,255,0.7), transparent 60%),
    radial-gradient(1px 1px at 28% 78%, rgba(220,235,255,0.5), transparent 60%),
    radial-gradient(1px 1px at 44% 18%, rgba(220,235,255,0.6), transparent 60%),
    radial-gradient(1px 1px at 60% 56%, rgba(220,235,255,0.55), transparent 60%),
    radial-gradient(1px 1px at 76% 38%, rgba(220,235,255,0.6), transparent 60%),
    radial-gradient(1px 1px at 88% 80%, rgba(220,235,255,0.5), transparent 60%);
    opacity:.85;animation:bootStarTwinkle 6.5s ease-in-out infinite;}
  @keyframes bootStarTwinkle{0%,100%{opacity:.45;}50%{opacity:.95;}}
  .boot-title{font-size:20px;letter-spacing:8px;color:#bfe9ff;text-shadow:0 0 14px rgba(110,200,255,.35);position:relative;z-index:1;}
  .boot-sub{font-size:11px;color:#5b7da3;letter-spacing:3px;position:relative;z-index:1;opacity:.85;}
  .boot-orb{width:34px;height:34px;border-radius:50%;background:radial-gradient(circle,rgba(140,224,255,.65) 0%,rgba(58,120,200,.4) 60%,transparent 100%);animation:orb 2.8s ease-in-out infinite;position:relative;z-index:1;}
  @keyframes orb{0%,100%{transform:scale(0.95);opacity:.55;}50%{transform:scale(1.05);opacity:.85;}}
  .boot-stage.fading{transition:opacity .8s ease;opacity:0;pointer-events:none;}
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
// === Decrypt + Boot（无爆闪柔光过渡）===
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
  // 注入到解码后 HTML 中的「过渡保护层」—— 单层柔和遮罩，避免双 fade 叠加
  var TRANSITION_GUARD = '\\n<style id="__pb_style">html,body{background:#03060e!important;}#__post_boot{position:fixed;inset:0;background:#03060e;z-index:2147483647;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:14px;color:#bfe9ff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;letter-spacing:6px;font-size:13px;transition:opacity 1.2s ease;pointer-events:none;will-change:opacity;}#__post_boot .__pb_orb{width:22px;height:22px;border-radius:50%;background:radial-gradient(circle,rgba(140,224,255,.3) 0%,rgba(58,120,200,.12) 60%,transparent 100%);animation:__pb_orb 3s ease-in-out infinite;}@keyframes __pb_orb{0%,100%{transform:scale(.96);opacity:.3;}50%{transform:scale(1.03);opacity:.55;}}#__post_boot.gone{opacity:0;}</style>\\n';
  var TRANSITION_HTML = '<div id="__post_boot"><div class="__pb_orb"></div><div>已抵达 · 数字彼岸</div></div><script data-pb="1">window.addEventListener(\\'load\\',function(){setTimeout(function(){function safeFade(){var pb=document.getElementById(\\'__post_boot\\');if(!pb)return;pb.classList.add(\\'gone\\');setTimeout(function(){if(pb.parentNode)pb.parentNode.removeChild(pb);var st=document.getElementById(\\'__pb_style\\');if(st&&st.parentNode)st.parentNode.removeChild(st);},1400);}if(window.requestAnimationFrame){requestAnimationFrame(function(){requestAnimationFrame(safeFade);});}else{safeFade();}},900);});<\\/script>';

  function injectGuard(html){
    // 在 </head> 前插入样式
    if(html.indexOf('</head>')!==-1){
      html=html.replace('</head>', TRANSITION_GUARD + '</head>');
    } else {
      html=TRANSITION_GUARD+html;
    }
    // 在 <body ...> 之后立刻插入遮罩
    html=html.replace(/(<body[^>]*>)/, '$1'+TRANSITION_HTML);
    return html;
  }

  setTimeout(function(){
    try {
      var html = injectGuard(dec(__p,__k));
      // 先把启动器淡出（与新文档过渡叠加，避免硬切）
      var st=document.getElementById('__boot_stage');
      if(st){st.classList.add('fading');}
      // 锁定 documentElement 背景，防止 document.open 瞬间出现白底
      document.documentElement.style.background='#03060e';
      // 短暂等淡出 + 浏览器吸收 → 再写入新文档
      setTimeout(function(){
        document.open();
        document.write(html);
        document.close();
      }, 280);
    } catch(e) {
      var st2=document.getElementById('__boot_stage');
      if(st2){st2.innerHTML='<div style="color:#ff8aa8">启动失败：'+ (e&&e.message||e) +'</div>';}
    }
  }, 700);
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
