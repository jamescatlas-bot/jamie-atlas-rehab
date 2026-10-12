# Oversized photo props for the studio

Giant cardboard cutouts clients hold for a photo after a session. Same idea as the "giant cardboard cutout marketing" reels: the prop is comically big, people want to be photographed with it, and they post it themselves with the brand on it.

Two sets, same sizes and files either way.

**Photo set (use these).** A thumbs up shot on a green screen and a hand gripping a 5 kg hex dumbbell, both from Unsplash at full camera resolution (4000 x 6000 and 6000 x 4000), cut out of their backdrops. Hands only, no cuff and no text, because clients stand in front of the promo banner and the banner does the branding. Credits are in `source/CREDITS.md`. Jamie's own 1200 px photos from the first pass are kept in `source/` as `jamie-*.jpg` but no longer used.

Each prop comes in three skin tones. Light, medium and deep are a colour shift of the real hand, so hair, knuckles, veins and shading all stay.

Both hands print at the same scale: twice life size. The two photos were shot at different distances and show different parts of the hand, so the script measures the widest run of skin in each photo and scales it from what that span measures in real life (wrist to curled fingertips on the thumbs up, across the fist on the dumbbell).

| Prop | Finished size | File base name |
|---|---|---|
| Thumbs up, light / medium / deep | 34 x 34 in | `photo-thumbs-up-light`, `-medium`, `-deep` |
| Hand holding the dumbbell, light / medium / deep | 26 x 15 in | `photo-dumbbell-light`, `-medium`, `-deep` |

Want them bigger or smaller? Change `LIFE_SIZE_X` at the top of `photo_props.py` (2.0 = twice life size) and re-run. Everything scales together and the hands stay matched. The print files are 150 pixels per inch, built from photos that give roughly 90 pixels per inch on the thumbs up and 180 on the dumbbell at this size, which is plenty for a prop viewed from a few feet.

**Illustrated set (backup).** Flat vector versions of the same four props in the site colours, in case a shop wants pure vector or the photo prints too soft.

| Prop | Finished size | File base name |
|---|---|---|
| Dumbbell, JA plates, "JAMIE ATLAS" on the bar | 48 x 22 in | `dumbbell` |
| Thumbs up, light / medium / deep | 28 x 36 in | `thumbs-up-light`, `thumbs-up-medium`, `thumbs-up-deep` |

Every prop has a 0.6 in white border around the art, and that border is where the cut goes. There is no hand hole, because a hole through a hand looks wrong. Ask the shop to glue a cardboard strap or a strip of foam board across the back as a handle, or do it yourself with hot glue. Clients grip the strap and the prop sits flat against their chest.

## What is in `dist/`

- `print/*-print.pdf`. Full size, one page each. Send these to a sign shop. The magenta hairline is the cut contour (named `CutContour` in the SVG). The illustrated set is pure vector; the photo set is the photo at true size with a vector cut line on top.
- `svg/*.svg`. Editable masters. Illustrated ones have all text as outlines, so no fonts needed. Photo ones wrap the picture with the cut path. Open in Illustrator, Inkscape, Affinity or Canva (Canva imports SVG).
- `cutouts/*.png`. The two photos with the backdrop removed and a transparent background, for anything else (stories, the website, a sticker).
- `home-print/*-tiled-letter.pdf`. The same art tiled onto US Letter pages with a 0.5 in overlap, crop guides, tile labels and an assembly map on page 1. For a home or office printer.
- `preview/*.png`. Previews for sharing with the shop or for an Instagram story "coming soon".

## Getting them made

### Option A. Sign shop (recommended, 1 to 3 days, roughly $35 to $70 per prop)

Email or upload the four `print` PDFs. Ask for this, word for word:

> Direct print on 5 mm white foam board (Gatorboard or 3 mm PVC if you have it, it survives more sessions), matte or satin finish, contour cut on the magenta line. Finished sizes: thumbs up 34 x 34 in, dumbbell 26 x 15 in. Single sided. Please add a cardboard strap handle on the back of each.

Places that do this in Denver without fuss: FedEx Office (ask for "foam board print, contour cut"), Staples print, any local sign shop, or online at Signs.com, Vistaprint (foam board signs), or Printful. Online shops usually want you to pick the nearest standard size then upload. For the thumbs up pick 36 x 36 in and ask for a contour cut; for the dumbbell pick 30 x 18 in or 36 x 24 in. The white border is already in the art so a straight rectangle cut still looks fine if contour cutting costs extra.

If a shop cannot contour cut: order a rectangle and cut the border yourself with a snap-off blade and a straight edge. Foam board cuts easily.

### Option B. Home printer, cardboard and glue (one evening, under $20)

1. Print the `home-print` PDF at 100 percent, actual size. Turn off "fit to page". The map page tells you the grid.
2. Trim the right and bottom edge of each page on the dashed line, overlap with the next page so the art lines up, tape the back.
3. Spray adhesive or glue stick the whole sheet onto foam board or a flattened moving box. Press flat under books while it dries.
4. Cut around the outside of the white border. Hot-glue a strip of cardboard across the back as a handle.
5. Optional: a coat of clear matte spray so fingerprints wipe off.

Heavier paper (28 lb or card stock) makes the seams less visible.

## Materials that hold up

- 5 mm foam board: light, cheap, bends if you leave it against a radiator. Fine for a trial run.
- 3/16 in Gatorboard: stiffer, dents less, about double the price. Buy this once you know the props work.
- 3 mm PVC (Sintra): nearly indestructible, heavier. For the dumbbell if clients keep swinging it.

The thumbs up is nearly three feet each way. On 5 mm foam board it will flex. Gatorboard or PVC fixes that, or glue two foam board layers back to back.

## Using them in the studio

- Pick one spot with the cleanest wall and the best light and keep the props on a hook there. A photo station only works if it takes ten seconds.
- Hand the client the thumbs up that matches their skin tone, or let them pick. That is why there are three.
- Phrase it as a choice, not a request: "Want the big thumbs up or the big dumbbell for your victory photo?"
- Take it on their phone, not yours, then they already have it to post. Ask them to tag @jamieatlasfitness.
- Portrait orientation, waist up, prop held at chest height so the name reads.

## Caption starters (Jamie's voice, edit as needed)

- Session done. Thumb size is accurate.
- The dumbbell is fake. The work was not.
- Four feet of dumbbell. Zero pain in the shoulder. Good day.
- Big thumbs up for showing up. That is most of it.

## Regenerating or changing the files

```
pip install cairosvg fonttools shapely pypdf reportlab pillow opencv-python-headless numpy
python3 marketing/photo-props/generate.py      # illustrated set
python3 marketing/photo-props/photo_props.py   # photo set
```

For the photo set, the size multiplier is `LIFE_SIZE_X` at the top of `photo_props.py`, each photo's real-world span is `span_in` in `PROPS`, and the skin tone targets are in `retone()`. To swap in a different hand, replace `source/thumbs-up.jpg` with a photo on a plain or green backdrop, hand filling the frame, and re-run. A photo with other things in it (the dumbbell one has a second dumbbell and a shoe) gets `erase` and `keep` polygons in `PROPS`, in fractions of the frame, that paint out what is not the prop. For the illustrated set, sizes, colours and the skin tone palette are at the top of `generate.py`. Change `THUMB_W`, `THUMB_H`, `DB_W`, `DB_H` for a different finished size; everything else scales. Fonts are Inter Black and Inter Bold from the site; the script turns them into outlines so the print files never depend on a font being installed.
