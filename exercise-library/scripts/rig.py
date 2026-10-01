"""Skeleton for the body: joints found on the mesh, weights painted automatically, IK for arms and legs.

Bone names follow a plain convention: root (pelvis), spine1, spine2, chest, neck, head,
clavicle/upperarm/forearm/hand .L/.R, thigh/shin/foot/toe .L/.R, plus IK controls:
ik_foot.* (feet stay planted), ik_hand.* (hands follow the bar), pole_knee.*, pole_elbow.*.
The body faces -Y, its left is +X, units are metres.
"""
import bpy
import numpy as np
from mathutils import Vector

import studio


def _slice_centroid(co, z, halfband, mask):
    sel = mask & (np.abs(co[:, 2] - z) < halfband)
    return co[sel].mean(0) if sel.any() else None


def find_joints(co):
    """Joint centres for a standing body in its rest pose (arms hanging down)."""
    H = co[:, 2].max(); s = H / 1.8
    x, y, z = co.T
    J = {}
    torso = np.abs(x) < 0.12 * s
    yc = lambda zz: _slice_centroid(co, zz, 0.01 * H, torso)[1]
    for name, f in (('pelvis', 0.53), ('spine1', 0.6), ('spine2', 0.68), ('chest', 0.755), ('neck', 0.83)):
        J[name] = np.array([0.0, yc(f * H), f * H])
    chin = studio.find_chin(co)
    J['head'] = np.array([0.0, yc(chin - 0.02 * s) + 0.01 * s, chin - 0.02 * s])
    J['head_top'] = np.array([0.0, J['head'][1], H])
    for side, sx in (('L', 1), ('R', -1)):
        leg = (sx * x > 0.01 * s) & (sx * x < 0.2 * s)
        knee = _slice_centroid(co, 0.285 * H, 0.008 * H, leg)
        ankle = _slice_centroid(co, 0.065 * H, 0.006 * H, leg)
        thighc = _slice_centroid(co, 0.46 * H, 0.008 * H, leg)
        J['hip.' + side] = np.array([thighc[0] * 0.9, thighc[1], 0.505 * H])
        J['knee.' + side] = knee
        J['ankle.' + side] = np.array([ankle[0], ankle[1] + 0.01 * s, 0.05 * H])
        foot = leg & (z < 0.03 * H)
        tip = co[foot][np.argmin(co[foot][:, 1])]
        J['ball.' + side] = np.array([ankle[0], tip[1] + 0.06 * s, 0.015 * H])
        J['toe.' + side] = np.array([ankle[0], tip[1], 0.012 * H])
        arm = (sx * x > 0.19 * s) & (z > 0.4 * H)
        shoulder = _slice_centroid(co, 0.79 * H, 0.008 * H, sx * x > 0.14 * s)
        elbow = _slice_centroid(co, 0.62 * H, 0.008 * H, arm)
        wrist = _slice_centroid(co, 0.485 * H, 0.006 * H, arm)
        tip = co[arm][np.argmin(co[arm][:, 2])]
        J['shoulder.' + side] = np.array([shoulder[0] * 0.95, shoulder[1], 0.805 * H])
        J['clavicle.' + side] = np.array([sx * 0.025 * s, J['shoulder.' + side][1] - 0.02 * s, 0.8 * H])
        J['elbow.' + side] = elbow + np.array([0, 0.012 * s, 0])
        J['wrist.' + side] = wrist
        J['hand.' + side] = wrist + (tip - wrist) * 0.55
    return J


def build_armature(J):
    arm_data = bpy.data.armatures.new('Rig')
    rig = bpy.data.objects.new('Rig', arm_data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    def bone(name, head, tail, parent=None, connect=False, deform=True, roll=0.0):
        b = eb.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        b.roll = roll
        if parent:
            b.parent = eb[parent]; b.use_connect = connect
        b.use_deform = deform
        return b

    bone('root', J['pelvis'], J['spine1'])
    bone('spine1', J['spine1'], J['spine2'], 'root', True)
    bone('spine2', J['spine2'], J['chest'], 'spine1', True)
    bone('chest', J['chest'], J['neck'], 'spine2', True)
    bone('neck', J['neck'], J['head'], 'chest', True)
    bone('head', J['head'], J['head_top'], 'neck', True)
    for s in ('L', 'R'):
        bone('thigh.' + s, J['hip.' + s], J['knee.' + s], 'root')
        bone('shin.' + s, J['knee.' + s], J['ankle.' + s], 'thigh.' + s, True)
        bone('foot.' + s, J['ankle.' + s], J['ball.' + s], 'shin.' + s, True)
        bone('toe.' + s, J['ball.' + s], J['toe.' + s], 'foot.' + s, True)
        bone('clavicle.' + s, J['clavicle.' + s], J['shoulder.' + s], 'chest')
        bone('upperarm.' + s, J['shoulder.' + s], J['elbow.' + s], 'clavicle.' + s, True)
        bone('forearm.' + s, J['elbow.' + s], J['wrist.' + s], 'upperarm.' + s, True)
        bone('hand.' + s, J['wrist.' + s], J['hand.' + s], 'forearm.' + s, True)
        # Controls (not part of the skin)
        bone('ik_foot.' + s, J['ankle.' + s], J['ball.' + s], None, deform=False)
        knee = J['knee.' + s]
        bone('pole_knee.' + s, knee + [0, -0.5, 0], knee + [0, -0.55, 0], None, deform=False)  # fixed in the room, like the feet
        bone('ik_hand.' + s, J['wrist.' + s], J['hand.' + s], 'chest', deform=False)
        el = J['elbow.' + s]
        bone('pole_elbow.' + s, el + [0, 0.45, -0.1], el + [0, 0.5, -0.1], 'chest', deform=False)
    # Consistent bone rolls so rotations mean the same thing on every bone.
    for b in eb:
        b.select = True
    bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front = True

    for s in ('L', 'R'):
        pb = rig.pose.bones
        ik = pb['shin.' + s].constraints.new('IK')
        ik.target, ik.subtarget, ik.chain_count = rig, 'ik_foot.' + s, 2
        ik.pole_target, ik.pole_subtarget, ik.pole_angle = rig, 'pole_knee.' + s, -np.pi / 2
        cr = pb['foot.' + s].constraints.new('COPY_ROTATION'); cr.target, cr.subtarget = rig, 'ik_foot.' + s
        ik = pb['forearm.' + s].constraints.new('IK')
        ik.target, ik.subtarget, ik.chain_count = rig, 'ik_hand.' + s, 2
        ik.pole_target, ik.pole_subtarget, ik.pole_angle = rig, 'pole_elbow.' + s, np.pi / 2
        ik.influence = 0.0            # arms hang free until an exercise turns hand IK on
        cr = pb['hand.' + s].constraints.new('COPY_ROTATION'); cr.target, cr.subtarget = rig, 'ik_hand.' + s
        cr.influence = 0.0
    return rig


def skin(rig, proxy, targets):
    """Paint weights on the low-detail proxy (bone heat), then copy them to each detailed mesh."""
    bpy.ops.object.select_all(action='DESELECT')
    proxy.select_set(True); rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for obj in targets:
        dt = obj.modifiers.new('Weights', 'DATA_TRANSFER')
        dt.object = proxy
        dt.use_vert_data = True
        dt.data_types_verts = {'VGROUP_WEIGHTS'}
        dt.vert_mapping = 'POLYINTERP_NEAREST'
        dt.layers_vgroup_select_src = 'ALL'
        dt.layers_vgroup_select_dst = 'NAME'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.datalayout_transfer(modifier=dt.name)
        bpy.ops.object.modifier_apply(modifier=dt.name)
        am = obj.modifiers.new('Rig', 'ARMATURE'); am.object = rig
        am.use_deform_preserve_volume = True
        obj.parent = rig
    proxy.hide_render = True
    proxy.hide_viewport = True


def build_rigged_body(source='GEO-body_male_realistic'):
    """Detailed body + shorts, skinned to a new rig. Muscle masks are computed in the rest pose."""
    body, shorts = studio.build_body(source)
    fields = studio.muscle_masks(body)
    proxy = studio.load_hbm_body(source, levels=1)
    co, _, _ = studio.mesh_arrays(proxy)
    J = find_joints(co)
    rig = build_armature(J)
    skin(rig, proxy, [body, shorts])
    return rig, body, shorts, fields, J
