// Central site configuration — change anything here, the whole site updates.
// Phone is Google Voice business line, NOT Jamie's personal cell (720-203-3084).

export const SITE = {
  name: 'Jamie Atlas Rehab & Performance',
  shortName: 'Jamie Atlas',
  tagline: 'Get out of chronic pain. Get back to your sport.',
  description:
    'Cognitive Functional Therapy + 30 years of strength coaching for Denver adults 40+. We work the gap between PT discharge and athletic performance.',
  url: 'https://jamieatlas.com',
  serviceArea: ['Denver', 'Lakewood', 'Aurora', 'Littleton', 'Boulder', 'Englewood', 'Highlands Ranch'],

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

  hours: {
    weekdays: '7:00 AM – 5:00 PM',
    saturday: '9:00 AM – 1:00 PM',
    sunday: 'Closed',
  },

  social: {
    instagram: '@jamieatlasfitness',
    instagramUrl: 'https://www.instagram.com/jamieatlasfitness/',
  },

  media: [
    { name: '9News', label: 'Featured on 9News' },
    { name: 'Denver Post', label: 'Featured in the Denver Post' },
    { name: 'UPWARD Women', label: 'Featured by UPWARD Women' },
  ],

  credentials: [
    { name: 'Cognitive Functional Therapy (CFT)', short: 'CFT' },
    { name: 'NSCA Certified Strength & Conditioning Specialist', short: 'NSCA-CSCS' },
    { name: 'NASM Certified Personal Trainer', short: 'NASM-CPT' },
    { name: 'BSc Neuroscience, University of Western Australia', short: 'BSc Neuroscience' },
  ],
} as const;
