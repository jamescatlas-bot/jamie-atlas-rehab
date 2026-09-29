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


def set_pose(rig, J, depth):
    """depth 0 = standing, 1 = bottom of the squat. Feet stay planted through foot IK."""
    s = (J['head_top'][2]) / 1.8
    pb = rig.pose.bones
    e = studio.smoothstep(0, 1, np.array(depth))
    lean = math.radians(-28 * e)              # pelvis tips forward
    pb['root'].rotation_mode = 'XYZ'
    pb['root'].rotation_euler = (lean, 0, 0)
    pb['root'].location = (0, -0.36 * s * e, 0.13 * s * e)    # down, and back
    for n, a in (('spine1', -8), ('spine2', -6), ('chest', 4), ('neck', 16)):
        pb[n].rotation_mode = 'XYZ'; pb[n].rotation_euler = (math.radians(a * e), 0, 0)
    for side in ('L', 'R'):
        pb['pole_knee.' + side].location = (0, 0, 0)


def main():
    studio.reset()
    rig, body, shorts, fields, J = rigmod.build_rigged_body()
    M = {'chrome': studio.simple_material('Chrome', (0.6, 0.62, 0.66), 0.22, metal=1.0),
         'metal': studio.simple_material('Metal', (0.08, 0.085, 0.095), 0.35, metal=0.9),
         'plate': studio.simple_material('Plate', (0.02, 0.02, 0.022), 0.55, spec=0.3)}
    clay = studio.body_material()
    body.data.materials.append(clay)
    shorts.data.materials.append(studio.shorts_material())
    studio.set_glow(body, fields, ['quads', 'glutes'])
    studio.glow_on_shorts(body, shorts)

    # Bar on the upper back (high-bar position), held by both hands.
    H = J['head_top'][2]; s = H / 1.8
    co, _, _ = studio.mesh_arrays(body)
    near = co[(np.abs(co[:, 0]) < 0.05) & (np.abs(co[:, 2] - 0.815 * H) < 0.01)]
    bar_pos = Vector((0, near[:, 1].max() + 0.02, 0.815 * H))
    bar = barbell(M)
    bar.location = bar_pos
    bar.parent = rig; bar.parent_type = 'BONE'; bar.parent_bone = 'chest'
    bar.matrix_parent_inverse = (rig.matrix_world @ rig.pose.bones['chest'].matrix @
                                 __import__('mathutils').Matrix.Translation((0, rig.pose.bones['chest'].length, 0))).inverted()
    pb = rig.pose.bones
    for side, sx in (('L', 1), ('R', -1)):
        grip = Vector((sx * 0.3 * s, bar_pos.y, bar_pos.z))
        ikh = pb['ik_hand.' + side]
        rest = rig.data.bones['ik_hand.' + side].head_local
        # ik_hand is parented to chest; in rest pose its location offset is in bone-local space
        mw = rig.data.bones['ik_hand.' + side].matrix_local
        ikh.location = mw.inverted().to_3x3() @ (grip - rest)
        pb['forearm.' + side].constraints['IK'].influence = 1.0
        pb['hand.' + side].constraints['Copy Rotation'].influence = 0.0
        pb['pole_elbow.' + side].location = (0, 0, 0)

    studio.build_studio(cam_dir=(1.0, -0.45, 0.1), target=(0, 0.05, H * 0.52), frame_height=H * 1.3, lens=85)
    if '--still' in args:
        set_pose(rig, J, 1.0)
        studio.setup_render(samples=24)
        bpy.context.scene.render.filepath = str(OUT / 'squat_check.png')
        OUT.mkdir(parents=True, exist_ok=True)
        bpy.ops.render.render(write_still=True)
        set_pose(rig, J, 0.0)
        bpy.context.scene.render.filepath = str(OUT / 'squat_check_top.png')
        bpy.ops.render.render(write_still=True)
        return

    # One rep, rendered frame by frame; the video repeats it three times for a seamless loop.
    studio.setup_render(samples=int(next((a.split('=')[1] for a in args if a.startswith('--samples=')), 40)))
    FRAMES.mkdir(parents=True, exist_ok=True)
    for f in range(REP):
        set_pose(rig, J, depth_at(f))
        bpy.context.scene.render.filepath = str(FRAMES / f'{f:04d}.png')
        bpy.ops.render.render(write_still=True)
        print(f'frame {f + 1}/{REP}', flush=True)
    encode()


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
    """MP4 (H.264, plays in WhatsApp and iMessage) and a GIF under 5 MB."""
    import subprocess
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    OUT.mkdir(parents=True, exist_ok=True)
    lst = FRAMES / 'loop.txt'
    lst.write_text(''.join(f"file '{FRAMES / f'{f:04d}.png'}'\nduration {1 / FPS:.6f}\n" for _ in range(reps) for f in range(REP)))
    mp4, gif = OUT / 'barbell-back-squat.mp4', OUT / 'barbell-back-squat.gif'
    subprocess.run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-r', str(FPS), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-movflags', '+faststart', str(mp4)], check=True)
    for width, fps, colors in ((400, 15, 128), (360, 12, 96), (320, 12, 64)):
        subprocess.run([ff, '-y', '-i', str(mp4), '-vf',
                        f'fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={colors}:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
                        str(gif)], check=True)
        if gif.stat().st_size < 5_000_000:
            break
    print('wrote', mp4, mp4.stat().st_size, 'and', gif, gif.stat().st_size)


if __name__ == '__main__':
    main()
