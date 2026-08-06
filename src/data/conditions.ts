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
  /** Slugs of related conditions, rendered as internal links at the foot of the page. */
  related: string[];
  /**
   * The bridge between the two buyers. Someone arrives in pain; once the pain
   * settles, a good proportion of them want to get back to a sport. This makes
   * that path explicit instead of leaving them to find it.
   * Only set on the four body-part pages.
   */
  nextStep?: {
    heading: string;
    body: string;
    links: { label: string; slug: string }[];
  };
}

export const CONDITIONS: Condition[] = [
  {
    slug: 'post-surgical-return-to-sport',
    navTitle: 'Post-Surgical Return-to-Sport',
    title: 'Finish the rehab your insurance didn’t pay for',
    metaTitle: 'Post-Surgical Return-to-Sport Rehab, Denver',
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
    related: ['masters-athlete-injuries', 'cognitive-functional-therapy'],
  },
  {
    slug: 'chronic-back-pain',
    navTitle: 'Chronic Back Pain',
    title: 'Chronic back pain isn’t a life sentence',
    metaTitle: 'Chronic Back Pain Treatment in Denver',
    metaDescription:
      'Cognitive Functional Therapy for chronic low back pain in Denver — validated in the 2023 Lancet RESTORE trial. For when PT and injections haven’t worked.',
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
          'Disc bulges, degeneration, and arthritis show up on scans of people with no pain at all — at rates that rise with age, like gray hair. Imaging findings matter in a small number of cases (and I screen for those), but for most persistent back pain they don’t explain the pain and they don’t predict recovery.',
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
    related: ['cognitive-functional-therapy', 'sciatica'],
    nextStep: {
      heading: 'Once the pain settles, what then?',
      body:
        "Getting out of pain is the first half. Most people then discover the thing they actually wanted was to get back to something — the bike, the trail, the barbell, a full day on their feet without bracing for it. That rebuild is a different piece of work, and it's the part I've spent thirty years on.",
      links: [
        { label: 'Post-surgical return-to-sport', slug: '/what-we-treat/post-surgical-return-to-sport' },
        { label: 'Masters athlete injuries (40+)', slug: '/what-we-treat/masters-athlete-injuries' },
      ],
    },
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
    related: ['chronic-back-pain', 'cognitive-functional-therapy'],
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
    related: ['post-surgical-return-to-sport', 'chronic-back-pain'],
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
    related: ['chronic-back-pain', 'sciatica'],
  },
  {
    slug: 'neck-pain',
    navTitle: 'Persistent Neck Pain',
    title: 'Neck pain that keeps coming back',
    metaTitle: 'Neck Pain Treatment in Denver',
    metaDescription:
      'Persistent neck pain, stiffness and headaches that returned after massage, adjustments or short-course PT. A nervous-system-informed approach in Denver.',
    intro:
      "You're in pain, and somewhere along the way you stopped expecting anyone to fix it. Not for lack of trying — the massage, the adjustments, the scan, somebody's theory about your posture. <strong>We get it.</strong> That's exactly who this studio was built for: the people who kept looking after everything else came up short.",
    sections: [
      {
        heading: 'Why has the relief never lasted?',
        paragraphs: [
          "The maddening part was never the pain itself. It was Tuesday's relief being gone by Thursday. <strong>You don't need more relief — you need to stop needing it.</strong>",
          "Massage, adjustment, dry needling, a new pillow. All of them are good at turning the volume down, and all of them aim at the spot that hurts. That is the symptom. It isn't what keeps producing it.",
          "A neck that keeps flaring is almost never one angry muscle waiting to be switched on or dialed down. It's a web, and your neck is one strand of it:" +
            '<ul>' +
            '<li>how much load your neck and shoulders can genuinely handle</li>' +
            '<li>how long you hold a position before anything moves</li>' +
            '<li>sleep, stress, and the weeks when both are bad at once</li>' +
            '<li>the movements you quietly stopped making months ago</li>' +
            "<li>what you believe is going on in there</li>" +
            '</ul>',
          "<strong>Pull on one strand and the web hands the pain straight back.</strong> That's not a failure of the treatments you tried. It's what happens when a single thread gets treated in isolation.",
        ],
      },
      {
        heading: 'Is it my posture?',
        paragraphs: [
          "You've been told to sit up straight more times than you can count. You've tried it. It didn't hold. <strong>That isn't a discipline problem.</strong>",
          "It's probably not your posture alone. The link between how you sit and how your neck feels is far weaker than you've been told, and plenty of people with textbook-bad posture have no pain at all.",
          "What a neck objects to is staying in one position, not the position itself — and even that is only one strand. A neck with real strength behind it handles a long day at a desk. That part is trainable.",
        ],
      },
      {
        heading: 'My scan showed degeneration.',
        paragraphs: [
          'Almost everyone your age has it, including people with no pain at all. It shows up on a scan the way gray hair shows up in a mirror.',
          "Finding it doesn't tell us it's causing your pain, and it doesn't predict how well you'll do. If yours is one of the few presentations that needs a physician first, I'll tell you plainly.",
        ],
      },
      {
        heading: 'What actually happens here?',
        paragraphs: [
          "First session, we work out what your neck responds to — what sets it off, what settles it, what you've stopped doing. Then we give those things back, alongside real strength work for the neck, upper back and shoulders.",
          "<strong>We work the whole web, not the sore spot.</strong> Most people feel something shift in that first hour. That's the start, not the finish — holding onto it usually takes six to eight sessions.",
        ],
      },
    ],
    faq: [
      {
        q: 'Do you crack or adjust necks?',
        a: 'No. Manipulation can feel good briefly, but it does not build the capacity that stops the pain returning. Everything here is active — movement, graded exposure and progressive strength work you can eventually do without me.',
      },
      {
        q: 'My neck pain comes with headaches. Can that be helped?',
        a: 'Often, yes. Headaches that originate from the neck usually improve as the neck desensitizes and gets stronger. I will also flag it if your headache pattern looks like something that needs a physician instead.',
      },
      {
        q: 'How many sessions will I need?',
        a: 'Most people land in the six to eight range. You will get an honest estimate after the first assessment, not an open-ended commitment.',
      },
    ],
    related: ['cognitive-functional-therapy', 'shoulder-pain'],
    nextStep: {
      heading: 'Once the pain settles, what then?',
      body:
        "A neck that no longer hurts at rest is not the same as a neck that tolerates a long ride, an overhead session, or a full week at a desk. Building that tolerance is the second half of the job.",
      links: [
        { label: 'Masters athlete injuries (40+)', slug: '/what-we-treat/masters-athlete-injuries' },
        { label: 'Post-surgical return-to-sport', slug: '/what-we-treat/post-surgical-return-to-sport' },
      ],
    },
  },
  {
    slug: 'shoulder-pain',
    navTitle: 'Shoulder Pain',
    title: 'A shoulder that rest hasn’t fixed',
    metaTitle: 'Shoulder Pain Treatment in Denver',
    metaDescription:
      'Rotator cuff pain, impingement and stiff shoulders that did not settle with rest or a cortisone shot. Graded loading and strength work in Denver.',
    intro:
      'You cannot sleep on that side. Reaching overhead has become something you plan around. You have rested it, maybe had a cortisone shot, and it was better right up until you tried to use it properly again. Shoulders rarely recover from rest alone — they recover from being loaded well.',
    sections: [
      {
        heading: 'Why hasn’t rest worked?',
        paragraphs: [
          'Rest calms an irritated shoulder down, and it also lets the tissue lose capacity. When you return to what you were doing, the demand is unchanged but your tolerance is lower than when you stopped — so it flares, and the obvious conclusion is that you need more rest. That loop is where most people are stuck by the time they reach me.',
          'The way out is loading the shoulder in a dose it can currently handle, then raising that dose steadily until it exceeds what your sport or your job asks of it.',
        ],
      },
      {
        heading: 'What about my rotator cuff tear?',
        paragraphs: [
          'Rotator cuff tears are found on scans of large numbers of people with no shoulder pain at all, and the rate climbs with age. A tear on a report does not, by itself, explain your symptoms or mean you need surgery.',
          'Substantial evidence now supports progressive loading as a first-line approach for most degenerative cuff problems, with outcomes comparable to surgery in many cases. Some shoulders do need a surgeon — traumatic full-thickness tears and genuine loss of function among them — and I will tell you straight if yours is one of them.',
        ],
      },
      {
        heading: 'Is it impingement?',
        paragraphs: [
          'That label has fallen out of favor for good reason. The idea that a bony spur is mechanically pinching a tendon has not held up well, and decompression surgery has performed poorly against placebo in controlled trials.',
          'What tends to be true instead: an irritable tendon, a shoulder that has lost strength through range, and a movement pattern built around protecting it. All three respond to the same thing — progressive, well-dosed loading.',
        ],
      },
      {
        heading: 'What does the work look like?',
        paragraphs: [
          'An assessment of what the shoulder can currently tolerate, then a programme that starts just inside that boundary and moves it. Alongside that, we address the sleep disruption and the guarding that come with any long-running shoulder problem.',
          'You keep using the arm throughout, with modifications. Total rest is almost never the answer.',
        ],
      },
    ],
    faq: [
      {
        q: 'Should I get a cortisone injection?',
        a: 'It can be a useful window — pain down far enough to start loading properly. As a standalone treatment it tends to disappoint, because it does not change the capacity problem underneath. That is a conversation for you and your physician; I will work with whatever you decide.',
      },
      {
        q: 'Can I keep lifting or swimming?',
        a: 'Usually yes, in a modified dose. Keeping you in your sport while we fix the shoulder is an explicit goal, not an afterthought.',
      },
      {
        q: 'How long does a shoulder take?',
        a: 'Shoulders are typically slower than backs — tendons adapt at their own pace. Expect six to eight sessions with meaningful independent work between them, and an honest estimate after the first assessment.',
      },
    ],
    related: ['cognitive-functional-therapy', 'neck-pain'],
    nextStep: {
      heading: 'Once the pain settles, what then?',
      body:
        "Shoulders are where the gap between 'not painful' and 'actually reliable' is widest. Pressing, swimming, throwing and carrying all ask for capacity you don't get back by simply becoming pain-free — you get it back by building it.",
      links: [
        { label: 'Masters athlete injuries (40+)', slug: '/what-we-treat/masters-athlete-injuries' },
        { label: 'Post-surgical return-to-sport', slug: '/what-we-treat/post-surgical-return-to-sport' },
      ],
    },
  },
  {
    slug: 'knee-pain',
    navTitle: 'Knee Pain',
    title: 'A knee that hasn’t settled with rest',
    metaTitle: 'Knee Pain Treatment in Denver',
    metaDescription:
      'Knee pain, arthritis and meniscus problems that did not settle with rest or an injection. Progressive strength work for Denver adults who want to keep moving.',
    intro:
      'Stairs. Getting out of the car. The first mile of a hike, or the last one. You have rested it, iced it, maybe had an injection or a scan that used the word "degenerative" — and it is still there. Knees very rarely recover from being protected. They recover from being loaded properly.',
    sections: [
      {
        heading: 'Why hasn’t resting it worked?',
        paragraphs: [
          'Rest settles an irritated knee, and at the same time the muscles around it get weaker and the joint loses tolerance. When you go back to what you were doing, the demand has not changed but your capacity is lower than when you stopped. It flares. The obvious conclusion is that you need more rest, and the loop tightens.',
          'What breaks it is loading the knee at a dose it can currently handle and then raising that dose deliberately, until it comfortably exceeds what your day and your sport ask of it.',
        ],
      },
      {
        heading: 'I’ve been told it’s arthritis — or “bone on bone”',
        paragraphs: [
          'Joint changes on imaging correlate poorly with how much pain someone has and how well they function. Plenty of people with significant radiographic osteoarthritis have little or no pain, and plenty with mild changes hurt a lot.',
          'More usefully: exercise therapy is a first-line treatment for knee osteoarthritis in essentially every major clinical guideline, and it reliably improves both pain and function. "Bone on bone" is a description of an X-ray. It is not a prognosis, and it is not a reason to stop loading the leg.',
        ],
      },
      {
        heading: 'What about a meniscus tear? Do I need surgery?',
        paragraphs: [
          'For degenerative meniscal tears — the kind that show up gradually in middle age rather than from a specific traumatic twist — several high-quality randomised trials have found arthroscopic surgery produces outcomes no better than structured exercise therapy. Many people improve substantially without an operation.',
          'Traumatic tears, locking knees, and genuine mechanical block are a different category and belong with a surgeon. Part of the first session is working out which one you are, and I will say so plainly if you need a referral rather than me.',
        ],
      },
      {
        heading: 'What does the work look like?',
        paragraphs: [
          'An honest assessment of what the knee currently tolerates, then progressive strength work for the quads, hips and calves — the structures that decide how much load actually reaches the joint. Alongside that, a graded return to whatever the pain has taken from you: stairs, hiking, running, skiing.',
          'You keep moving throughout, with modifications. Most people work with me for six to eight sessions and then continue independently.',
        ],
      },
    ],
    faq: [
      {
        q: 'Will running or squatting wear my knees out faster?',
        a: 'No. The evidence points the other way — recreational runners have lower rates of knee osteoarthritis than sedentary people, and loaded movement is how cartilage and bone stay healthy. What causes trouble is doing too much too soon, not the movement itself.',
      },
      {
        q: 'I’m scheduled for a knee replacement. Is there any point?',
        a: 'Yes, on both sides of it. Going into surgery stronger is one of the better predictors of how the recovery goes, and the work afterwards is where the outcome is actually decided. I do a lot of the second kind.',
      },
      {
        q: 'How many sessions will I need?',
        a: 'Typically six to eight. You will get a realistic estimate after the first assessment rather than an open-ended commitment.',
      },
    ],
    related: ['post-surgical-return-to-sport', 'masters-athlete-injuries'],
    nextStep: {
      heading: 'Once the pain settles, what then?',
      body:
        "A quiet knee on the flat is not a knee you trust on a descent, in a squat rack, or on the last day of a ski week. Closing that gap is the work most people actually came for, whether or not they'd have said so at the start.",
      links: [
        { label: 'Post-surgical return-to-sport', slug: '/what-we-treat/post-surgical-return-to-sport' },
        { label: 'Masters athlete injuries (40+)', slug: '/what-we-treat/masters-athlete-injuries' },
      ],
    },
  },
];
