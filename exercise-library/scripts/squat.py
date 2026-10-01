"""Stage 2: barbell back squat, side view, quads and glutes glowing, 3-rep loop.

    python exercise-library/scripts/squat.py            full render -> output/library/barbell-back-squat.mp4 / .gif
    python exercise-library/scripts/squat.py --still    one low-quality frame at the bottom, to check the pose
"""
import math
import pathlib
import sys

import bpy
import numpy as np
from mathutils import Euler, Vector

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import studio  # noqa: E402
import rig as rigmod  # noqa: E402

OUT = studio.ROOT / 'output' / 'library'
FRAMES = studio.ROOT / 'output' / 'frames' / 'barbell-back-squat'
FPS = 30
REP = 78            # frames per rep (2.6 s)
args = sys.argv[1:]


def barbell(M):
    """Olympic bar with two plates and a collar each side, centred on the origin along X."""
    objs = []
    def cyl(r, depth, x, mat, verts=48):
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=(x, 0, 0), rotation=(0, math.pi / 2, 0))
        o = bpy.context.active_object; o.data.materials.append(mat)
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
        objs.append(o)
    cyl(0.014, 2.2, 0, M['chrome'], 24)
    for sx in (1, -1):
        cyl(0.025, 0.42, sx * 0.9, M['chrome'], 24)
        cyl(0.225, 0.05, sx * 0.47, M['plate'])
        cyl(0.225, 0.04, sx * 0.52, M['plate'])
        cyl(0.04, 0.05, sx * 0.575, M['metal'])
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    bar = bpy.context.active_object; bar.name = 'Barbell'
    return bar


def squat_geometry(J, bar_pos, e):
    """Where the pelvis goes and how far the torso leans at squat depth e (0-1).

    Built like a coach would describe it, in the side (sagittal) plane:
    the feet stay put, the shins lean forward up to 35 degrees, the thighs finish
    just below parallel, and the torso leans only as far as needed to keep the bar
    directly over mid-foot. Returns (pelvis offset in world y/z, lean in degrees).
    """
    s = J['head_top'][2] / 1.8
    A = np.array(J['ankle.L'][1:]); K = np.array(J['knee.L'][1:]); Hp = np.array(J['hip.L'][1:])
    Ls, Lt = np.linalg.norm(K - A), np.linalg.norm(Hp - K)
    shin = math.radians(35 * e)                       # forward lean of the shin
    thigh = math.radians(95 * e)                      # thigh angle from vertical (95 = hip crease just below the knee)
    knee = A + Ls * np.array([-math.sin(shin), math.cos(shin)])
    hip = knee + Lt * np.array([math.sin(thigh), math.cos(thigh)])
    pelvis_rest = np.array(J['pelvis'][1:])
    r = Hp - pelvis_rest                              # hip joint relative to the pelvis bone
    b = np.array([bar_pos.y, bar_pos.z]) - pelvis_rest
    mid = (J['ankle.L'][1] + J['toe.L'][1]) / 2

    def rot(v, a):
        return np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)])

    def bar_y(a):
        pelvis = hip - rot(r, a)
        return (pelvis + rot(b, a))[0]
    goal = (1 - e) * (pelvis_rest + b)[0] + e * mid
    lo, hi = 0.0, math.radians(70)
    for _ in range(40):
        a = (lo + hi) / 2
        if bar_y(a) > goal:
            lo = a
        else:
            hi = a
    a = (lo + hi) / 2
    pelvis = hip - rot(r, a)
    return pelvis - pelvis_rest, math.degrees(a)


BAR = None


def set_pose(rig, J, depth):
    """depth 0 = standing, 1 = bottom. Neutral spine, chest up, head in line; feet planted (foot IK)."""
    e = float(studio.smoothstep(0, 1, np.array(depth)))
    (dy, dz), lean = squat_geometry(J, BAR, e)
    (dy0, dz0), lean0 = squat_geometry(J, BAR, 0.0)    # standing must be exactly the rest pose
    dy, dz, lean = dy - (1 - e) * dy0, dz - (1 - e) * dz0, lean - (1 - e) * lean0
    pb = rig.pose.bones
    pb['root'].rotation_mode = 'XYZ'
    pb['root'].rotation_euler = (math.radians(-lean), 0, 0)
    pb['root'].location = (0, dz, dy)                 # bone space: Y is up, Z is toward the back
    for n, a in (('spine1', 1), ('spine2', 2), ('chest', 3), ('neck', 0)):
        pb[n].rotation_mode = 'XYZ'; pb[n].rotation_euler = (math.radians(a * e), 0, 0)


def arm_space(rig, name, matrix):
    rig.pose.bones[name].matrix = matrix
    bpy.context.view_layer.update()


def setup_technique(rig, J, bar_pos):
    """Stance, grip and elbow position for a back squat."""
    from mathutils import Matrix
    s = J['head_top'][2] / 1.8
    for side, sx in (('L', 1), ('R', -1)):
        rest = rig.data.bones['ik_foot.' + side].matrix_local
        a = Vector(J['ankle.' + side])
        turn = Matrix.Rotation(math.radians(sx * 18), 4, 'Z')          # toes out ~18 degrees
        widen = Matrix.Translation((sx * 0.055 * s, 0, 0))              # about shoulder width
        arm_space(rig, 'ik_foot.' + side, widen @ Matrix.Translation(a) @ turn @ Matrix.Translation(-a) @ rest)
        toe_dir = turn.to_3x3() @ Vector((0, -1, 0))
        knee = Vector(J['knee.' + side]) + Vector((sx * 0.055 * s, 0, 0))
        prest = rig.data.bones['pole_knee.' + side].matrix_local
        arm_space(rig, 'pole_knee.' + side, Matrix.Translation(knee + toe_dir * 0.6 - prest.translation) @ prest)
        # Hands just outside the shoulders on the bar, elbows pulled down and back
        hrest = rig.data.bones['ik_hand.' + side].matrix_local
        grip = Vector((sx * 0.34 * s, bar_pos.y, bar_pos.z))
        arm_space(rig, 'ik_hand.' + side, Matrix.Translation(grip - hrest.translation) @ hrest)
        erest = rig.data.bones['pole_elbow.' + side].matrix_local
        el = Vector(J['elbow.' + side])
        arm_space(rig, 'pole_elbow.' + side, Matrix.Translation(el + Vector((sx * 0.2, 0.35, -0.5)) - erest.translation) @ erest)
        rig.pose.bones['forearm.' + side].constraints['IK'].influence = 1.0


ANGLES = {'side': (1.0, -0.35, 0.05), 'front45': (0.75, -1.0, 0.1)}


def render_angle(name, H, samples, frames):
    for o in [o for o in bpy.data.objects if o.type in ('LIGHT', 'CAMERA') or o.name.startswith('Plane')]:
        bpy.data.objects.remove(o)
    studio.build_studio(cam_dir=ANGLES[name], target=(0, 0.02, H * 0.5), frame_height=H * 1.36, lens=85)
    studio.setup_render(samples=samples)
    out = FRAMES / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def main():
    if '--encode' in args:
        return encode()
    studio.reset()
    rig, body, shorts, fields, J = rigmod.build_rigged_body()
    M = {'chrome': studio.simple_material('Chrome', (0.6, 0.62, 0.66), 0.22, metal=1.0),
         'metal': studio.simple_material('Metal', (0.08, 0.085, 0.095), 0.35, metal=0.9),
         'plate': studio.simple_material('Plate', (0.02, 0.02, 0.022), 0.55, spec=0.3)}
    body.data.materials.append(studio.body_material())
    shorts.data.materials.append(studio.shorts_material())
    studio.set_glow(body, fields, ['quads', 'glutes'])
    studio.glow_on_shorts(body, shorts)

    # Bar on the upper back (high-bar position, on the traps).
    H = J['head_top'][2]
    co, _, _ = studio.mesh_arrays(body)
    near = co[(np.abs(co[:, 0]) < 0.05) & (np.abs(co[:, 2] - 0.815 * H) < 0.01)]
    bar_pos = Vector((0, near[:, 1].max() + 0.02, 0.815 * H))
    bar = barbell(M)
    bar.location = bar_pos
    bar.parent = rig; bar.parent_type = 'BONE'; bar.parent_bone = 'chest'
    from mathutils import Matrix
    chest = rig.pose.bones['chest']
    bar.matrix_parent_inverse = (rig.matrix_world @ chest.matrix @ Matrix.Translation((0, chest.length, 0))).inverted()
    setup_technique(rig, J, bar_pos)
    global BAR
    BAR = bar_pos
    for d in (0.0, 0.5, 1.0):
        print('depth', d, 'pelvis offset / lean:', [np.round(x, 3) for x in squat_geometry(J, bar_pos, d)])

    samples = int(next((a.split('=')[1] for a in args if a.startswith('--samples=')), 32))
    if '--still' in args:
        for name in ANGLES:
            out = render_angle(name, H, 20, None)
            for d, tag in ((0.0, 'top'), (0.5, 'mid'), (1.0, 'bottom')):
                set_pose(rig, J, d)
                bpy.context.scene.render.filepath = str(out / f'check_{tag}.png')
                bpy.ops.render.render(write_still=True)
        return

    # One rep per angle, rendered frame by frame; the video repeats it three times for a seamless loop.
    # Frames already on disk are skipped, so an interrupted render picks up where it stopped.
    # --max-frames=N stops after N new frames (keeps each run short).
    budget = int(next((a.split('=')[1] for a in args if a.startswith('--max-frames=')), 10**6))
    for name in ANGLES:
        todo = [f for f in range(REP) if not (FRAMES / name / f'{f:04d}.png').exists()]
        if not todo or budget <= 0:
            continue
        out = render_angle(name, H, samples, REP)
        for f in todo:
            if budget <= 0:
                break
            budget -= 1
            set_pose(rig, J, depth_at(f))
            bpy.context.scene.render.filepath = str(out / f'{f:04d}.png')
            bpy.ops.render.render(write_still=True)
            print(f'{name} frame {f + 1}/{REP}', flush=True)
    if all((FRAMES / n / f'{f:04d}.png').exists() for n in ANGLES for f in range(REP)):
        encode()
    else:
        print('not finished yet: run again to continue')


def depth_at(f):
    """Squat depth over one rep: stand, 1.1 s down, short pause, 0.9 s up, stand."""
    t = f / FPS
    if t < 0.25:
        return 0.0
    if t < 1.35:
        return (t - 0.25) / 1.1
    if t < 1.5:
        return 1.0
    if t < 2.4:
        return 1 - (t - 1.5) / 0.9
    return 0.0


def encode(reps=3):
    """One MP4 (H.264, plays in WhatsApp and iMessage) and GIF (under 5 MB) per angle,
    plus both angles side by side for review."""
    import subprocess
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    OUT.mkdir(parents=True, exist_ok=True)
    vids = []
    for name in ANGLES:
        frames = FRAMES / name
        lst = frames / 'loop.txt'
        lst.write_text(''.join(f"file '{frames / f'{f:04d}.png'}'\nduration {1 / FPS:.6f}\n" for _ in range(reps) for f in range(REP)))
        mp4, gif = OUT / f'barbell-back-squat-{name}.mp4', OUT / f'barbell-back-squat-{name}.gif'
        subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-r', str(FPS),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-movflags', '+faststart', str(mp4)], check=True)
        for width, fps, colors in ((400, 15, 128), (360, 12, 96), (320, 12, 64)):
            subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(mp4), '-vf',
                            f'fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={colors}:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
                            str(gif)], check=True)
            if gif.stat().st_size < 5_000_000:
                break
        vids.append(mp4)
        print('wrote', mp4, mp4.stat().st_size, gif, gif.stat().st_size)
    both = OUT / 'barbell-back-squat-two-angles.mp4'
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', str(vids[0]), '-i', str(vids[1]), '-filter_complex',
                    '[0:v]pad=iw+16:ih:0:0:color=0x0b0d12[a];[a][1:v]hstack=inputs=2,scale=1456:-2',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-movflags', '+faststart', str(both)], check=True)
    print('wrote', both, both.stat().st_size)


if __name__ == '__main__':
    main()
