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
    title: 'Your post-surgery recovery took you almost to the finish line. We’re here to get you the rest of the way — and then some',
    metaTitle: 'Post-Surgical Return-to-Sport Rehab, Denver',
    schemaType: 'MedicalProcedure',
    metaDescription:
      'Insurance PT got you to "functional." We get you back to skiing, cycling, lifting, and running. Post-surgical return-to-sport rehabilitation in Denver.',
    intro:
      'The surgery went fine. The twelve sessions of physical therapy got you up the stairs, back in the car, back at work — and then someone wrote "functional" on a form and the referral ran out. <strong>You didn’t have surgery to be functional.</strong> You had it to get back on the bike, back on the slopes, back under the bar. Nobody in that chain was paid to take you there.',
    sections: [
      {
        heading: 'Why did the rehab stop before you were back?',
        paragraphs: [
          'It wasn’t your therapist. It was the brief they were handed. <strong>Insurance pays to make you functional, not to make you an athlete again.</strong>',
          'Discharge measures the things the system measures — and every one of them is a floor, not a ceiling:' +
            '<ul>' +
            '<li>can you walk without a limp</li>' +
            '<li>can you manage stairs and get in and out of a car</li>' +
            '<li>can you do your job</li>' +
            '<li>has your range come back to something close to the other side</li>' +
            '</ul>',
          'Clear all four and coverage ends, whether your goal was the grocery store or a century ride. The six to nine months of progressive loading between those two is real work, it is well described, and almost nobody sells it — because almost nobody gets reimbursed for it.',
          'That is the part I do. One-on-one, 45–60 minutes, starting from your discharge and ending at your sport.',
        ],
      },
      {
        heading: 'Why are you still nervous about loading it?',
        paragraphs: [
          'Because the fear is doing its job. <strong>Your nervous system has no way of knowing the surgeon fixed it.</strong>',
          'Tissue heals on a timeline. Confidence does not. Long after the repair is solid, the system that got you hurt is still on guard — and it shows up as stiffness that comes and goes, strength that doesn’t match the scan, and a quiet reluctance to take that joint anywhere near the movement that put you on the table.',
          'That reluctance is the symptom. It is not the thing to argue with. What changes it is evidence: find the edge of what genuinely feels safe, load it properly, let you feel yourself be strong there, then move the edge. Repeat until the edge is past what your sport asks of you.',
          '<strong>You don’t talk yourself out of the fear. You out-train it.</strong>',
        ],
      },
      {
        heading: 'What actually happens here?',
        paragraphs: [
          'First visit is a full hour: the whole history, a full movement assessment, and a straight conversation about your sport and your timeline. You leave with a plan and a number of sessions, not an open tab.',
          'After that it is progressive strength work built around three things — the surgery you had, the sport you want back, and the week you actually live in. Usually one session a week with work of your own in between.',
          '<strong>We don’t guess at when you’re ready.</strong> Load, range and confidence get tracked, you pass sport-specific benchmarks, and then you graduate. That last part is the point.',
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
      'Cognitive Functional Therapy combined with Applied Functional Science for chronic low back pain in Denver. For when PT and injections haven’t worked.',
    intro:
      'You have done the physical therapy. You have been adjusted. Somewhere in there was an injection, or a scan that found something and still didn’t explain why Tuesday is fine and Thursday isn’t. <strong>We get it.</strong> By the time most people reach this studio they have stopped expecting an answer and started managing around the pain instead. That is a reasonable response to what you’ve been offered. It isn’t the only option left.',
    sections: [
      {
        heading: 'Why hasn’t any of it held?',
        paragraphs: [
          'Everything you tried was aimed at the place that hurts. <strong>The place that hurts is the symptom, not the engine.</strong>',
          'Massage it, adjust it, inject it, brace it, strengthen the core. Every one of those turns the volume down for a while, and every one of them treats your back as a piece of failing hardware. After three months, that is rarely what is going on.',
          'A back that keeps flaring is a web, and the tissue is one strand of it:' +
            '<ul>' +
            '<li>how much load your back and hips can genuinely tolerate right now</li>' +
            '<li>how you brace, guard and hold your breath when you bend</li>' +
            '<li>sleep, stress, and the weeks when both go at once</li>' +
            '<li>the movements you quietly stopped making a year ago</li>' +
            '<li>what you believe is happening in there when it grabs</li>' +
            '</ul>',
          '<strong>Pull one strand and the web hands the pain straight back.</strong> That is not a failure of the treatments you tried. It is what happens when one thread gets treated on its own.',
        ],
      },
      {
        heading: 'What’s the method?',
        paragraphs: [
          'It is the thing that treats the whole web: <strong>Cognitive Functional Therapy combined with a method known as Applied Functional Science</strong> — a system that identifies when the symptom and the cause of the pain are in different places, and how to use the whole body to create a different outcome than traditional methods.',
          'And it is not fringe. In the 2023 RESTORE trial published in The Lancet, nearly 500 people with chronic low back pain were randomized to CFT or usual care. CFT produced large improvements in pain and disability that were still holding at twelve months, and at the three-year follow-up. Durability like that is rare in this research.',
          'What it looks like in the room is less dramatic than it sounds. We make sense of your pain story together — properly, not as a formality. We look at the whole body, not just the sore spot, to find where the problem is actually being driven from. Then we go back into the movements you have been avoiding, bending, lifting, sitting, whatever yours are, in doses your system can actually accept. Then we make you strong there, because that is what makes the change stay.',
        ],
      },
      {
        heading: 'My scan showed a disc bulge.',
        paragraphs: [
          'So do the scans of enormous numbers of people who have no back pain at all, at rates that climb steadily with age. <strong>It shows up on a scan the way grey hair shows up in a mirror.</strong>',
          'That does not make your pain imaginary and it does not make the scan useless. It means finding a bulge doesn’t tell us it is causing your pain, and it doesn’t predict how well you will do. A small number of presentations do need a physician first, and I screen for those — if yours is one, I will say so plainly.',
          'The plan gets built around what your back can do and relearn. Not around a picture of it.',
        ],
      },
    ],
    faq: [
      {
        q: 'How is this different from physical therapy?',
        a: 'Sessions are 45–60 minutes one-on-one (not a rushed insurance slot), the approach targets the pain system rather than just the tissue, and the endpoint is your sport and your life — not discharge paperwork.',
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
        "Getting out of pain is the first half. Most people then discover the thing they actually wanted was to get back to something — the bike, the trail, the barbell, a full day on their feet without bracing for it. That rebuild is a different piece of work, and it's the part I've spent twenty years on.",
      links: [
        { label: 'Post-surgical return-to-sport', slug: '/what-we-treat/post-surgical-return-to-sport' },
        { label: 'Masters athlete injuries (40+)', slug: '/what-we-treat/masters-athlete-injuries' },
      ],
    },
  },
  {
    slug: 'sciatica',
    navTitle: 'Back Pain and Sciatica',
    title: 'Sciatica that hasn’t responded to the usual treatments',
    metaTitle: 'Persistent Sciatica Treatment in Denver',
    metaDescription:
      'Radicular leg pain that didn’t respond to chiropractic, epidurals, or short-course PT. A nervous-system-informed approach to persistent sciatica in Denver.',
    intro:
      'It burns, or it shoots, or it goes numb somewhere below the knee — and it has outlasted everything you threw at it. You stretched the piriformis. You got adjusted. Maybe there was an epidural that worked for six weeks, or didn’t work at all. <strong>Sciatica that lasts is a different problem from sciatica that starts.</strong> Most plans are still treating the first one.',
    sections: [
      {
        heading: 'Why is it still there after the disc settled?',
        paragraphs: [
          'Because by now the disc is probably not the thing driving it. <strong>The nerve got sensitive, and sensitivity outlasts irritation.</strong>',
          'Most disc-related nerve pain settles within weeks to a few months. When leg symptoms carry on past that, what has usually changed is the threshold — the nerve fires at provocations it used to ignore, and ordinary movement gets flagged as something to protect you from.',
          'Which is why the standard advice quietly makes it worse. Rest, avoid, wait it out: all of it lowers the threshold further. A sensitized nerve gets its tolerance back the same way everything else does, by being asked for a bit more than it did yesterday and no more than it can take.',
        ],
      },
      {
        heading: 'What has to be ruled out first?',
        paragraphs: [
          'A short list, and it matters. <strong>A small number of these belong with a physician before they belong with me.</strong>',
          'Progressive weakness in the leg. Numbness in the saddle area. Any change in bladder or bowel control. Those get referred, immediately and without hedging.',
          'Everything else — which is the overwhelming majority — is exactly the kind of case this work is built for. Part of the first session is establishing which of the two you are, and I will tell you plainly rather than start a plan I don’t believe in.',
        ],
      },
      {
        heading: 'What does the work look like?',
        paragraphs: [
          'Less dramatic than what you have already tried, and considerably more durable. <strong>We stop chasing the leg and start rebuilding what feeds it.</strong>',
          'The plan works on four things at once:' +
            '<ul>' +
            '<li>movement the nerve tolerates, dosed so it calms rather than flares</li>' +
            '<li>progressive strength for the hip, trunk and leg</li>' +
            '<li>the sleep and stress load that amplify nerve pain more than most people expect</li>' +
            '<li>a graded return to whatever the pain took — walking, hiking, riding, standing through a workday</li>' +
            '</ul>',
          'It is probably not one tight muscle, and it is probably not something a stretch was ever going to reach. Nerve pain is slower to turn around than back pain and it does turn around. Most people are in the six to eight session range.',
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
      'You are 45, or 55, or 65, and stopping was never on the table. But the calf keeps going. The shoulder flares every ski season. The knee swells after the long rides and you have started planning the week around it. <strong>The injuries aren’t the problem — the cycle is.</strong> Train, break, rest, come back, break again. Each lap costs more than the last one, and the cycle is breakable.',
    sections: [
      {
        heading: 'Why do the same injuries keep coming back?',
        paragraphs: [
          'Because rest fixes the wrong half of it. <strong>Rest takes away the pain and takes your capacity with it.</strong>',
          'The pain settles, so you go back to your sport — but the demand is exactly what it was, and you are weaker than you were when you stopped. It flares. Obvious conclusion: rest more. The loop tightens, and each round leaves you with less than the one before.',
          'What sits underneath almost every recurring masters injury is a capacity gap: your sport asks for more than the tissue is currently prepared to give. That gap doesn’t close by waiting. It closes by loading.',
        ],
      },
      {
        heading: 'Do you have to train less now?',
        paragraphs: [
          'No — and the version of this you have been told is mostly wrong. <strong>"You’re just getting older" is a shrug, not a diagnosis.</strong>',
          'What actually changes with age is the margin. Recovery takes longer, tissue tolerates less sloppiness, and the thing you got away with at 30 now costs you two weeks. Smaller margin, same principles.',
          'The evidence on strength training for masters athletes is about as unambiguous as this field gets. Athletes over 40 who lift stay in their sport longer, get hurt less, and perform better. It is the least fashionable answer available and it is still the right one.',
        ],
      },
      {
        heading: 'What does working together look like?',
        paragraphs: [
          'It starts with the pattern, not just the flare. <strong>Treating this week’s injury without closing the gap that produced it just buys you the next one.</strong>',
          'So we look at three things: the injury in front of us, the demands of your sport, and the training history that got you here. Then we build something that handles all three at once.',
          'You keep training the whole way through, modified. Detraining is the enemy — it is what made the last three cycles worse, and there is almost never a good reason to stop entirely. Most masters athletes work with me for six to eight sessions and then keep a check-in cadence through their season.',
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
    navTitle: 'Cognitive Functional Therapy and AFS — our special sauce',
    title: 'The evidence-based approach most providers don’t know',
    metaTitle: 'Cognitive Functional Therapy (CFT) in Denver',
    schemaType: 'MedicalTherapy',
    metaDescription:
      'What Cognitive Functional Therapy is, the Lancet RESTORE evidence behind it, and how it combines with Applied Functional Science in practice. One of a handful of practitioners in Colorado.',
    intro:
      'If you have already read the other pages on this site, this is the method underneath all of them: <strong>Cognitive Functional Therapy combined with a method known as Applied Functional Science</strong> — a system that identifies when the symptom and the cause of the pain are in different places, and how to use the whole body to create a different outcome than traditional methods. CFT treats the whole system that produces your pain, not the tissue that stopped being the story months ago — the beliefs, the guarding, the movements you quietly dropped, the sleep and the stress that turn the volume up. It is the approach validated in the 2023 Lancet RESTORE trial, and I am one of a handful of practitioners in Colorado trained in it.',
    sections: [
      {
        heading: 'What’s the evidence?',
        paragraphs: [
          'Better than almost anything else in this field. <strong>That is not a small claim, and it is not mine.</strong>',
          'The RESTORE trial, published in The Lancet in 2023, randomized nearly 500 people with chronic low back pain to CFT or usual care. CFT produced large, clinically meaningful improvements in pain and disability — still holding at twelve months, and still holding at the three-year follow-up published in 2025.',
          'Durability is the part worth pausing on. Plenty of things help chronic pain for six weeks. Very little in the literature is still ahead of usual care three years later.',
        ],
      },
      {
        heading: 'How is it different from the physical therapy you’ve had?',
        paragraphs: [
          'Three ways, and the first one is the one people don’t expect. <strong>It starts with your story, and the story is the treatment, not the paperwork.</strong>',
          'Most histories are taken to fill a form. This one is taken to work out why your system became protective in the first place — because pain that makes sense to you is pain you can start to change. People often feel something shift in that conversation alone.',
          'Second, it uses graded experiments rather than instructions. We go into a movement you were told, or told yourself, is dangerous — and you feel the pain change in the room, with your own body, while you are standing there. That is a different kind of evidence from being reassured.',
          'Third, it takes the amplifiers seriously: sleep, stress, and the boom-and-bust activity pattern almost everyone falls into. Ignore those and the rest doesn’t hold.',
          '<strong>Then I add the part most CFT practitioners can’t.</strong> Twenty years of strength coaching, to rebuild real capacity once the system has calmed down. Desensitizing without strengthening is temporary. Strengthening without desensitizing never gets off the ground.',
        ],
      },
      {
        heading: 'Who is it for?',
        paragraphs: [
          'Anyone whose pain outlasted the healing. <strong>Past three months, tissue-focused treatment has usually stopped being the right tool.</strong>',
          'Back pain is the best-studied application by a distance, and it is where the trial evidence sits. But the principles are about how persistent pain is produced, not about which body part is complaining:' +
            '<ul>' +
            '<li>necks that flare no matter how the desk is set up</li>' +
            '<li>shoulders that never came back after the rest</li>' +
            '<li>knees written off as arthritis</li>' +
            '<li>pain that stayed on after a successful surgery</li>' +
            '<li>the fear of movement that follows all of the above</li>' +
            '</ul>',
          'If your pain is new, or it is one of the presentations that needs a physician first, I will tell you that instead of booking you in.',
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
      'You cannot sleep on that side. Reaching for anything above shoulder height is something you plan now, not something you do. You rested it, maybe had a cortisone shot, and it was genuinely better — right up until you tried to use the arm properly again. <strong>Shoulders almost never recover from being protected.</strong> They recover from being loaded well, which is close to the opposite of what most people are told.',
    sections: [
      {
        heading: 'Why didn’t rest work?',
        paragraphs: [
          'It worked. That is the trap. <strong>Rest takes the pain away and takes the tolerance with it.</strong>',
          'The shoulder calms down, so you go back to the pressing or the swimming or the two hours of overhead work your job involves. The demand hasn’t changed. Your capacity is lower than it was when you stopped. It flares, and the obvious conclusion is more rest.',
          'By the time most people reach me they have been round that loop three or four times, and each lap ended with a smaller shoulder than the last. The way out is to load it at a dose it can take today, then raise that dose deliberately until it comfortably clears what you actually ask of it.',
        ],
      },
      {
        heading: 'What about my rotator cuff tear?',
        paragraphs: [
          'It probably matters less than the report made it sound. <strong>Cuff tears turn up on the scans of huge numbers of people with no shoulder pain at all</strong>, and the rate climbs steadily with age.',
          'That does not make yours irrelevant. It means a tear on a piece of paper does not, on its own, explain your symptoms or decide that you need an operation.',
          'The evidence for progressive loading as a first-line approach to degenerative cuff problems is now substantial, with outcomes comparable to surgery across a good number of trials. Some shoulders genuinely do belong with a surgeon — traumatic full-thickness tears, real loss of function, a shoulder that cannot be lifted at all. If yours is one of those I will say so at the first session rather than sell you eight of them.',
        ],
      },
      {
        heading: 'Is it impingement?',
        paragraphs: [
          'That word has quietly fallen out of use, and for a good reason. <strong>The picture of a bone pinching a tendon has not held up.</strong>',
          'Decompression surgery — built entirely on that idea — has performed poorly against placebo procedures in controlled trials. Which is about as direct a test of a theory as this field gets.',
          'What tends to be true instead is less tidy, and it is a web rather than a single fault:' +
            '<ul>' +
            '<li>a tendon that has become irritable and reacts to more than it used to</li>' +
            '<li>strength lost through the middle and upper part of the range</li>' +
            '<li>a movement pattern quietly rebuilt around protecting it</li>' +
            '<li>months of broken sleep, which lowers the threshold for all of the above</li>' +
            '</ul>',
          '<strong>All four respond to the same thing.</strong> Not to a label.',
        ],
      },
      {
        heading: 'What does the work look like?',
        paragraphs: [
          'First we find the boundary — what the shoulder tolerates right now, honestly measured rather than guessed at. Then the program starts just inside it and moves it.',
          'Alongside that we deal with the two things that come with every long-running shoulder and get treated as side effects: the disrupted sleep, and the guarding you are no longer aware of doing.',
          '<strong>You keep using the arm the whole time</strong>, modified where it needs to be. Total rest is almost never the answer, and it is usually the thing that got the shoulder here.',
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
      'Stairs. Getting out of the car. The first mile of a hike, or the last one. You rested it, iced it, maybe had an injection, and somewhere along the line a scan came back with the word "degenerative" on it and nobody explained what that actually meant for you. <strong>Knees rarely recover from being protected.</strong> They recover from being loaded properly — and almost nobody says that out loud.',
    sections: [
      {
        heading: 'Why didn’t resting it work?',
        paragraphs: [
          'It did work, briefly, and that is what makes it so convincing. <strong>Rest settles the knee and quietly shrinks it at the same time.</strong>',
          'While the joint is calming down, the quads and hips around it are getting weaker and the joint’s own tolerance is dropping. Then you go back to the stairs, the trail, the ride. The demand is identical. Your capacity is not.',
          'It flares, the obvious conclusion is more rest, and the loop tightens by one notch. What breaks it is loading the knee at a dose it can genuinely handle now, then raising that dose on purpose until it clears what your week actually asks of it.',
        ],
      },
      {
        heading: 'I’ve been told it’s arthritis — or "bone on bone"',
        paragraphs: [
          'That sentence has ended more people’s activity than the arthritis has. <strong>"Bone on bone" is a description of an X-ray, not a prognosis.</strong>',
          'What the joint looks like on imaging tracks poorly with how much it hurts and how well it works. Plenty of people with significant changes on film have little or no pain. Plenty with mild changes hurt a great deal. Neither group is faking.',
          'More useful than the picture: exercise therapy is a first-line treatment for knee osteoarthritis in essentially every major clinical guideline written, and it reliably improves both pain and function. Not as a consolation prize before the replacement — as the treatment.',
          '<strong>It is not a reason to stop loading the leg. It is the reason to start.</strong>',
        ],
      },
      {
        heading: 'What about a meniscus tear? Do I need surgery?',
        paragraphs: [
          'Depends entirely on which kind you have, and the two get talked about as though they were one thing. <strong>Most middle-aged meniscus tears are wear, not an event.</strong>',
          'For those degenerative tears — the ones that appear gradually rather than from a specific twist you can still remember — several high-quality randomized trials have found arthroscopic surgery produces outcomes no better than structured exercise therapy. A lot of people get substantially better without an operation.',
          'A traumatic tear, a knee that locks, a genuine mechanical block: different category, belongs with a surgeon. Working out which one you are is part of the first session, and if it is the second one I will say so plainly rather than start a program.',
        ],
      },
      {
        heading: 'What does the work look like?',
        paragraphs: [
          'It starts above and below the knee, which surprises people. <strong>The joint is where it hurts. It is rarely where the problem is being decided.</strong>',
          'So the work is progressive strength for the quads, hips and calves — the structures that determine how much load ever reaches the joint at all — alongside a graded return to whatever the pain took from you:' +
            '<ul>' +
            '<li>a full flight of stairs without thinking about it</li>' +
            '<li>the descent on a hike, not just the climb</li>' +
            '<li>getting back to running, riding or skiing</li>' +
            '<li>a day on your feet that doesn’t cost you the evening</li>' +
            '</ul>',
          'You keep moving throughout, modified where it needs to be. Most people are in the six to eight session range and then carry on under their own steam.',
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
