"""Render candidate bodies side by side in the look-test setup (blank head, shorts, quads glowing).

    python exercise-library/scripts/compare_bodies.py

Needs assets/human_base_meshes_bundle.blend (Blender Studio's CC0 Human Base Meshes pack,
kept as a release download: github.com/jamescatlas-bot/jamie-atlas-rehab/releases/tag/body-model).
"""
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import studio  # noqa: E402

OUT = studio.ROOT / 'output' / 'look-test'
OUT.mkdir(parents=True, exist_ok=True)
CANDIDATES = {
    'hbm_male_realistic': 'GEO-body_male_realistic',
    'hbm_male_stylized': 'GEO-body_male_stylized',
    'hbm_female_realistic': 'GEO-body_female_realistic',
}
only = sys.argv[1:] or list(CANDIDATES)
studio.VOXEL = 0.0022

for key in only:
    studio.reset()
    body, shorts = studio.build_body(CANDIDATES[key])
    masks = studio.muscle_masks(body)
    body.data.materials.append(studio.body_material())
    shorts.data.materials.append(studio.simple_material('Shorts', (0.012, 0.012, 0.014), 0.75, spec=0.3))
    studio.set_glow(body, masks, ['quads'])
    H = max(v.co.z for v in body.data.vertices)
    studio.build_studio(cam_dir=(0.55, -1.0, 0.16), target=(0, 0, H * 0.51), frame_height=H * 1.24)
    studio.setup_render(samples=128)
    bpy.context.scene.render.filepath = str(OUT / f'{key}.png')
    bpy.ops.render.render(write_still=True)
    print('wrote', OUT / f'{key}.png')
