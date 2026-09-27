# video-breakdown

Turn an exercise video (a YouTube Short, or any local file) into:

1. one clip per exercise, split at the visual cuts,
2. a contact sheet and a timestamped list (with YouTube jump links), and
3. a faceless re-render of each clip: the mover's pose, tracked frame by
   frame with MediaPipe, drawn as a plain charcoal figure on a blank gym
   backdrop. No face, no clothing, no original footage in the output.

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
```

Outputs land in `work/`:

| file | what |
|------|------|
| `segments.json` | raw cut times and the cleaned segment list |
| `clips/exercise_NN.mp4` | original footage, one file per exercise |
| `contact_sheet.jpg` | one frame per exercise with its time range |
| `faceless/exercise_NN_faceless.mp4` | faceless re-render of each exercise |
| `report.md` | count, table of segments, jump links |

## Tuning

- `--threshold 0.3` ffmpeg scene score. Lower it (0.2) if cuts are missed,
  raise it (0.4 to 0.5) if camera whip-pans register as cuts.
- `--min-len 1.5` segments shorter than this are folded into the previous
  one, so a two-frame flash or title card never counts as an exercise.
- `--merge-gap 0.5` cuts closer together than this count as one.
- `--out-height 960` height of the faceless render.

Steps can be run individually (`download`, `scenes`, `split`, `faceless`)
so you can re-tune scene detection without re-downloading.

## Limits

- Scene detection finds *hard cuts*. A video that shows several exercises
  in one continuous take will come back as one segment; split it manually
  by editing `segments.json` and re-running `split` and `faceless`.
- The faceless figure follows a single person. If two people are in
  frame it tracks the most prominent one.
- Fast, partly occluded or side-on movements can make limbs jitter; the
  renderer smooths landmarks between frames, but it is a tracked figure,
  not a generated actor.
