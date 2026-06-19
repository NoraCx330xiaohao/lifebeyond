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
  - 共有 5 个标签页：`resonance / discover / following / trending / nearby`，**严禁**删改这 5 个原社区模块。
  - 标签切换通过 `switchCommunityTab(tab)`，galaxy-only 标签（仅 `resonance`）会隐藏帖子流；其余标签在右侧 360px 抽屉里渲染 `.community-feed`。
- **文明记忆宇宙（顶层视图 view-civilization，与彼岸足迹同级）**：
  - 触发：dock 第 4 个节点 `data-view="civilization"` → `showView('civilization')` → `initCivilizationView()`。**不在社区子模块里**，是独立顶层视图，仿照 shiyun（诗云）形态做"自由漫游的星海"。
  - 容器：`#view-civilization`（独立 canvas `#civilization-canvas`、HUD `#civilization-hud`、工具栏 `#civilization-toolbar`、图例 `#civilization-legend`）。
  - 渲染管线：独立 `civCanvas / civCtx / civCamera`（来自 `makeCamera()`）+ 独立 `animateCivilizationView()` 循环。屏幕空间星空 + 世界空间内容（应用 `civCamera.scale/x/y` 变换）。事件监听器在 `currentView !== 'civilization'` 时全部短路返回。
  - 数据：`civilizationDimensions`（6 影响力扇区：社会贡献 / 创新推动 / 和平行动 / 人文精神 / 教育影响 / 时代改变）+ `civilizationEras`（6 历史时代壳层：当代 / 工业革命 / 文艺复兴 / 丝绸之路 / 古代中国 / 古希腊 / 古埃及）+ `civilizationFigures`（60+ 人物，每人锚定到 era × dim 二维坐标，不按财富与名气排序）+ `civilizationWhispers`（匿名记忆低语池）。
  - **空间结构（仿诗云朝代壳层）**：
    - **同心壳层** = 时代：内层是当代，外层是更古老的时代（最远到古埃及），每层一个椭圆环
    - **角度扇区** = 影响力维度：六维各占 60°（六道辐射方向）
    - **每颗人物星 = 时代壳半径 × 维度扇区角度 + 微扰动**（有"厚度"的星海）
    - 时代标识星挂在该壳的西北方位，扇区灯塔挂在最外圈
  - **背景星海**：三层粒子（深空尘埃 1200 + 中层微星 460 + 前景闪烁星 140）≈ 1800 颗光点
  - **记忆光线**：`civilizationConnections` —— 共享 `related` 标签的人物两两之间的曲线，hover 时高亮（仿诗云的 4849 条赠诗弧线）
  - **记忆低语**：`civilizationWhispers` 池中随机句子，**点击空白处**会从光标位置升起一段匿名独白并淡出（仿诗云"在虚空中点击 unrank 出诗"）。`summonCivilizationWhisper(x, y)` 写入 `civilizationWhispersAlive`，`drawCivilizationWhispers()` 每帧绘制并更新生命值。
  - 渲染：`initCivilizationSystem()` 基于 `civCanvas` 中心点布局（影响力外环 / 时代内环 / 人物挂载） → `drawCivilizationView()` 每帧绘制：背景星空 → 多色文明深空星云 → 同心环 → 中心文明心跳 → 时代内环（带卫星粉尘） → 影响力外环（带能量光带 + 卫星簇） → 人物到时代的细光线 → 人物星点（带 twinkle）。
  - 工具栏 `#civilization-toolbar`：影响力 chip + 时代 chip + 搜索框 + 重置按钮。`setCivDimFilter(id)` / `setCivEraFilter(id)` 会让 civCamera 飞到对应星系并放大；`onCivSearch(q)` / `isFigureFiltered(f)` 控制人物 dim/亮显。
  - 漫游：滚轮缩放 / 拖拽平移 / 点击星点（事件统一通过 `if (currentView !== 'civilization') return;` 短路保护，不与社区/足迹相互干扰）。
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
