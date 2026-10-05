"""Still of the body standing front-on in the studio, as the character image for AI motion transfer.

    python exercise-library/scripts/character_image.py
Writes output/ai-test/character_glow.png (quads and glutes glowing) and character_plain.png.
"""
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import studio  # noqa: E402

OUT = studio.ROOT / 'output' / 'ai-test'
OUT.mkdir(parents=True, exist_ok=True)
studio.reset()
body, shorts = studio.build_body()
fields = studio.muscle_masks(body)
body.data.materials.append(studio.body_material())
shorts.data.materials.append(studio.shorts_material())
H = max(v.co.z for v in body.data.vertices)
studio.build_studio(cam_dir=(0.0, -1.0, 0.06), target=(0, 0, H * 0.5), frame_height=H * 1.22, lens=70)
studio.setup_render(samples=96)
for name, muscles in (('character_glow', ['quads', 'glutes']), ('character_plain', [])):
    studio.set_glow(body, fields, muscles)
    studio.glow_on_shorts(body, shorts)
    bpy.context.scene.render.filepath = str(OUT / f'{name}.png')
    bpy.ops.render.render(write_still=True)
    print('wrote', OUT / f'{name}.png')
