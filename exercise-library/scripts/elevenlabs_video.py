"""Run a video generation through the ElevenLabs API and download the result.

    python elevenlabs_video.py OUT.mp4 --model=bytedance-seedance-v2.5 --prompt="..." \
        --image=char.png --video=motion.mp4 [--aspect=9:16 --res=720p --secs=5]

The API key is not read here: the session's network proxy adds it to every request
to api.elevenlabs.io (stored as an API credential on the cloud environment).
"""
import base64
import json
import pathlib
import sys
import time
import urllib.request

API = 'https://api.elevenlabs.io/v1/flows/video'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = {}
for a in sys.argv[1:]:
    if a.startswith('--'):
        k, _, v = a[2:].partition('=')
        opt.setdefault(k, []).append(v)
one = lambda k, d=None: opt.get(k, [d])[0]


def inline(path, kind):
    p = pathlib.Path(path)
    mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.mp4': 'video/mp4', '.mov': 'video/quicktime'}[p.suffix.lower()]
    return {'type': 'inline_base64', 'content_base64': base64.b64encode(p.read_bytes()).decode(), 'mime_type': mime}


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={'Content-Type': 'application/json'}, method='POST' if body else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f'ElevenLabs said {e.code}: {e.read().decode()[:800]}')


body = {'model_id': one('model', 'bytedance-seedance-v2.5'), 'prompt': one('prompt'),
        'aspect_ratio': one('aspect', '9:16'), 'resolution': one('res', '720p'),
        'duration_secs': int(one('secs', '5')), 'generate_audio': False}
if 'image' in opt:
    body['images'] = [inline(p, 'image') for p in opt['image']]
if 'video' in opt:
    body['videos'] = [inline(p, 'video') for p in opt['video']]
job = call(API, body)
print('started', job['id'], flush=True)
t0 = time.time()
while True:
    time.sleep(10)
    st = call(f"{API}/{job['id']}")
    print(f"{int(time.time() - t0)}s {st['status']}", flush=True)
    if st['status'] == 'completed':
        urllib.request.urlretrieve(st['content_url'], args[0])
        print('wrote', args[0])
        break
    if st['status'] == 'failed':
        sys.exit(f"failed: {st.get('failure_reason')} - {st.get('error_message')}")
    if time.time() - t0 > 1500:
        sys.exit('still running after 25 min; check the id later: ' + job['id'])
