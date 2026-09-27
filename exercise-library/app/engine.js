// Exercise preview engine: faceless 3D body, studio, equipment, muscle glow, camera.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';

const D2R = Math.PI / 180;
const V = () => new THREE.Vector3();
const SPHERE = new THREE.SphereGeometry(1, 32, 22);

export const MUSCLES = ['quads', 'hamstrings', 'glutes', 'glute_med', 'adductors', 'hip_flexors', 'calves', 'pecs', 'lats',
  'upper_back', 'traps', 'delts', 'rear_delts', 'biceps', 'triceps', 'forearms', 'abs', 'obliques', 'lower_back'];
const POSTERIOR = new Set(['hamstrings', 'glutes', 'calves', 'lats', 'upper_back', 'traps', 'rear_delts', 'triceps', 'lower_back', 'glute_med']);

function makeMaterials() {
  return {
    skin: new THREE.MeshStandardMaterial({ color: 0xb3b7be, roughness: 0.58, metalness: 0.04 }),
    shorts: new THREE.MeshStandardMaterial({ color: 0x141619, roughness: 0.82 }),
    glow: new THREE.MeshStandardMaterial({ color: 0xff6a2c, emissive: 0xff3c10, emissiveIntensity: 1.6, roughness: 0.45 }),
    glow2: new THREE.MeshStandardMaterial({ color: 0xd9784e, emissive: 0xa8401c, emissiveIntensity: 0.55, roughness: 0.5 }),
    rim: new THREE.MeshBasicMaterial({ color: new THREE.Color(0.55, 0.32, 2.2), side: THREE.BackSide, transparent: true, opacity: 0.9, depthWrite: false }),
    metal: new THREE.MeshStandardMaterial({ color: 0x2c3139, roughness: 0.32, metalness: 0.85 }),
    chrome: new THREE.MeshStandardMaterial({ color: 0x9aa3ad, roughness: 0.22, metalness: 0.95 }),
    rubber: new THREE.MeshStandardMaterial({ color: 0x0f1012, roughness: 0.6, metalness: 0.1 }),
    pad: new THREE.MeshStandardMaterial({ color: 0x121317, roughness: 0.78 }),
    mat: new THREE.MeshStandardMaterial({ color: 0x1c2029, roughness: 0.92 }),
    wall: new THREE.MeshStandardMaterial({ color: 0x1a1f27, roughness: 0.9 }),
    band: new THREE.MeshStandardMaterial({ color: 0x2f7d63, roughness: 0.55, emissive: 0x0a2a20, emissiveIntensity: 0.5 }),
    cable: new THREE.MeshStandardMaterial({ color: 0x0b0c0e, roughness: 0.5 }),
    bad: new THREE.MeshBasicMaterial({ color: new THREE.Color(7, 0.3, 0.2), transparent: true, opacity: 0.95 }),
    good: new THREE.MeshBasicMaterial({ color: new THREE.Color(0.3, 2.8, 0.7), transparent: true, opacity: 0.92 }),
  };
}

function lathe(len, radii, mat) {
  // Tapered limb pointing down -Y from its joint, rounded at both ends.
  const pts = [];
  const r0 = radii[0], r1 = radii[radii.length - 1];
  pts.push(new THREE.Vector2(0.0001, -len - r1 * 0.75));
  pts.push(new THREE.Vector2(r1 * 0.72, -len - r1 * 0.5));
  for (let i = radii.length - 1; i >= 0; i--) pts.push(new THREE.Vector2(radii[i], -len * (i / (radii.length - 1))));
  pts.push(new THREE.Vector2(r0 * 0.72, r0 * 0.5));
  pts.push(new THREE.Vector2(0.0001, r0 * 0.75));
  const m = new THREE.Mesh(new THREE.LatheGeometry(pts, 28), mat);
  m.castShadow = true;
  return m;
}

// ---------------------------------------------------------------- Figure
export class Figure {
  constructor(mats) {
    this.mats = mats;
    this.root = new THREE.Group();
    this.points = {};
    this.muscles = [];
    this.j = {};
    this.build();
  }

  ell(parent, pos, rad, mat, rot) {
    const m = new THREE.Mesh(SPHERE, mat);
    m.position.set(...pos);
    m.scale.set(...rad);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    parent.add(m);
    return m;
  }
  muscle(name, parent, pos, rad, rot, base) {
    const m = this.ell(parent, pos, rad, base || this.mats.skin, rot);
    const rim = new THREE.Mesh(SPHERE, this.mats.rim);
    const k = 0.014;
    rim.scale.set(1 + k / rad[0], 1 + k / rad[1], 1 + k / rad[2]);
    rim.visible = false;
    m.add(rim);
    this.muscles.push({ name, mesh: m, rim, base: base || this.mats.skin });
    return m;
  }
  point(name, parent, pos) {
    const o = new THREE.Object3D();
    o.position.set(...pos);
    parent.add(o);
    this.points[name] = o;
  }

  build() {
    const { skin, shorts } = this.mats;
    const R = this.root;
    // Pelvis (in shorts)
    this.ell(R, [0, -0.02, 0], [0.158, 0.12, 0.112], shorts);
    this.ell(R, [0, 0.04, 0], [0.142, 0.06, 0.1], shorts);
    for (const s of [1, -1]) {
      this.muscle('glutes', R, [s * 0.074, -0.065, -0.07], [0.086, 0.1, 0.072], null, shorts);
      this.muscle('glute_med', R, [s * 0.128, 0.0, -0.025], [0.05, 0.07, 0.06], null, shorts);
      this.muscle('hip_flexors', R, [s * 0.075, -0.045, 0.078], [0.042, 0.06, 0.032], [0, 0, s * 0.3], shorts);
    }
    this.point('pelvisBottom', R, [0, -0.15, -0.05]);
    this.point('pelvisBack', R, [0, -0.03, -0.135]);
    this.point('hipFront', R, [0, -0.05, 0.12]);
    this.point('pelvisSideL', R, [0.17, -0.05, 0]);
    this.point('pelvisSideR', R, [-0.17, -0.05, 0]);

    // Spine (lower torso)
    const spine = new THREE.Group(); spine.position.set(0, 0.06, 0); R.add(spine); this.j.spine = spine;
    this.ell(spine, [0, 0.09, 0], [0.132, 0.14, 0.098], skin);
    for (const row of [0.045, 0.1, 0.155]) for (const s of [1, -1])
      this.muscle('abs', spine, [s * 0.033, row, 0.078], [0.031, 0.03, 0.022]);
    for (const s of [1, -1]) {
      this.muscle('obliques', spine, [s * 0.1, 0.07, 0.035], [0.04, 0.1, 0.06]);
      this.muscle('lower_back', spine, [s * 0.042, 0.09, -0.068], [0.04, 0.11, 0.036]);
    }
    this.point('lowBack', spine, [0, 0.07, -0.11]);

    // Chest (upper torso)
    const chest = new THREE.Group(); chest.position.set(0, 0.18, 0); spine.add(chest); this.j.chest = chest;
    this.ell(chest, [0, 0.13, 0], [0.158, 0.19, 0.112], skin);
    for (const s of [1, -1]) {
      this.muscle('pecs', chest, [s * 0.074, 0.2, 0.078], [0.08, 0.062, 0.042], [0, 0, s * 0.18]);
      this.muscle('lats', chest, [s * 0.118, 0.1, -0.035], [0.056, 0.15, 0.075], [0, 0, s * 0.22]);
      this.muscle('upper_back', chest, [s * 0.06, 0.2, -0.086], [0.066, 0.09, 0.04]);
      this.muscle('traps', chest, [s * 0.07, 0.3, -0.032], [0.08, 0.04, 0.052], [0, 0, -s * 0.35]);
    }
    this.point('upperBack', chest, [0, 0.18, -0.125]);
    this.point('chestFront', chest, [0, 0.14, 0.125]);

    const neck = new THREE.Group(); neck.position.set(0, 0.31, 0); chest.add(neck); this.j.neck = neck;
    const nm = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.056, 0.13, 20), skin); nm.position.y = 0.05; nm.castShadow = true; neck.add(nm);
    const head = new THREE.Group(); head.position.set(0, 0.1, 0); neck.add(head);
    this.ell(head, [0, 0.1, 0.004], [0.084, 0.108, 0.098], skin);
    this.ell(head, [0, 0.038, 0.028], [0.066, 0.05, 0.07], skin);
    this.point('headTop', head, [0, 0.21, 0]);
    this.point('headBack', head, [0, 0.1, -0.1]);

    for (const [side, s] of [['L', 1], ['R', -1]]) {
      // Arm
      const sh = new THREE.Group(); sh.position.set(s * 0.198, 0.27, -0.01); chest.add(sh);
      const ua = new THREE.Group(); ua.rotation.order = 'XZY'; sh.add(ua);
      ua.add(lathe(0.29, [0.052, 0.05, 0.046, 0.042, 0.037], skin));
      this.muscle('delts', ua, [s * 0.01, -0.03, 0.016], [0.062, 0.08, 0.058]);
      this.muscle('rear_delts', ua, [s * 0.012, -0.035, -0.03], [0.05, 0.068, 0.044]);
      this.muscle('biceps', ua, [0, -0.15, 0.027], [0.04, 0.086, 0.04]);
      this.muscle('triceps', ua, [0, -0.14, -0.03], [0.043, 0.1, 0.04]);
      const fa = new THREE.Group(); fa.position.set(0, -0.29, 0); ua.add(fa);
      fa.add(lathe(0.25, [0.041, 0.043, 0.037, 0.03, 0.025], skin));
      this.muscle('forearms', fa, [0, -0.07, 0.004], [0.045, 0.085, 0.04]);
      this.point('elbow' + side, fa, [0, 0, -0.04]);
      const hand = new THREE.Group(); hand.position.set(0, -0.25, 0); fa.add(hand);
      this.ell(hand, [0, -0.055, 0.004], [0.028, 0.06, 0.045], skin);
      this.point('hand' + side, hand, [0, -0.07, 0]);
      this.j['sh' + side] = sh; this.j['ua' + side] = ua; this.j['fa' + side] = fa; this.j['hand' + side] = hand;

      // Leg
      const hip = new THREE.Group(); hip.rotation.order = 'XZY'; hip.position.set(s * 0.09, -0.07, 0); R.add(hip);
      hip.add(lathe(0.43, [0.085, 0.082, 0.074, 0.064, 0.054, 0.047], skin));
      const shortLeg = lathe(0.17, [0.094, 0.092, 0.089], shorts); hip.add(shortLeg);
      this.muscle('quads', hip, [0, -0.215, 0.03], [0.07, 0.18, 0.058]);
      this.muscle('hamstrings', hip, [0, -0.215, -0.03], [0.062, 0.17, 0.055]);
      this.muscle('adductors', hip, [-s * 0.045, -0.13, 0], [0.04, 0.12, 0.05]);
      const knee = new THREE.Group(); knee.position.set(0, -0.43, 0); hip.add(knee);
      this.ell(knee, [0, 0, 0.035], [0.04, 0.042, 0.03], skin);
      knee.add(lathe(0.42, [0.05, 0.055, 0.049, 0.04, 0.032, 0.027], skin));
      this.muscle('calves', knee, [0, -0.12, -0.034], [0.05, 0.11, 0.048]);
      this.point('knee' + side, knee, [0, 0, 0.06]);
      this.point('ankleBack' + side, knee, [0, -0.35, -0.06]);
      this.point('ankleFront' + side, knee, [0, -0.35, 0.06]);
      const ankle = new THREE.Group(); ankle.position.set(0, -0.42, 0); knee.add(ankle);
      this.ell(ankle, [0, -0.045, 0.05], [0.045, 0.036, 0.12], skin);
      this.point('heel' + side, ankle, [0, -0.08, -0.04]);
      this.point('toe' + side, ankle, [0, -0.08, 0.16]);
      this.j['hip' + side] = hip; this.j['knee' + side] = knee; this.j['ankle' + side] = ankle;
    }
    this.groundAll = Object.keys(this.points).filter((k) => !['lowBack'].includes(k));
  }

  setHighlight(primary = [], secondary = []) {
    const P = new Set(primary), S = new Set(secondary);
    for (const m of this.muscles) {
      if (P.has(m.name)) { m.mesh.material = this.mats.glow; m.rim.visible = true; }
      else if (S.has(m.name)) { m.mesh.material = this.mats.glow2; m.rim.visible = false; }
      else { m.mesh.material = m.base; m.rim.visible = false; }
    }
  }

  apply(P) {
    const d = (v) => (v || 0) * D2R;
    const j = this.j;
    this.root.rotation.order = 'YXZ';
    this.root.rotation.set(d(P.p), d(P.y), d(P.r));
    this.root.position.set(P.x || 0, P.yh ?? 1.0, P.z || 0);
    j.spine.rotation.set(d(P.s), d((P.st || 0) * 0.5), d(P.sl));
    j.chest.rotation.set(d(P.c), d((P.st || 0) * 0.5), 0);
    j.neck.rotation.set(d(P.n), 0, 0);
    for (const [side, s] of [['L', 1], ['R', -1]]) {
      const l = P[side] || {};
      const hf = l.hf ?? 0, k = l.k ?? 2, fl = l.fl ?? 1;
      j['hip' + side].rotation.set(-d(hf), -s * d(l.hr), s * d(l.ha ?? 4));
      j['knee' + side].rotation.set(d(k), 0, 0);
      j['ankle' + side].rotation.set(-fl * d((P.p || 0) - hf + k) + d(l.an), 0, 0);
      j['sh' + side].rotation.set(0, -s * d(l.h), 0);
      j['ua' + side].rotation.set(-d(l.sf), s * d(l.sr), s * d(l.sa ?? 7));
      j['fa' + side].rotation.set(-d(l.e ?? 8), 0, 0);
    }
  }

  wp(name, out = V()) {
    if (name === 'handMid') {
      const a = this.points.handL.getWorldPosition(V()), b = this.points.handR.getWorldPosition(V());
      return out.copy(a).add(b).multiplyScalar(0.5);
    }
    return this.points[name].getWorldPosition(out);
  }
  centroid(names) {
    const c = V();
    for (const n of names) c.add(this.wp(n));
    return c.multiplyScalar(1 / names.length);
  }
  minY(names) {
    let m = Infinity;
    for (const n of names) m = Math.min(m, this.wp(n).y);
    return m;
  }
}

// ---------------------------------------------------------------- pose math
const LIMB_KEYS = ['hf', 'ha', 'hr', 'k', 'an', 'fl', 'sf', 'sa', 'h', 'sr', 'e'];
const LIMB_DEF = { hf: 0, ha: 4, hr: 0, k: 2, an: 0, fl: 1, sf: 0, sa: 7, h: 0, sr: 0, e: 8 };
const BODY_KEYS = ['p', 'r', 'y', 'x', 'z', 'yh', 's', 'c', 'n', 'st', 'sl'];
function full(P) {
  const o = { L: {}, R: {} };
  for (const k of BODY_KEYS) o[k] = P[k] ?? (k === 'yh' ? 1.0 : 0);
  for (const s of ['L', 'R']) for (const k of LIMB_KEYS) o[s][k] = P[s]?.[k] ?? LIMB_DEF[k];
  return o;
}
function lerpPose(a, b, w) {
  const o = { L: {}, R: {} };
  for (const k of BODY_KEYS) o[k] = a[k] + (b[k] - a[k]) * w;
  for (const s of ['L', 'R']) for (const k of LIMB_KEYS) o[s][k] = a[s][k] + (b[s][k] - a[s][k]) * w;
  return o;
}
function addPose(a, mod, w) {
  if (!mod || !w) return a;
  const o = { ...a, L: { ...a.L }, R: { ...a.R } };
  for (const k in mod) {
    if (k === 'L' || k === 'R') for (const q in mod[k]) o[k][q] += mod[k][q] * w;
    else o[k] += mod[k] * w;
  }
  return o;
}
const ease = (x) => x * x * (3 - 2 * x);

// ---------------------------------------------------------------- props
function box(w, h, d, mat) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.castShadow = true; m.receiveShadow = true; return m; }
function cyl(r, len, mat, seg = 20) { const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, seg), mat); m.castShadow = true; return m; }
function rodBetween(mesh, a, b) {
  const d = V().subVectors(b, a);
  const len = d.length() || 0.0001;
  mesh.position.copy(a).addScaledVector(d, 0.5);
  mesh.scale.set(1, len, 1);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
}
function dumbbell(M, big = 1) {
  const g = new THREE.Group();
  const h = cyl(0.016, 0.15, M.chrome); h.rotation.z = Math.PI / 2; g.add(h);
  for (const s of [1, -1]) {
    const w = cyl(0.052 * big, 0.065, M.rubber, 6); w.rotation.z = Math.PI / 2; w.position.x = s * 0.105; g.add(w);
  }
  return g;
}
function kettlebell(M) {
  const g = new THREE.Group();
  const b = new THREE.Mesh(SPHERE, M.rubber); b.scale.set(0.1, 0.095, 0.1); b.position.y = -0.14; b.castShadow = true; g.add(b);
  const hdl = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.013, 10, 24, Math.PI), M.rubber); hdl.position.y = -0.06; hdl.rotation.z = 0; g.add(hdl);
  for (const s of [1, -1]) { const p = cyl(0.013, 0.06, M.rubber); p.position.set(s * 0.06, -0.07, 0); g.add(p); }
  return g;
}
function barbell(M, len = 2.0, plateR = 0.225) {
  const g = new THREE.Group();
  const bar = cyl(0.014, len, M.chrome); bar.rotation.z = Math.PI / 2; g.add(bar);
  if (plateR) for (const s of [1, -1]) {
    const p = cyl(plateR, 0.05, M.rubber, 36); p.rotation.z = Math.PI / 2; p.position.x = s * (len / 2 - 0.2); g.add(p);
    const c = cyl(0.03, 0.08, M.metal); c.rotation.z = Math.PI / 2; c.position.x = s * (len / 2 - 0.13); g.add(c);
  }
  return g;
}

// ---------------------------------------------------------------- Stage
const VIEWS = {
  side: [1, 0.16, 0.1], sideR: [-1, 0.16, 0.1], back: [0.12, 0.2, -1], front: [0.14, 0.16, 1], three: [0.8, 0.18, 0.85],
  threeBack: [0.85, 0.3, -0.7], over: [0.45, 0.85, -0.55], low: [0.28, 0.02, -1], top: [0.05, 0.85, 1],
};

export class Stage {
  constructor(width = 720, height = 1280) {
    this.M = makeMaterials();
    const r = this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    r.setPixelRatio(1);
    r.setSize(width, height, false);
    r.toneMapping = THREE.ACESFilmicToneMapping;
    r.toneMappingExposure = 1.05;
    r.shadowMap.enabled = true;
    r.shadowMap.type = THREE.PCFSoftShadowMap;
    this.canvas = r.domElement;

    const scene = this.scene = new THREE.Scene();
    scene.background = this.backdrop();
    scene.fog = new THREE.Fog(0x10141b, 6, 14);
    this.camera = new THREE.PerspectiveCamera(30, width / height, 0.05, 40);

    // Floor: a dim mirror under a dark matte layer gives a subtle reflection.
    const mirror = new Reflector(new THREE.PlaneGeometry(30, 30), { textureWidth: 512, textureHeight: 512, color: 0x6c717a, clipBias: 0.003 });
    mirror.rotation.x = -Math.PI / 2; mirror.position.y = -0.002; scene.add(mirror);
    this.mirror = mirror;
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.MeshStandardMaterial({ color: 0x10141a, roughness: 0.95, transparent: true, opacity: 0.9 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

    // Lights
    scene.add(new THREE.HemisphereLight(0x9fb0d0, 0x07090c, 0.55));
    const key = this.key = new THREE.DirectionalLight(0xfff1e6, 2.6);
    key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.radius = 6; key.shadow.bias = -0.0005;
    Object.assign(key.shadow.camera, { left: -2, right: 2, top: 2.5, bottom: -1.5, near: 0.5, far: 12 });
    scene.add(key, key.target);
    this.rimA = new THREE.DirectionalLight(0x7d9cff, 4.2);
    this.rimB = new THREE.DirectionalLight(0xb58cff, 3.0);
    this.fill = new THREE.DirectionalLight(0x8fa3c8, 0.5);
    scene.add(this.rimA, this.rimB, this.fill);

    this.figure = new Figure(this.M);
    scene.add(this.figure.root);
    this.props = new THREE.Group(); scene.add(this.props);
    this.glowBalls = [0, 1].map(() => { const m = new THREE.Mesh(SPHERE, this.M.bad); m.scale.setScalar(0.058); m.visible = false; scene.add(m); return m; });

    this.composer = new EffectComposer(r);
    this.composer.setPixelRatio(1);
    this.composer.addPass(new RenderPass(scene, this.camera));
    this.bloom = new UnrealBloomPass(new THREE.Vector2(width, height), 0.85, 0.55, 0.92);
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());
    this.size = [width, height];
  }

  backdrop() {
    const c = document.createElement('canvas'); c.width = 256; c.height = 512;
    const g = c.getContext('2d');
    const lin = g.createLinearGradient(0, 0, 0, 512);
    lin.addColorStop(0, '#0b0e13'); lin.addColorStop(0.55, '#171c25'); lin.addColorStop(1, '#0c0f14');
    g.fillStyle = lin; g.fillRect(0, 0, 256, 512);
    const rad = g.createRadialGradient(128, 220, 10, 128, 220, 230);
    rad.addColorStop(0, 'rgba(70,85,115,0.35)'); rad.addColorStop(1, 'rgba(70,85,115,0)');
    g.fillStyle = rad; g.fillRect(0, 0, 256, 512);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }

  setSize(w, h) {
    if (this.size[0] === w && this.size[1] === h) return;
    this.size = [w, h];
    this.renderer.setSize(w, h, false);
    this.composer.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    if (this.ex) this.frameCamera();
  }

  // ---- placing the body in the world
  place(P, g) {
    const f = this.figure;
    f.apply(P);
    const root = f.root;
    root.updateMatrixWorld(true);
    if (g.level) {
      const { a, b, axis = 'p', range = 30, off = 0 } = g.level;
      const base = P[axis] || 0;
      const fn = (v) => {
        f.apply({ ...P, [axis]: v });
        root.updateMatrixWorld(true);
        return (f.minY(a) - off) - f.minY(b);
      };
      let lo = base - range, hi = base + range, flo = fn(lo), best = lo, bestF = Math.abs(flo), found = false;
      const N = 12;
      for (let i = 1; i <= N; i++) {
        const v = base - range + (2 * range * i) / N, fv = fn(v);
        if (Math.abs(fv) < bestF) { bestF = Math.abs(fv); best = v; }
        if (!found && Math.sign(fv) !== Math.sign(flo)) { hi = v; found = true; break; }
        lo = v; flo = fv;
      }
      if (found) {
        for (let i = 0; i < 16; i++) {
          const m = (lo + hi) / 2, fm = fn(m);
          if (Math.sign(fm) === Math.sign(flo)) { lo = m; flo = fm; } else hi = m;
        }
        best = (lo + hi) / 2;
      }
      P = { ...P, [axis]: best };
      f.apply(P);
      root.updateMatrixWorld(true);
    }
    const shift = (dx, dy, dz) => { root.position.x += dx; root.position.y += dy; root.position.z += dz; root.updateMatrixWorld(true); };
    const all = (pts) => (pts === 'all' ? f.groundAll : pts);
    if (g.lock && this.lockTarget) {
      const c = f.centroid(g.lock); const t = this.lockTarget;
      shift(t.x - c.x, t.y - c.y, t.z - c.z);
    } else {
      if (g.pin) { const c = f.centroid(g.pin); const t = g.pinAt; shift(t[0] - c.x, t[1] - c.y, t[2] - c.z); }
      if (g.ground) shift(0, (g.groundY || 0) - f.minY(all(g.ground)), 0);
      if (g.anchor) {
        const c = f.centroid(all(g.anchor)); const [ax, az] = g.anchorAt || [0, 0];
        shift(ax - c.x, 0, az - c.z);
      }
    }
    return { pos: root.position.clone(), P };
  }

  gFor(key) { const s = this.spec; return s.poseG?.[key] || s.poses[key]?.g || s.g || {}; }

  poseAt(t, variant) {
    const s = this.spec, seq = s.seq;
    const C = this.cycle;
    const n = seq.length;
    let u = ((t % C) + C) % C / (C / n);
    const i = Math.floor(u) % n; u -= Math.floor(u);
    const hold = s.hold ? 0 : 0.14;
    const w = u < hold ? 0 : ease((u - hold) / (1 - hold));
    const ka = seq[i], kb = seq[(i + 1) % n];
    let P = lerpPose(this.full[ka], this.full[kb], w);
    let fw = 0;
    if (variant === 'fault' && this.fault) {
      const fk = this.fault.key;
      fw = (ka === fk ? 1 - w : 0) + (kb === fk ? w : 0);
      fw = 0.2 + 0.8 * fw;
      P = addPose(P, this.fault.mod, fw);
    }
    return { P, ka, kb, w, fw };
  }

  pose(t, variant = 'normal') {
    const { P, ka, kb, w } = this.poseAt(t, variant);
    const ga = this.gFor(ka), gb = this.gFor(kb);
    if (ga === gb || w === 0 || w === 1) {
      this.place(P, w === 1 ? gb : ga);
    } else {
      const A = this.place(P, ga), B = this.place(P, gb);
      const Pm = { ...P, p: A.P.p + (B.P.p - A.P.p) * w, r: A.P.r + (B.P.r - A.P.r) * w };
      this.figure.apply(Pm);
      this.figure.root.position.lerpVectors(A.pos, B.pos, w);
      this.figure.root.updateMatrixWorld(true);
    }
    for (const u of this.updaters) u();
  }

  // ---- load an exercise
  load(ex) {
    this.ex = ex;
    const build = window.MOTIONS[ex.motion];
    if (!build) throw new Error('Unknown motion ' + ex.motion);
    const spec = this.spec = build(ex.opts || {});
    spec.seq = spec.seq || ['A', 'B'];
    this.full = {};
    for (const k in spec.poses) this.full[k] = full(spec.poses[k]);
    this.cycle = spec.T * spec.seq.length / 2;
    const fk = ex.fault && spec.faults?.[ex.fault];
    this.fault = fk ? { key: fk, ...window.FAULTS[ex.fault] } : null;
    this.figure.setHighlight(ex.muscles, ex.secondary);

    // Where locked points sit, taken from the first pose.
    this.lockTarget = null;
    const g0 = this.gFor(spec.seq[0]);
    this.place(this.full[spec.seq[0]], { ...g0, lock: null });
    if (g0.lock || spec.g?.lock) this.lockTarget = this.figure.centroid(g0.lock || spec.g.lock);

    // First-pose world points for placing equipment.
    const ptA = {};
    for (const n of [...Object.keys(this.figure.points), 'handMid']) ptA[n] = this.figure.wp(n);
    this.ptA = ptA;

    // Props
    this.clearAttached();
    this.props.clear();
    this.updaters = [];
    const all = [...(spec.props || []), ...this.loadProps(ex.load)];
    for (const p of all) this.addProp(p);
    this.pose(0);
    this.frameCamera();
  }

  loadProps(load) {
    switch (load) {
      case 'dumbbells': return [{ type: 'dumbbells' }];
      case 'dumbbellsNeutral': return [{ type: 'dumbbells', neutral: true }];
      case 'goblet': case 'dumbbellCenter': return [{ type: 'dumbbellMid' }];
      case 'kettlebell': return [{ type: 'kettlebellMid' }];
      case 'barbell': return [{ type: 'barbell', plates: true }];
      case 'barbellBack': return [{ type: 'barbellBack' }];
      default: return [];
    }
  }

  addProp(p) {
    const M = this.M, f = this.figure, A = this.ptA, G = this.props;
    const add = (o) => { G.add(o); return o; };
    const every = (fn) => this.updaters.push(fn);
    const under = (names) => { const c = V(); let y = Infinity; for (const n of names) { c.add(A[n]); y = Math.min(y, A[n].y); } c.multiplyScalar(1 / names.length); return { c, y }; };
    switch (p.type) {
      case 'mat': {
        const box3 = new THREE.Box3();
        for (const n of f.groundAll) box3.expandByPoint(A[n]);
        const c = box3.getCenter(V());
        const long = p.along === 'x' ? 1.9 : 0.62, wide = p.along === 'x' ? 0.62 : 1.9;
        const m = add(box(long, 0.012, wide, M.mat)); m.position.set(c.x, 0.006, c.z); m.castShadow = false; m.userData.noFrame = true;
        break;
      }
      case 'bench': {
        const { c, y } = under(p.under);
        const h = p.h === 'auto' ? Math.max(0.2, y - 0.005) : p.h;
        const len = p.len || 1.2, w = p.wide ? 0.9 : 0.34;
        const g = add(new THREE.Group());
        const pad = box(p.alongZ === false ? len : w, 0.07, p.alongZ === false ? w : len, M.pad); pad.position.y = h - 0.035; g.add(pad);
        const frame = box(0.08, h - 0.07, len * 0.8, M.metal); frame.position.y = (h - 0.07) / 2; g.add(frame);
        for (const s of [1, -1]) { const ft = box(p.wide ? 0.8 : 0.36, 0.04, 0.06, M.metal); ft.position.set(0, 0.02, s * len * 0.42); g.add(ft); }
        g.position.set(p.x ?? c.x, 0, c.z + (p.extend || 0));
        break;
      }
      case 'box': {
        const b = add(box(p.w, p.h, p.d, M.pad)); b.position.set(p.x, p.h / 2, p.z);
        break;
      }
      case 'chair': {
        const s = A[p.at];
        const g = add(new THREE.Group()); g.position.set(0, 0, s.z + 0.04);
        const h = s.y - 0.005;
        const seat = box(0.46, 0.05, 0.44, M.pad); seat.position.y = h - 0.025; g.add(seat);
        const back = box(0.46, 0.5, 0.04, M.pad); back.position.set(0, h + 0.27, -0.24); g.add(back);
        for (const x of [-0.2, 0.2]) for (const z of [-0.2, 0.2]) { const l = box(0.03, h - 0.05, 0.03, M.metal); l.position.set(x, (h - 0.05) / 2, z); g.add(l); }
        for (const x of [-0.2, 0.2]) { const l = box(0.03, 0.5, 0.03, M.metal); l.position.set(x, h + 0.25, -0.23); g.add(l); }
        break;
      }
      case 'wall': {
        const z = A[p.at].z - (p.gap || 0);
        const w = add(box(4, 3, 0.05, M.wall)); w.position.set(0, 1.5, z - 0.025);
        break;
      }
      case 'dumbbells': {
        for (const s of ['L', 'R']) {
          const d = dumbbell(M); d.position.set(0, -0.06, 0.005);
          if (p.neutral) d.rotation.y = Math.PI / 2;
          f.j['hand' + s].add(d);
          G.userData.attached = (G.userData.attached || []).concat(d);
        }
        break;
      }
      case 'dumbbell': {
        const d = dumbbell(M); d.position.set(0, -0.06, 0.005); f.j['hand' + (p.hand || 'R')].add(d);
        G.userData.attached = (G.userData.attached || []).concat(d);
        break;
      }
      case 'dumbbellMid': {
        const d = add(dumbbell(M, 1.25)); d.rotation.z = Math.PI / 2;
        every(() => { d.position.copy(f.wp('handMid')); d.position.y -= 0.02; });
        break;
      }
      case 'dumbbellOn': {
        const d = add(dumbbell(M, 1.3)); d.scale.set(2.2, 1, 1);
        every(() => { d.position.copy(f.centroid(p.at)); d.position.y += 0.07; });
        break;
      }
      case 'kettlebellMid': {
        const k = add(kettlebell(M));
        every(() => {
          k.position.copy(f.wp('handMid'));
          const dir = V().subVectors(f.wp('handMid'), f.centroid(['elbowL', 'elbowR'])).normalize();
          k.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir);
        });
        break;
      }
      case 'barbell': {
        const b = add(barbell(M, p.plates ? 2.0 : 1.6, p.plates ? 0.225 : 0));
        every(() => { b.position.copy(f.wp('handMid')); b.position.y -= 0.005; });
        break;
      }
      case 'barbellBack': {
        const b = barbell(M, 2.0, 0.225); b.position.set(0, 0.29, -0.075); f.j.chest.add(b);
        G.userData.attached = (G.userData.attached || []).concat(b);
        break;
      }
      case 'band': {
        const rod = add(cyl(0.012, 1, M.band, 10));
        every(() => {
          const a = f.wp(p.from);
          const b = p.toWorld ? V().set(...p.toWorld) : f.wp(p.to);
          rodBetween(rod, a, b);
        });
        if (p.anchor) { const post = add(box(0.1, 1.3, 0.1, M.metal)); post.position.set(p.toWorld[0] + 0.05, 0.65, p.toWorld[2]); }
        break;
      }
      case 'cable': {
        const [px, py, pz] = p.pulley;
        if (p.column !== false) {
          const ch = Math.max(py + 0.3, 1.2);
          const col = add(box(0.16, ch, 0.16, M.metal)); col.position.set(px, ch / 2, pz + 0.12);
          const base = add(box(0.6, 0.05, 0.6, M.metal)); base.position.set(px, 0.025, pz + 0.12);
        }
        const wheel = add(cyl(0.045, 0.03, M.chrome)); wheel.rotation.z = Math.PI / 2; wheel.position.set(px, py, pz);
        const line = add(cyl(0.006, 1, M.cable, 8));
        const handle = add(cyl(0.015, 0.34, M.chrome)); handle.rotation.z = Math.PI / 2;
        every(() => {
          const h = f.wp('handMid');
          rodBetween(line, V().set(px, py, pz), h);
          handle.position.copy(h);
        });
        break;
      }
      case 'pulldown': {
        const seatY = A.pelvisBottom.y, seatZ = A.pelvisBottom.z;
        const colZ = seatZ + 0.55;
        const col = add(box(0.16, 2.5, 0.16, M.metal)); col.position.set(0, 1.25, colZ);
        const beam = add(box(0.1, 0.1, 0.62, M.metal)); beam.position.set(0, 2.45, colZ - 0.3);
        const seat = add(box(0.46, 0.07, 0.42, M.pad)); seat.position.set(0, seatY - 0.035, seatZ + 0.05);
        const post = add(box(0.08, seatY - 0.07, 0.08, M.metal)); post.position.set(0, (seatY - 0.07) / 2, seatZ + 0.05);
        const kneeY = Math.max(A.kneeL.y, A.kneeR.y) + 0.07;
        const kp = add(cyl(0.05, 0.5, M.pad)); kp.rotation.z = Math.PI / 2; kp.position.set(0, kneeY, A.kneeL.z - 0.1);
        const kpost = add(box(0.05, 0.05, colZ - A.kneeL.z + 0.1, M.metal)); kpost.position.set(0, kneeY, (colZ + A.kneeL.z - 0.1) / 2);
        const top = V().set(0, 2.42, colZ - 0.58);
        const wheel = add(cyl(0.05, 0.03, M.chrome)); wheel.rotation.z = Math.PI / 2; wheel.position.copy(top);
        const line = add(cyl(0.006, 1, M.cable, 8));
        const bar = add(cyl(0.016, 1.2, M.chrome)); bar.rotation.z = Math.PI / 2;
        every(() => { const h = f.wp('handMid'); bar.position.copy(h); rodBetween(line, top, h); });
        break;
      }
      case 'pullupBar': {
        const bar = add(cyl(0.017, 1.5, M.chrome)); bar.rotation.z = Math.PI / 2; bar.position.set(0, 2.3, 0);
        for (const s of [1, -1]) { const post = add(box(0.07, 2.36, 0.07, M.metal)); post.position.set(s * 0.78, 1.18, 0); }
        break;
      }
      case 'legPress': {
        // Back pad along the trunk and a seat under the pelvis, taken from the first pose.
        const pb = A.pelvisBack, ub = A.upperBack;
        const v = V().subVectors(ub, pb); const len = v.length() + 0.35; v.normalize();
        const back = add(box(0.5, len, 0.07, M.pad));
        back.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v);
        const nrm = new THREE.Vector3(0, 0, 1).applyQuaternion(back.quaternion);
        back.position.copy(pb).addScaledVector(v, len / 2 - 0.25).addScaledVector(nrm, -0.04);
        const seat = add(box(0.5, 0.07, 0.4, M.pad)); seat.position.set(0, A.pelvisBottom.y - 0.04, A.pelvisBottom.z + 0.08);
        seat.rotation.x = -0.25;
        const frame = add(box(0.1, A.pelvisBottom.y - 0.05, 0.1, M.metal)); frame.position.set(0, (A.pelvisBottom.y - 0.05) / 2, A.pelvisBottom.z);
        const plate = add(box(0.75, 0.035, 0.5, M.rubber));
        const rails = [];
        for (const s of [1, -1]) rails.push(add(cyl(0.025, 1, M.chrome)));
        const soles = ['heelL', 'toeL', 'heelR', 'toeR'];
        // Rails follow the line the foot plate travels between the two key poses.
        const P0 = this.full[this.spec.seq[0]], P1 = this.full[this.spec.seq[1]];
        this.place(P1, this.gFor(this.spec.seq[1]));
        const far = this.figure.centroid(soles);
        this.place(P0, this.gFor(this.spec.seq[0]));
        const near = this.figure.centroid(soles);
        const dir = V().subVectors(near, far).normalize();
        rails.forEach((r, i) => {
          const s = i ? -1 : 1;
          const a = far.clone().addScaledVector(dir, -0.3); a.x = s * 0.3; a.y -= 0.12;
          const b = near.clone().addScaledVector(dir, 0.6); b.x = s * 0.3; b.y -= 0.12;
          rodBetween(r, a, b);
        });
        const q = new THREE.Quaternion();
        every(() => {
          f.j.ankleL.getWorldQuaternion(q);
          plate.quaternion.copy(q);
          const c = f.centroid(soles);
          const down = new THREE.Vector3(0, -1, 0).applyQuaternion(q);
          plate.position.copy(c).addScaledVector(down, 0.02);
        });
        break;
      }
      case 'legCurl': {
        const top = 0.62 - 0.005;
        const zc = (A.chestFront.z + A.kneeL.z) / 2 + 0.05;
        const len = Math.abs(A.chestFront.z - A.kneeL.z) + 0.1;
        const pad = add(box(0.36, 0.08, len, M.pad)); pad.position.set(0, top - 0.04, zc);
        const frame = add(box(0.08, top - 0.08, len * 0.8, M.metal)); frame.position.set(0, (top - 0.08) / 2, zc);
        const pivot = V().set(0, A.kneeL.y, A.kneeL.z);
        const arm = add(cyl(0.02, 1, M.metal)); const roll = add(cyl(0.045, 0.34, M.pad)); roll.rotation.z = Math.PI / 2;
        every(() => { const c = f.centroid(['ankleBackL', 'ankleBackR']); roll.position.copy(c); roll.position.addScaledVector(V().subVectors(c, pivot).normalize(), 0.0); rodBetween(arm, pivot.clone().setX(0.24), c.clone().setX(0.24)); });
        break;
      }
      case 'legExt': {
        const s = A.pelvisBottom;
        const seat = add(box(0.46, 0.07, 0.46, M.pad)); seat.position.set(0, s.y - 0.035, s.z + 0.08);
        const back = add(box(0.46, 0.62, 0.07, M.pad)); back.position.set(0, s.y + 0.33, s.z - 0.17); back.rotation.x = -0.12;
        const frame = add(box(0.1, s.y - 0.07, 0.1, M.metal)); frame.position.set(0, (s.y - 0.07) / 2, s.z + 0.05);
        const pivot = V().set(0.26, A.kneeL.y, A.kneeL.z);
        const arm = add(cyl(0.02, 1, M.metal)); const roll = add(cyl(0.045, 0.34, M.pad)); roll.rotation.z = Math.PI / 2;
        every(() => { const c = f.centroid(['ankleFrontL', 'ankleFrontR']); roll.position.copy(c); rodBetween(arm, pivot, c.clone().setX(0.26)); });
        break;
      }
    }
  }

  clearAttached() {
    for (const o of this.props.userData.attached || []) o.parent?.remove(o);
    this.props.userData.attached = [];
  }

  frameCamera() {
    const f = this.figure, spec = this.spec;
    const pts = [];
    const keys = Object.keys(spec.poses);
    const names = spec.frame === 'legs'
      ? ['kneeL', 'kneeR', 'heelL', 'heelR', 'toeL', 'toeR', 'hipFront', 'pelvisBack']
      : [...f.groundAll, 'headTop'];
    for (const k of keys) {
      this.place(this.full[k], this.gFor(k));
      for (const u of this.updaters) u();
      for (const n of names) pts.push(f.wp(n));
    }
    if (spec.frame !== 'legs') {
      this.props.updateMatrixWorld(true);
      this.props.traverse((o) => {
        if (!o.isMesh || o.geometry.parameters?.width > 3 || o.userData.noFrame) return;
        const b = new THREE.Box3().setFromObject(o);
        if (b.max.y - b.min.y > 2.2) { b.min.y = Math.max(b.min.y, 0); b.max.y = Math.min(b.max.y, 2.45); }
        pts.push(b.min, b.max);
      });
    }
    if (spec.frame === 'legs') pts.push(V().set(0, 0, 0));
    const box3 = new THREE.Box3().setFromPoints(pts);
    const c = box3.getCenter(V());
    const split = this.size[0] / this.size[1] > 0.8;
    const view = split && this.fault?.view && ['side', 'sideR'].includes(this.ex.camera) ? (this.ex.faultCamera || this.fault.view) : this.ex.camera;
    const dir = V().set(...(VIEWS[view] || VIEWS.side)).normalize();
    const up = new THREE.Vector3(0, 1, 0);
    const fwd = dir.clone().negate();
    const right = V().crossVectors(fwd, up).normalize();
    const upv = V().crossVectors(right, fwd).normalize();
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, z1 = -Infinity;
    for (const p of pts) {
      const q = V().subVectors(p, c);
      const x = q.dot(right), y = q.dot(upv), z = q.dot(dir);
      x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); z1 = Math.max(z1, z);
    }
    const cam = this.camera;
    const tanV = Math.tan((cam.fov * D2R) / 2);
    const fillH = split ? 0.64 : (spec.frame === 'legs' ? 0.7 : 0.6), fillW = 0.86;
    const hh = (y1 - y0) / 2, hw = (x1 - x0) / 2;
    const dist = Math.max(hh / (tanV * fillH), hw / (tanV * cam.aspect * fillW)) + z1;
    const target = c.clone().addScaledVector(right, (x0 + x1) / 2).addScaledVector(upv, (y0 + y1) / 2);
    if (!split) target.addScaledVector(upv, dist * tanV * 0.04);
    cam.position.copy(target).addScaledVector(dir, dist);
    cam.lookAt(target);
    cam.updateMatrixWorld();

    // Light rig relative to the camera: key from front-left, two cool rims behind.
    this.key.position.copy(target).addScaledVector(dir, 3).addScaledVector(right, -2.2).addScaledVector(up, 3.2);
    this.key.target.position.copy(target);
    this.rimA.position.copy(target).addScaledVector(dir, -3).addScaledVector(right, 2.6).addScaledVector(up, 1.6);
    this.rimB.position.copy(target).addScaledVector(dir, -3).addScaledVector(right, -2.6).addScaledVector(up, 1.2);
    this.fill.position.copy(target).addScaledVector(dir, 2).addScaledVector(right, 2.5).addScaledVector(up, 0.5);
    this.pose(0);
  }

  render(t, variant = 'normal') {
    this.pose(t, variant);
    const glow = variant !== 'normal' && this.fault ? this.fault.glow : [];
    this.glowBalls.forEach((b, i) => {
      b.visible = !!glow[i];
      if (!glow[i]) return;
      b.material = variant === 'fault' ? this.M.bad : this.M.good;
      this.figure.wp(glow[i], b.position);
    });
    this.composer.render();
    return this.canvas;
  }
}

// ---------------------------------------------------------------- Muscle map thumbnails
export class MiniMap {
  constructor() {
    this.M = makeMaterials();
    this.M.skin.color.set(0x8e939b);
    this.M.shorts.color.set(0x1a1c20);
    const r = this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    r.setPixelRatio(1); r.setSize(150, 250, false);
    r.toneMapping = THREE.ACESFilmicToneMapping;
    this.scene = new THREE.Scene();
    this.scene.add(new THREE.HemisphereLight(0xc8d2e6, 0x101218, 1.4));
    const k = new THREE.DirectionalLight(0xffffff, 1.6); k.position.set(1, 2, 3); this.scene.add(k);
    const k2 = new THREE.DirectionalLight(0xffffff, 1.2); k2.position.set(-1, 2, -3); this.scene.add(k2);
    this.fig = new Figure(this.M);
    this.fig.apply(full({ L: { sa: 16, e: 10 }, R: { sa: 16, e: 10 } }));
    this.scene.add(this.fig.root);
    this.cam = new THREE.PerspectiveCamera(22, 150 / 250, 0.1, 20);
  }
  render(primary, secondary) {
    this.fig.setHighlight(primary, secondary);
    const views = { front: [0, 0, 1], back: [0, 0, -1], side: [1, 0, 0] };
    const out = {};
    for (const [name, d] of Object.entries(views)) {
      this.cam.position.set(d[0] * 5.4, 1.0, d[2] * 5.4);
      this.cam.lookAt(0, 0.92, 0);
      this.renderer.render(this.scene, this.cam);
      const c = document.createElement('canvas'); c.width = 150; c.height = 250;
      c.getContext('2d').drawImage(this.renderer.domElement, 0, 0);
      out[name] = c;
    }
    const post = primary.filter((m) => POSTERIOR.has(m)).length;
    out.best = post > primary.length / 2 ? 'back' : 'front';
    return out;
  }
}

export { full as fullPose };
