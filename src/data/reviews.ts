// Verbatim Google reviews (5.0★, 11 reviews as of 2026-07-09).
// Source: doc 21. Mary Jo's and Kelli's quotes are truncated on the listing
// view — swap in full text once pulled from each review's "More" link.

export const GOOGLE_RATING = { stars: 5.0, count: 11 };

export const REVIEWS_URL = 'https://g.page/r/CaD6oA48IT1hEBM';
export const WRITE_REVIEW_URL = 'https://g.page/r/CaD6oA48IT1hEBM/review';

export interface Review {
  name: string;
  text: string;
}

// Only the 3 most recent reviews are shown (per Jamie, 2026-07-09).
// Verified against the live listing: Mary Jo Brooks (1 mo), Colley Moe (1 mo),
// Alia Nicholson (2 mo). Kelli Gould is also ~2 mo but her text is truncated
// on the listing view, so Alia holds the third slot.
export const REVIEWS: Review[] = [
  {
    name: 'Mary Jo Brooks',
    text: 'I went to him for knee pain because of a torn meniscus and arthritis. One doctor told me I needed surgery... A month after I started working with Jamie, my knee improved.',
  },
  {
    name: 'Colley Moe',
    text: 'Jamie really helped my chronic neck pain and provided ways I could ease the movement at home. My ankles continue to strengthen with his routine and guidance as well. Thanks for getting me back on the court Jamie!',
  },
  {
    name: 'Alia Nicholson',
    text: "Jamie is amazing to work with. He is so patient and responsive! He helped my daughter with back pain and a very unique rehab. He has a gift for this work and we couldn't be more grateful for his time and expertise helping her navigate her pain and rehab!! Five stars all the way. Thank you Jamie!",
  },
];

// Intro offer (doc 21): one price, three doors. Label rotates seasonally.
export const OFFER = {
  regularPrice: '$97',
  specialPrice: '$57',
  specialLabel: 'Summer Special',
  assessments: [
    {
      name: 'Return-to-Sport Assessment',
      body: 'Insurance PT discharged you, but "cleared" isn\'t the same as confident. For skiers, lifters, cyclists and runners who want to get back to their sport — we find what\'s missing between rehab and performance, and map the rebuild.',
    },
    {
      name: 'Pain & Performance Assessment',
      body: 'Chronic back, neck, hip or knee pain that hasn\'t responded to what you\'ve tried. An assessment based on Cognitive Functional Therapy and Applied Functional Science — how you actually move, load and guard — and a plan that isn\'t just more stretching.',
    },
    {
      name: 'Comeback Assessment',
      body: 'An injury, a surgery, or a long layoff knocked you off track and it\'s been easier to stay off it. We assess where your body really is today and build the road back to the life you want to be living.',
    },
  ],
};
