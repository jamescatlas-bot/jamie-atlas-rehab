# video-breakdown

Turn an exercise video (a YouTube Short, or any local file such as a screen
recording) into:

1. one clip per exercise, with repeats of the same movement flagged,
2. a contact sheet and a timestamped report (with YouTube jump links when
   the source is a YouTube URL), and
3. a faceless re-render of each clip: the mover's pose, tracked frame by
   frame with MediaPipe, drawn as a plain charcoal figure on a blank gym
   backdrop, seen from the angle that shows the movement best. No face, no
   clothing, no original footage in the output.

## Setup

```bash
pip install -r tools/video-breakdown/requirements.txt
# ffmpeg must be on PATH. If it isn't:
ln -s "$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')" /usr/local/bin/ffmpeg
# MediaPipe needs libEGL on Linux:
sudo apt-get install -y libegl1 libgl1 libglib2.0-0
```

The pose model (about 9 MB) downloads itself on first run into
`~/.cache/video-breakdown/`.

## Run

```bash
python3 tools/video-breakdown/breakdown.py all "https://youtube.com/shorts/VIDEO_ID" --work work
python3 tools/video-breakdown/breakdown.py all recording.mp4 --work work
```

Outputs land in `work/`:

| file | what |
|------|------|
| `pose.json` | 2D and 3D pose landmarks for every frame and body |
| `segments.json` | cuts, shots, interlude count and the segment list |
| `clips/exercise_NN.mp4` | original footage, one file per exercise instance |
| `contact_sheet.jpg` | one frame per instance with its time range and pattern |
| `faceless/exercise_NN_faceless.mp4` | faceless re-render of each instance |
| `report.md` | distinct-exercise count, table of instances, jump links |

## How it decides where one exercise ends

1. **Cuts.** ffmpeg's scene score finds hard cuts (`--threshold`, default
   0.3) and softer jump cuts in the same framing (`--jump-threshold`,
   default 0.1).
2. **Interludes.** Frames whose colour is far from the video's dominant
   look (b-roll, a title card, a swipe to another video in a screen
   recording) are dropped.
3. **Posture.** Inside each shot every body is classified per frame as
   standing, hinge, squat or floor from its landmarks. Runs of the same
   movement become one exercise. Standing gaps shorter than `--rest-gap`
   (3 s) between two runs of the same movement are absorbed, because the
   top of every rep looks like standing. Getting down to or up from the
   floor reads as a hinge, so a floor run takes its short neighbours.
   Anything shorter than `--min-len` (2 s) is treated as rest.
4. **Repeats.** A later segment with the same pattern as an earlier one is
   flagged as a repeat, so a looping Short or a repeated circuit gives a
   count of distinct exercises as well as instances.

Steps can be run individually (`download`, `pose`, `scenes`, `split`,
`faceless`) so you can re-tune segmentation without re-running the tracker.

## Faceless render options

- `--view auto|front|three-quarter|side`. Auto uses side for hinge and
  floor patterns and three-quarter for squats. A hinge seen from the front
  collapses into nothing; from the side it is obvious.
- `--person N` picks which body to draw, counted left to right, when the
  automatic pick (tallest, most visible, steadiest track) chooses wrong.
- `--out-size 720x1280` output size. The figure is re-composed, so the
  output aspect does not have to match the source.

## Limits

- Posture classes cover lower-body and floor patterns. Standing upper-body
  work (curls, presses) is treated as rest. Extend `classify_frame` with a
  wrist-height rule if you need it.
- The 3D landmarks are estimated from a single camera. Prone positions and
  bodies partly hidden by another person can produce a jittery frame or a
  misplaced head. The renderer smooths and rejects large jumps, but it is a
  tracked figure, not a generated actor.
- Two people doing the same exercise are handled. Two people doing
  different exercises will be segmented by whichever movement is more
  "active" (floor beats hinge beats squat).
