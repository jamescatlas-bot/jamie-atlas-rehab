"""Side-by-side comparison of motion-transfer results.

    python compare_ai.py OUT.mp4 "Label A=path/a.mp4" "Label B=path/b.mp4" ...

Each clip is scaled to the same height, looped to the longest clip's length, labelled
along the top, and placed side by side.
"""
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
out, items = sys.argv[1], [a.split('=', 1) for a in sys.argv[2:]]
H = 960
inputs, filters = [], []
for i, (label, path) in enumerate(items):
    inputs += ['-stream_loop', '-1', '-i', path]
    safe = label.replace(':', ' ').replace("'", '')
    filters.append(f"[{i}:v]scale=-2:{H},setsar=1,fps=30,pad=iw+12:ih+56:6:56:color=0x0b0d12,"
                   f"drawtext=text='{safe}':x=(w-tw)/2:y=16:fontsize=30:fontcolor=white[v{i}]")
stack = ''.join(f'[v{i}]' for i in range(len(items))) + f'hstack=inputs={len(items)}[out]'
probe = [float(subprocess.run([FF, '-i', p], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')[-1])
         for _, p in items]
subprocess.run([FF, '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters) + ';' + stack,
                '-map', '[out]', '-t', str(max(probe)), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20',
                '-movflags', '+faststart', out], check=True)
print('wrote', out)
