# 数字彼岸 3.0 · 项目说明

## 项目概览
单 HTML 文件的「数字彼岸」沉浸式宇宙界面。所有 CSS / JS / Three.js 代码内联在 `index.html`，通过 native-static 模板的 Python http.server 提供静态预览。

## 关键文件
- `index.html`：主入口（含 5 个视图：彼岸 / 聊天 / 彼岸动态 / 社区 / 星图）。
- `.coze`：native-static 模板的运行配置，监听 `${DEPLOY_RUN_PORT}`。

## 重要模块定位
- **背景星空（Three.js）**：`#three-bg` 容器 + `initThreeBackground()`。
  - 着色器统一定义在 `starVertexShader / starFragmentShader / streamVertexShader / nebulaVertexShader / nebulaFragmentShader`。
  - 共享 uniform：`sharedUniforms = { uTime, uMouse, uResolution, uWaves[6] }`。
  - 鼠标移动波浪扩散：`emitMouseWave(x, y)` 节流推送波包到 `uWaves`，星点着色器中按 `(uTime - tEmit)` 的圆环高斯包络向外推开。
- **宇宙视图 2D Canvas**：`#universe-canvas`，由 `initUniverse / drawUniverse*` 系列函数绘制核心 / 星系节点 / 流星。
- **社区视图**：
  - 数据：`communityPosts`（含 `image` 字段为 Unsplash 缩略图）。
  - 渲染：`renderCommunityPosts(posts)` 输出 `.post-card`，`.post-card-img` 内组合 `<img class="pc-thumb">` + `<span class="pc-emoji">`。
  - 帖子提示：`.community-hint`（位于 `bottom:160px`，避开底部菜单）。
  - 共有 6 个标签页：`resonance / discover / following / trending / nearby / civilization`。前 5 个为原社区模块，**禁止删改**；第 6 个为「文明记忆宇宙」。
  - 标签切换通过 `switchCommunityTab(tab)`，galaxy-only 标签（`resonance` 与 `civilization`）会隐藏帖子流；其余标签在右侧 360px 抽屉里渲染 `.community-feed`。
- **文明记忆宇宙（civilization）**：
  - 数据：`civilizationDimensions`（6 影响力星系：社会贡献 / 创新推动 / 和平行动 / 人文精神 / 教育影响 / 时代改变）+ `civilizationEras`（6 历史时代：古代中国 / 古希腊 / 古埃及 / 丝绸之路 / 文艺复兴 / 工业革命）+ `civilizationFigures`（人物只是挂载在影响力星系下的星，可关联时代；按"影响 / 贡献 / 启发"组织，**不按财富与名气排序**）。
  - 渲染：`initCivilizationSystem()` → `drawCivilizationSector()` 在自己的 sector（位于六边形布局的第 6 个位置）绘制：中心心跳 → 时代内环 → 影响力外环 → 人物星点 → 人物到时代的细光线。
  - 交互：`handleCivilizationMouseMove / handleCivilizationClick`，hover 显示 tooltip，点击星点 / 影响力星系 / 时代分别打开 `openCivilizationFigure / openCivilizationDimension / openCivilizationEra`。
  - 跨星系联动：人物详情卡的 `related` 标签由 `navigateCivilizationTag(tag)` 处理；时代关键词跳到对应时代星系，"留学生 / 创业者 / 教育推动者"等跳到「发现星系」。
  - 收藏入口：`addCivilizationMemory(name)` 写入 `localStorage['lifebeyond_civ_memories']`，与「彼岸足迹 → 阅读笔记」共享记忆体系。
- **天气组件**：`#weather-widget` 已固定到左下角，`bottom:28px; left:48px;` 与 `.spatial-dock` 等高。
- **光标特效**：`initCosmicCursor()`（保留）；点击时 `spawnRipple` 产生光晕扩散（保留）。

## 本地运行
- 端口由 `DEPLOY_RUN_PORT` 决定，本仓默认 5000。
- 启动：`sh -c "python -m http.server ${DEPLOY_RUN_PORT} --bind 0.0.0.0"`（已写入 `.coze`）。

## 开发注意
- Three.js `ShaderMaterial` 配合 `vertexColors: true` 时，**不要**在自定义着色器里再次声明 `attribute vec3 color;` —— Three.js 会自动注入，重复声明会触发 `'color' : redefinition` 编译错误。
- 新增的 wave 着色器逻辑使用 `uTime` 而非真实秒数，调速参数（`age > 0.85`，`radius = age * 120.0`）已按 `time += 0.004` 的步长校准。
- 修改帖子数据时，新加字段需要向后兼容：`renderCommunityPosts` 没有 `image` 时回退到原 emoji 居中样式。
