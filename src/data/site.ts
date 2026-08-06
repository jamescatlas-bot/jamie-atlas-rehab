// Central site configuration — change anything here, the whole site updates.
// Phone is Google Voice business line, NOT Jamie's personal cell (720-203-3084).
//
// NAME: must match the Google Business Profile exactly. The Aug 2026 citation
// audit found 13 different business names in the wild; `name` below is the one
// canonical form. Historical variants live in `alternateNames` and are emitted
// as schema.org alternateName so Google can reconcile them to a single entity.
//
// ZIP: 80202 is correct, and matches the Google Business Profile.
// USPS returns 80202-3828 for 1800 Glenarm Pl. Local Falcon's cached record
// reports 80203 — that record is stale and wrong. Do NOT "fix" this to 80203.

export const SITE = {
  name: 'Jamie Atlas Rehabilitation & Personal Training',
  shortName: 'Jamie Atlas',
  tagline: 'Get out of chronic pain. Get back to your sport.',
  description:
    'Cognitive Functional Therapy + 30 years of strength coaching for Denver adults 40+. We work the gap between PT discharge and athletic performance.',
  url: 'https://jamieatlas.com',
  serviceArea: ['Denver', 'Lakewood', 'Aurora', 'Littleton', 'Boulder', 'Englewood', 'Highlands Ranch'],

  // Prior trading names, emitted as schema.org alternateName. This tells Google
  // that the legacy Bonza Bodies listings and the current business are one entity.
  alternateNames: [
    'Jamie Atlas Rehab & Performance',
    'Bonza Bodies',
    'Bonza Bodies Fitness',
    'Bonza Bodies Personal Training',
    'Bonza Bodies Goal Based Training Studio',
  ],

  contact: {
    phone: '(720) 257-9328',
    phoneTel: '+17202579328',
    email: 'jamie@jamieatlas.com',
    address: {
      street: '1800 Glenarm Place',
      level: 'Basement Level',
      city: 'Denver',
      state: 'CO',
      zip: '80202',
      lat: 39.7456983,
      lng: -104.9876237,
    },
    bookingUrl: 'https://calendly.com/jamescatlas/30min',
  },

  // Google Place ID — used to build the canonical Maps URL for schema sameAs.
  placeId: 'ChIJ44xKrdd4bIcRoPqgDjwhPWE',

  hours: {
    weekdays: '5:00 AM – 7:00 PM',
    saturday: '7:30 AM – 4:00 PM',
    sunday: 'Closed',
  },

  social: {
    instagram: '@jamieatlasfitness',
    instagramUrl: 'https://www.instagram.com/jamieatlasfitness/',
  },

  // Authoritative third-party profiles for this business, emitted as schema.org
  // sameAs. Only add profiles that are claimed and carry the canonical NAP —
  // adding an unclaimed or stale listing here reinforces the wrong entity.
  profiles: [
    'https://www.google.com/maps/place/?q=place_id:ChIJ44xKrdd4bIcRoPqgDjwhPWE',
    'https://www.yelp.com/biz/jamie-atlas-denver',
    'https://www.facebook.com/jamieatlas',
  ],

  // Services offered, emitted as schema.org availableService. Every one of the
  // 24 third-party listings found in the Aug 2026 audit categorises this
  // business as a gym; this is the on-site counter-signal.
  services: [
    'Post-surgical return-to-sport rehabilitation',
    'Chronic back pain treatment',
    'Cognitive Functional Therapy',
    'Persistent sciatica rehabilitation',
    'Masters athlete injury rehabilitation',
  ],

  media: [
    { name: '9News', label: 'Featured on 9News' },
    { name: 'Denver Post', label: 'Featured in the Denver Post' },
    { name: 'UPWARD Women', label: 'Featured by UPWARD Women' },
  ],

  // ===========================================================================
  // "AS FEATURED IN" STRIP — homepage, under the hero.
  //
  // Confirmed by Jamie 2026-08-06: he appeared in all six.
  //
  // `file` is optional. Leave it out and the strip renders a styled wordmark,
  // which looks finished on its own. To swap in a real logo:
  //   1. drop the file into  public/
  //   2. set  file: 'logo-9news.svg'  on that entry
  // Nothing else changes. Prefer SVG; a transparent PNG is fine.
  //
  // The strip forces everything to one grey, so low-res files hold up far
  // better here than they would at full colour.
  // ===========================================================================
  // `h` is the on-page height in px on desktop (mobile renders at 85%).
  // It is set PER LOGO on purpose. A single shared height does not work here:
  // FOX31 is a tall stacked box and The Denver Post is a 10:1 wordmark, so the
  // same 32px would leave one unreadably narrow and the other 300px wide. These
  // numbers are tuned so each mark carries roughly equal visual weight.
  //
  // Files live in public/press/. They were trimmed to their artwork and had
  // their background flooded to transparent, so the heights below are real
  // artwork heights, not padded canvas.
  PRESS_OUTLETS: [
    { name: 'FOX31', file: 'press/fox31.png', h: 54 },
    { name: 'Denver7', file: 'press/denver7.png', h: 40 },
    { name: '9NEWS', file: 'press/9news.png', h: 50 },
    { name: '5280', file: 'press/5280.png', h: 34 },
    { name: 'The Denver Post', file: 'press/denverpost.png', h: 17 },
    { name: "Runner's World", file: 'press/runnersworld.png', h: 17 },
  ],

  credentials: [
    { name: 'Cognitive Functional Therapy (CFT)', short: 'CFT' },
    { name: 'NSCA Certified Strength & Conditioning Specialist', short: 'NSCA-CSCS' },
    { name: 'NASM Certified Personal Trainer', short: 'NASM-CPT' },
    { name: 'BSc Neuroscience, University of Western Australia', short: 'BSc Neuroscience' },
  ],
} as const;

export const PRESS = SITE.PRESS_OUTLETS;
