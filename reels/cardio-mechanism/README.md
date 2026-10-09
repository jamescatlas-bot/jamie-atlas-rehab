# Cardio mechanism reels

Three vertical videos (1080x1920, 30 fps, silent) in the style of the "Why muscle gain takes weeks to show" timeline reel, but for cardio. Each one steps a playhead along a time axis while the body's adaptations fill in row by row, with an animated schematic panel above (heart-rate trace of the session, a fibre cross-section with mitochondria and capillaries, a nucleus sending signals, a blood vessel, the left ventricle).

| File | Protocol shown | Length |
|---|---|---|
| `video/cardio-steady.mp4` | Regular steady-state cardio, about 40 min at ~70% HRmax, 3x a week | 48 s |
| `video/cardio-4x4.mp4` | Norwegian 4x4: 4 x 4 min at 90-95% HRmax, 3 min easy between, 3x a week | 57 s |
| `video/cardio-zone2.mp4` | 300 min a week of zone 2, about 5 x 60 min at 60-70% HRmax | 50 s |

No music or voice track. Add music in the Instagram editor the same way the muscle reel did. The ElevenLabs key attached to this environment does not carry text-to-speech permission, so no narration was generated.

## How to rebuild or edit

```
cd reels/cardio-mechanism
node render.mjs data-steady.js out/steady 30          # writes PNG frames
ffmpeg -framerate 30 -i out/steady/f%05d.png -c:v libx264 -crf 19 -pix_fmt yuv420p video/cardio-steady.mp4
```

`render.mjs` needs Playwright with Chromium (it is pre-installed in the cloud session; adjust the two paths at the top otherwise). All copy, numbers, row colours and phase timing live in the three `data-*.js` files. `engine.html` is the layout and the animation. Fonts are bundled in `fonts/` (Fraunces, Inter, JetBrains Mono, all SIL Open Font License).

To preview without rendering, pass a list of seconds as a fourth argument and it writes single frames instead:

```
node render.mjs data-4x4.js out/check 30 "0,8,20,35,50"
```

## Where the numbers come from

The research was done from abstracts and secondary summaries because PubMed and the journal sites are blocked from the cloud container. Numbers marked (flag) were not confirmed against a full text and should be checked before being quoted in writing. On screen, every figure is rounded to what the evidence supports, and where studies disagree the video shows a range.

### Shared mechanism rows

**Signal (PGC-1α gene).** One session turns on the master gene for building mitochondria. Perry 2010 (J Physiol): PGC-1α mRNA more than 10-fold 4 h after the first interval session, back to baseline by 24 h; the burst shrinks with repeated sessions while the protein accumulates (+23% after one session, +30-40% plateau by sessions 3-7). Egan 2010 (J Physiol): 10.2-fold at 80% VO2peak vs 3.8-fold at 40% for the same calories. Pilegaard 2003: 7-10-fold mRNA, peak within 2 h. That is the "×4 to ×10" on the steady-state video, "×10" on the 4x4 video and "×3 to ×4" on the zone 2 video (zone 2 sits near the 40% end of Egan's comparison; Nordsborg 2010 reports ~3-fold at 70% VO2peak).

**Mitochondria.** Egan 2013 (PLoS One, daily 60 min at 80%): citrate synthase +35% by day 3. Talanian 2007 (J Appl Physiol, 7 interval sessions in 2 weeks): CS +20%, β-HAD +32%. Perry 2010: enzyme activity up by session 3. Hoppeler 1985 (J Appl Physiol, 6 weeks, 5x/week): mitochondrial volume density +40%. Meinild Lundby 2018 (Acta Physiol, 6 weeks): +55%. Montero 2015 (J Physiol, 6 weeks, 3-4x/week): +43%. Granata 2016/2018 (FASEB J, Sports Med): volume drives content, intensity drives respiration per mitochondrion. Coyle 1984: half the enzyme gain is lost within 3-8 weeks of stopping.

**Capillaries.** Hoier 2012 (J Physiol, 4 weeks of 60 min at 60% VO2max, 3x/week): capillary-to-fibre ratio +23%. Jensen 2004: +41% at 4 weeks with intense knee-extensor work. Andersen & Henriksson 1977 (8 weeks): +20%. Ingjer 1979 (24 weeks): +29%. Hoier 2010: endothelial cells proliferating 2-fold at 2 weeks, so bars start around day 10-14.

**Blood.** Gillen 1991 (J Appl Physiol): plasma volume +10% 24 h after one session of 8 x 4 min at 85%. Montero 2017 (AJP Regul, 3-4 x 60 min/week): plasma +16% at week 2, +21% at week 4, settling to +14% at week 8; red-cell volume +6% at week 4, +12% at week 8. Bonne 2014 and Montero 2015: removing the gained blood by phlebotomy removed most of the VO2max gain at 6 weeks, so early fitness is largely a blood-volume effect.

**Heart.** Helgerud 2007 (MSSE): stroke volume about +10% after 8 weeks in the interval groups. Bonne 2014: no structural heart change at 6 weeks. Spence 2011 (J Physiol): LV mass +8% at 6 months. Arbab-Zadeh 2014 (Circulation): LV mass +21%, stroke volume +24% after a year, with chamber enlargement only after month 6. Hence "blood per beat" rises within weeks, "wall grows after month 3".

**Resting pulse.** Reimers 2018 meta-analysis (J Clin Med): -2.7 to -5.8 bpm. Scharhag-Rosenberger 2009 (MSSE): -9 bpm at 12 months, about half of that by month 3 and all of it by month 6.

### Steady-state video (regular cardio, 3x/week)

VO2max: Murias 2010 (J Appl Physiol, 3 x 45 min at 70%, tested every 3 weeks): significant by week 3, +18% in young men and +31% in older men at 12 weeks. Scharhag-Rosenberger 2009 (3 x 45 min at 60% HRR): about +8% by month 3, +16% median at 12 months. Hickson 1981: half-time of the VO2max response about 10.5 days. HERITAGE (Bouchard 1999, Skinner 2001, 20 weeks): mean +384-400 mL/min, roughly +16-18% (flag: percent derived). Milanović 2015 meta: +4.9 mL/kg/min vs control. The video shows "no change" at day 1 and "+10 to 18%" by week 12.

### Norwegian 4x4 video

Helgerud 2007: 40 moderately trained men, 8 weeks, 3x/week, four groups matched for total work. 4x4 at 90-95% HRmax: VO2max +7.2%. 15/15 intervals: +5.5%. Continuous 70% HRmax and 85% HRmax: no significant change. Stroke volume about +10% in the interval groups. Lactate threshold as a percentage of VO2max unchanged in all groups. That is the "same work at 70%: 0%" line.

Støren 2017 (MSSE): 94 adults aged 20-70+, 8 weeks of 4x4, VO2max +9-13% in every age group, bigger gains from a lower starting point. Tjønna 2013 (PLoS One): overweight men, 10 weeks, +13% (4x4) vs +10% (1x4). Rognmo 2004: coronary patients, 10 weeks, +17.9% vs +7.9% moderate. Tjønna 2008 (Circulation): metabolic syndrome, 16 weeks, +35% vs +16%, artery dilation (FMD) +9% vs +5%. Wisløff 2007 (Circulation): heart failure, 12 weeks, +46% vs +14%. Ramos 2015 meta (Sports Med): FMD +4.3% HIIT vs +2.2% moderate. Talanian 2007: fat oxidation +36% and VO2peak +13% after 7 sessions in 2 weeks (10 x 4 min, women). Rognmo 2012 (Circulation, safety): 1 cardiac event per 23,182 hours of intervals vs 1 per 129,456 hours of moderate work in 4,846 cardiac rehab patients; both rates low.

Not used because unverified: Tjønna 2008 "PGC-1α +138%", Weston 2014 "19.4% vs 10.3%", any HIIT-over-moderate blood-pressure advantage (Costa 2018 found none at rest).

### Zone 2 video (300 min/week)

No trial tracks exactly 300 min/week of zone 2 week by week in untrained people, so this video combines the closest doses. Ross 2015 (Annals of Internal Medicine, 24 weeks, abdominally obese adults): the high-amount low-intensity arm did about 290 min/week at 50% VO2peak. All exercise arms improved VO2peak; the 290-min arm only separated from the 155-min arm at weeks 16-24; responders gained +0.49 L/min and 82% responded; waist -4.6 cm (the same as the vigorous arm). Per-arm mL/kg/min figures could not be retrieved (flag), so the video says "around 15%". Montero & Lundby 2017 (J Physiol): at 300 min/week, 0% non-responders after 6 weeks, compared with 69% at 60 min/week. Church 2007 (JAMA, DREW): 72/136/192 min/week at 50% gave +4.2/+6.0/+8.2% after 6 months, which is why the video keeps the 12-week number at about +10%. Greenleaf/Convertino 1983: +8.3% VO2max after 8 days of 2 h/day at 65%.

Fat burning: Phillips 1996 (J Appl Physiol, 2 h/day at 60%): whole-body fat oxidation +10% by day 5, a further +58% by day 31. Venables & Jeukendrup 2008 (MSSE, 4 weeks continuous at FATmax): +44%. Threshold: Davis 1979 (J Appl Physiol, 45 min/day, 4 days/week, 9 weeks): anaerobic threshold +15% as a share of VO2max. Carter 1999: lactate-threshold speed +6% at 6 weeks. Denis 1982: threshold gains lag behind, continuing to week 20-40.

## Limits

- The time axes are not linear (start, 1 day, 1 week, 4 weeks, 12 weeks are equally spaced), same as the muscle reel.
- Bars show when a change becomes measurable and roughly how big it gets. They are not fitted curves.
- Most studies are on untrained or moderately trained adults. Trained people adapt less and more slowly.
- The schematic panel is an illustration, not a micrograph. The chip in the corner says so.
