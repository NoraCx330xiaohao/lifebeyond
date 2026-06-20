// 文明记忆宇宙 · Civilization Galaxy
// Three.js WebGL 螺旋星系实现
// 与 experience.html 通过 globalThis.CivGalaxy 通信

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const ERA_COLORS = {
  '当代': new THREE.Color('#7fdfff'),
  '工业革命': new THREE.Color('#ff9b53'),
  '文艺复兴': new THREE.Color('#9b67ff'),
  '丝绸之路': new THREE.Color('#7be08c'),
  '古代中国': new THREE.Color('#ff6e9c'),
  '古希腊': new THREE.Color('#5ec8ff'),
  '古埃及': new THREE.Color('#f5d871')
};

const FALLBACK_COLOR = new THREE.Color('#ffffff');

const VERTEX_SHADER = /* glsl */`
  uniform float uTime;
  uniform float uPickedId;
  uniform float uHoveredId;
  uniform float uFlash;
  attribute float aSize;
  attribute float aSeed;
  attribute float aId;
  attribute float aFilter;
  varying vec3 vColor;
  varying float vAlpha;
  varying float vFocused;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float persp = 320.0 / max(0.1, -mv.z);
    float pulse = 0.85 + 0.15 * sin(uTime * 1.6 + aSeed * 6.2831);
    float focusBoost = 0.0;
    if (abs(aId - uPickedId) < 0.5) focusBoost = 2.4;
    else if (abs(aId - uHoveredId) < 0.5) focusBoost = 1.5;
    float flashBoost = uFlash * 2.0;
    gl_PointSize = (aSize + focusBoost + flashBoost) * persp * pulse;
    vColor = color;
    vAlpha = mix(0.18, 1.0, aFilter);
    vFocused = focusBoost;
    gl_Position = projectionMatrix * mv;
  }
`;

const FRAGMENT_SHADER = /* glsl */`
  varying vec3 vColor;
  varying float vAlpha;
  varying float vFocused;
  void main() {
    vec2 uv = gl_PointCoord - 0.5;
    float d = length(uv);
    if (d > 0.5) discard;
    float core = smoothstep(0.5, 0.0, d);
    float halo = smoothstep(0.5, 0.18, d) * 0.55;
    vec3 col = mix(vColor, vec3(1.0), core * 0.85);
    float alpha = (core + halo) * vAlpha;
    if (vFocused > 0.5) alpha = min(1.0, alpha * 1.4);
    gl_FragColor = vec4(col, alpha);
  }
`;

const BG_VERT = /* glsl */`
  attribute float aSize;
  attribute float aSeed;
  varying float vSeed;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = aSize;
    vSeed = aSeed;
    gl_Position = projectionMatrix * mv;
  }
`;

const BG_FRAG = /* glsl */`
  varying float vSeed;
  void main() {
    vec2 uv = gl_PointCoord - 0.5;
    float d = length(uv);
    if (d > 0.5) discard;
    float a = smoothstep(0.5, 0.0, d) * (0.4 + 0.4 * fract(vSeed * 13.0));
    gl_FragColor = vec4(0.85, 0.9, 1.0, a);
  }
`;

class CivilizationGalaxy {
  constructor() {
    this.figures = [];
    this.eraFilter = null;
    this.dimFilter = null;
    this.disposed = false;
    this.onHover = null;
    this.onClick = null;
    this.onVoidClick = null;
    this._raf = null;
    this._mouseNDC = new THREE.Vector2(-2, -2);
    this._lastPickedId = -1;
    this._hoveredId = -1;
    this._focusTarget = null;
  }

  init({ canvas, figures, onHover, onClick, onVoidClick }) {
    if (!canvas || this.scene) return;
    this.canvas = canvas;
    this.figures = figures || [];
    this.onHover = onHover || (() => {});
    this.onClick = onClick || (() => {});
    this.onVoidClick = onVoidClick || (() => {});

    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;

    this.scene = new THREE.Scene();
    this.scene.background = null;

    this.camera = new THREE.PerspectiveCamera(55, w / h, 0.1, 2000);
    this.camera.position.set(0, 110, 150);
    this.camera.lookAt(0, 0, 0);

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.setSize(w, h, false);
    this.renderer.setClearColor(0x000000, 0);

    // Ambient deep space gradient via fog
    this.scene.fog = new THREE.FogExp2(0x05071a, 0.0035);

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.enablePan = true;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.18;
    this.controls.minDistance = 35;
    this.controls.maxDistance = 480;
    this.controls.maxPolarAngle = Math.PI * 0.92;
    this.controls.target.set(0, 0, 0);

    this._buildBackgroundDust();
    this._buildGalaxy();
    this._buildCoreNebula();

    this.raycaster = new THREE.Raycaster();
    this.raycaster.params.Points.threshold = 1.6;

    this._bindEvents();
    this._startLoop();
    this._handleResize = () => this._resize();
    window.addEventListener('resize', this._handleResize);
  }

  _buildBackgroundDust() {
    const N = 5000;
    const positions = new Float32Array(N * 3);
    const sizes = new Float32Array(N);
    const seeds = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      const r = 700 + Math.random() * 400;
      const t = Math.random() * Math.PI * 2;
      const p = (Math.random() - 0.5) * Math.PI;
      positions[i * 3] = Math.cos(t) * Math.cos(p) * r;
      positions[i * 3 + 1] = Math.sin(p) * r * 0.6;
      positions[i * 3 + 2] = Math.sin(t) * Math.cos(p) * r;
      sizes[i] = 0.4 + Math.random() * 0.8;
      seeds[i] = Math.random();
    }
    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
    geom.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1));
    const mat = new THREE.ShaderMaterial({
      vertexShader: BG_VERT,
      fragmentShader: BG_FRAG,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.bgPoints = new THREE.Points(geom, mat);
    this.bgPoints.frustumCulled = false;
    this.scene.add(this.bgPoints);
  }

  _buildGalaxy() {
    // 螺旋星系：2 主旋臂 + 1 次旋臂 + 核心 + 弥散晕
    // 同时把每个 figure 嵌入 galaxy 作为高亮"特殊星"
    const dustCount = 12000;
    const figCount = this.figures.length;
    const total = dustCount + figCount;
    const positions = new Float32Array(total * 3);
    const colors = new Float32Array(total * 3);
    const sizes = new Float32Array(total);
    const seeds = new Float32Array(total);
    const ids = new Float32Array(total);
    const filters = new Float32Array(total);

    const mainArms = 6;
    const sideArms = 2;
    const totalArms = mainArms + sideArms; // 8 条旋臂

    const setColor = (idx, c) => {
      colors[idx * 3] = c.r;
      colors[idx * 3 + 1] = c.g;
      colors[idx * 3 + 2] = c.b;
    };

    const eraList = Object.keys(ERA_COLORS);

    // —— 12000 颗背景恒星 ——
    for (let i = 0; i < dustCount; i++) {
      const ratio = Math.random();
      let r, y, theta, baseColor;
      if (ratio < 0.20) {
        // 核心高密度盘面 (15% radius)
        r = Math.pow(Math.random(), 1.6) * 15;
        theta = Math.random() * Math.PI * 2;
        y = (Math.random() - 0.5) * 3;
        const hot = Math.random();
        baseColor = hot > 0.5 ? new THREE.Color('#ffe6b8') : new THREE.Color('#fff4dc');
      } else if (ratio < 0.80) {
        // 旋臂 60%
        const armIdx = Math.floor(Math.random() * totalArms);
        const branchAngle = (armIdx / totalArms) * Math.PI * 2;
        const t = Math.pow(Math.random(), 0.85);
        r = 12 + t * 88;
        const turn = 2.6;
        theta = branchAngle + t * turn + (Math.random() - 0.5) * 0.32;
        const thickness = 0.11;
        y = (Math.random() - 0.5) * thickness * (16 + r * 0.04);
        // 沿臂的随机扰动
        const jitter = (Math.random() - 0.5) * 4 * Math.pow(1 - t, 0.5);
        r += jitter;
        const eraIdx = Math.min(eraList.length - 1, Math.floor(t * eraList.length));
        baseColor = ERA_COLORS[eraList[eraIdx]].clone().lerp(new THREE.Color('#ffffff'), 0.35);
      } else {
        // 弥散晕 20%
        r = 30 + Math.random() * 90;
        theta = Math.random() * Math.PI * 2;
        y = (Math.random() - 0.5) * 18;
        baseColor = new THREE.Color().setHSL(0.55 + Math.random() * 0.2, 0.4, 0.7);
      }
      positions[i * 3] = Math.cos(theta) * r;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = Math.sin(theta) * r;
      sizes[i] = 0.6 + Math.random() * 1.8;
      seeds[i] = Math.random();
      ids[i] = -1;
      filters[i] = 1;
      setColor(i, baseColor);
    }

    // —— figure 节点（嵌入 galaxy）——
    this.figureIndex = new Map(); // id → array index
    for (let f = 0; f < figCount; f++) {
      const fig = this.figures[f];
      const idx = dustCount + f;
      const eraName = fig.era || eraList[0];
      const eraIdx = eraList.indexOf(eraName);
      const armIdx = (fig.dimIndex !== undefined ? fig.dimIndex : f) % totalArms;
      const branchAngle = (armIdx / totalArms) * Math.PI * 2;
      // era 决定半径段
      const segs = eraList.length;
      const eraSeg = (eraIdx >= 0 ? eraIdx : 0) / Math.max(1, segs - 1);
      const r = 18 + eraSeg * 78 + (Math.random() - 0.5) * 5;
      const theta = branchAngle + eraSeg * 2.6 + (Math.random() - 0.5) * 0.18;
      const y = (Math.random() - 0.5) * 4;
      positions[idx * 3] = Math.cos(theta) * r;
      positions[idx * 3 + 1] = y;
      positions[idx * 3 + 2] = Math.sin(theta) * r;
      const infl = Math.max(1, Math.min(10, fig.influence || 5));
      sizes[idx] = 3.4 + infl * 0.6;
      seeds[idx] = Math.random();
      ids[idx] = f;
      filters[idx] = 1;
      const c = (ERA_COLORS[eraName] || FALLBACK_COLOR).clone();
      setColor(idx, c);
      // 缓存初始 era / dim / 索引
      fig._galaxyIndex = idx;
      this.figureIndex.set(f, idx);
    }

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geom.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
    geom.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1));
    geom.setAttribute('aId', new THREE.BufferAttribute(ids, 1));
    geom.setAttribute('aFilter', new THREE.BufferAttribute(filters, 1));

    const mat = new THREE.ShaderMaterial({
      vertexShader: VERTEX_SHADER,
      fragmentShader: FRAGMENT_SHADER,
      uniforms: {
        uTime: { value: 0 },
        uPickedId: { value: -2 },
        uHoveredId: { value: -2 },
        uFocusId: { value: -2 },
        uFlash: { value: 0.0 }
      },
      vertexColors: true,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });

    this.galaxy = new THREE.Points(geom, mat);
    this.galaxy.frustumCulled = true;
    this.scene.add(this.galaxy);
    this.uniforms = mat.uniforms;

    this._dustCount = dustCount;
    this._figStartIdx = dustCount;
    this._totalCount = total;
  }

  _buildCoreNebula() {
    // 中央"白色闪光银河"亮核 - 用 Sprite 实现柔光
    const tex = this._makeRadialTex();
    const mat = new THREE.SpriteMaterial({
      map: tex,
      color: 0xfff4dc,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      opacity: 0.85
    });
    this.coreSprite = new THREE.Sprite(mat);
    this.coreSprite.scale.set(60, 60, 1);
    this.scene.add(this.coreSprite);

    // 第二层暖晕
    const mat2 = new THREE.SpriteMaterial({
      map: tex,
      color: 0xffd49a,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      opacity: 0.45
    });
    this.coreSprite2 = new THREE.Sprite(mat2);
    this.coreSprite2.scale.set(120, 120, 1);
    this.scene.add(this.coreSprite2);

    // 蓝紫外晕
    const mat3 = new THREE.SpriteMaterial({
      map: tex,
      color: 0x4a3f8f,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      opacity: 0.28
    });
    this.coreSprite3 = new THREE.Sprite(mat3);
    this.coreSprite3.scale.set(220, 220, 1);
    this.scene.add(this.coreSprite3);
  }

  _makeRadialTex() {
    const c = document.createElement('canvas');
    c.width = c.height = 256;
    const ctx = c.getContext('2d');
    const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.18, 'rgba(255,240,210,0.85)');
    g.addColorStop(0.5, 'rgba(255,180,120,0.25)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 256, 256);
    const t = new THREE.CanvasTexture(c);
    t.needsUpdate = true;
    return t;
  }

  _bindEvents() {
    const canvas = this.canvas;
    this._onMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this._mouseNDC.set(x, y);
      this._mouseScreen = { x: e.clientX, y: e.clientY };
    };
    // 用 pointerdown/up 距离 + 时长判断 click，避免 OrbitControls 拖拽误触
    this._pdown = null;
    this._onPointerDown = (e) => {
      this._pdown = { x: e.clientX, y: e.clientY, t: performance.now() };
    };
    this._onPointerUp = (e) => {
      if (!this._pdown) return;
      const dx = e.clientX - this._pdown.x;
      const dy = e.clientY - this._pdown.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      const dur = performance.now() - this._pdown.t;
      this._pdown = null;
      // 拖拽 / 长按 → 不当点击
      if (dist > 6 || dur > 480) return;
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this._mouseNDC.set(x, y);
      const fid = this._pickFigure();
      if (fid >= 0 && this.figures[fid]) {
        this.flyToFigure(fid);
        // 等飞行结束后再弹详情卡（飞行约 1.2s）
        const fig = this.figures[fid];
        setTimeout(() => this.onClick(fig), 1200);
      } else {
        // 点击空白 → 从虚空捞记忆
        this.onVoidClick(e.clientX, e.clientY);
      }
    };
    this._onClick = (e) => { /* 兼容老监听，不做事 */ };
    canvas.addEventListener('mousemove', this._onMove);
    canvas.addEventListener('pointerdown', this._onPointerDown);
    canvas.addEventListener('pointerup', this._onPointerUp);
  }

  _pickFigure() {
    if (!this.galaxy) return -1;
    this.raycaster.setFromCamera(this._mouseNDC, this.camera);
    const intersects = this.raycaster.intersectObject(this.galaxy);
    if (!intersects.length) return -1;
    // 只挑 figure 范围内的
    const ids = this.galaxy.geometry.attributes.aId.array;
    for (const it of intersects) {
      const id = ids[it.index];
      if (id >= 0) return id;
    }
    return -1;
  }

  flyToFigure(fid) {
    if (!this.figures[fid]) return;
    const idx = this.figureIndex.get(fid);
    if (idx === undefined) return;
    const pos = this.galaxy.geometry.attributes.position;
    const tx = pos.array[idx * 3];
    const ty = pos.array[idx * 3 + 1];
    const tz = pos.array[idx * 3 + 2];
    this._focusTarget = { x: tx, y: ty, z: tz, t: 0 };
    this.controls.autoRotate = false;
    // 高亮被点击的星球（持续放大 + 光环）— uPickedId 用 figure id
    if (this.uniforms && this.uniforms.uPickedId) {
      this.uniforms.uPickedId.value = fid;
    }
  }

  setEraFilter(eraName) {
    this.eraFilter = eraName || null;
    this._refreshFilter();
  }

  setDimFilter(dimIndex) {
    this.dimFilter = (dimIndex !== undefined && dimIndex !== null) ? dimIndex : null;
    this._refreshFilter();
  }

  setSearch(query) {
    this._search = (query || '').trim().toLowerCase();
    this._refreshFilter();
  }

  resetFilters() {
    this.eraFilter = null;
    this.dimFilter = null;
    this._search = '';
    this._refreshFilter();
    this._focusTarget = null;
    this.controls.autoRotate = true;
    this.controls.target.set(0, 0, 0);
    if (this.uniforms && this.uniforms.uPickedId) {
      this.uniforms.uPickedId.value = -1;
    }
  }

  /* 星系闪光 — 虚空捞记忆时全屏脉冲 */
  flashGalaxy() {
    if (!this.uniforms) return;
    this._flashTime = performance.now();
    this._flashActive = true;
  }

  _refreshFilter() {
    if (!this.galaxy) return;
    const filters = this.galaxy.geometry.attributes.aFilter.array;
    const ids = this.galaxy.geometry.attributes.aId.array;
    const total = filters.length;
    const hasFilter = !!(this.eraFilter || this.dimFilter !== null || (this._search && this._search.length));
    for (let i = 0; i < total; i++) {
      const id = ids[i];
      if (id < 0) {
        filters[i] = hasFilter ? 0.42 : 1.0;
      } else {
        const fig = this.figures[id];
        let pass = true;
        if (this.eraFilter && fig.era !== this.eraFilter) pass = false;
        if (this.dimFilter !== null && fig.dimIndex !== this.dimFilter) pass = false;
        if (this._search && this._search.length) {
          const t = (fig.name || '') + (fig.title || '') + (fig.role || '');
          if (!t.toLowerCase().includes(this._search)) pass = false;
        }
        filters[i] = pass ? 1.0 : 0.18;
      }
    }
    this.galaxy.geometry.attributes.aFilter.needsUpdate = true;
  }

  _resize() {
    if (!this.renderer || !this.canvas) return;
    const w = this.canvas.clientWidth || window.innerWidth;
    const h = this.canvas.clientHeight || window.innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  _startLoop() {
    let last = performance.now();
    const loop = (now) => {
      if (this.disposed) return;
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const t = now * 0.001;

      if (this.galaxy) {
        this.galaxy.material.uniforms.uTime.value = t;
        this.galaxy.material.uniforms.uHoveredId.value = this._hoveredId;
      }
      if (this.coreSprite) {
        const breathe = 0.85 + 0.15 * Math.sin(t * 0.6);
        this.coreSprite.material.opacity = 0.85 * breathe;
        this.coreSprite2.material.opacity = 0.45 * breathe;
        this.coreSprite3.material.opacity = 0.28 * breathe;
      }

      // hover pick (节流：每 4 帧一次)
      if (!this._hoverFrame) this._hoverFrame = 0;
      this._hoverFrame++;
      if (this._hoverFrame % 4 === 0) {
        const fid = this._pickFigure();
        if (fid !== this._hoveredId) {
          this._hoveredId = fid;
          if (fid >= 0 && this.figures[fid]) {
            this.onHover(this.figures[fid], this._mouseScreen);
          } else {
            this.onHover(null, this._mouseScreen);
          }
        }
      }

      // flash 脉冲衰减 — 虚空捞记忆时全屏闪光
      if (this._flashActive) {
        const age = (performance.now() - this._flashTime) / 1000;
        if (age < 1.2) {
          this.uniforms.uFlash.value = Math.max(0, 1.0 - age / 1.2) * 0.6;
        } else {
          this.uniforms.uFlash.value = 0;
          this._flashActive = false;
        }
      }

      // focus animate — 相机跟随飞向目标星球
      if (this._focusTarget) {
        const f = this._focusTarget;
        f.t = Math.min(1, f.t + dt * 0.42);
        const ease = 1 - Math.pow(1 - f.t, 3);
        const tx = f.x;
        const ty = f.y;
        const tz = f.z;
        this.controls.target.lerp(new THREE.Vector3(tx, ty, tz), 0.085);
        // 把相机拉近到目标星球附近
        const cam = this.camera;
        const dir = new THREE.Vector3().subVectors(cam.position, this.controls.target).normalize();
        const targetDist = 22 + (1 - ease) * 70; // 起点远 → 终点 22
        const want = new THREE.Vector3().copy(this.controls.target).add(dir.multiplyScalar(targetDist));
        cam.position.lerp(want, 0.085);
        if (f.t >= 1) {
          // 飞行结束，保持焦点高亮（不清 uFocusId），但解锁自由控制
          this._focusTarget = null;
        }
      }

      this.controls.update();
      this.renderer.render(this.scene, this.camera);
      this._raf = requestAnimationFrame(loop);
    };
    this._raf = requestAnimationFrame(loop);
  }

  dispose() {
    this.disposed = true;
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this._handleResize) window.removeEventListener('resize', this._handleResize);
    if (this.canvas) {
      if (this._onMove) this.canvas.removeEventListener('mousemove', this._onMove);
      if (this._onClick) this.canvas.removeEventListener('click', this._onClick);
      if (this._onPointerDown) this.canvas.removeEventListener('pointerdown', this._onPointerDown);
      if (this._onPointerUp) this.canvas.removeEventListener('pointerup', this._onPointerUp);
    }
    if (this.galaxy) {
      this.galaxy.geometry.dispose();
      this.galaxy.material.dispose();
    }
    if (this.bgPoints) {
      this.bgPoints.geometry.dispose();
      this.bgPoints.material.dispose();
    }
    [this.coreSprite, this.coreSprite2, this.coreSprite3].forEach(s => {
      if (s) {
        if (s.material.map) s.material.map.dispose();
        s.material.dispose();
      }
    });
    if (this.controls) this.controls.dispose();
    if (this.renderer) this.renderer.dispose();
    this.scene = null;
    this.galaxy = null;
    this.bgPoints = null;
    this.controls = null;
    this.renderer = null;
  }
}

const instance = new CivilizationGalaxy();
globalThis.CivGalaxy = {
  init: (opts) => instance.init(opts),
  dispose: () => { instance.dispose(); },
  setEraFilter: (e) => instance.setEraFilter(e),
  setDimFilter: (d) => instance.setDimFilter(d),
  setSearch: (q) => instance.setSearch(q),
  resetFilters: () => instance.resetFilters(),
  flyToFigure: (id) => instance.flyToFigure(id),
  isReady: () => !!instance.scene
};
