/* Motion library.
 *
 * Every exercise is a short loop between two or more key poses. A pose is a
 * set of joint angles in degrees:
 *   p, r, y   whole-body pitch (+ leans forward / face down), roll, yaw
 *   s, c, n   spine, chest and neck flexion (+ curls forward)
 *   st        spine twist
 *   L / R     per side: hf hip flexion, ha hip abduction, hr hip internal rotation,
 *             k knee flexion, an ankle (+ toes down), fl keep foot flat (0-1),
 *             sf shoulder flexion, sa shoulder abduction, h horizontal (+ toward front),
 *             sr arm rotation, e elbow flexion
 * `g` says how the body meets the world: which points touch the floor, which
 * stay anchored, which stay locked where they were in the first pose.
 */
(function () {
  const both = (limb) => ({ L: { ...limb }, R: { ...limb } });
  const merge = (...parts) => {
    const out = { L: {}, R: {} };
    for (const p of parts) {
      if (!p) continue;
      for (const k in p) {
        if (k === 'L' || k === 'R') Object.assign(out[k], p[k]);
        else out[k] = p[k];
      }
    }
    return out;
  };
  const mirror = (pose) => {
    const m = { ...pose, L: { ...(pose.R || {}) }, R: { ...(pose.L || {}) } };
    for (const k of ['r', 'y', 'st', 'sl']) if (m[k]) m[k] = -m[k];
    if (m.x) m.x = -m.x;
    return m;
  };

  const FEET = ['heelL', 'heelR', 'toeL', 'toeR'];
  const STAND_G = { ground: FEET, anchor: FEET };

  // Arm presets
  const ARMS = {
    hang: both({ sf: 0, sa: 8, e: 8 }),
    hips: both({ sf: -15, sa: 32, e: 95, sr: -40 }),
    cross: both({ sf: 62, sa: 22, e: 140, h: 25 }),
    forward: both({ sf: 88, sa: 8, e: 4 }),
    goblet: both({ sf: 28, sa: 14, e: 138, h: 20 }),
    backbar: both({ sf: -25, sa: 62, e: 118, sr: 70 }),
  };

  const STAND = merge(both({ ha: 5 }), ARMS.hang);

  const M = {};

  // ---------- LEGS ----------
  M.squat = (o = {}) => {
    const arms = ARMS[o.arms || 'forward'];
    const sumo = o.sumo ? both({ ha: 30, hr: -28 }) : null;
    const A = merge(STAND, arms, sumo, o.arms === 'forward' ? both({ sf: 88 }) : null);
    let B = merge(
      { p: 18, s: 24 },
      both({ hf: 108, k: 118, ha: 12 }),
      arms,
      sumo ? both({ ha: 38, hr: -30, hf: 98 }) : null,
      o.arms === 'forward' ? both({ sf: 128 }) : null,
      o.arms === 'hang' ? both({ sf: 42 }) : null,
    );
    if (o.sumo) B = merge(B, { p: 10, s: 10 }, both({ sf: o.arms === 'hang' ? 20 : undefined }));
    if (o.depth) B = merge(B, both({ hf: o.depth, k: o.depth + 8 }));
    return { poses: { A, B }, g: STAND_G, T: 2.6, faults: { knees_cave: 'B', heels_lift: 'B' } };
  };

  M.wallSit = () => {
    const base = merge({ s: -2 }, both({ hf: 88, k: 90, ha: 8 }), both({ sf: 45, sa: 12, e: 30 }));
    return {
      poses: { A: base, B: merge(base, { s: 1, n: 3 }) }, g: STAND_G, T: 3, hold: true,
      props: [{ type: 'wall', at: 'upperBack', gap: 0.0 }],
    };
  };

  M.sitToStand = () => ({
    poses: {
      A: merge({ p: 8, s: 8 }, both({ hf: 92, k: 92, ha: 8 }), ARMS.cross),
      B: merge(STAND, ARMS.cross),
    },
    g: STAND_G, T: 3,
    props: [{ type: 'chair', at: 'pelvisBottom', from: 'A' }],
    faults: { knees_cave: 'A' },
  });

  const split = (front, back, depth) => ({
    [front]: { hf: depth ? 88 : 28, k: depth ? 92 : 12, ha: 4 },
    [back]: { hf: depth ? -12 : -26, k: depth ? 100 : 18, an: depth ? 62 : 38, ha: 4 },
  });
  M.splitSquat = (o = {}) => {
    const arms = o.dumbbells ? ARMS.hang : ARMS.hips;
    return {
      poses: {
        A: merge({ s: 2 }, split('L', 'R', false), arms),
        B: merge({ s: 6 }, split('L', 'R', true), arms),
      },
      g: { ground: FEET, anchor: ['heelL', 'toeL'] }, T: 2.8,
      faults: { knees_cave: 'B' },
    };
  };

  M.reverseLunge = () => {
    const S = merge(STAND, ARMS.hips);
    const L = merge({ s: 6 }, split('L', 'R', true), ARMS.hips);
    return {
      poses: { S, L, R: mirror(L) }, seq: ['S', 'L', 'S', 'R'],
      g: { ground: FEET, anchor: FEET }, T: 2.6, cycles: 2,
    };
  };

  M.bulgarian = () => {
    const A = merge({ s: 8 }, { L: { hf: 22, k: 10 }, R: { hf: -34, k: 82, an: -60, fl: 0 } }, ARMS.hang);
    const B = merge({ s: 18, p: 4 }, { L: { hf: 92, k: 95 }, R: { hf: -8, k: 118, an: -60, fl: 0 } }, both({ sf: 18, sa: 8 }));
    return {
      poses: { A, B }, g: { ground: ['heelL', 'toeL'], anchor: ['heelL', 'toeL'] }, T: 2.8,
      props: [{ type: 'bench', under: ['toeR'], from: 'A', h: 'auto', len: 0.5, alongZ: true }],
      faults: { knees_cave: 'B' },
    };
  };

  M.stepUp = () => ({
    poses: {
      A: merge({ s: 10 }, { L: { hf: 68, k: 76 }, R: { hf: 0, k: 4 } }, ARMS.hang, { g: { ground: ['heelR', 'toeR'], anchor: ['heelL', 'toeL'], anchorAt: [0.09, 0.2] } }),
      B: merge({ s: 2 }, { L: { hf: 2, k: 4 }, R: { hf: 18, k: 34, an: 20, fl: 0 } }, ARMS.hang, { g: { ground: ['heelL', 'toeL'], groundY: 0.40, anchor: ['heelL', 'toeL'], anchorAt: [0.09, 0.2] } }),
    },
    g: {}, T: 3,
    props: [{ type: 'box', x: 0.09, z: 0.23, w: 0.5, d: 0.45, h: 0.40 }],
    faults: { knees_cave: 'A' },
  });

  M.lateralLunge = () => {
    const S = merge(both({ ha: 24 }), ARMS.cross);
    const L = merge({ p: 30, s: 14 }, { L: { hf: 92, k: 100, ha: 22 }, R: { hf: 24, k: 0, ha: 34 } }, ARMS.cross);
    return {
      poses: { S, L, R: mirror(L) }, seq: ['S', 'L', 'S', 'R'],
      g: { ground: FEET, anchor: FEET }, T: 2.6, cycles: 2,
    };
  };

  M.standingAbduction = () => ({
    poses: {
      A: merge(STAND, { R: { sa: 35, e: 40 }, L: { sa: 20 } }),
      B: merge(STAND, { sl: 0, L: { ha: 34, sa: 20 }, R: { sa: 35, e: 40 } }),
    },
    g: { ground: ['heelR', 'toeR'], anchor: ['heelR', 'toeR'], anchorAt: [-0.09, 0] }, T: 2.4,
  });

  M.bridge = (o = {}) => {
    const legsA = both({ hf: 48, k: 100 });
    if (o.single) legsA.R = { hf: 80, k: 8 };
    return {
      poses: {
        A: merge({ p: -90 }, legsA, both({ sf: 0, sa: 14, e: 2 })),
        B: merge({ p: -118 }, both({ hf: -4, k: 84 }), o.single ? { R: { hf: 8, k: 4 } } : null, both({ sf: -28, sa: 14, e: 2 })),
      },
      g: {
        level: { a: ['upperBack'], b: o.single ? ['heelL', 'toeL'] : FEET, axis: 'p', range: 30 },
        ground: ['upperBack', ...FEET], anchor: ['heelL', 'heelR'],
      },
      T: 2.6, faults: { arch_back: 'B' }, frame: 'wide',
      props: [{ type: 'mat', along: 'z' }],
    };
  };

  M.hinge = (o = {}) => {
    const kind = o.kind || 'rdl';
    const A = merge(STAND, both({ sf: 0, sa: 6, e: 4 }));
    let B;
    if (kind === 'rdl') B = merge({ p: 72, s: 2 }, both({ hf: 88, k: 20 }), both({ sf: 74, sa: 6, e: 4 }));
    if (kind === 'deadlift') B = merge({ p: 52, s: 6 }, both({ hf: 104, k: 78, ha: 10 }), both({ sf: 58, sa: 10, e: 2 }));
    if (kind === 'swing') {
      B = merge({ p: 70, s: 4 }, both({ hf: 92, k: 30, ha: 12 }), both({ sf: 20, sa: 4, e: 4 }));
      A.L.sf = A.R.sf = 90;
      A.L.sa = A.R.sa = 4;
    }
    return {
      poses: kind === 'swing' ? { A: B, B: A } : { A, B },
      g: STAND_G, T: kind === 'swing' ? 1.5 : 3,
      faults: { back_round: kind === 'swing' ? 'A' : 'B' },
    };
  };

  M.singleLegRdl = () => ({
    poses: {
      A: merge(STAND, { R: { hf: -4, k: 10, an: 20, fl: 0 } }),
      B: merge({ p: 76, s: 2 }, { L: { hf: 84, k: 16 }, R: { hf: -6, k: 4, an: -10, fl: 0 } }, both({ sf: 76, sa: 8, e: 4 })),
    },
    g: { ground: ['heelL', 'toeL'], anchor: ['heelL', 'toeL'] }, T: 3.2,
    faults: { back_round: 'B' },
  });

  M.calfRaise = (o = {}) => ({
    poses: {
      A: merge(STAND, o.seated ? null : ARMS.hips),
      B: merge(STAND, o.seated ? null : ARMS.hips, both({ an: 34 })),
    },
    g: { ground: FEET, anchor: ['toeL', 'toeR'] }, T: 2, frame: o.seated ? null : 'legs',
  });

  M.seatedCalf = () => ({
    poses: {
      A: merge(both({ hf: 90, k: 88, ha: 6 }), both({ sf: 22, sa: 10, e: 58 })),
      B: merge(both({ hf: 96, k: 88, ha: 6, an: 32 }), both({ sf: 24, sa: 10, e: 62 })),
    },
    g: { ground: FEET, anchor: FEET },
    props: [{ type: 'bench', under: ['pelvisBottom'], from: 'A', h: 'auto', len: 1.1 }, { type: 'dumbbellOn', at: ['kneeL', 'kneeR'] }],
    T: 2,
  });

  M.legPress = () => ({
    poses: {
      A: merge({ p: -52, yh: 0.62 }, both({ hf: 104, k: 18, ha: 10, an: -118, fl: 1 }), both({ sf: 20, sa: 30, e: 30 })),
      B: merge({ p: -52, yh: 0.62 }, both({ hf: 140, k: 108, ha: 14, an: -118, fl: 1 }), both({ sf: 20, sa: 30, e: 30 })),
    },
    g: {}, T: 2.8,
    props: [{ type: 'legPress' }],
    faults: { knees_cave: 'B' },
  });

  M.legCurl = () => ({
    poses: {
      A: merge({ p: 90 }, both({ hf: 0, k: 2, an: -70, fl: 0 }), both({ sf: 150, sa: 30, e: 60 })),
      B: merge({ p: 90 }, both({ hf: 4, k: 115, an: -70, fl: 0 }), both({ sf: 150, sa: 30, e: 60 })),
    },
    g: { ground: ['chestFront', 'hipFront'], groundY: 0.62, anchor: ['hipFront'] },
    props: [{ type: 'legCurl' }], T: 2.6,
  });

  M.legExtension = (o = {}) => ({
    poses: {
      A: merge({ p: -8, yh: 0.58 }, both({ hf: 90, k: 90, ha: 6, an: -10, fl: 0 }), both({ sf: 20, sa: 20, e: 30 })),
      B: merge({ p: -8, yh: 0.58 }, both({ hf: 90, k: 4, ha: 6, an: -10, fl: 0 }), both({ sf: 20, sa: 20, e: 30 })),
    },
    g: {}, T: 2.6,
    props: [o.chair ? { type: 'chair', at: 'pelvisBottom', from: 'A' } : { type: 'legExt' }],
  });

  const SIDE_LYING = (legs) => merge({ r: 90 }, legs,
    { R: { sf: 0, sa: 168, e: 60, sr: 0 }, L: { sf: 10, sa: 16, e: 50 } });
  M.clamshell = () => ({
    poses: {
      A: SIDE_LYING(both({ hf: 48, k: 88 })),
      B: SIDE_LYING(merge(both({ hf: 48, k: 88 }), { L: { ha: 42, hr: -18 } })),
    },
    g: { ground: 'all', anchor: ['pelvisSideR'] }, T: 2.4, frame: 'wide',
    props: [{ type: 'mat', along: 'x' }],
  });
  M.sideLegRaise = () => ({
    poses: {
      A: SIDE_LYING(merge(both({ hf: 4, k: 4 }), { R: { hf: 22, k: 50 } })),
      B: SIDE_LYING(merge(both({ hf: 4, k: 4 }), { R: { hf: 22, k: 50 }, L: { ha: 40 } })),
    },
    g: { ground: 'all', anchor: ['pelvisSideR'] }, T: 2.4, frame: 'wide',
    props: [{ type: 'mat', along: 'x' }],
  });

  M.lateralWalk = () => {
    const base = merge({ p: 12, s: 10 }, both({ hf: 38, k: 44, ha: 8 }), ARMS.hips);
    return {
      poses: { S: base, L: merge(base, { L: { ha: 24 } }), R: merge(base, { R: { ha: 24 } }) },
      seq: ['S', 'L', 'S', 'R'], g: STAND_G, T: 2, cycles: 2,
      props: [{ type: 'band', from: 'kneeL', to: 'kneeR' }],
      faults: { knees_cave: 'L' },
    };
  };

  const QUAD = merge({ p: 90 }, both({ hf: 90, k: 90, an: -10, fl: 0 }), both({ sf: 90, sa: 6, e: 2 }));
  const QUAD_G = { level: { a: ['handL', 'handR'], b: ['kneeL', 'kneeR'], axis: 'p', range: 25 }, ground: 'all', anchor: ['kneeL', 'kneeR'] };
  M.donkeyKick = () => ({
    poses: { A: QUAD, B: merge(QUAD, { L: { hf: -20, k: 92, an: -10, fl: 0 } }) },
    g: { ...QUAD_G, level: { ...QUAD_G.level, b: ['kneeR'] } }, T: 2.4, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }],
  });
  M.fireHydrant = () => ({
    poses: { A: QUAD, B: merge(QUAD, { L: { ha: 52, hf: 88 } }) },
    g: { ...QUAD_G, level: { ...QUAD_G.level, b: ['kneeR'] } }, T: 2.4, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }],
  });
  M.birdDog = () => {
    const L = merge(QUAD, { L: { sf: 178, e: 0 }, R: { hf: 0, k: 2, an: 20 } });
    return {
      poses: { S: QUAD, L, R: mirror(L) }, seq: ['S', 'L', 'S', 'R'],
      g: QUAD_G, poseG: { L: { ...QUAD_G, level: { a: ['handR'], b: ['kneeL'], axis: 'p', range: 25 } }, R: { ...QUAD_G, level: { a: ['handL'], b: ['kneeR'], axis: 'p', range: 25 } } },
      T: 3, cycles: 2, frame: 'wide', faults: { arch_back: 'L' },
      props: [{ type: 'mat', along: 'z' }],
    };
  };
  M.catCow = () => ({
    poses: { A: merge(QUAD, { s: -18, c: -16, n: -22 }, both({ sf: 56 })), B: merge(QUAD, { s: 22, c: 20, n: 26 }, both({ sf: 132 })) },
    g: QUAD_G, T: 4, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }],
  });

  // ---------- PUSH ----------
  const PLANK_G = (a, b, off) => ({ level: { a, b, axis: 'p', range: 40, off: off || 0 }, ground: b, anchor: a });
  M.pushup = (o = {}) => {
    const legs = o.knees ? both({ hf: 0, k: 80, an: 0, fl: 0 }) : both({ hf: 0, k: 0, an: -75, fl: 0 });
    const A = merge({ p: 72 }, legs, both({ sf: 72, sa: 12, e: 0 }));
    const B = merge({ p: 86 }, legs, both({ sf: 8, sa: 22, e: 84 }));
    const b = o.knees ? ['kneeL', 'kneeR'] : ['toeL', 'toeR'];
    const off = o.incline ? 0.45 : 0;
    return {
      poses: { A, B }, g: PLANK_G(['handL', 'handR'], b, off), T: 2.4, frame: 'wide',
      props: o.incline ? [{ type: 'bench', under: ['handL', 'handR'], from: 'A', h: 0.45, len: 0.45, wide: true }] : [{ type: 'mat', along: 'z' }],
      faults: { hips_sag: 'B' },
    };
  };
  M.pikePushup = () => ({
    poses: {
      A: merge({ p: 132 }, both({ hf: 100, k: 0, an: -30, fl: 0 }), both({ sf: 170, sa: 10, e: 0 })),
      B: merge({ p: 140 }, both({ hf: 104, k: 0, an: -30, fl: 0 }), both({ sf: 120, sa: 22, e: 88 })),
    },
    g: PLANK_G(['handL', 'handR'], ['toeL', 'toeR']), T: 2.6, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }],
  });

  const BENCH_LEGS = both({ hf: -8, k: 84, ha: 16 });
  M.benchPress = (o = {}) => ({
    poses: {
      A: merge({ p: -90 }, BENCH_LEGS, both({ sf: 90, sa: 12, e: 2 })),
      B: merge({ p: -90 }, BENCH_LEGS, both({ sf: 30, sa: 74, h: -16, e: 88, sr: 0 })),
    },
    g: { ground: FEET, anchor: FEET, lock: ['upperBack'] }, T: 2.6,
    props: [{ type: 'bench', under: ['upperBack', 'pelvisBack'], from: 'A', h: 'auto', len: 1.2, extend: -0.15 }, o.barbell ? { type: 'barbell', plates: true } : { type: 'dumbbells', axis: 'x' }],
    faults: { arch_back: 'B' },
  });

  M.shoulderPress = () => ({
    poses: {
      A: merge(STAND, both({ sf: 10, sa: 78, e: 100, sr: 88 })),
      B: merge(STAND, both({ sf: 6, sa: 166, e: 8, sr: 88 })),
    },
    g: STAND_G, T: 2.4, faults: { arch_back: 'B' },
  });
  M.lateralRaise = () => ({
    poses: { A: merge(STAND, both({ sa: 12, e: 12 })), B: merge(STAND, both({ sa: 84, e: 16, sf: 8 })) },
    g: STAND_G, T: 2.4,
  });
  M.frontRaise = () => ({
    poses: { A: merge(STAND, both({ sf: 4, sa: 6, e: 6 })), B: merge(STAND, both({ sf: 88, sa: 6, e: 6 })) },
    g: STAND_G, T: 2.4,
  });
  M.benchDip = () => ({
    poses: {
      A: merge({ yh: 0.62 }, both({ hf: 76, k: 4, ha: 6, an: 30, fl: 0 }), both({ sf: -38, sa: 14, e: 0 })),
      B: merge({ yh: 0.62, s: 6 }, both({ hf: 60, k: 0, ha: 6, an: 40, fl: 0 }), both({ sf: -70, sa: 14, e: 92 })),
    },
    g: { ground: ['heelL', 'heelR'], anchor: ['heelL', 'heelR'], anchorAt: [0, 0.9], lock: ['handL', 'handR'] }, T: 2.4,
    props: [{ type: 'bench', under: ['handL', 'handR'], from: 'A', h: 'auto', len: 0.45, wide: true, extend: -0.1 }],
  });
  M.overheadTriceps = () => ({
    poses: {
      A: merge(STAND, both({ sf: 168, sa: 14, e: 142, h: 20 })),
      B: merge(STAND, both({ sf: 168, sa: 14, e: 8, h: 20 })),
    },
    g: STAND_G, T: 2.4,
  });
  M.pushdown = () => ({
    poses: {
      A: merge({ p: 10 }, STAND, { p: 10 }, both({ sf: 4, sa: 8, e: 104 })),
      B: merge({ p: 10 }, STAND, { p: 10 }, both({ sf: 4, sa: 8, e: 6 })),
    },
    g: STAND_G, T: 2.2,
    props: [{ type: 'cable', pulley: [0, 2.05, 0.5], to: ['handL', 'handR'] }],
  });
  M.wallSlide = () => ({
    poses: {
      A: merge(STAND, both({ sf: 0, sa: 82, e: 92, sr: 88 })),
      B: merge(STAND, both({ sf: 0, sa: 160, e: 16, sr: 88 })),
    },
    g: STAND_G, T: 3,
    props: [{ type: 'wall', at: 'upperBack', gap: 0.0 }],
  });

  // ---------- PULL ----------
  M.pulldown = () => ({
    poses: {
      A: merge({ yh: 0.66, s: -6 }, both({ hf: 88, k: 92, ha: 10 }), both({ sa: 158, e: 8, sr: 88 })),
      B: merge({ yh: 0.66, s: -12 }, both({ hf: 88, k: 92, ha: 10 }), both({ sf: 10, sa: 44, e: 112, sr: 88 })),
    },
    g: { ground: FEET, anchor: FEET, lock: ['pelvisBottom'] }, T: 2.6,
    props: [{ type: 'pulldown' }],
    faults: { lean_back: 'B' },
  });
  M.pullup = () => ({
    poses: {
      A: merge(both({ hf: 20, k: 50 }), both({ sa: 160, e: 6, sr: 88 })),
      B: merge({ s: -6 }, both({ hf: 24, k: 56 }), both({ sf: 10, sa: 46, e: 116, sr: 88 })),
    },
    g: { pin: ['handL', 'handR'], pinAt: [0, 2.3, 0], lock: ['handL', 'handR'] }, T: 2.8,
    props: [{ type: 'pullupBar' }],
  });
  M.bentRow = () => ({
    poses: {
      A: merge({ p: 52, s: 2 }, both({ hf: 72, k: 26 }), both({ sf: 54, sa: 10, e: 4 })),
      B: merge({ p: 52, s: 2 }, both({ hf: 72, k: 26 }), both({ sf: -18, sa: 16, e: 92 })),
    },
    g: STAND_G, T: 2.4, faults: { back_round: 'A' },
  });
  M.singleArmRow = () => ({
    poses: {
      A: merge({ p: 84, s: 0 }, { L: { hf: 92, k: 90, an: 0, fl: 0 }, R: { hf: 78, k: 6 } }, { L: { sf: 84, sa: 8, e: 0 }, R: { sf: 84, sa: 8, e: 4 } }),
      B: merge({ p: 84, s: 0 }, { L: { hf: 92, k: 90, an: 0, fl: 0 }, R: { hf: 78, k: 6 } }, { L: { sf: 84, sa: 8, e: 0 }, R: { sf: 6, sa: 14, e: 96 } }),
    },
    g: { ground: ['heelR', 'toeR'], anchor: ['heelR', 'toeR'], anchorAt: [-0.2, 0] }, T: 2.4,
    props: [{ type: 'bench', under: ['kneeL', 'handL'], from: 'A', h: 'auto', len: 1.1, x: 0.1 }, { type: 'dumbbell', hand: 'R' }],
  });
  M.cableRow = () => ({
    poses: {
      A: merge({ p: 6, yh: 0.55 }, both({ hf: 84, k: 22, ha: 6, an: -40 }), both({ sf: 86, sa: 8, e: 0 })),
      B: merge({ p: -4, yh: 0.55 }, both({ hf: 84, k: 22, ha: 6, an: -40 }), both({ sf: -14, sa: 12, e: 96 })),
    },
    g: { pin: ['pelvisBottom'], pinAt: [0, 0.46, 0] }, T: 2.4,
    props: [{ type: 'bench', under: ['pelvisBottom'], from: 'A', h: 'auto', len: 0.9 }, { type: 'cable', pulley: [0, 0.5, 1.2], to: ['handL', 'handR'], column: true }],
    faults: { back_round: 'A' },
  });
  M.pullApart = () => ({
    poses: {
      A: merge(STAND, both({ sa: 90, h: 86, e: 0 })),
      B: merge(STAND, both({ sa: 90, h: -4, e: 0 })),
    },
    g: STAND_G, T: 2.2, props: [{ type: 'band', from: 'handL', to: 'handR' }],
  });
  M.facePull = () => ({
    poses: {
      A: merge(STAND, both({ sa: 88, h: 84, e: 2, sr: 88 })),
      B: merge(STAND, both({ sa: 88, h: -18, e: 104, sr: 88 })),
    },
    g: STAND_G, T: 2.4,
    props: [{ type: 'cable', pulley: [0, 1.55, 1.25], to: ['handL', 'handR'], column: true }],
  });
  M.curl = () => ({
    poses: { A: merge(STAND, both({ sf: 2, sa: 8, e: 6 })), B: merge(STAND, both({ sf: 12, sa: 8, e: 138 })) },
    g: STAND_G, T: 2.2,
  });
  M.reverseFly = () => ({
    poses: {
      A: merge({ p: 62, s: 2 }, both({ hf: 78, k: 22 }), both({ sf: 62, sa: 6, e: 18 })),
      B: merge({ p: 62, s: 2 }, both({ hf: 78, k: 22 }), both({ sf: 62, sa: 84, e: 18 })),
    },
    g: STAND_G, T: 2.4,
  });
  M.superman = () => ({
    poses: {
      A: merge({ p: 90 }, both({ hf: 0, k: 0, an: 50, fl: 0 }), both({ sf: 172, sa: 14, e: 4 })),
      B: merge({ p: 90, s: -14, c: -12, n: -10 }, both({ hf: -16, k: 0, an: 50, fl: 0 }), both({ sf: 162, sa: 14, e: 4 })),
    },
    g: { ground: 'all', anchor: ['hipFront'] }, T: 2.6, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }],
  });

  // ---------- CORE ----------
  M.plank = () => {
    const A = merge({ p: 80 }, both({ hf: 0, k: 0, an: -75, fl: 0 }), both({ sf: 80, sa: 10, e: 92 }));
    return {
      poses: { A, B: merge(A, { s: 1, n: 2 }) }, hold: true,
      g: PLANK_G(['elbowL', 'elbowR'], ['toeL', 'toeR']), T: 3, frame: 'wide',
      props: [{ type: 'mat', along: 'z' }], faults: { hips_sag: 'A' },
    };
  };
  M.sidePlank = () => {
    const A = merge({ r: 72 }, both({ hf: 0, k: 0, ha: 0 }), { R: { sa: 78, e: 92, sf: 0 }, L: { sa: 12, e: 6 } });
    return {
      poses: { A, B: merge(A, { r: 76 }) }, hold: true,
      g: { level: { a: ['elbowR'], b: ['heelR', 'toeR'], axis: 'r', range: 25 }, ground: ['elbowR', 'heelR', 'toeR'], anchor: ['elbowR'] },
      T: 3, frame: 'wide', props: [{ type: 'mat', along: 'x' }],
    };
  };
  const SUPINE = { p: -90 };
  M.deadBug = () => {
    const S = merge(SUPINE, both({ hf: 90, k: 90, an: 10, fl: 0 }), both({ sf: 90, sa: 6, e: 0 }));
    const L = merge(S, { L: { sf: 168 }, R: { hf: 14, k: 2 } });
    return {
      poses: { S, L, R: mirror(L) }, seq: ['S', 'L', 'S', 'R'],
      g: { ground: ['upperBack', 'pelvisBack'], anchor: ['pelvisBack'] }, T: 3, cycles: 2, frame: 'wide',
      props: [{ type: 'mat', along: 'z' }], faults: { arch_back: 'L' },
    };
  };
  M.crunch = () => ({
    poses: {
      A: merge(SUPINE, both({ hf: 48, k: 100 }), ARMS.cross),
      B: merge(SUPINE, { s: 28, c: 16, n: 8 }, both({ hf: 48, k: 100 }), ARMS.cross),
    },
    g: { ground: ['pelvisBack', 'heelL', 'heelR', 'upperBack'], anchor: ['pelvisBack'] }, T: 2.2, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }],
  });
  M.legRaise = () => ({
    poses: {
      A: merge(SUPINE, both({ hf: 12, k: 2, an: 20, fl: 0 }), both({ sf: 0, sa: 14 })),
      B: merge(SUPINE, both({ hf: 88, k: 4, an: 20, fl: 0 }), both({ sf: 0, sa: 14 })),
    },
    g: { ground: ['pelvisBack', 'upperBack'], anchor: ['pelvisBack'] }, T: 3, frame: 'wide',
    props: [{ type: 'mat', along: 'z' }], faults: { arch_back: 'A' },
  });
  M.russianTwist = () => {
    const base = merge({ p: -38, s: 6 }, both({ hf: 60, k: 86, an: 10, fl: 0, ha: 8 }), both({ sf: 30, sa: 8, e: 78, h: 40 }));
    return {
      poses: { S: base, L: merge(base, { st: 40 }), R: merge(base, { st: -40 }) },
      seq: ['S', 'L', 'S', 'R'], g: { ground: ['pelvisBottom'], anchor: ['pelvisBottom'] },
      T: 2.2, cycles: 2, props: [{ type: 'mat', along: 'z' }],
    };
  };
  M.mountainClimber = () => {
    const S = merge({ p: 74 }, both({ hf: 0, k: 0, an: -75, fl: 0 }), both({ sf: 74, sa: 12, e: 0 }));
    const L = merge(S, { L: { hf: 96, k: 110, an: -20 } });
    const g = (b) => PLANK_G(['handL', 'handR'], b);
    return {
      poses: { L, R: mirror(L) }, seq: ['L', 'R'],
      g: g(['toeR']), poseG: { L: g(['toeR']), R: g(['toeL']) },
      T: 0.9, cycles: 4, frame: 'wide', props: [{ type: 'mat', along: 'z' }],
    };
  };
  M.pallof = () => ({
    poses: {
      A: merge({ p: 4 }, both({ hf: 14, k: 16, ha: 10 }), both({ sf: 34, sa: 10, e: 118, h: 30 })),
      B: merge({ p: 4 }, both({ hf: 14, k: 16, ha: 10 }), both({ sf: 88, sa: 4, e: 2, h: 14 })),
    },
    g: STAND_G, T: 2.6,
    props: [{ type: 'band', from: 'handMid', toWorld: [1.3, 1.15, 0.1], anchor: true }],
  });
  M.farmerMarch = () => {
    const S = merge(STAND, both({ sf: 0, sa: 10, e: 2 }));
    const L = merge(S, { L: { hf: 70, k: 80, an: 10 } });
    return {
      poses: { L, S, R: mirror(L) }, seq: ['S', 'L', 'S', 'R'],
      g: STAND_G, poseG: { L: { ground: ['heelR', 'toeR'], anchor: ['heelR', 'toeR'], anchorAt: [-0.09, 0] }, R: { ground: ['heelL', 'toeL'], anchor: ['heelL', 'toeL'], anchorAt: [0.09, 0] } },
      T: 1.8, cycles: 2,
    };
  };
  M.hipFlexorStretch = () => {
    const A = merge({ p: 0 }, { L: { hf: 80, k: 86 }, R: { hf: -12, k: 92, an: 60, fl: 0 } }, ARMS.hips);
    const B = merge({ p: -4 }, { L: { hf: 70, k: 104 }, R: { hf: -30, k: 88, an: 60, fl: 0 } }, both({ sf: 172, sa: 10, e: 6 }));
    return { poses: { A, B }, g: { ground: ['heelL', 'toeL', 'kneeR'], anchor: ['kneeR'] }, T: 4, frame: 'wide', props: [{ type: 'mat', along: 'z' }] };
  };

  // Fault demos: what gets added to the pose, which joint glows, and the captions.
  const FAULTS = {
    knees_cave: { mod: both({ ha: -20, hr: 30 }), glow: ['kneeL', 'kneeR'], view: 'three', bad: 'Knees caving in', good: 'Knees track over toes' },
    heels_lift: { mod: merge({ p: -6 }, both({ an: 26, fl: 1, k: 14 })), glow: ['heelL', 'heelR'], bad: 'Heels lifting', good: 'Whole foot down' },
    back_round: { mod: { s: 26, c: 22, n: -8 }, glow: ['lowBack'], bad: 'Lower back rounding', good: 'Long, neutral spine' },
    hips_sag: { mod: merge({ s: -16 }, both({ hf: -16 })), glow: ['lowBack'], bad: 'Hips sagging', good: 'Straight line, head to heels' },
    arch_back: { mod: { s: -18, c: -10 }, glow: ['lowBack'], bad: 'Lower back arching', good: 'Ribs down, back steady' },
    lean_back: { mod: { s: -26, p: -8 }, glow: ['lowBack'], bad: 'Leaning back to cheat the weight', good: 'Chest tall, small lean' },
  };

  window.MOTIONS = M;
  window.FAULTS = FAULTS;
  window.POSE_UTIL = { both, merge, mirror };
})();
