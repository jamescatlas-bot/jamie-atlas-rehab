// YouTube videos, supplied by Jamie 2026-07-30.
// Press clips are official 9NEWS channel segments featuring Jamie (except the raw boxing spot).

export interface Video {
  id: string; // YouTube video ID
  title: string;
}

export const PRESS_VIDEOS: Video[] = [
  { id: 'ji3xvNk3T4M', title: '3 glute exercises to add to your workout (9NEWS)' },
  { id: 'NUTTTyyo8qE', title: 'Wellness Wednesday: Stretches and exercises for hiking (9NEWS)' },
  { id: '5EhGpjWFBgU', title: 'Workouts and stretches to help your golf game (9NEWS)' },
  { id: 'f_SoiKUqHak', title: '3 tips for better posture in the workplace (9NEWS)' },
  { id: 'eCYSIo1lKuY', title: 'Posture exercises for returning to the workplace (9NEWS)' },
  { id: '8ALP3EhbWN0', title: 'Wellness Wednesday: Ways to improve your balance (9NEWS)' },
  { id: '3pjgcMCT0rQ', title: '9NEWS boxing spot (raw footage)' },
];

// Instagram posts supplied by Jamie 2026-08-01 — to be reviewed/categorized and
// embedded (or re-hosted) in a future session. IG embeds need Meta's embed.js,
// so decide placement deliberately before adding.
export const INSTAGRAM_POSTS: string[] = [
  'https://www.instagram.com/p/CLoByboB9-i/',
  'https://www.instagram.com/p/CLfRo2ABdG4/',
  'https://www.instagram.com/p/CLrgc0PhJ_K/',
  'https://www.instagram.com/p/B4wGgtYFDXY/',
  'https://www.instagram.com/p/CRNifVeBKQ7/',
  'https://www.instagram.com/p/BIjjHVcjH_x/',
  'https://www.instagram.com/p/B9FYxWxln80/',
  'https://www.instagram.com/p/CLnoH5Ihy8S/',
  'https://www.instagram.com/p/BoR5yTGHIj6/',
  'https://www.instagram.com/p/CI9y32FBOEy/',
  'https://www.instagram.com/tv/CVs3H7TBQCu/',
];

/**
 * ============================================================================
 * CLIENT VIDEO TESTIMONIALS
 * ============================================================================
 *
 * 21 clips, uploaded by Jamie to YouTube as unlisted Shorts on 2026-08-05.
 * All are VERTICAL (9:16) — the cards are built for portrait, not widescreen.
 *
 *
 * >>> JAMIE: THIS IS THE FILE YOU EDIT. <<<
 *
 * Every entry below has an empty `bio: ''` waiting for you. Type between the
 * quote marks. That text appears beside the video — on desktop it sits to the
 * LEFT of the clip, on a phone it sits underneath.
 *
 * What to put in a bio — two or three sentences:
 *   - who they are in a sentence (age bracket, work, sport — no surnames)
 *   - what they had been living with, and for how long
 *   - what they had already tried before they got to you
 *
 * That third one is the load-bearing part. "Eighteen months, two courses of
 * physio and a cortisone injection" is what makes a visitor think *that's me*.
 *
 * WORDS TO NEVER USE: cure, miracle, guaranteed, permanent, or any phrasing
 * that implies these results are typical. Describe what happened to one person.
 *
 * Leaving a bio empty is safe — the card renders fine without it.
 *
 *
 * TWO STANDING RULES, decided 2026-08-02:
 *
 * 1. PROOF SITS NEXT TO THE CLAIM. Every video carries the condition page it
 *    belongs on. Someone with neck pain does not care about the back clips.
 *    Twenty videos in one pile reads as an infomercial; the same twenty sorted
 *    by body part read as depth.
 *
 * 2. EXPLAIN THE SPEED ONCE, NOT ON EVERY CARD. The "why can this change so
 *    fast" framing lives in <SpeedExplainer />, shown once above any block of
 *    videos. `note` is therefore optional — use it only where one specific clip
 *    needs its own context. Ten hedges in a row read defensively.
 *
 * ORDER MATTERS. Condition pages show the FIRST THREE entries for that
 * condition, in the order they appear below. Jamie's chosen three are first in
 * each group; the rest still appear in full on /testimonials.
 */
export type ConditionSlug =
  | 'chronic-back-pain'
  | 'sciatica'
  | 'neck-pain'
  | 'shoulder-pain'
  | 'knee-pain'
  | 'post-surgical-return-to-sport'
  | 'masters-athlete-injuries'
  | 'cognitive-functional-therapy';

export interface Testimonial {
  id: string; // YouTube video ID
  condition: ConditionSlug; // which condition page this appears on
  title: string; // plain descriptive title — used for schema + screen readers
  headline: string; // the short caption shown above the bio
  bio?: string; // JAMIE FILLS THIS IN — who they are and what they had tried
  note?: string; // optional extra context for this specific clip
  // Frame shape. The 2026-08-05 batch are all Shorts (portrait) — that's the
  // default. The two older uploads are widescreen and 4:3 respectively, and
  // would be badly cropped by a portrait frame.
  orientation?: 'portrait' | 'landscape' | 'classic';
  uploadDate?: string;
  featured?: boolean; // true = also appears on the homepage
}

export const TESTIMONIAL_VIDEOS: Testimonial[] = [
  // ===========================================================================
  // NECK PAIN — page shows the first THREE: Monique, Danielle, Sandy.
  // Natasha sits fourth on purpose, so she appears only in the /testimonials
  // library, per Jamie 2026-08-05.
  // ===========================================================================
  {
    id: 'X5EquRG2d24',
    condition: 'neck-pain',
    title: "Client testimonial — Monique, 4 weeks of neck pain rated 7/10",
    headline: "Monique — 4 weeks of 7/10 neck pain",
    bio: "A stay-at-home mom, four weeks in. Pain went from 7/10 to 0/10 in 40 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'SkaGhF5C628',
    condition: 'neck-pain',
    title: "Client testimonial — Danielle, 6 weeks of neck pain rated 7/10",
    headline: "Danielle — 6 weeks of 7/10 neck pain",
    bio: "A skier who'd had it for six weeks. Pain went from 7/10 to 0/10 in 40 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: '-gdriOBWpS0',
    condition: 'neck-pain',
    title: "Client testimonial — Sandy, 3 years of neck pain rated 8/10",
    headline: "Sandy — 3 years of 8/10 neck pain",
    bio: "An office worker who'd had it for three years. Pain went from 8/10 to 0/10 in three weeks — and her tears of happiness are 100% in-the-moment real.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
    featured: true,
  },
  {
    id: 'Y3SSXfeul9M',
    condition: 'neck-pain',
    title: "Client testimonial — Natasha, 4 weeks of neck pain rated 7/10",
    headline: "Natasha — 4 weeks of 7/10 neck pain",
    bio: "A Pilates devotee, four weeks in. Pain went from 7/10 to 1/10 in 30 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },

  // ===========================================================================
  // KNEE PAIN — Cindy first, per Jamie.
  // ===========================================================================
  {
    id: 'Ar2YTC_8vTY',
    condition: 'knee-pain',
    title: "Client testimonial — Cindy, a lifetime of knee pain rated 6/10",
    headline: "Cindy — a lifetime of 6/10 knee pain",
    bio: "A walker who'd had pain lunging for as long as she could remember. Pain went from 6/10 to 2/10 in 10 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'nPUisex9g_s',
    condition: 'knee-pain',
    title: "Client testimonial — Meghan, knee pain after an ACL tear, 4 out of 10 down to 0",
    headline: "Meghan — 4/10 knee pain after an ACL tear",
    bio: "An MMA fighter with a recent ACL tear. Pain went from 4/10 to 0/10 in 50 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'Vc04UjsZ8wA',
    condition: 'knee-pain',
    title: "Client testimonial — Brad, 6 months of knee pain rated 6/10",
    headline: "Brad — 6 months of 6/10 knee pain",
    bio: "A hiker who'd had it for six months. Pain went from 6/10 to 1/10 in 50 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },

  // ===========================================================================
  // SHOULDER PAIN — Samantha first, per Jamie. Page shows the first three.
  // ===========================================================================
  {
    id: 'r76KZHBcyNk',
    condition: 'shoulder-pain',
    title: "Client testimonial — Samantha, 5 years of shoulder pain rated 7/10",
    headline: "Samantha — 5 years of 7/10 shoulder pain",
    bio: "A kickboxer who'd had it for five years. Pain went from 7/10 to 1/10 in 20 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: '31I4nnADI_s',
    condition: 'shoulder-pain',
    title: "Client testimonial — Heather, 6 weeks of shoulder nerve pain rated 10/10",
    headline: "Heather — 6 weeks of 10/10 shoulder nerve pain",
    bio: "A fitness instructor with six weeks of nerve pain. Pain went from 10/10 to 1/10 in 45 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
    // Featured 2026-08-06: gives the homepage a 10/10 case and a third body
    // part (neck + back + shoulder), so the proof block reads as range.
    featured: true,
  },
  {
    id: 'Mo2yzytV12M',
    condition: 'shoulder-pain',
    title: "Client testimonial — Judy, 6 months of shoulder pain rated 10/10",
    headline: "Judy — 6 months of 10/10 shoulder pain",
    bio: "A mom who'd been at 10/10 for six months. Pain went from 10/10 to 4/10 in 60 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'oVUovrIO0m8',
    condition: 'shoulder-pain',
    title: "Client testimonial — Sharon, 4 months of shoulder pain rated 6/10",
    headline: "Sharon — 4 months of 6/10 shoulder pain",
    bio: "A traveling salesperson, four months in. Pain went from 6/10 to 2/10 in two weeks.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'ijhLo50nWpA',
    condition: 'shoulder-pain',
    title: "Client testimonial — Clay, 10 years of shoulder pain rated 7/10",
    headline: "Clay — 10 years of 7/10 shoulder pain",
    bio: "A pickleball player who'd had it for ten years. Pain went from 7/10 to 1/10 in three weeks.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: '3ElcDHKLHVY',
    condition: 'shoulder-pain',
    title: "Client testimonial — Kendall, 2 weeks of shoulder pain rated 6/10",
    headline: "Kendall — 2 weeks of 6/10 shoulder pain",
    bio: "An office manager, two weeks in. Pain went from 6/10 to 2/10 in 45 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },

  // ===========================================================================
  // CHRONIC BACK PAIN — Kelly first, per Jamie. Page shows the first three.
  // ===========================================================================
  {
    id: 'Ts1vlG3fz_0',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Kelly, 12 months of back pain rated 8/10",
    headline: "Kelly — 12 months of 8/10 back pain",
    bio: "An athlete who'd had it for a year. Pain went from 8/10 to 0/10 in 35 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'qGHHUMxU_NU',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Dax, 5 days of back pain rated 10/10",
    headline: "Dax — 5 days of 10/10 back pain",
    bio: "A golfer, five days in and at 10/10. Pain went from 10/10 to 0/10 in two weeks.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'qHzrGaiAB-Q',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Matthew, 7 weeks of back pain rated 7/10",
    headline: "Matthew — 7 weeks of 7/10 back pain",
    bio: "A football player, seven weeks in. Pain went from 7/10 to 3/10 in 60 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'DcPAJmkb1z8',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Colleen, 8 weeks of back pain rated 7/10",
    headline: "Colleen — 8 weeks of 7/10 back pain",
    bio: "A riding instructor, eight weeks in. Pain went from 7/10 to 0/10 in 55 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'T01Y32utAXU',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Katrina, 4 weeks of back pain rated 6/10",
    headline: "Katrina — 4 weeks of 6/10 back pain",
    bio: "An equestrian, four weeks in. Pain went from 6/10 to 0/10 in 50 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
    featured: true,
  },
  {
    id: 'oLZDLUR8BP0',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Alexis, 2 months of back pain rated 10/10",
    headline: "Alexis — 2 months of 10/10 back pain",
    bio: "A receptionist who had been at 10/10 for two months. Pain went from 10/10 to 1/10 in 60 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: '83raGZissVc',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Penelope, 5 weeks of back pain rated 7/10",
    headline: "Penelope — 5 weeks of 7/10 back pain",
    bio: "A tennis player, five weeks in. Pain went from 7/10 to 0/10 in 60 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
  {
    id: 'erAOrteinvo',
    condition: 'chronic-back-pain',
    title: "Client testimonial — Chris, 8 weeks of back pain rated 7/10",
    headline: "Chris — 8 weeks of 7/10 back pain",
    bio: "A dad, eight weeks in. Pain went from 7/10 to 1/10 in 50 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },

  // ===========================================================================
  // SCIATICA — 2 clips.
  // ===========================================================================
  {
    id: 'jj9HW5h-Myc',
    condition: 'sciatica',
    title: "Client testimonial — Kendra, two years of shooting sciatic pain resolved",
    headline: "Kendra — 2 years of shooting sciatic pain",
    bio: "A volleyball player, two years of shooting sciatic pain. Down to 0/10 in 20 minutes.",
    note: 'Your results may vary.',
    orientation: 'landscape', // 1280x720 — filmed before the Shorts batch
    uploadDate: '2026-07-30',
  },
  {
    id: 'WZARvxb52uk',
    condition: 'sciatica',
    title: "Client testimonial — Tony, two weeks of severe back pain down to 1 out of 10",
    headline: "Tony — 2 weeks of lightning-bolt back pain",
    bio: "A mountain biker, two weeks of what he called lightning-bolt pain. Down to 1/10 in 50 minutes.",
    note: 'Your results may vary.',
    uploadDate: '2026-08-05',
  },
];

/**
 * The lead testimonial on /testimonials.
 *
 * Sits ABOVE the body-part groups, on its own, before any of the single-joint
 * clips. It is a different kind of proof: not "my shoulder moved", but an older
 * client describing what the training changed about how he lives. That belongs
 * at the top, framing everything under it, rather than buried in a group.
 *
 * Deliberately NOT in TESTIMONIAL_VIDEOS — that array drives the body-part
 * groups, and this clip is not about one joint.
 *
 * 480x360, filmed years before the 2026 batch, hence orientation 'classic'.
 */
export const LEAD_TESTIMONIAL: Testimonial = {
  id: 'wX7ayi3Qm-g',
  condition: 'masters-athlete-injuries',
  title: 'Client testimonial — Tom H. on what the training changed',
  headline: 'What it changes, past a certain age.',
  bio: '',
  orientation: 'classic',
  uploadDate: '2026-07-30',
};

export const FEATURED_TESTIMONIALS = TESTIMONIAL_VIDEOS.filter(t => t.featured);

/**
 * Videos for one condition page.
 *
 * Deliberately capped at three. Nobody watches the fourth clip on a service
 * page, and every extra one costs page weight for no conversion. The full
 * library lives on /testimonials, where volume is the point — twenty-one clips
 * sorted by body part read as "this happens here routinely" rather than as
 * cherry-picking.
 */
export function testimonialsFor(slug: string, limit = 3): Testimonial[] {
  return TESTIMONIAL_VIDEOS.filter(t => t.condition === slug).slice(0, limit);
}

/** How many exist in total for a condition — used for the "see all" link. */
export function testimonialCount(slug: string): number {
  return TESTIMONIAL_VIDEOS.filter(t => t.condition === slug).length;
}
