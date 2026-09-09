// Verbatim Google reviews (5.0 stars, 20 reviews as of 2026-09-09).

export const GOOGLE_RATING = { stars: 5.0, count: 20 };

export const REVIEWS_URL = 'https://g.page/r/CaD6oA48IT1hEBM';
export const WRITE_REVIEW_URL = 'https://g.page/r/CaD6oA48IT1hEBM/review';

export interface Review {
  name: string;
  text: string;
}

// The three most recent reviews (Jamie sent the links 9 Sep 2026; pulled
// verbatim from Google Maps). Order matches the homepage doors: return to
// sport, hurt then training, strength over 60. Marcus's last sentence is cut
// (it misspells the name); Adrienne and Susan run in full, per Jamie.
export const REVIEWS: Review[] = [
  {
    name: 'Marcus Kret',
    text: 'I met Jamie when I had maximized my physical therapy program after ACL and medial meniscus reconstruction. It was the perfect transition for a "back to sport" program. We worked a ton on functional strength and stability. Thanks to Jamie\'s guidance, I was able to ski 50 days in my return to skiing, 55 the following year, and 61 days in \'25–\'26. In addition to the results, I saw, Jamie had a good evidence based approach which really spoke to me as I am a medical doctor myself.',
  },
  {
    name: 'Adrienne Rule',
    text: 'I found Jamie through a recommendation from a coworker after hurting my back after a strenuous backpacking trip and lucky for me we work in the same building! Since being rehabilitated from my back pain, I continue to see Jamie ongoing for regular workouts (since he\'s the only person i would trust to work me hard but not put me are risk of reinjury) and probably will forever. At Jamie\'s studio I get a caring, results focused top-tier personal trainer experience paired with the clinical precision of a physical therapist. Why would I go anywhere else?',
  },
  {
    name: 'Susan Keicher',
    text: 'Jamie has been my trainer for 3 1/2 years. I came to him as a 60 something woman who had never been on a workout routine. He has transformed me into a lean, mean work out machine. I am in the best shape of my life. He excels in targeted therapies. If your hip is giving you pain, he has specific exercises to relieve the pain. Joint or spine issues, he has a solution. My workouts address weight training for strength, balance, stretching and Pilates. He excels in creating individual work outs that give results. I highly recommend him as a trainer if you need rehabilitation or just need to get into shape.',
  },
];

// Intro offer (doc 21): one price, three doors. Label rotates seasonally.
export const OFFER = {
  regularPrice: '$97',
  specialPrice: '$57',
  specialLabel: 'first-visit price',
  assessments: [
    {
      name: 'Return-to-Sport Assessment',
      body: 'Insurance PT discharged you, but "cleared" isn\'t the same as confident. For skiers, lifters, cyclists and runners who want to get back to their sport — we find what\'s missing between rehab and performance, and map the rebuild.',
    },
    {
      name: 'Pain and Performance Assessment',
      body: 'Chronic back, neck, hip or knee pain that hasn\'t responded to what you\'ve tried. An assessment based on Cognitive Functional Therapy and Applied Functional Science — how you actually move, load and guard — and a plan that isn\'t just more stretching.',
    },
    {
      name: 'Comeback Assessment',
      body: 'An injury, a surgery, or a long layoff knocked you off track and it\'s been easier to stay off it. We assess where your body really is today and build the road back to the life you want to be living.',
    },
  ],
};
