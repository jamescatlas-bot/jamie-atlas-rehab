// The three "click here if this is you" landing pages (Jamie, 2026-08-08).
// One page per homepage door. Voice rules: PAS lead-in, one bolded power line
// in the opening, past tense for failed relief, empathy before explanation,
// bullets somewhere, hedge the obvious, never cure/guaranteed/permanent.
// Paragraphs render with set:html, so <strong>/<ul>/<a> work inside strings.

export interface Segment {
  slug: string;
  doorTitle: string; // matches the homepage door heading
  metaTitle: string;
  metaDescription: string;
  h1: string;
  intro: string[];
  whyUsHeading: string;
  whyUs: string[];
}

export const SEGMENTS: Segment[] = [
  {
    slug: 'cleared-but-not-ready',
    doorTitle: 'Cleared by your PT but still not ready for sport/life',
    metaTitle: 'Discharged From PT But Not Ready to Return? | Jamie Atlas Denver',
    metaDescription:
      "Your PT said you're done. Your body disagrees. The bridge between 'cleared' and 'confident' — one-on-one rebuilding for sport and life in downtown Denver.",
    h1: "Cleared by your PT — but you don't feel ready",
    intro: [
      "The discharge paperwork says you're done. The insurance company agrees. So why does the staircase still make you think first? Why haven't you signed back up for the league, the trail, the class? <strong>The system said you're finished. Your body hasn't signed off. We take your body's side.</strong>",
      "Here's what nobody explained at your last appointment: rehab ended because your visits ran out or your scores hit “functional” — not because you were ready for the life you actually want back. “Functional” meant you could climb stairs and carry groceries. It was never measured against your sport, your job site, your grandkids, your mountains.",
      "The gap you're feeling is real: <ul><li>Cleared for daily life — not for what you love</li><li>Strong in the clinic, hesitant everywhere else</li><li>Exercises you outgrew months ago, with nothing to replace them</li><li>Range of motion that came back without the confidence to use it</li></ul>",
      "That hesitation isn't weakness, and it isn't in your head. It's your nervous system asking for evidence before it lets you go all-in again. Nobody was ever paid to provide that evidence — that's the part of the process the system leaves out.",
    ],
    whyUsHeading: 'The rebuild nobody was paid to give you',
    whyUs: [
      "This is the specialty of the studio: the ground between “medically cleared” and “genuinely ready.” We start from your full story — the injury, the surgery if there was one, the rehab you already did, and the goals nobody asked you about. Then we load you, step by step, until your body has proof it can trust itself again. Not pushed past what it accepts — shown what it can do.",
      "Every session is one-on-one with Jamie Atlas, Pain &amp; Performance Specialist — 45–60 minutes at a private downtown Denver studio. Your rehabilitation, your training and your at-home plan are all built by the same person, so nothing gets lost in a handoff.",
      "And if your case isn't a fit, we'll tell you plainly and point you to the right person who can help. No pressure either way.",
    ],
  },
  {
    slug: 'still-in-pain',
    doorTitle: "You've tried everything and you're still in pain",
    metaTitle: 'Still in Pain After PT, Chiro & Injections? | Jamie Atlas Denver',
    metaDescription:
      "You did the PT, the adjustments, the injections — and the pain came back. What most treatment misses, and a different way forward. Downtown Denver.",
    h1: "You've tried everything — and you're still in pain",
    intro: [
      "The physical therapy ran its course. The adjustments felt good for a day, maybe two. The injection bought a few quiet months, and then it didn't. You did everything you were told to do — and you're still hurting. <strong>You are not broken, and you are not out of options. You were given the wrong map.</strong>",
      "Here's the part nobody sat you down and explained: when pain has been around long enough, the sore spot stops being the whole story. Your nervous system learns the pain. It starts protecting you before you even move. Treatment after treatment was aimed at the tissue — while the alarm system itself was what needed retraining. That's probably why the relief never lasted.",
      "If your history looks like this, you're in the right place: <ul><li>PT exercises that helped a little, then plateaued</li><li>Adjustments that never held</li><li>Injections that wore off</li><li>Massage that felt wonderful until Tuesday</li><li>Rest that made you weaker, not better</li><li>A scan, a scary word on it, and no plan</li></ul>",
      "None of that failing you was your fault. Every one of those treatments has its place — they just weren't built for what your pain has become.",
    ],
    whyUsHeading: "Why people who've been everywhere end up here",
    whyUs: [
      "This studio is built for exactly one kind of person: someone whose pain outlasted the system. The results we get come from Cognitive Functional Therapy combined with a method known as Applied Functional Science — a system that identifies when the symptom and the cause of the pain are in different places, and how to use the whole body to create a different outcome than traditional methods. We start by finding the movements you can already do free of pain, and build outward from there. Not by pushing through. Through what your body will actually accept.",
      "Every session is one-on-one with Jamie Atlas, Pain &amp; Performance Specialist — 45–60 minutes at a private downtown Denver studio. No aides, no shared appointments, no printed sheet of exercises.",
      "And if we can't help you, we'll say so — and point you to the right person who can.",
    ],
  },
  {
    slug: 'worried-about-reinjury',
    doorTitle: "You want to work out but you're worried about reinjuring your body",
    metaTitle: 'Train Without Reinjury — One-on-One in Denver | Jamie Atlas',
    metaDescription:
      'You want to work out but the last injury is still in the room. Performance training with rehab expertise as the safety net — one-on-one in downtown Denver.',
    h1: 'You want to train — without getting hurt again',
    intro: [
      "You're not fragile, and you're not unmotivated. You're careful — because you've been burned. Every workout since the injury has had a second voice in it: <em>watch the back, don't trust the knee, maybe not so heavy.</em> <strong>It's not your job to know which exercises your body is ready for. It's mine.</strong>",
      "Most training programs were written for bodies with no history. Yours has one. Push blindly and you flared it up; protect it forever and it got weaker — and the rest of you followed. The middle path — loading your body enough to build it without waking the old injury — is a genuine skill, and it's one most gyms never had to learn.",
      "You might recognize the loop: <ul><li>Start a program, feel great for three weeks</li><li>One wrong session, and the old pain flickers</li><li>Back off completely — lose the progress</li><li>Start again, a little more discouraged each time</li></ul>",
      "That loop was never a discipline problem. It's a programming problem — and it ends when someone who understands both training and pain writes the plan.",
    ],
    whyUsHeading: 'Training with a safety net',
    whyUs: [
      "This is not a gym. It's a specialty rehabilitation and sports performance studio — which means the person writing your training plan carries twenty years of coaching plus the pain science most trainers were never taught. Your program is built around your body's history, present and future goals, and it adjusts the moment your body says something.",
      "Every session is one-on-one with Jamie Atlas, Pain &amp; Performance Specialist — 45–60 minutes at a private downtown Denver studio. Your training, rehabilitation and at-home plans all come from the same brain, so nothing contradicts and nothing slips through.",
      "And if what you need isn't what we do, we'll tell you straight and recommend the right person. No pressure either way.",
    ],
  },
];
