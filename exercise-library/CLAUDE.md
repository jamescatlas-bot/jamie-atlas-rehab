# Project: premium 3D exercise GIFs for my clients

I'm Jamie Atlas, a personal trainer and rehab specialist in Denver. I want a library of looping exercise GIFs that look like a high-end fitness app: a realistic, muscular, faceless grey 3D body doing each exercise on real gym equipment, with the working muscles glowing. I send them to clients by text or WhatsApp.

A reference screenshot is in this folder as `reference.jpg`. Open it and study it before you start. Match that look and quality. Don't copy any logo or brand name from it.

I'm not a coder. Explain what you're doing in plain English, spell out any acronym the first time, and ask me before installing anything big. If a result falls short of the reference, say so plainly and tell me what would close the gap.

## The look (match reference.jpg)

### The body
- Realistic athletic male anatomy with clearly defined muscles: delts, pecs, lats, abs, quads, hamstrings, glutes, calves. It should look like a sculpted grey clay statue, not a mannequin or stick figure.
- Smooth matte light-grey material. Soft highlights so the muscle shapes read clearly.
- Face present in shape but completely featureless: no eyes, mouth or hair.
- Plain black shorts only. Barefoot or plain shoes.
- Suggested free source: MPFB (the MakeHuman plugin for Blender), which builds realistic human bodies with a muscle-definition setting and a CC0 licence, meaning free for any use. Use a better free option if you know one, or tell me if I should buy a paid anatomy model and which kind.

### Muscle highlights
- The target muscles glow in saturated colour on top of the grey skin: orange-red for the prime mover, with a thin purple-to-blue rim light along the muscle edge, like the reference.
- Do this with painted masks for each muscle group on the body texture, driven by an emission shader, plus bloom or glare so it actually glows.
- Make it data-driven: I name the muscles (for example `quads, glutes`) and the script lights them up. Build masks for at least: quads, hamstrings, glutes, calves, pecs, lats, upper back, delts, biceps, triceps, abs, obliques, lower back.

### Scene, camera and lighting
- Dark charcoal studio background (near-black blue-grey), no visible walls.
- Moody lighting: one soft key light, a cool rim light behind the body, subtle floor reflection.
- Real gym equipment modelled in dark metal and black padding where the exercise needs it: barbell and plates, bench, lat pulldown machine, leg press, cable column, dumbbells, calf raise block, floor mat. Build simple but convincing versions in Blender, or use free CC0 models.
- Camera angle chosen per exercise to show the working muscle best (back view for pulldowns, low angle for calves, side view for squats and leg press), just like the reference.
- Vertical format, 9:16 (like a phone screen), 720 x 1280 for the master render.

### On-screen extras
1. **Muscle map inset.** A small strip at the top showing 3 or 4 tiny figures (front, back, sides) with the target muscle lit up, and the relevant view outlined in a glowing magenta or green box.
2. **Right vs wrong.** For some exercises, a split-screen version: top half shows a common fault with a red X icon and the problem joint glowing red, bottom half shows correct form with a green check and the joint glowing green. Example: leg press with knees caving in vs knees tracking over toes.
3. **Personal label (optional).** A clean strip at the bottom with the exercise name, sets and reps, and one cue using the client's first name, plus "Jamie Atlas Personal Training" in small text.

### Output
- Smooth loop of 2 to 3 reps, 24 to 30 fps.
- Export both an MP4 (best quality, small file, plays in iMessage and WhatsApp) and a GIF under 5 MB.
- Save to `/output/library/<exercise>.mp4` and `.gif`, and personalised versions to `/output/clients/<client>/`.

## Motion
Movement comes from one of these, in this order:
1. Mixamo (Adobe's free animation site) animations like squat, push-up and lunge. I'll download them if a login is needed; tell me exactly which files.
2. My own exercise videos in `/videos`, or free Pexels clips I've downloaded there. Extract joint movement only with MediaPipe (Google's free body-tracking tool) or a better free pose tool, smooth out the jitter, and apply it to the 3D body.
3. Hand-keyframed motion in Blender for machine exercises where tracking fails, like leg press and lat pulldown.

Nothing from the source video (face, body, clothes, background) ever appears in the output. Only the motion is used. Don't download videos from anywhere yourself.

## Build order
Stop after each stage, show me the result, and wait for my OK.

1. **Look test (most important).** Render one still image of the body standing in the studio with the quads glowing. Put it side by side with `reference.jpg` and tell me honestly how close it is. We iterate here until the body, lighting and glow look right. Don't animate anything until I approve this.
2. **First animation.** Barbell back squat, side view, glowing quads and glutes, 3-rep loop.
3. **Equipment and angles.** Lat pulldown from behind with the lats glowing, and a standing calf raise from a low angle.
4. **Muscle map inset.** Add the top strip to all three.
5. **Right vs wrong.** Leg press split-screen with knees caving in vs tracking correctly.
6. **Batch mode.** Read `exercises.csv` and render everything in one command:

```
exercise,motion_file,muscles,camera,equipment,fault_demo
Barbell back squat,squat.fbx,"quads,glutes",side,barbell,
Lat pulldown,pulldown.fbx,"lats,biceps",back,pulldown_machine,
Leg press,legpress.fbx,"quads,glutes",side,leg_press,knees_cave
```

7. **Personal labels.** Read `clients.csv` (client, exercise, sets_reps, cue) and render the labelled versions.
8. **README.** Plain-English guide to adding exercises and clients and running the whole thing.

## Folder layout
```
reference.jpg   the look to match
/videos         source videos I add
/motion         Mixamo files and extracted motion
/assets         body model, muscle masks, equipment
/scripts        all code
/output         finished files
exercises.csv
clients.csv
```

## Source videos (free Pexels licence, I'll download them)
1. Barbell squat: https://www.pexels.com/video/man-doing-barbell-squats-5319755/
2. Barbell squat, side view: https://www.pexels.com/video/side-view-of-a-man-doing-barbell-squats-5319759/
3. Bodyweight squat: https://www.pexels.com/video/man-doing-exercise-7426039/
4. Push-up: https://www.pexels.com/video/man-doing-push-ups-6388436/
5. Push-up variation: https://www.pexels.com/video/a-man-doing-a-push-ups-8858126/
6. Deadlift: https://www.pexels.com/video/young-man-lifting-bar-in-deadlift-9778003/
7. Deadlift, vertical: https://www.pexels.com/video/man-lifting-weights-in-a-gym-12890962/
8. Deadlift with mirror (tracking may struggle): https://www.pexels.com/video/deadlift-back-workout-14180867/
9. Lunge: a side-on clip from https://www.pexels.com/search/videos/lunges/
10. Glute bridge: a side-on clip from https://www.pexels.com/search/videos/glute%20bridge/
