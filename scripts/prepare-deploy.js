#!/usr/bin/env node
/**
 * prepare-deploy.js
 * 生成可推送到 GitHub 公开仓库的干净部署目录 `deploy/`
 * 只包含面向用户的加密产物，绝不包含未加密源码。
 *
 * 用法：
 *   node scripts/build-protected.js   # 先确保 protected 是最新
 *   node scripts/prepare-deploy.js    # 再生成 deploy/
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DEPLOY = path.join(ROOT, 'deploy');

// 白名单：只有这些文件会进入 deploy/，源码 / 构建脚本一律不会出现
const FILES_TO_COPY = [
  'index.html',
  'lifebeyond.byzmy.protected.html',
  'lifebeyond.byzmy.pro.protected.html',
  'experience-protected.html',
  'experience-pro-protected.html',
];

// 黑名单关键字：复制时再做一次防呆校验，文件名含这些字样直接拒绝
const FORBIDDEN_HINTS = [
  '.byzmy.html',
  '.byzmy.pro.html',
  'experience.html',
  'experience-pro.html',
  'experience-standalone.html',
  'civilization-galaxy.js',
  'gallery.html',
  'scripts/',
  'server.py',
  '.coze',
  '.git',
  'AGENTS.md',
  'DESIGN.md',
];

function isForbidden(filename) {
  return FORBIDDEN_HINTS.some(hint => filename.endsWith(hint) || filename.includes('/' + hint));
}

function emptyDir(dir) {
  if (!fs.existsSync(dir)) return;
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    const s = fs.statSync(p);
    if (s.isDirectory()) {
      emptyDir(p);
      fs.rmdirSync(p);
    } else {
      fs.unlinkSync(p);
    }
  }
}

function copyFile(src, dst) {
  fs.copyFileSync(src, dst);
  const size = fs.statSync(dst).size;
  console.log(`  ${path.relative(ROOT, src)} → deploy/${path.basename(dst)} (${(size/1024).toFixed(1)}K)`);
}

function main() {
  console.log('[prepare-deploy] 开始生成部署目录');

  // 1. 清空 deploy/
  if (fs.existsSync(DEPLOY)) {
    emptyDir(DEPLOY);
  } else {
    fs.mkdirSync(DEPLOY);
  }

  // 2. 复制白名单文件
  let copied = 0;
  for (const name of FILES_TO_COPY) {
    if (isForbidden(name)) {
      console.error(`[prepare-deploy] 拒绝复制（黑名单命中）：${name}`);
      process.exit(1);
    }
    const src = path.join(ROOT, name);
    if (!fs.existsSync(src)) {
      console.warn(`[prepare-deploy] 警告：缺失 ${name}，跳过`);
      continue;
    }
    copyFile(src, path.join(DEPLOY, name));
    copied++;
  }

  // 3. 在 deploy/ 内写一个 .nojekyll，避免 GitHub Pages 处理特殊文件名
  fs.writeFileSync(path.join(DEPLOY, '.nojekyll'), '');

  // 4. 写一个 README 提醒用户这是部署目录
  fs.writeFileSync(path.join(DEPLOY, 'README.md'),
`# LifeBeyond Deploy

此目录是**自动生成**的部署产物。请通过项目根目录的：
\`\`\`
node scripts/build-protected.js && node scripts/prepare-deploy.js
\`\`\`
重新生成。

**不要手动编辑**此目录里的文件，改动会被下次构建覆盖。

# 文件

| 文件 | 说明 |
|---|---|
| index.html | 落地页 |
| lifebeyond.byzmy.protected.html | 免费版（加密） |
| lifebeyond.byzmy.pro.protected.html | Pro 版（加密） |
| experience-protected.html | 免费版备份命名 |
| experience-pro-protected.html | Pro 版备份命名 |
`);

  console.log(`[prepare-deploy] 完成，共复制 ${copied} 个文件 + .nojekyll + README.md`);
  console.log(`[prepare-deploy] 部署目录：${DEPLOY}`);
}

main();
