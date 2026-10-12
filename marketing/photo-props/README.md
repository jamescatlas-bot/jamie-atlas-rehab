# Oversized photo props for the studio

Giant cardboard cutouts clients hold for a photo after a session. Same idea as the "giant cardboard cutout marketing" reels: the prop is comically big, people want to be photographed with it, and they post it themselves with the brand on it.

Four props:

| Prop | Finished size | File base name |
|---|---|---|
| Dumbbell, JA plates, "JAMIE ATLAS" on the bar | 48 x 22 in | `dumbbell` |
| Thumbs up, light skin tone | 28 x 36 in | `thumbs-up-light` |
| Thumbs up, medium skin tone | 28 x 36 in | `thumbs-up-medium` |
| Thumbs up, deep skin tone | 28 x 36 in | `thumbs-up-deep` |

Every prop has a 0.6 in white border around the art (that is where the cut goes) and a hand hole so a client can grip it from behind the way the reel shows.

## What is in `dist/`

- `print/*-print.pdf`. Full size, one page each, vector. Send these to a sign shop. The magenta hairline is the cut contour (named `CutContour` in the SVG), and the small magenta rectangle is the hand hole.
- `svg/*.svg`. Editable masters. All text is already outlines, so no fonts needed. Open in Illustrator, Inkscape, Affinity or Canva (Canva imports SVG).
- `home-print/*-tiled-letter.pdf`. The same art tiled onto US Letter pages with a 0.5 in overlap, crop guides, tile labels and an assembly map on page 1. For a home or office printer.
- `preview/*.png`. Previews for sharing with the shop or for an Instagram story "coming soon".

## Getting them made

### Option A. Sign shop (recommended, 1 to 3 days, roughly $35 to $70 per prop)

Email or upload the four `print` PDFs. Ask for this, word for word:

> Direct print on 5 mm white foam board (Gatorboard or 3 mm PVC if you have it, it survives more sessions), matte or satin finish, contour cut on the magenta line, hand hole cut out. Finished sizes: dumbbell 48 x 22 in, thumbs up 28 x 36 in, three of them. Single sided.

Places that do this in Denver without fuss: FedEx Office (ask for "foam board print, contour cut"), Staples print, any local sign shop, or online at Signs.com, Vistaprint (foam board signs), or Printful. Online shops usually want you to pick the nearest standard size then upload. For the thumbs up pick 36 x 48 in and ask for a contour cut; for the dumbbell pick 48 x 24 in. The white border is already in the art so a straight rectangle cut still looks fine if contour cutting costs extra.

If a shop cannot contour cut: order a rectangle and cut the border yourself with a snap-off blade and a straight edge. Foam board cuts easily. Cut the hand hole from the back.

### Option B. Home printer, cardboard and glue (one evening, under $20)

1. Print the `home-print` PDF at 100 percent, actual size. Turn off "fit to page". The map page tells you the grid.
2. Trim the right and bottom edge of each page on the dashed line, overlap with the next page so the art lines up, tape the back.
3. Spray adhesive or glue stick the whole sheet onto foam board or a flattened moving box. Press flat under books while it dries.
4. Cut around the outside of the white border and cut out the hand hole.
5. Optional: a coat of clear matte spray so fingerprints wipe off.

Heavier paper (28 lb or card stock) makes the seams less visible.

## Materials that hold up

- 5 mm foam board: light, cheap, bends if you leave it against a radiator. Fine for a trial run.
- 3/16 in Gatorboard: stiffer, dents less, about double the price. Buy this once you know the props work.
- 3 mm PVC (Sintra): nearly indestructible, heavier. For the dumbbell if clients keep swinging it.

The dumbbell is 48 in wide. On 5 mm foam board it will flex at the bar. Gatorboard or PVC fixes that, or glue two foam board layers back to back.

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
pip install cairosvg fonttools shapely pypdf reportlab pillow
python3 marketing/photo-props/generate.py
```

Sizes, colours and the skin tone palette are at the top of `generate.py`. Change `THUMB_W`, `THUMB_H`, `DB_W`, `DB_H` for a different finished size; everything else scales. Fonts are Inter Black and Inter Bold from the site; the script turns them into outlines so the print files never depend on a font being installed.
