# Exercise Library

A searchable library of 66 exercises, each with an animated 3D preview (a faceless grey body with the working muscles glowing). Pick an exercise, add your client's name, sets and a cue, then make a video to send by WhatsApp or iMessage.

## Using it

Open `output/exercise-library.html` in Chrome or Safari. It needs an internet connection the first time, to load the free 3D library (three.js).

1. Search by name, muscle ("glutes"), equipment ("dumbbell") or need ("rehab"). The filters narrow it by body area, home or gym, muscle, rehab-friendly, and exercises with a right-vs-wrong demo.
2. Tap an exercise to see it move. Toggles turn on the muscle map, the right-vs-wrong split screen and the client label.
3. Type the client's first name, change the sets and reps, and pick or write a cue.
4. **Make video** records a few clean reps (5 to 9 seconds). **Save video** keeps the file. **Copy text message** gives you a note to paste with it.

Safari and recent Chrome save MP4, which WhatsApp and iMessage play. Older browsers save WebM; the app tells you when that happens.

## Files

```
app/exercises.js   the database: one entry per exercise (muscles, cues, mistakes, camera, equipment)
app/motions.js     how each exercise moves: start and end poses as joint angles
app/engine.js      the 3D body, studio lighting, equipment, muscle glow and camera
app/ui.js          search, preview, labels, video and message
app/index.html     page layout and styles
scripts/build.mjs  joins everything into output/exercise-library.html and writes exercises.csv
exercises.csv      spreadsheet copy of the database, in the column format the render pipeline in CLAUDE.md reads
CLAUDE.md          the full brief for the premium rendered version
reference.jpg      the look to match
```

## Adding an exercise

Copy an entry in `app/exercises.js` that moves the same way (for example, copy "Goblet squat" to make "Heels-elevated goblet squat"), change the name, muscles and cues, then run:

```
node exercise-library/scripts/build.mjs
```

A new kind of movement needs a new motion in `app/motions.js`. Ask Claude to add it.

## What this is and isn't

These previews are drawn live in the browser. They are accurate enough to show a client the movement, the working muscles and the common fault, but the body is simpler than the sculpted anatomy in `reference.jpg`. The premium version in `CLAUDE.md` renders each exercise in Blender with a detailed anatomy model and real motion capture, and saves finished MP4 and GIF files. The same `exercises.csv` feeds that pipeline.
