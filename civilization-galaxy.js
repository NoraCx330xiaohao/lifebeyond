import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class CivilizationGalaxy {
  constructor() {
    this.scene = null; this.camera = null; this.renderer = null;
    this.controls = null; this.canvas = null;
    this.galaxy = null; this.bgPoints = null;
    this.coreSprite = null; this.coreSprite2 = null; this.coreSprite3 = null;
    this.uniforms = null;
    this.figures = []; this.figureIndex = new Map();
    this.raycaster = new THREE.Raycaster();
    this.raycaster.params.Points.threshold = 4.5;
    this._mouseNDC = new THREE.Vector2(-9, -9);
    this._mouseScreen = { x: 0, y: 0 };
    this._hoveredId = -1; this._hoverFrame = 0;
    this._focusTarget = null; this._flyCallback = null;
    this._flashActive = false; this._flashTime = 0;
    this._highlightEra = null; this._highlightDim = null;
    this.eraFilter = null; this.dimFilter = null; this._search = '';
    this.disposed = false; this._raf = null;
    this.onHover = () => {};
    this.onClick = () => {};
    this.onVoidClick = () => {};
  }

  async init(opts) {
    this.canvas = opts.canvas;
    this.figures = opts.figures || [];
    if (opts.onHover) this.onHover = opts.onHover;
    if (opts.onClick) this.onClick = opts.onClick;
    if (opts.onVoidClick) this.onVoidClick = opts.onVoidClick;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x000005);

    const w = this.canvas.clientWidth || window.innerWidth;
    const h = this.canvas.clientHeight || window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(55, w / h, 0.5, 2000);
    this.camera.position.set(0, 55, 150);

    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: false });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(w, h, false);

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.25;
    this.controls.minDistance = 35;
    this.controls.maxDistance = 480;
    this.controls.target.set(0, 0, 0);

    this._buildBgStars();
    this._buildGalaxy();
    this._buildCore();
    this._bindEvents();

    this._handleResize = () => this._resize();
    window.addEventListener('resize', this._handleResize);

    if (opts.onProgress) opts.onProgress(100);
    this._startLoop();
  }

  /* ──── Background Star Dust ──── */
  _buildBgStars() {
    const N = 5000;
    const pos = new Float32Array(N * 3);
    const sizes = new Float32Array(N);
    const cols = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      pos[i*3]   = (Math.random() - 0.5) * 1200;
      pos[i*3+1] = (Math.random() - 0.5) * 1200;
      pos[i*3+2] = (Math.random() - 0.5) * 1200;
      sizes[i] = 0.6 + Math.random() * 1.2;
      const b = 0.5 + Math.random() * 0.5;
      cols[i*3] = b; cols[i*3+1] = b; cols[i*3+2] = b + Math.random() * 0.15;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
    geo.setAttribute('color', new THREE.BufferAttribute(cols, 3));

    const mat = new THREE.PointsMaterial({
      size: 1.2, vertexColors: true, transparent: true, opacity: 0.55,
      depthWrite: false, sizeAttenuation: true
    });
    this.bgPoints = new THREE.Points(geo, mat);
    this.scene.add(this.bgPoints);
  }

  /* ──── Main Galaxy ──── */
  _buildGalaxy() {
    const figures = this.figures;
    const figCount = figures.length;
    const bgCount = 12000;
    const N = figCount + bgCount;
    const totalArms = 8;

    const positions = new Float32Array(N * 3);
    const colors = new Float32Array(N * 3);
    const sizes = new Float32Array(N);
    const ids = new Float32Array(N);      // -1 = background star, >=0 = figure index
    const filters = new Float32Array(N);
    const focus = new Float32Array(N);     // 0 = normal, 1 = focus-target
    const phases = new Float32Array(N);    // random phase for twinkle
    const eraArr = new Float32Array(N);    // era index (0-6)
    const dimArr = new Float32Array(N);    // dim index (0-5)

    ids.fill(-1);
    filters.fill(1.0);
    focus.fill(0);
    phases.fill(0);
    eraArr.fill(-1);
    dimArr.fill(-1);

    // Galaxy spiral model: logarithmic spiral r = a * e^(b*theta)
    const ARM_A = 4.0;
    const ARM_B = 0.18;
    const GALAXY_R = 100;
    const GALAXY_H = 8;

    // Background star placement: 3 zones
    let idx = 0;
    // Core disk (20%)
    const coreCount = Math.floor(bgCount * 0.2);
    for (let i = 0; i < coreCount; i++) {
      const r = Math.random() * GALAXY_R * 0.15;
      const theta = Math.random() * Math.PI * 2;
      const y = (Math.random() - 0.5) * GALAXY_H * 0.4;
      positions[idx*3]   = r * Math.cos(theta);
      positions[idx*3+1] = y;
      positions[idx*3+2] = r * Math.sin(theta);
      const bright = 0.7 + Math.random() * 0.3;
      colors[idx*3] = bright; colors[idx*3+1] = bright * 0.95; colors[idx*3+2] = bright * 0.85;
      sizes[idx] = 1.8 + Math.random() * 2.5;
      phases[idx] = Math.random() * 6.28;
      idx++;
    }

    // Spiral arms (60%) — 8 arms
    const armCount = Math.floor(bgCount * 0.6);
    for (let i = 0; i < armCount; i++) {
      const arm = i % totalArms;
      const armAngle = (arm / totalArms) * Math.PI * 2;
      const t = 0.05 + Math.random() * 0.95; // position along arm (full range)
      const r = 12 + t * 80; // linear radius 12→92
      const clampedR = Math.min(r, GALAXY_R);
      const jitter = (Math.random() - 0.5) * 2.5; // tight arm width
      const aJitter = (Math.random() - 0.5) * 0.15; // narrow angular spread
      const theta = armAngle + t * 6.5 + aJitter; // 6.5 radians ≈ 1 full turn
      const y = (Math.random() - 0.5) * GALAXY_H * (1 - t * 0.6);
      positions[idx*3]   = clampedR * Math.cos(theta) + jitter * 0.3;
      positions[idx*3+1] = y;
      positions[idx*3+2] = clampedR * Math.sin(theta) + jitter * 0.3;
      const bright = 0.3 + Math.random() * 0.5;
      const hueShift = Math.random();
      if (hueShift < 0.3) { // warm
        colors[idx*3] = bright; colors[idx*3+1] = bright * 0.85; colors[idx*3+2] = bright * 0.6;
      } else if (hueShift < 0.6) { // blue
        colors[idx*3] = bright * 0.6; colors[idx*3+1] = bright * 0.75; colors[idx*3+2] = bright;
      } else { // white
        colors[idx*3] = bright; colors[idx*3+1] = bright; colors[idx*3+2] = bright;
      }
      sizes[idx] = 1.0 + Math.random() * 2.0;
      phases[idx] = Math.random() * 6.28;
      idx++;
    }

    // Diffuse halo (20%)
    const haloCount = bgCount - coreCount - armCount;
    for (let i = 0; i < haloCount; i++) {
      const r = 15 + Math.random() * (GALAXY_R - 15);
      const theta = Math.random() * Math.PI * 2;
      const y = (Math.random() - 0.5) * GALAXY_H * 2;
      positions[idx*3]   = r * Math.cos(theta);
      positions[idx*3+1] = y;
      positions[idx*3+2] = r * Math.sin(theta);
      const bright = 0.15 + Math.random() * 0.35;
      colors[idx*3] = bright; colors[idx*3+1] = bright; colors[idx*3+2] = bright + 0.08;
      sizes[idx] = 0.6 + Math.random() * 1.4;
      phases[idx] = Math.random() * 6.28;
      idx++;
    }

    // Figure particles — placed near their era/dim coordinates
    const eraColors = [
      [0.55, 0.85, 1.0],  // 当代 — 冰蓝
      [1.0, 0.65, 0.2],   // 工业革命 — 暖橙
      [0.85, 0.3, 0.55],  // 文艺复兴 — 紫红
      [0.25, 0.85, 0.45], // 丝绸之路 — 翠绿
      [0.95, 0.55, 0.7],  // 古代中国 — 粉
      [0.3, 0.55, 0.95],  // 古希腊 — 蓝
      [0.95, 0.8, 0.25],  // 古埃及 — 金
    ];
    const eraList = ['当代','工业革命','文艺复兴','丝绸之路','古代中国','古希腊','古埃及'];

    for (let fi = 0; fi < figCount; fi++) {
      const fig = figures[fi];
      const eraIdx = eraList.indexOf(fig.era);
      const dimIdx = fig.dimIndex !== undefined ? fig.dimIndex : 0;
      const arm = fi % totalArms;
      const armBase = (arm / totalArms) * Math.PI * 2;
      const eraDist = eraIdx >= 0 ? 25 + eraIdx * 12 : 50;
      // log-spiral placement matching background stars
      const r = eraDist + (Math.random() - 0.5) * 8;
      const spiralAngle = armBase + Math.log(Math.max(r, 1)) * SPIRAL_B;
      const theta = spiralAngle + (dimIdx / 6) * 0.4 + (Math.random() - 0.5) * 0.15;
      const y = (Math.random() - 0.5) * GALAXY_H * 0.3;

      positions[idx*3]   = r * Math.cos(theta);
      positions[idx*3+1] = y;
      positions[idx*3+2] = r * Math.sin(theta);

      const col = eraIdx >= 0 ? eraColors[eraIdx] : [0.8, 0.8, 0.9];
      colors[idx*3]   = col[0];
      colors[idx*3+1] = col[1];
      colors[idx*3+2] = col[2];

      sizes[idx] = 3.4 + (fig.influence || 5) * 0.6;
      ids[idx] = fi;
      filters[idx] = 1.0;
      focus[idx] = 0;
      phases[idx] = Math.random() * 6.28;
      eraArr[idx] = eraIdx;
      dimArr[idx] = dimIdx;

      this.figureIndex.set(fi, idx);
      idx++;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geo.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
    geo.setAttribute('aId', new THREE.BufferAttribute(ids, 1));
    geo.setAttribute('aFilter', new THREE.BufferAttribute(filters, 1));
    geo.setAttribute('aFocus', new THREE.BufferAttribute(focus, 1));
    geo.setAttribute('aPhase', new THREE.BufferAttribute(phases, 1));
    geo.setAttribute('aEra', new THREE.BufferAttribute(eraArr, 1));
    geo.setAttribute('aDim', new THREE.BufferAttribute(dimArr, 1));

    // Custom shaders
    const vertShader = `
      attribute float aSize;
      attribute float aId;
      attribute float aFilter;
      attribute float aFocus;
      attribute float aPhase;
      attribute float aEra;
      attribute float aDim;
      uniform float uTime;
      uniform float uHoveredId;
      uniform float uPickedId;
      uniform float uFlash;
      uniform float uFocusTime;
      uniform float uHighlightEra;
      uniform float uHighlightDim;
      varying vec3 vColor;
      varying float vAlpha;
      varying float vIsFigure;
      void main() {
        vColor = color;
        vIsFigure = step(0.0, aId);
        float pulse = 1.0 + 0.04 * sin(uTime * 1.5 + aPhase);
        float dimAlpha = aFilter;
        // Hover / Picked glow
        float hoverBoost = 1.0;
        if (aId >= 0.0 && aId == uHoveredId) hoverBoost = 2.0;
        if (aId >= 0.0 && aId == uPickedId) hoverBoost = 2.4;
        // Era / Dim highlight — pulse matching stars
        float hlEra = 0.0;
        float hlDim = 0.0;
        if (uHighlightEra >= 0.0 && abs(aEra - uHighlightEra) < 0.5) {
          hlEra = 0.5 + 0.5 * sin(uTime * 4.0 + aPhase);
        }
        if (uHighlightDim >= 0.0 && abs(aDim - uHighlightDim) < 0.5) {
          hlDim = 0.5 + 0.5 * sin(uTime * 4.0 + aPhase);
        }
        float hlBoost = 1.0 + max(hlEra, hlDim) * 1.8;
        float s = aSize * hoverBoost * hlBoost * pulse * dimAlpha;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = max(1.0, s * (320.0 / -mvPosition.z));
        gl_Position = projectionMatrix * mvPosition;
        vAlpha = dimAlpha + uFlash * 0.35 + max(hlEra, hlDim) * 0.4;
        // Focus star glow
        if (aFocus > 0.5) {
          float focusPulse = 0.7 + 0.3 * sin(uTime * 3.0);
          vAlpha = min(1.0, vAlpha + focusPulse * 0.5);
          gl_PointSize *= 1.5;
        }
      }
    `;

    const fragShader = `
      varying vec3 vColor;
      varying float vAlpha;
      varying float vIsFigure;
      void main() {
        vec2 uv = gl_PointCoord - 0.5;
        float d = length(uv);
        if (d > 0.5) discard;
        float core = smoothstep(0.5, 0.0, d);
        float glow = smoothstep(0.5, 0.15, d);
        vec3 col = mix(vColor, vec3(1.0), core * 0.7);
        float a = glow * clamp(vAlpha, 0.0, 1.0);
        // Figure stars get extra white core
        if (vIsFigure > 0.5) {
          float bright = smoothstep(0.18, 0.0, d);
          col = mix(col, vec3(1.0), bright * 0.8);
          a = max(a, glow * 0.9);
        }
        gl_FragColor = vec4(col, a);
      }
    `;

    this.uniforms = {
      uTime: { value: 0 },
      uHoveredId: { value: -1 },
      uPickedId: { value: -1 },
      uFlash: { value: 0 },
      uFocusTime: { value: 0 },
      uHighlightEra: { value: -1 },
      uHighlightDim: { value: -1 },
    };

    const mat = new THREE.ShaderMaterial({
      vertexShader: vertShader,
      fragmentShader: fragShader,
      uniforms: this.uniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexColors: true,
    });

    this.galaxy = new THREE.Points(geo, mat);
    this.scene.add(this.galaxy);
  }

  /* ──── Core Glow Sprites ──── */
  _buildCore() {
    const tex = this._makeRadialTex();
    const mat1 = new THREE.SpriteMaterial({
      map: tex, color: 0xffffff, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.85
    });
    this.coreSprite = new THREE.Sprite(mat1);
    this.coreSprite.scale.set(55, 55 * 0.62, 1);
    this.scene.add(this.coreSprite);

    const mat2 = new THREE.SpriteMaterial({
      map: tex, color: 0xffd49a, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.45
    });
    this.coreSprite2 = new THREE.Sprite(mat2);
    this.coreSprite2.scale.set(120, 120 * 0.62, 1);
    this.scene.add(this.coreSprite2);

    const mat3 = new THREE.SpriteMaterial({
      map: tex, color: 0x4a3f8f, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: 0.28
    });
    this.coreSprite3 = new THREE.Sprite(mat3);
    this.coreSprite3.scale.set(220, 220 * 0.62, 1);
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

  /* ──── Events ──── */
  _bindEvents() {
    const canvas = this.canvas;
    this._onMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this._mouseNDC.set(x, y);
      this._mouseScreen = { x: e.clientX, y: e.clientY };
    };
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
      if (dist > 6 || dur > 480) return; // drag / long press → ignore
      const rect = canvas.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this._mouseNDC.set(x, y);
      const fid = this._pickFigure();
      if (fid >= 0 && this.figures[fid]) {
        this.flyToFigure(fid);
      } else {
        // Void click → summon memory from void
        this.onVoidClick(e.clientX, e.clientY);
      }
    };
    canvas.addEventListener('mousemove', this._onMove);
    canvas.addEventListener('pointerdown', this._onPointerDown);
    canvas.addEventListener('pointerup', this._onPointerUp);
  }

  _pickFigure() {
    if (!this.galaxy) return -1;
    this.raycaster.setFromCamera(this._mouseNDC, this.camera);
    const intersects = this.raycaster.intersectObject(this.galaxy);
    if (!intersects.length) return -1;
    const idArr = this.galaxy.geometry.attributes.aId.array;
    for (const it of intersects) {
      const id = idArr[it.index];
      if (id >= 0) return id;
    }
    return -1;
  }

  /* ──── Fly camera to figure ──── */
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
    if (this.uniforms && this.uniforms.uPickedId) {
      this.uniforms.uPickedId.value = fid;
    }
    // Set focus attribute on the figure particle
    const focusArr = this.galaxy.geometry.attributes.aFocus.array;
    // Reset all focus
    for (let i = 0; i < focusArr.length; i++) focusArr[i] = 0;
    focusArr[idx] = 1;
    this.galaxy.geometry.attributes.aFocus.needsUpdate = true;
    // Callback after flight
    const fig = this.figures[fid];
    this._flyCallback = () => this.onClick(fig);
  }

  /* ──── Reset camera to start ──── */
  resetCamera() {
    this._focusTarget = null;
    this._flyCallback = null;
    this.controls.autoRotate = true;
    this.controls.target.set(0, 0, 0);
    this.camera.position.set(0, 55, 150);
    if (this.uniforms) {
      this.uniforms.uPickedId.value = -1;
    }
    // Reset focus attribute
    if (this.galaxy) {
      const focusArr = this.galaxy.geometry.attributes.aFocus.array;
      for (let i = 0; i < focusArr.length; i++) focusArr[i] = 0;
      this.galaxy.geometry.attributes.aFocus.needsUpdate = true;
    }
  }

  /* ──── Filters ──── */
  setEraFilter(eraName) { this.eraFilter = eraName || null; this._refreshFilter(); }
  setDimFilter(dimIndex) { this.dimFilter = (dimIndex !== undefined && dimIndex !== null) ? dimIndex : null; this._refreshFilter(); }
  setSearch(query) { this._search = (query || '').trim().toLowerCase(); this._refreshFilter(); }
  resetFilters() {
    this.eraFilter = null; this.dimFilter = null; this._search = '';
    this._refreshFilter();
    this.resetCamera();
  }

  /* ──── Era / Dim highlight (toolbar chips) ──── */
  setEraHighlight(eraName) {
    const eraList = ['当代','工业革命','文艺复兴','丝绸之路','古代中国','古希腊','古埃及'];
    if (!eraName) {
      this._highlightEra = null;
      if (this.uniforms) this.uniforms.uHighlightEra.value = -1;
      return;
    }
    const idx = eraList.indexOf(eraName);
    this._highlightEra = idx;
    if (this.uniforms) this.uniforms.uHighlightEra.value = idx;
  }

  setDimHighlight(dimIndex) {
    if (dimIndex === null || dimIndex === undefined) {
      this._highlightDim = null;
      if (this.uniforms) this.uniforms.uHighlightDim.value = -1;
      return;
    }
    this._highlightDim = dimIndex;
    if (this.uniforms) this.uniforms.uHighlightDim.value = dimIndex;
  }

  /* ──── Galaxy flash — void memory flash ──── */
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

  /* ──── Render Loop ──── */
  _startLoop() {
    let last = performance.now();
    const loop = (now) => {
      if (this.disposed) return;
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const t = now * 0.001;

      // Uniforms
      if (this.galaxy) {
        this.uniforms.uTime.value = t;
        this.uniforms.uHoveredId.value = this._hoveredId;
      }

      // Core breathing
      if (this.coreSprite) {
        const breathe = 0.85 + 0.15 * Math.sin(t * 0.6);
        this.coreSprite.material.opacity = 0.85 * breathe;
        this.coreSprite2.material.opacity = 0.45 * breathe;
        this.coreSprite3.material.opacity = 0.28 * breathe;
      }

      // Hover pick (throttled: every 4 frames)
      this._hoverFrame = (this._hoverFrame || 0) + 1;
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

      // Flash pulse decay
      if (this._flashActive) {
        const age = (performance.now() - this._flashTime) / 1000;
        if (age < 1.2) {
          this.uniforms.uFlash.value = Math.max(0, 1.0 - age / 1.2) * 0.6;
        } else {
          this.uniforms.uFlash.value = 0;
          this._flashActive = false;
        }
      }

      // Camera fly-to
      if (this._focusTarget) {
        const f = this._focusTarget;
        f.t = Math.min(1, f.t + dt * 0.35);
        const ease = 1 - Math.pow(1 - f.t, 3);
        this.controls.target.lerp(new THREE.Vector3(f.x, f.y, f.z), 0.09);
        const cam = this.camera;
        const dir = new THREE.Vector3().subVectors(cam.position, this.controls.target).normalize();
        const targetDist = 18 + (1 - ease) * 90;
        const want = new THREE.Vector3().copy(this.controls.target).add(dir.multiplyScalar(targetDist));
        cam.position.lerp(want, 0.09);
        if (f.t >= 1) {
          this._focusTarget = null;
          if (this._flyCallback) { const cb = this._flyCallback; this._flyCallback = null; cb(); }
        }
      }

      this.controls.update();
      this.renderer.render(this.scene, this.camera);
      this._raf = requestAnimationFrame(loop);
    };
    this._raf = requestAnimationFrame(loop);
  }

  /* ──── Dispose ──── */
  dispose() {
    this.disposed = true;
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this._handleResize) window.removeEventListener('resize', this._handleResize);
    if (this.canvas) {
      if (this._onMove) this.canvas.removeEventListener('mousemove', this._onMove);
      if (this._onPointerDown) this.canvas.removeEventListener('pointerdown', this._onPointerDown);
      if (this._onPointerUp) this.canvas.removeEventListener('pointerup', this._onPointerUp);
    }
    if (this.galaxy) { this.galaxy.geometry.dispose(); this.galaxy.material.dispose(); }
    if (this.bgPoints) { this.bgPoints.geometry.dispose(); this.bgPoints.material.dispose(); }
    [this.coreSprite, this.coreSprite2, this.coreSprite3].forEach(s => {
      if (s) { if (s.material.map) s.material.map.dispose(); s.material.dispose(); }
    });
    if (this.controls) this.controls.dispose();
    if (this.renderer) this.renderer.dispose();
    this.scene = null; this.galaxy = null; this.bgPoints = null;
    this.controls = null; this.renderer = null;
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
  resetCamera: () => instance.resetCamera(),
  flashGalaxy: () => instance.flashGalaxy(),
  setEraHighlight: (era) => instance.setEraHighlight(era),
  setDimHighlight: (dim) => instance.setDimHighlight(dim),
  isReady: () => !!instance.scene
};
