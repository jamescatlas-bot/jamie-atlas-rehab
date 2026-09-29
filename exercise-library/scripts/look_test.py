"""Stage 1 look test: one still of the body standing in the studio with the quads glowing.

    python exercise-library/scripts/look_test.py              (uses Blender's `bpy` module)
    python exercise-library/scripts/look_test.py --masks      (debug: every muscle mask in its own colour)

Writes output/look-test/look_test.png and look_test_vs_reference.png.
"""
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import studio  # noqa: E402

OUT = studio.ROOT / 'output' / 'look-test'
OUT.mkdir(parents=True, exist_ok=True)
args = sys.argv[1:]
samples = int(next((a.split('=')[1] for a in args if a.startswith('--samples=')), 128))

studio.reset()
body, shorts = studio.build_body()
masks = studio.muscle_masks(body)
body.data.materials.append(studio.body_material())
shorts.data.materials.append(studio.simple_material('Shorts', (0.012, 0.012, 0.014), 0.75, spec=0.3))

if '--masks' in args:
    import numpy as np
    colors = np.random.default_rng(3).uniform(0.15, 1, (len(masks), 3))
    col = np.full((len(body.data.vertices), 3), 0.35)
    for (name, heads), c in zip(masks.items(), colors):
        for d in heads:
            m = studio.head_core(d)
            col = col * (1 - m[:, None]) + c * m[:, None]
    a = body.data.color_attributes.new('dbg', 'FLOAT_COLOR', 'POINT')
    a.data.foreach_set('color', np.concatenate([col, np.ones((len(col), 1))], 1).ravel().astype('float32'))
    mat = body.data.materials[0]; nt = mat.node_tree
    ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'dbg'
    nt.links.new(ca.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    nt.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    studio.set_glow(body, masks, [])
    bpy.data.materials['Clay'].node_tree.nodes['Mix'].inputs['A'].default_value = (1, 1, 1, 1)
    shots = {'masks_front': (0.0, -1, 0.1), 'masks_back': (0.0, 1, 0.1), 'masks_side': (1, -0.2, 0.1)}
else:
    studio.set_glow(body, masks, ['quads'])
    shots = {'look_test': (0.55, -1.0, 0.16)}

for name, d in shots.items():
    for o in [o for o in bpy.data.objects if o.type in ('LIGHT', 'CAMERA') or o.name.startswith('Plane')]:
        bpy.data.objects.remove(o)
    H = max(v.co.z for v in body.data.vertices)
    studio.build_studio(cam_dir=d, target=(0, 0, H * 0.51), frame_height=H * 1.24)
    studio.setup_render(samples=samples if name == 'look_test' else 24)
    bpy.context.scene.render.filepath = str(OUT / f'{name}.png')
    bpy.ops.render.render(write_still=True)
    print('wrote', OUT / f'{name}.png')

if '--masks' not in args:
    try:
        from PIL import Image
        ref = Image.open(studio.ROOT / 'reference.jpg').convert('RGB')
        ours = Image.open(OUT / 'look_test.png').convert('RGB')
        h = 1280
        ref = ref.resize((round(ref.width * h / ref.height), h))
        sheet = Image.new('RGB', (ref.width + ours.width + 20, h), (12, 14, 18))
        sheet.paste(ref, (0, 0)); sheet.paste(ours, (ref.width + 20, 0))
        sheet.save(OUT / 'look_test_vs_reference.png')
        print('wrote', OUT / 'look_test_vs_reference.png')
    except ImportError:
        print('Pillow not installed: skipped the side-by-side')
