# LifeBeyond · 部署指南

把 LifeBeyond 部署到自有域名（如 `lifebeyond.app`）+ Cloudflare Pages，**完全免费、永久在线、自动 HTTPS、不用备案**。

---

## 一、准备工作

### 1. 注册 GitHub 账号

打开 https://github.com → 右上 **Sign up** → 用邮箱注册（建议用 Gmail，跨境注册更顺）。

### 2. 注册 Cloudflare 账号

打开 https://dash.cloudflare.com/sign-up → 同样邮箱注册。

### 3. 注册一个域名（30~80 元/年）

推荐 **Cloudflare Registrar** 自己买，省一道转入麻烦：

- 进 Cloudflare → 左侧 **Domain Registration** → **Register Domains**
- 搜 `lifebeyond.app`（推荐，¥80/年，自带强制 HTTPS）或 `lifebeyond.io`（¥250/年，更国际化）
- ⚠️ **不要选 `.cn`**，那是 ICP 备案的坑

如果 Cloudflare 不卖，可去 [Namecheap](https://www.namecheap.com)、[GoDaddy](https://www.godaddy.com)、[Spaceship](https://www.spaceship.com) 买。

---

## 二、本地准备部署产物

### 1. 重新构建（任何代码改动后都要做）

```bash
node scripts/build-protected.js    # 1️⃣ 把源码加密混淆成 .protected.html
node scripts/prepare-deploy.js     # 2️⃣ 把要发布的文件复制到 deploy/
```

构建完 `deploy/` 目录里只会有这些**绝对安全可公开**的文件：

```
deploy/
├── .nojekyll                              # 告诉 GitHub Pages 不要做 Jekyll 处理
├── README.md
├── index.html                             # 落地页
├── lifebeyond.byzmy.protected.html        # 免费版（加密）
├── lifebeyond.byzmy.pro.protected.html    # Pro 版（加密）
├── experience-protected.html              # 免费版（备份命名）
└── experience-pro-protected.html          # Pro 版（备份命名）
```

> ⚠️ **绝对不要把项目根目录的整个仓库推到 GitHub 公开仓库！** 那里面有未加密的源码（`lifebeyond.byzmy.html`、`experience.html`、`civilization-galaxy.js` 等），一旦公开等于把整个项目送人。

---

## 三、推送到 GitHub

### 1. 新建 GitHub 仓库

- 登录 GitHub → 右上 ➕ → **New repository**
- 仓库名：`lifebeyond-web`（随意）
- 选 **Public**（CF Pages 免费版只支持公开仓库；如果你买了 CF Pages Pro 可以选 Private）
- 不要勾任何初始化选项
- 点 **Create repository**

### 2. 把 `deploy/` 内容推到 GitHub

在你本地电脑（不是这个沙箱）打开终端：

```bash
# 把 deploy/ 目录下的文件下载到你本地
# 方法：在 IDE 里右键 deploy 文件夹 → 下载 → 解压到本地

cd ~/Downloads/deploy        # 进入你解压后的目录
git init
git add .
git commit -m "Initial deploy"
git branch -M main
git remote add origin https://github.com/你的用户名/lifebeyond-web.git
git push -u origin main
```

回到 GitHub 仓库页面刷新，应该能看到 7 个文件已上传 ✓

---

## 四、Cloudflare Pages 部署

### 1. 连接 GitHub 仓库

- 登录 https://pages.cloudflare.com → **Create a project** → **Connect to Git**
- 授权 Cloudflare 访问你的 GitHub → 选 `lifebeyond-web` 仓库
- **Build settings**：
  - Framework preset: **None**
  - Build command: **留空**
  - Build output directory: **`/`**
- 点 **Save and Deploy**
- 等 30 秒 → 拿到一个临时地址 `lifebeyond-web.pages.dev`，打开能看到落地页

### 2. 绑定你的自有域名

- CF Pages 项目页 → **Custom domains** → **Set up a custom domain**
- 输入 `lifebeyond.app` → **Continue** → **Activate domain**
- 同步操作 `www.lifebeyond.app`（让两种写法都能访问）

> 如果你的域名买在 Cloudflare：自动添加 DNS 记录 ✓  
> 如果买在其他注册商：CF 会让你添加一条 CNAME 记录，照着复制粘贴到你注册商的 DNS 管理页

### 3. 等 HTTPS 证书签发

5~30 分钟自动完成。完成后访问：

```
https://lifebeyond.app                                    → 落地页
https://lifebeyond.app/lifebeyond.byzmy.protected.html    → 免费版直链
https://lifebeyond.app/lifebeyond.byzmy.pro.protected.html → Pro 版直链
```

---

## 五、后续更新

任何时候改了代码：

```bash
# 在 Coze IDE 里
node scripts/build-protected.js
node scripts/prepare-deploy.js

# 在本地终端
cd ~/Downloads/deploy
git add .
git commit -m "更新：xxx"
git push
```

Cloudflare Pages 检测到 GitHub 仓库变化后**自动重新部署**，约 30 秒生效。

---

## 六、常见问题

### Q1：CF Pages 部署后访问空白页？
→ 检查 GitHub 仓库根目录是否有 `index.html`（不是套在 `deploy/` 子目录里）。确保 push 的是 deploy 目录的**内容**而不是 deploy 文件夹本身。

### Q2：HTTPS 证书一直不签发？
→ 大概率 DNS 没生效。在终端跑 `nslookup lifebeyond.app`，能解析到 CF 的 IP 才算 OK。

### Q3：CF Pages 流量耗尽？
→ Pages 免费版**无限带宽**，不会耗尽。但**每月 500 次构建**有上限，普通个人完全够用。

### Q4：能不能用国内服务？
→ 不能。`.cn` 必须 ICP 备案；国内静态托管全部要求实名 + 备案。如果坚持要 `.cn`，唯一可行路径是 *阿里云 OSS + CDN + 完整 ICP 备案*，时间 10~20 天 + 内容受限于个人备案规则，**不推荐**。

### Q5：源码会不会通过 GitHub 仓库泄漏？
→ 不会。我们只推送 `deploy/` 目录，它里面只有：
- 已经做了 XOR + Base64 双层混淆 + 反调试的 `.protected.html`
- 公开的落地页 `index.html`
- 不含任何 `.byzmy.html` / `civilization-galaxy.js` / 构建脚本

但要注意：**`.protected.html` 的加密强度只能挡住普通用户**，无法对抗专业人员。真正敏感的逻辑（如果有）应该放后端，不要放前端。

---

## 七、安全自检清单（推送前必看）

每次准备推送到 GitHub 前，在 IDE 里跑一遍：

```bash
ls deploy/
```

确认输出**只**包含：
- `.nojekyll`
- `README.md`
- `index.html`
- `*-protected.html`（4 份）

如果出现 `lifebeyond.byzmy.html`、`experience.html`、`civilization-galaxy.js`、`server.py`、`.coze`、`scripts/` 等字样，**停止推送**，先 `node scripts/prepare-deploy.js` 重新生成。

---

部署成功后欢迎把访问链接发我，我可以帮你检查站点可用性、链接完整性、HTTPS 配置等。
