// The five core condition pages under /what-we-treat/.
// Each page follows the format: H1 as outcome, H2s as questions, FAQ, CTA.

export interface ConditionSection {
  heading: string;
  paragraphs: string[];
}

export interface Condition {
  slug: string;
  title: string; // H1 — outcome-focused
  navTitle: string; // short title for cards/nav
  metaTitle: string;
  metaDescription: string;
  /** schema.org type for the page's `about` entity. Defaults to MedicalCondition. */
  schemaType?: 'MedicalCondition' | 'MedicalTherapy' | 'MedicalProcedure';
  intro: string;
  sections: ConditionSection[];
  faq: { q: string; a: string }[];
}

export const CONDITIONS: Condition[] = [
  {
    slug: 'post-surgical-return-to-sport',
    navTitle: 'Post-Surgical Return-to-Sport',
    title: 'Finish the rehab your insurance didn’t pay for',
    metaTitle: 'Post-Surgical Return-to-Sport Training in Denver',
    schemaType: 'MedicalProcedure',
    metaDescription:
      'Insurance PT got you to "functional." We get you back to skiing, cycling, lifting, and running. Post-surgical return-to-sport rehabilitation in Denver.',
    intro:
      'Your surgery worked. Your twelve sessions of physical therapy got you walking, climbing stairs, "functional." Then you were discharged — and you’re still nowhere near the bike, the slopes, or the barbell. That gap between "cleared" and "back" is exactly where this work lives.',
    sections: [
      {
        heading: 'Why does insurance PT stop before you’re actually back?',
        paragraphs: [
          'Insurance-based physical therapy is built to restore basic function — walking, dressing, working. Once you hit those milestones, coverage ends, regardless of whether your goal was a 5k or a century ride. The 6–9 months of progressive loading between "functional" and "athletic" is not something the system pays for, so almost nobody provides it.',
          'That’s the rebuild I do. One-on-one, 60–90 minute sessions that pick up where your PT discharge left off and end at your sport — with objective return-to-sport benchmarks, not guesswork.',
        ],
      },
      {
        heading: 'Why are you still afraid to load the joint?',
        paragraphs: [
          'After surgery, your nervous system becomes protective. Even when the tissue has healed, the brain often keeps guarding — which shows up as stiffness, weakness that doesn’t match the scan, and fear of the exact movement that injured you.',
          'Graded exposure done right fixes this: we find the edge of what feels safe, load it, prove to your nervous system that you’re strong there, then move the edge. It’s systematic, measurable, and it’s the part most rehab skips.',
        ],
      },
      {
        heading: 'What does the process look like?',
        paragraphs: [
          'First visit: full movement assessment, history, and a frank conversation about your sport and your timeline. You leave with a plan and a realistic number of sessions.',
          'Then: progressive strength work built around your surgery, your sport, and your schedule — typically one session a week with independent work between. We track load, range, and confidence until you pass sport-specific benchmarks, then you graduate.',
        ],
      },
    ],
    faq: [
      {
        q: 'How soon after surgery can I start?',
        a: 'Most people come to me after insurance PT ends — usually 2–6 months post-op. If you’re earlier than that, I’ll coordinate with your surgeon’s protocol.',
      },
      {
        q: 'Do you replace my physical therapist?',
        a: 'No — I start where PT discharge ends. If you still have coverage, use it. When it runs out and you’re not back to your sport, that’s when this work makes sense.',
      },
      {
        q: 'How many sessions does it take?',
        a: 'Typically 6–8 sessions spread over 2–4 months, depending on the surgery and the sport. You’ll get an honest estimate at the first visit — not an open-ended commitment.',
      },
    ],
  },
  {
    slug: 'chronic-back-pain',
    navTitle: 'Chronic Back Pain',
    title: 'Chronic back pain isn’t a life sentence',
    metaTitle: 'Chronic Back Pain Treatment in Denver — Cognitive Functional Therapy',
    metaDescription:
      'Cognitive Functional Therapy for chronic low back pain in Denver — the approach validated in the 2023 Lancet RESTORE trial. When PT, chiropractic, and injections haven’t worked.',
    intro:
      'You’ve done physical therapy. You’ve been adjusted. Maybe you’ve had injections, or an MRI that "showed something" but didn’t explain why you still hurt. If your back pain has lasted more than three months and keeps coming back, the problem usually isn’t the tissue anymore — it’s a pain system stuck in protection mode. That is treatable.',
    sections: [
      {
        heading: 'Why hasn’t anything worked so far?',
        paragraphs: [
          'Most back pain treatment targets tissue: massage it, adjust it, inject it, strengthen the "core." But in persistent pain, research consistently shows the driver is a sensitized nervous system — shaped by guarding habits, fear of bending and lifting, poor sleep, stress, and unhelpful beliefs about a "damaged" spine.',
          'Treatments that ignore that system produce short-lived relief. That’s why the pain keeps coming back the moment you do what you actually love.',
        ],
      },
      {
        heading: 'What is Cognitive Functional Therapy?',
        paragraphs: [
          'Cognitive Functional Therapy (CFT) is a structured, evidence-based approach that retrains both the beliefs and the movement patterns that keep back pain going. In the 2023 RESTORE trial published in The Lancet, CFT produced large, sustained improvements in pain and disability compared with usual care — results that held at the three-year follow-up.',
          'In practice it looks like this: we make sense of your pain story together, then systematically rebuild the movements you’ve been avoiding — bending, lifting, sitting, whatever your triggers are — in a graded way that proves to your nervous system it’s safe. Then we make you strong there, so the change lasts.',
        ],
      },
      {
        heading: 'What about my MRI findings?',
        paragraphs: [
          'Disc bulges, degeneration, and arthritis show up on scans of people with no pain at all — at rates that rise with age, like grey hair. Imaging findings matter in a small number of cases (and I screen for those), but for most persistent back pain they don’t explain the pain and they don’t predict recovery.',
          'You are not your MRI. The plan is built around what your body can do and relearn — not around a picture.',
        ],
      },
    ],
    faq: [
      {
        q: 'How is this different from physical therapy?',
        a: 'Sessions are 60–90 minutes one-on-one (not a rushed insurance slot), the approach targets the pain system rather than just the tissue, and the endpoint is your sport and your life — not discharge paperwork.',
      },
      {
        q: 'Is it safe to move if it hurts?',
        a: 'Hurt and harm are not the same thing in persistent pain. Part of the first sessions is showing you — in real time — how much your pain can change with strategy, which is usually the moment people stop being afraid of it.',
      },
      {
        q: 'How many sessions will I need?',
        a: 'Most clients need 6–8 sessions. Chronic, complex cases can take longer, and I’ll tell you honestly which one you are after the first assessment.',
      },
    ],
  },
  {
    slug: 'sciatica',
    navTitle: 'Persistent Sciatica',
    title: 'Sciatica that hasn’t responded to the usual treatments',
    metaTitle: 'Persistent Sciatica Treatment in Denver',
    metaDescription:
      'Radicular leg pain that didn’t respond to chiropractic, epidurals, or short-course PT. A nervous-system-informed approach to persistent sciatica in Denver.',
    intro:
      'Leg pain that burns, shoots, or tingles below the knee. You’ve stretched the piriformis, been adjusted, maybe had an epidural. It helped for a while — or not at all. Persistent sciatica has a nervous-system component that most treatment plans never address, and that’s usually the missing piece.',
    sections: [
      {
        heading: 'Why does sciatica persist after the disc has healed?',
        paragraphs: [
          'Most disc-related nerve irritation settles within weeks to months. When leg pain persists beyond that, the nerve itself has often become sensitized — it fires with less provocation, and normal movement gets flagged as a threat. Rest and avoidance make sensitized nerves worse, not better.',
          'The way out is graded, progressive loading of the nerve and the movements you’ve been avoiding — dosed carefully enough that the system calms down instead of flaring up.',
        ],
      },
      {
        heading: 'What does treatment involve?',
        paragraphs: [
          'First, a proper assessment to rule out the small set of cases that need medical referral — progressive weakness, numbness in the saddle area, bladder or bowel changes. Those go to a physician first, and I’ll tell you plainly if that’s you.',
          'For everyone else: a plan that combines nerve-tolerant movement, progressive strength work for the hip and trunk, sleep and stress factors that amplify nerve pain, and a graded return to walking, hiking, running, or riding — whatever the pain took from you.',
        ],
      },
    ],
    faq: [
      {
        q: 'Should I get an MRI first?',
        a: 'Not necessarily. Unless you have red-flag symptoms or surgery is on the table, imaging rarely changes the plan for persistent sciatica — and scary-sounding findings often make fear (and pain) worse.',
      },
      {
        q: 'Is walking good or bad for sciatica?',
        a: 'Usually good — in the right dose. The skill is finding your current tolerance and building from it systematically instead of the boom-bust cycle of overdoing it on good days.',
      },
      {
        q: 'What if I’ve already had surgery?',
        a: 'Post-surgical sciatica responds to the same graded approach. If you’re past the surgical healing window and still have leg symptoms, this is exactly the kind of case I work with.',
      },
    ],
  },
  {
    slug: 'masters-athlete-injuries',
    navTitle: 'Masters Athlete Injuries',
    title: 'Stay in your sport for the next twenty years',
    metaTitle: 'Masters Athlete Injury Rehab in Denver (40+)',
    metaDescription:
      'Recurring injuries for athletes 40+: tendinopathy, joint pain, the boom-bust cycle. Break the pattern and keep training. Masters athlete rehab in Denver.',
    intro:
      'You’re 45, or 55, or 65, and you have no intention of stopping. But the calf keeps going. The shoulder flares every ski season. The knee swells after long rides. You’re stuck in a cycle: train, break, rest, repeat — and each cycle costs you more fitness than the last. The cycle is breakable.',
    sections: [
      {
        heading: 'Why do the same injuries keep coming back?',
        paragraphs: [
          'Recurring injuries in masters athletes almost always come down to a capacity gap: the demands of your sport exceed what the tissue is currently prepared for, usually because rest — the standard prescription — heals the pain but shrinks the capacity. You return to sport weaker than you left, and the cycle repeats.',
          'The fix is unfashionable and effective: progressive strength work that raises the tissue’s capacity above your sport’s demands, programmed around your training so you don’t have to stop doing what you love while we fix it.',
        ],
      },
      {
        heading: 'Do you have to train less as you age?',
        paragraphs: [
          'You have to train smarter, recover more deliberately, and strength train — the evidence on that is unambiguous. Masters athletes who lift stay in sport longer, get injured less, and perform better. What you don’t have to do is accept "you’re just getting older" as a diagnosis. It isn’t one.',
        ],
      },
      {
        heading: 'What does working together look like?',
        paragraphs: [
          'We assess the injury, the sport, and the training history — then build a plan that treats the current flare and closes the capacity gap that caused it. You keep training throughout, with modifications, because detraining is the enemy.',
          'Most masters athletes work with me for 6–8 sessions, then keep a periodic check-in cadence through their season.',
        ],
      },
    ],
    faq: [
      {
        q: 'I’ve been told I have arthritis / bone-on-bone. Is it over?',
        a: 'No. Joint changes on imaging correlate poorly with pain and function, and strength work reliably improves both — even in significant osteoarthritis. "Bone-on-bone" is a description, not a verdict.',
      },
      {
        q: 'Can I keep running / riding / skiing during rehab?',
        a: 'Almost always yes, in a modified dose. Total rest is rarely the answer, and keeping you in your sport is an explicit goal of the plan.',
      },
      {
        q: 'Is this personal training?',
        a: 'It’s rehabilitation that ends in performance. The strength work looks like training because it is — but it’s sequenced around an injury, a pain system, and return-to-sport benchmarks.',
      },
    ],
  },
  {
    slug: 'cognitive-functional-therapy',
    navTitle: 'Cognitive Functional Therapy',
    title: 'The evidence-based approach most providers don’t know',
    metaTitle: 'Cognitive Functional Therapy (CFT) in Denver',
    schemaType: 'MedicalTherapy',
    metaDescription:
      'What Cognitive Functional Therapy is, the Lancet RESTORE evidence behind it, and how CFT works in practice. One of a handful of practitioners in Colorado.',
    intro:
      'Cognitive Functional Therapy (CFT) is a structured approach to persistent pain that treats the whole system — the beliefs, the guarding, the avoided movements, the sleep and stress that turn pain up — instead of chasing tissue that healed long ago. It’s the approach validated in the 2023 Lancet RESTORE trial, and I’m one of a handful of practitioners in Colorado trained in it.',
    sections: [
      {
        heading: 'What’s the evidence?',
        paragraphs: [
          'The RESTORE trial, published in The Lancet in 2023, randomized nearly 500 people with chronic low back pain to CFT or usual care. CFT produced large, clinically significant improvements in pain and disability — sustained at 12 months, and still holding at the three-year follow-up published in 2025. Effect sizes of that durability are rare in chronic pain research.',
        ],
      },
      {
        heading: 'How is CFT different from regular physical therapy?',
        paragraphs: [
          'Three ways. First, it starts with your story — a detailed history that makes sense of why your pain system became protective, because pain that makes sense is pain you can change. Second, it uses graded behavioral experiments: we test the movements you’ve been told (or told yourself) are dangerous, and you experience the pain changing in real time. Third, it addresses the lifestyle amplifiers — sleep, stress, activity patterns — that keep the system sensitized.',
          'Then I add the part most CFT practitioners can’t: thirty years of strength coaching to rebuild real capacity once the pain system calms down. Desensitization without strength is temporary. Strength without desensitization never starts.',
        ],
      },
      {
        heading: 'Who is CFT for?',
        paragraphs: [
          'Anyone whose pain has persisted past normal healing time — typically three months or more — and hasn’t responded to tissue-focused treatment. Back pain is the best-studied application, but the principles apply to persistent pain generally: necks, shoulders, knees, post-surgical pain, and the fear of movement that follows all of them.',
        ],
      },
    ],
    faq: [
      {
        q: 'Is CFT "it’s all in your head"?',
        a: 'No. Your pain is real and physical. CFT is grounded in the neuroscience of how real pain is produced and amplified — and how it can be turned down. Nothing about it dismisses what you feel.',
      },
      {
        q: 'How many CFT sessions does it take?',
        a: 'The RESTORE protocol used about seven sessions over twelve weeks. My clients typically land in the same range: 6–8 sessions, then independence.',
      },
      {
        q: 'Do I need a referral?',
        a: 'No referral needed. Book a consultation directly — the first conversation establishes whether you’re a fit before you commit to anything.',
      },
    ],
  },
];
