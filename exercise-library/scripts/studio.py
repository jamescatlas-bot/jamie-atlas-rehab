"""Shared Blender building blocks: the body, the muscle masks, the materials and the studio.

Runs inside Blender's Python (the `bpy` module). Coordinates are Blender's: Z up,
the body faces -Y, the body's left side is +X, units are metres.
"""
import gzip
import math
import pathlib

import bmesh
import bpy
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
MPFB = ROOT / 'assets' / 'mpfb2'

# How the base body is shaped: MakeHuman targets and their weights.
BODY_TARGETS = {
    'macrodetails/universal-male-young-maxmuscle-averageweight': 0.55,
    'macrodetails/universal-male-young-maxmuscle-minweight': 0.45,
    'macrodetails/african-male-young': 1 / 3,
    'macrodetails/asian-male-young': 1 / 3,
    'macrodetails/caucasian-male-young': 1 / 3,
    'macrodetails/proportions/male-young-maxmuscle-averageweight-idealproportions': 1.0,
    'macrodetails/height/male-young-maxmuscle-averageweight-maxheight': 0.25,
    'arms/l-upperarm-muscle-incr': 0.8, 'arms/r-upperarm-muscle-incr': 0.8,
    'arms/l-lowerarm-muscle-incr': 0.5, 'arms/r-lowerarm-muscle-incr': 0.5,
    'arms/l-upperarm-shoulder-muscle-incr': 0.8, 'arms/r-upperarm-shoulder-muscle-incr': 0.8,
    'legs/l-upperleg-muscle-incr': 0.8, 'legs/r-upperleg-muscle-incr': 0.8,
    'legs/l-lowerleg-muscle-incr': 0.7, 'legs/r-lowerleg-muscle-incr': 0.7,
    'torso/torso-muscle-dorsi-incr': 0.7, 'torso/torso-muscle-pectoral-incr': 0.6,
    'torso/torso-vshape-incr': 0.5, 'stomach/stomach-tone-incr': 1.0,
    'stomach/stomach-pregnant-decr': 0.5, 'pelvis/pelvis-tone-incr': 0.6,
    'neck/neck-scale-horiz-incr': 0.3,
}

HEAD_ITER = 150     # smoothing passes on the new head
VOXEL = 0.0035      # remesh detail in metres (smaller = finer, slower)



# ---------------------------------------------------------------- mesh data
def read_obj(path):
    verts, groups, g = [], {}, None
    for line in open(path):
        if line.startswith('v '):
            verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('g '):
            g = line.split()[1]
        elif line.startswith('f '):
            groups.setdefault(g, []).append([int(t.split('/')[0]) - 1 for t in line.split()[1:]])
    return np.array(verts), groups


def read_target(name):
    idx, off = [], []
    with gzip.open(MPFB / 'targets' / f'{name}.target.gz', 'rt') as f:
        for line in f:
            p = line.split()
            if len(p) == 4 and not line.startswith('#'):
                idx.append(int(p[0]))
                off.append([float(x) for x in p[1:]])
    return np.array(idx), np.array(off)


def shaped_vertices():
    verts, groups = read_obj(MPFB / '3dobjs' / 'base.obj')
    for name, w in BODY_TARGETS.items():
        idx, off = read_target(name)
        verts[idx] += off * w
    # MakeHuman: decimetres, Y up, facing +Z  ->  Blender: metres, Z up, facing -Y
    v = np.stack([verts[:, 0], -verts[:, 2], verts[:, 1]], axis=1) * 0.1
    return v, groups


def make_object(name, verts, faces):
    used = np.unique(np.concatenate([np.array(f) for f in faces]))
    remap = {int(o): i for i, o in enumerate(used)}
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts[used].tolist(), [], [[remap[i] for i in f] for f in faces])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def mesh_arrays(obj):
    me = obj.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    no = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('normal', no)
    ed = np.empty(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get('vertices', ed)
    return co.reshape(-1, 3), no.reshape(-1, 3), ed.reshape(-1, 2)


def neighbour_average(values, edges, n):
    acc = np.zeros_like(values); cnt = np.zeros(n)
    np.add.at(acc, edges[:, 0], values[edges[:, 1]]); np.add.at(acc, edges[:, 1], values[edges[:, 0]])
    np.add.at(cnt, edges[:, 0], 1); np.add.at(cnt, edges[:, 1], 1)
    cnt[cnt == 0] = 1
    return acc / (cnt[:, None] if values.ndim == 2 else cnt)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- body
def taubin(p, edges, weight, passes, lam=0.6, mu=-0.63):
    """Smooth without shrinking: alternate a smoothing step and a slightly larger inflating step."""
    wf = weight[:, None] if np.ndim(weight) else weight
    for _ in range(passes):
        p = p + wf * lam * (neighbour_average(p, edges, len(p)) - p)
        p = p + wf * mu * (neighbour_average(p, edges, len(p)) - p)
    return p


def faceless_head(obj):
    """Swap the MakeHuman face for a smooth, featureless head of the same shape.

    The eyes and lips are deep folds in the mesh, so no amount of smoothing removes
    them. Instead a sphere is shrunk onto the skull and jaw, smoothed until blank,
    and fused to the neck by rebuilding the whole body as one surface (voxel remesh).
    """
    from mathutils.bvhtree import BVHTree
    co, _, _ = mesh_arrays(obj)
    top = co[:, 2].max(); s = top / 1.8
    chin = top - 0.232 * s
    head = co[co[:, 2] > chin - 0.01 * s]
    core = head[np.abs(head[:, 0]) < np.percentile(np.abs(head[:, 0]), 90)]
    lo, hi = core.min(0), core.max(0)
    centre = (lo + hi) / 2; centre[0] = 0
    radius = (hi - lo) / 2 * np.array([1.0, 1.0, 1.03])

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=72, v_segments=48, radius=1.0)
    sph = np.array([v.co[:] for v in bm.verts]) * radius + centre
    edges = np.array([[e.verts[0].index, e.verts[1].index] for e in bm.edges])
    faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()

    tree = BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get())
    snap = np.array([tree.find_nearest(p.tolist())[0][:] for p in sph])
    sph = sph * 0.3 + snap * 0.7
    sph = taubin(sph, edges, 1.0, HEAD_ITER)
    # Pull the upper head toward a clean egg (no brow, nose or cheek shapes);
    # the jaw and neck keep their real shape so the head still sits naturally.
    d = (sph - centre) / radius
    egg = centre + d / np.linalg.norm(d, axis=1, keepdims=True) * radius * np.array([0.97, 0.97, 1.0])
    k = smoothstep(-0.55, -0.1, d[:, 2])[:, None] * 0.8
    sph = sph * (1 - k) + egg * k
    sph = taubin(sph, edges, 1.0, 30)
    sph += (sph - centre) * 0.015        # tiny inflate so no old feature pokes through

    # Cut the old head off just above the jaw line, cap it, and add the new head.
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > chin + 0.012 * s], context='VERTS')
    bmesh.ops.holes_fill(bm, edges=bm.edges, sides=0)
    base = len(bm.verts)
    new = [bm.verts.new(p.tolist()) for p in sph]
    for f in faces:
        try:
            bm.faces.new([new[i] for i in f])
        except ValueError:
            pass
    bm.to_mesh(obj.data); bm.free()

    rm = obj.modifiers.new('Fuse', 'REMESH')
    rm.mode = 'VOXEL'; rm.voxel_size = VOXEL * s; rm.adaptivity = 0
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier='Fuse')

    co, _, ed = mesh_arrays(obj)
    seam = smoothstep(chin - 0.06 * s, chin - 0.01 * s, co[:, 2]) * (1 - smoothstep(chin + 0.05 * s, chin + 0.09 * s, co[:, 2]))
    p = taubin(co, ed, 0.35 + 0.65 * seam, 6)
    p = taubin(p, ed, seam, 45)
    obj.data.vertices.foreach_set('co', p.ravel())
    obj.data.update()
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.shade_smooth()


def build_body():
    verts, groups = shaped_vertices()
    verts[:, 2] -= verts[:, 2][np.unique(np.concatenate([np.array(f) for f in groups['body']]))].min()
    body = make_object('Body', verts, groups['body'])
    faceless_head(body)
    sub = body.modifiers.new('Subdivision', 'SUBSURF'); sub.levels = 0; sub.render_levels = 1
    for p in body.data.polygons:
        p.use_smooth = True

    # Shorts cut from MakeHuman's tights helper: waist to mid-thigh.
    H = verts[:, 2].max()
    tights = [f for f in groups['helper-tights'] if all(0.37 * H < verts[i, 2] < 0.62 * H for i in f)]
    shorts = make_object('Shorts', verts, tights)
    bm = bmesh.new(); bm.from_mesh(shorts.data)
    for z, keep_above in ((0.585 * H, False), (0.435 * H, True)):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1),
                               clear_inner=keep_above, clear_outer=not keep_above)
    bm.to_mesh(shorts.data); bm.free()
    for p in shorts.data.polygons:
        p.use_smooth = True
    so = shorts.modifiers.new('Thickness', 'SOLIDIFY'); so.thickness = 0.006; so.offset = 1
    ss = shorts.modifiers.new('Subdivision', 'SUBSURF'); ss.levels = 1; ss.render_levels = 2
    return body, shorts


# ---------------------------------------------------------------- muscle map
# Each muscle is one or more heads. A head is an ellipse drawn on the surface of a
# body segment in (angle around the segment, position along it) coordinates:
#   segment, angle centre (0 = front, +90 = outer side, 180 = back), angle half-width,
#   start and end along the segment (0-1), teardrop skew, bulge depth in mm
HEADS = {
    'quads': [('thigh', 4, 24, 0.05, 0.88, 0.0, 5), ('thigh', 62, 34, 0.1, 0.93, 0.1, 5), ('thigh', -44, 26, 0.5, 1.0, -0.5, 5)],
    'hamstrings': [('thigh', 148, 30, 0.12, 0.95, 0, 4), ('thigh', -150, 30, 0.1, 0.95, 0, 4)],
    'adductors': [('thigh', -100, 32, 0.0, 0.6, 0.3, 3)],
    'calves': [('shin', 142, 34, 0.04, 0.55, 0.2, 5), ('shin', -150, 34, 0.02, 0.62, 0.2, 5)],
    'glutes': [('pelvis', 145, 40, 0.0, 1.0, 0.1, 5)],
    'pecs': [('chest', 40, 34, 0.0, 1.0, 0.25, 5)],
    'abs': [('abs1', 10, 9, 0.0, 1.0, 0, 3), ('abs2', 10, 9, 0.0, 1.0, 0, 3), ('abs3', 10, 9, 0.0, 1.0, 0, 3)],
    'obliques': [('waist', 72, 22, 0.0, 1.0, 0, 2)],
    'lats': [('back', 118, 30, 0.0, 1.0, 0.45, 4)],
    'lower_back': [('waist', 166, 13, 0.0, 1.0, 0, 3)],
    'upper_back': [('chest', 158, 22, 0.0, 1.0, 0, 3)],
    'traps': [('yoke', 150, 55, 0.0, 1.0, 0, 3)],
    'delts': [('upperarm', 25, 48, 0.0, 0.42, 0.3, 4), ('upperarm', 95, 42, 0.0, 0.45, 0.3, 4)],
    'rear_delts': [('upperarm', 165, 40, 0.0, 0.42, 0.3, 3)],
    'biceps': [('upperarm', 15, 52, 0.32, 0.92, 0, 4)],
    'triceps': [('upperarm', 175, 58, 0.25, 0.95, -0.2, 4)],
    'forearms': [('forearm', 40, 75, 0.02, 0.7, 0.4, 3), ('forearm', -120, 60, 0.02, 0.65, 0.4, 2)],
}
# Torso bands as (bottom, top) fractions of body height
TORSO = {'pelvis': (0.455, 0.56), 'waist': (0.555, 0.665), 'abs1': (0.655, 0.7), 'abs2': (0.615, 0.66),
         'abs3': (0.575, 0.62), 'back': (0.6, 0.77), 'chest': (0.7, 0.79), 'yoke': (0.79, 0.86)}


def _segment_coords(co, no, H):
    """Angle and position along each body segment, per side. Returns {(segment, side): (angle, t, member)}."""
    x, y, z = co.T
    s = H / 1.8
    out = {}
    for sx in (1, -1):
        # Arms (A-pose): fit a line through each arm's vertices
        top = co[(sx * x > 0.21 * s) & (sx * x < 0.27 * s) & (z > 0.7 * H)].mean(0)
        wrist = co[(sx * x > 0.45 * s) & (z > 0.585 * H) & (z < 0.64 * H)].mean(0)
        axis = (wrist - top) / np.linalg.norm(wrist - top)
        shoulder = top - axis * 0.05 * s
        rel = co - shoulder
        proj = rel @ axis
        radial = rel - np.outer(proj, axis)
        front = np.array([0, -1.0, 0]) - axis * (-axis[1]); front /= np.linalg.norm(front)
        lat = np.cross(axis, front) * -sx; lat /= np.linalg.norm(lat)
        ang = np.degrees(np.arctan2(radial @ lat, radial @ front))
        dist = np.linalg.norm(radial, axis=1)
        member = (dist < 0.075 * s) & (proj > -0.03 * s) & (sx * x > 0.12 * s)
        out[('upperarm', sx)] = (ang, proj / (0.29 * s), member)
        out[('forearm', sx)] = (ang, (proj - 0.29 * s) / (0.26 * s), member)
        # Legs: follow the centre of each leg slice
        legv = (sx * x > 0.005) & (z < 0.5 * H)
        bins = np.linspace(0, 0.5 * H, 41)
        idx = np.clip(np.digitize(z, bins) - 1, 0, 39)
        cx = np.zeros(40); cy = np.zeros(40)
        for b in range(40):
            sel = legv & (idx == b)
            if sel.any():
                cx[b], cy[b] = x[sel].mean(), y[sel].mean()
        ang = np.degrees(np.arctan2(sx * (x - cx[idx]), -(y - cy[idx])))
        knee, hip, ankle = 0.285 * H, 0.475 * H, 0.05 * H
        out[('thigh', sx)] = (ang, (hip - z) / (hip - knee), legv)
        out[('shin', sx)] = (ang, (knee - z) / (knee - ankle), legv)
        # Torso: angle around the vertical axis
        torso = (np.abs(x) < 0.2 * s) | (z > 0.8 * H)
        ycen = 0.0
        ang = np.degrees(np.arctan2(sx * x, -(y - ycen)))
        side = sx * x > -0.01 * s
        for name, (b, t) in TORSO.items():
            out[(name, sx)] = (ang, (t * H - z) / ((t - b) * H), torso & side & ~out[('upperarm', sx)][2])
    return out


def muscle_masks(obj, sculpt=True):
    """Per-head distance fields (0 at the head's centre, 1 at its edge) for every muscle.

    With sculpt=True each head is also raised a few millimetres, which deepens the
    grooves between muscles so the anatomy reads like a sculpted statue.
    """
    co, no, ed = mesh_arrays(obj)
    H = co[:, 2].max()
    seg = _segment_coords(co, no, H)
    fields = {}
    bulge = np.zeros(len(co))
    for muscle, heads in HEADS.items():
        fields[muscle] = []
        for (segment, ac, hw, t0, t1, skew, depth) in heads:
            d = np.full(len(co), np.inf)
            for sx in (1, -1):
                ang, t, member = seg[(segment, sx)]
                tm, th = (t0 + t1) / 2, (t1 - t0) / 2
                v = (t - tm) / th
                width = hw * np.clip(1 + skew * v, 0.3, 2)
                u = ((ang - ac + 180) % 360 - 180) / width
                dd = (np.abs(u) ** 2.2 + np.abs(v) ** 2.2) ** (1 / 2.2)
                dd[~member] = np.inf
                d = np.minimum(d, dd)
            for _ in range(2):
                fin = np.where(np.isfinite(d), d, 3.0)
                d = np.where(np.isfinite(d), 0.5 * fin + 0.5 * neighbour_average(fin, ed, len(fin)), d)
            fields[muscle].append(d)
            bulge += depth * 0.001 * (H / 1.8) * np.clip(1 - np.where(np.isfinite(d), d, 9) ** 2, 0, 1) ** 1.5
    if sculpt:
        b = bulge
        for _ in range(3):
            b = 0.5 * b + 0.5 * neighbour_average(b, ed, len(b))
        obj.data.vertices.foreach_set('co', (co + no * b[:, None]).ravel())
        obj.data.update()
    return fields


def head_core(d):
    return 1 - smoothstep(0.8, 0.95, np.where(np.isfinite(d), d, 9))


def head_rim(d):
    d = np.where(np.isfinite(d), d, 9)
    return smoothstep(0.74, 0.86, d) * (1 - smoothstep(0.93, 1.03, d))


def set_glow(obj, fields, primary, secondary=()):
    """Light up the named muscles: orange core, purple-blue rim on each head's edge, softer secondaries."""
    n = len(obj.data.vertices)
    core, rim, second = np.zeros(n), np.zeros(n), np.zeros(n)
    for name in primary:
        for d in fields[name]:
            core = np.maximum(core, head_core(d)); rim = np.maximum(rim, head_rim(d))
    for name in secondary:
        for d in fields[name]:
            second = np.maximum(second, head_core(d))
    for attr, vals in (('glow', core), ('rim', rim), ('glow2', second)):
        a = obj.data.attributes.get(attr) or obj.data.attributes.new(attr, 'FLOAT', 'POINT')
        a.data.foreach_set('value', vals.astype(np.float32))


# ---------------------------------------------------------------- materials
def _node(nt, kind, loc, **props):
    n = nt.nodes.new(kind); n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def body_material():
    mat = bpy.data.materials.new('Clay')
    mat.use_nodes = True
    nt = mat.node_tree; L = nt.links
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.36, 0.375, 0.4, 1)
    bsdf.inputs['Roughness'].default_value = 0.5
    bsdf.inputs['Specular IOR Level'].default_value = 0.45
    bsdf.inputs['Sheen Weight'].default_value = 0.15
    attr = _node(nt, 'ShaderNodeAttribute', (-1100, 200), attribute_name='glow')
    core = _node(nt, 'ShaderNodeMapRange', (-850, 350), interpolation_type='SMOOTHSTEP')
    core.inputs['From Min'].default_value = 0.3; core.inputs['From Max'].default_value = 0.65
    L.new(attr.outputs['Fac'], core.inputs['Value'])
    lo = _node(nt, 'ShaderNodeAttribute', (-850, 100), attribute_name='rim')
    rim = _node(nt, 'ShaderNodeMath', (-650, 100), operation='MULTIPLY', use_clamp=True)
    L.new(lo.outputs['Fac'], rim.inputs[0]); rim.inputs[1].default_value = 1.0
    # Secondary muscles: a softer amber, no rim
    attr2 = _node(nt, 'ShaderNodeAttribute', (-1100, -250), attribute_name='glow2')
    sec = _node(nt, 'ShaderNodeMapRange', (-850, -250), interpolation_type='SMOOTHSTEP')
    sec.inputs['From Min'].default_value = 0.4; sec.inputs['From Max'].default_value = 0.8
    L.new(attr2.outputs['Fac'], sec.inputs['Value'])
    # Surface colour: grey -> orange-red under the glow
    mix = _node(nt, 'ShaderNodeMix', (-400, 350), data_type='RGBA')
    mix.inputs['A'].default_value = (0.36, 0.375, 0.4, 1); mix.inputs['B'].default_value = (0.95, 0.1, 0.015, 1)
    L.new(core.outputs['Result'], mix.inputs['Factor'])
    mix2 = _node(nt, 'ShaderNodeMix', (-200, 350), data_type='RGBA')
    mix2.inputs['B'].default_value = (0.75, 0.33, 0.14, 1)
    L.new(mix.outputs['Result'], mix2.inputs['A']); L.new(sec.outputs['Result'], mix2.inputs['Factor'])
    L.new(mix2.outputs['Result'], bsdf.inputs['Base Color'])
    # Emission: orange core + purple-to-blue rim along the muscle edge
    hue = _node(nt, 'ShaderNodeMix', (-400, -50), data_type='RGBA')
    hue.inputs['A'].default_value = (0.25, 0.1, 1.0, 1); hue.inputs['B'].default_value = (0.55, 0.05, 1.0, 1)
    L.new(core.outputs['Result'], hue.inputs['Factor'])
    rimc = _node(nt, 'ShaderNodeMix', (-200, -50), data_type='RGBA', blend_type='MULTIPLY')
    rimc.inputs['Factor'].default_value = 1
    boost = _node(nt, 'ShaderNodeMath', (-550, -200), operation='MULTIPLY')
    boost.inputs[1].default_value = 1.4
    L.new(hue.outputs['Result'], rimc.inputs['A'])
    rim3 = _node(nt, 'ShaderNodeCombineColor', (-400, -200))
    L.new(rim.outputs['Value'], boost.inputs[0])
    for i in range(3):
        L.new(boost.outputs['Value'], rim3.inputs[i])
    L.new(rim3.outputs['Color'], rimc.inputs['B'])
    corec = _node(nt, 'ShaderNodeMix', (-200, 150), data_type='RGBA')
    corec.inputs['A'].default_value = (0, 0, 0, 1); corec.inputs['B'].default_value = (1.0, 0.16, 0.02, 1)
    L.new(core.outputs['Result'], corec.inputs['Factor'])
    add = _node(nt, 'ShaderNodeMix', (0, 50), data_type='RGBA', blend_type='ADD')
    add.inputs['Factor'].default_value = 1
    L.new(corec.outputs['Result'], add.inputs['A']); L.new(rimc.outputs['Result'], add.inputs['B'])
    L.new(add.outputs['Result'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 1.6
    # Muscle definition: darken the grooves between muscles (ambient occlusion + curvature)
    ao = _node(nt, 'ShaderNodeAmbientOcclusion', (-1100, 600), samples=16)
    ao.inputs['Distance'].default_value = 0.06
    geo = _node(nt, 'ShaderNodeNewGeometry', (-1100, 800))
    pt = _node(nt, 'ShaderNodeMapRange', (-850, 800))
    pt.inputs['From Min'].default_value = 0.46; pt.inputs['From Max'].default_value = 0.54
    pt.inputs['To Min'].default_value = 1.0; pt.inputs['To Max'].default_value = 1.0
    L.new(geo.outputs['Pointiness'], pt.inputs['Value'])
    aom = _node(nt, 'ShaderNodeMapRange', (-850, 600))
    aom.inputs['To Min'].default_value = 0.45
    L.new(ao.outputs['AO'], aom.inputs['Value'])
    shade = _node(nt, 'ShaderNodeMath', (-650, 700), operation='MULTIPLY')
    L.new(pt.outputs['Result'], shade.inputs[0]); L.new(aom.outputs['Result'], shade.inputs[1])
    tone = _node(nt, 'ShaderNodeMix', (-400, 600), data_type='RGBA', blend_type='MULTIPLY')
    tone.inputs['Factor'].default_value = 1
    L.new(shade.outputs['Value'], tone.inputs['B'])
    L.new(tone.outputs['Result'], mix.inputs['A'])
    tone.inputs['A'].default_value = (0.36, 0.375, 0.4, 1)
    return mat


def simple_material(name, color, rough, metal=0.0, spec=0.5):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    return mat


# ---------------------------------------------------------------- studio
def area_light(name, loc, target, energy, color, size):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy = energy; light.color = color; light.shape = 'RECTANGLE'
    light.size, light.size_y = size
    obj = bpy.data.objects.new(name, light)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    look_at(obj, target)  # lights and cameras both point down their local -Z
    return obj


def look_at(obj, target):
    d = np.array(target) - np.array(obj.location)
    obj.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)


def build_studio(cam_dir=(0.55, -1.0, 0.18), target=(0, 0, 0.93), frame_height=2.05):
    scene = bpy.context.scene
    world = bpy.data.worlds.new('Studio'); scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.008, 0.012, 1)

    floor_mat = simple_material('Floor', (0.012, 0.014, 0.019), 0.22, spec=0.6)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    floor = bpy.context.active_object; floor.data.materials.append(floor_mat)

    # No walls: the floor simply falls off into the dark background.

    d = np.array(cam_dir, float); d /= np.linalg.norm(d)
    right = np.cross(d, [0, 0, 1]); right /= np.linalg.norm(right)
    t = np.array(target)
    area_light('Key', tuple(t + d * 3 - right * 2.2 + [0, 0, 2.6]), tuple(t), 260, (1.0, 0.95, 0.9), (1.6, 1.6))
    area_light('RimA', tuple(t - d * 2.6 + right * 1.8 + [0, 0, 1.2]), tuple(t + [0, 0, 0.2]), 520, (0.45, 0.58, 1.0), (0.5, 2.2))
    area_light('RimB', tuple(t - d * 2.6 - right * 1.8 + [0, 0, 0.9]), tuple(t + [0, 0, 0.1]), 380, (0.68, 0.5, 1.0), (0.5, 2.2))
    area_light('Fill', tuple(t + d * 3.5 + right * 2.5 + [0, 0, 0.5]), tuple(t), 35, (0.7, 0.78, 1.0), (2.5, 2.5))
    area_light('Pool', (0, 0.6, 3.0), (0, 0.6, 0), 90, (0.55, 0.62, 0.85), (1.2, 1.2))

    cam_data = bpy.data.cameras.new('Camera'); cam_data.lens = 50
    cam_data.sensor_fit = 'VERTICAL'; cam_data.sensor_height = 24
    cam = bpy.data.objects.new('Camera', cam_data); scene.collection.objects.link(cam)
    dist = (frame_height / 2) / math.tan(math.atan(12 / 50))
    cam.location = tuple(t + d * dist)
    look_at(cam, t)
    scene.camera = cam
    return cam


def setup_render(width=720, height=1280, samples=128):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'
    scene.render.image_settings.file_format = 'PNG'
    # Bloom so the muscle glow actually glows
    scene.use_nodes = True
    nt = scene.node_tree
    rl, comp = nt.nodes['Render Layers'], nt.nodes['Composite']
    glare = nt.nodes.new('CompositorNodeGlare')
    glare.glare_type = 'BLOOM' if 'BLOOM' in [e.identifier for e in glare.bl_rna.properties['glare_type'].enum_items] else 'FOG_GLOW'
    glare.quality = 'HIGH'
    settings = {'Threshold': 2.0, 'Strength': 0.7, 'Size': 0.55} if 'Threshold' in glare.inputs else {}
    for k, v in settings.items():
        glare.inputs[k].default_value = v
    if not settings:
        glare.threshold, glare.size = 1.0, 7
    nt.links.new(rl.outputs['Image'], glare.inputs['Image'])
    nt.links.new(glare.outputs['Image'], comp.inputs['Image'])


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
