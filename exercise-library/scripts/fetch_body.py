"""Copy the free (CC0) MakeHuman body files this pipeline needs into assets/mpfb2.

They come from the `anny` package on PyPI, which bundles MPFB2's base mesh and
shape targets. Run once:  python exercise-library/scripts/fetch_body.py
"""
import pathlib, subprocess, sys, tempfile, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets' / 'mpfb2'
KEEP = [
    'LICENSE.md', '3dobjs/base.obj',
    'targets/macrodetails/universal-male-young-maxmuscle-averageweight.target.gz',
    'targets/macrodetails/universal-male-young-maxmuscle-minweight.target.gz',
    'targets/macrodetails/african-male-young.target.gz',
    'targets/macrodetails/asian-male-young.target.gz',
    'targets/macrodetails/caucasian-male-young.target.gz',
    'targets/macrodetails/proportions/male-young-maxmuscle-averageweight-idealproportions.target.gz',
    'targets/macrodetails/height/male-young-maxmuscle-averageweight-maxheight.target.gz',
] + [f'targets/{d}/{s}-{p}-muscle-incr.target.gz' for d, p in
     [('arms', 'upperarm'), ('arms', 'lowerarm'), ('arms', 'upperarm-shoulder'), ('legs', 'upperleg'), ('legs', 'lowerleg')] for s in 'lr'] + [
    'targets/torso/torso-muscle-dorsi-incr.target.gz', 'targets/torso/torso-muscle-pectoral-incr.target.gz',
    'targets/torso/torso-vshape-incr.target.gz', 'targets/stomach/stomach-tone-incr.target.gz',
    'targets/stomach/stomach-pregnant-decr.target.gz', 'targets/pelvis/pelvis-tone-incr.target.gz',
    'targets/neck/neck-scale-horiz-incr.target.gz',
]

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, '-m', 'pip', 'download', '--no-deps', '-q', 'anny==0.6.0', '-d', tmp], check=True)
    wheel = next(pathlib.Path(tmp).glob('anny-*.whl'))
    with zipfile.ZipFile(wheel) as z:
        for rel in KEEP:
            out = DEST / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(z.read('anny/data/mpfb2/' + rel))
print(f'Copied {len(KEEP)} files to {DEST}')
