// 9NEWS segment transcript pages (/9news/<slug>). Reprinted with 9NEWS's written
// permission (held by Jamie, not published). Transcripts were cleaned from 9NEWS's
// own live captions on 24 Oct 2026: repeats removed, spelling and obvious
// mishearings fixed, speakers labelled. Gaps the captions garbled were filled
// with a best guess from context and approved by Jamie (24 Oct 2026).
// Three segments (Oct 2020 slopes, Jan 2021 balance, Feb 2021 hip) are NOT here:
// their captions were unusable.
//
// note2026 sits above the video; afterword sits after the transcript.
// Both render with set:html, so <a> and <strong> work. No em dashes in new copy.

export interface Line {
  speaker: string;
  text: string;
}

export interface RelatedLink {
  href: string;
  label: string;
}

export interface NineNewsPage {
  slug: string;
  id: string; // YouTube id on 9NEWS's channel
  title: string;
  date: string; // ISO, air date
  description: string;
  note2026?: string;
  transcript: Line[];
  afterword: string[];
  related: RelatedLink[];
  clientVideoId?: string; // a TESTIMONIAL_VIDEOS id to show in the afterword
  clipEndsEarly?: boolean;
}

const J = 'Jamie';

export const NINENEWS_PAGES: NineNewsPage[] = [
  {
    slug: 'getting-ready-for-ski-season',
    id: 'cRGFMTXOeGc',
    title: 'Getting ready for ski season',
    date: '2021-11-10',
    description:
      "Jamie Atlas's 9NEWS segment on three moves for skiers: edge control on a balance board, side-foot curtsy lunges and BOSU jumps. Full transcript.",
    transcript: [
      { speaker: J, text: `Snow season is upon us, which means it's time to get ready for skiing. Now, if you haven't been doing the things you need to do to minimize your risk of injury on the mountain and also improve your performance, I'm here to help you out. Here are my three favorite moves for skiers.` },
      { speaker: J, text: `Now, we all know the balance board really well. Here's what you don't think about on skis: it's not about center control, it's about edge control. So I want to find myself at the front half of the board and try to hold my balance there. It's a very different experience being in the front half or the back half, trying to keep that toe or heel control. That'll save you a lot of pain and sorrow.` },
      { speaker: J, text: `The next one. If you think about skiing, skiing is not about straight up and down. Skiing is about giving me some knee bend with some drift. So here's my favorite exercise to do for that side hip muscle. That's the fancy term for it. We're going to go sideways now. You know curtsy lunges, but I'm going to do it differently. I'm going to do side-foot curtsy lunges. The reason I put that foot sideways is that now, to get back up, I can't use my calf to get me up, so I have to use this guy right here. And then come up, and then back down again. All the weight's in this leg. Nice and easy. Remember that one. Do yourself a favor.` },
      { speaker: J, text: `So right now, the BOSU ball. We know and love this one. I want to jump and land both feet here, not on the black, not on the white. I want to go boom and land, boom and land, and work those side muscles and power.` },
      { speaker: J, text: `Those three exercises are going to make sure you have the best year yet skiing in the mountains. For more tips like these, visit 9news.com.` },
    ],
    afterword: [
      `Four winters on, I'd keep all three. The one I'd underline is the first: skiing happens on the front and back edges of your feet, not the flat middle, so that's where your balance work should live.`,
      `If a knee is the reason you're nervous about this season, the clip below is Meghan, a client with knee pain after an ACL tear. One person's result, not a promise, but it shows what the work looks like.`,
    ],
    clientVideoId: 'nPUisex9g_s',
    related: [
      { href: '/resources/ski-season-prep', label: 'Ski season prep: the complete Denver guide' },
      { href: '/resources/ski-squats', label: 'Ski squats: train for the turn' },
      { href: '/resources/balance-training', label: 'Balance training' },
      { href: '/9news/skiers-and-boarders-ready-for-the-season', label: 'On 9NEWS, 2019: getting skiers and boarders ready' },
      { href: '/for/skiers', label: 'Personal training for skiers' },
    ],
  },
  {
    slug: 'skiers-and-boarders-ready-for-the-season',
    id: 'knOOnKnnAc4',
    title: 'Helping skiers and boarders get ready for the season',
    date: '2019-11-20',
    description:
      "Jamie Atlas on 9NEWS with two snowboard drills: the offloaded squat and front-to-back jump landings on a balance board. Full transcript and a 2026 update.",
    note2026: `At the end of this one I tell snowboarders to stretch to avoid shoulder injuries. Most snowboard shoulder injuries come from falls, and I haven't seen good evidence that stretching prevents them. What I'd say today: build strength through the shoulders and upper back, and learn to fall with your arms bent and tucked. The two leg drills I still use every season.`,
    transcript: [
      { speaker: 'Host', text: `A couple of weeks ago we talked about fitness to get ready for ski season. Today we'll get ready for snowboard season and keep us safe while we're out there.` },
      { speaker: J, text: `We can all do the standard thing: get your legs and upper body strong, getting ready for snowboarding or skiing. I ski and snowboard. Learning how to do the snowboarding fully has been really interesting. It's helping me get creative and give exercises to my clients. Here are two that I love to do. One is, think about snowboarding: it's loading on that front foot to get good control, and also the back foot to some extent. We'll do an offloaded squat. 15-pounder here. I'll have you hold it in one hand, right here. Keep it not close to the middle but right on that shoulder, like you've got right there. I'll have you squat down. You just did the sneaky hand, where you took the left hand and said, let me help it. If you do that at home, it doesn't help you. We'll go again. Boom, and up. Beautiful. Just keep that by the head. You'll notice as you do this, you're feeling that core stabilize, but when you look in the mirror, everything is centered. You aren't drifting left. You feel that?` },
      { speaker: 'Host', text: `Yeah. Looks centered.` },
      { speaker: J, text: `You look dead center. The core and everything there is loading on one side. This is starting to be more true to snowboarding.` },
      { speaker: 'Host', text: `I can feel it.` },
      { speaker: J, text: `The second thing is when you think about our power and the ability to react. Of course, going through the snow, we need to make sure we have good front-to-back balance.` },
      { speaker: 'Host', text: `All about the edges.` },
      { speaker: J, text: `I'll give you some advanced movements. Super fun one. You'll stand next to it and I'll have you jump from here. We'll have the board going front to back, and you'll go from here, stick the landing, step off.` },
      { speaker: 'Host', text: `And you just showed us it's possible to land without landing on the front or back edge. On the count of three, I'll jump over.` },
      { speaker: J, text: `And then land and try to balance. You got it, good. Boom. Yeah. Look at that.` },
      { speaker: 'Host', text: `That was great. How many do we want to do?` },
      { speaker: J, text: `We'd do ten to the left, also ten to the right. It's just a fun drill. If you fail at it and are horrible, that's great. We want to learn how to get that front foot control.` },
      { speaker: 'Host', text: `I'll try one more time. Getting cocky here. Like a cat.` },
      { speaker: J, text: `Like a tired cat. That's one I love. And also, most snowboarders, if they hurt themselves, it's their shoulders. Make sure you do a lot of stretching. We don't want the shoulder injury.` },
      { speaker: 'Host', text: `Sounds good.` },
    ],
    afterword: [
      `The offloaded squat has aged the best of anything in this clip. Holding the weight on one side asks your trunk to do what it does on a board: stay level while the load is lopsided.`,
      `For the shoulder side of things, the shoulder exercises article below is where I'd start now, ahead of any stretching routine.`,
    ],
    related: [
      { href: '/resources/snowboard-conditioning', label: 'Snowboard conditioning' },
      { href: '/resources/shoulder-exercises', label: 'Shoulder exercises' },
      { href: '/9news/exercises-for-snowboarders', label: 'On 9NEWS, 2022: 3 muscle exercises for snowboarders' },
      { href: '/9news/getting-ready-for-ski-season', label: 'On 9NEWS, 2021: getting ready for ski season' },
    ],
  },
  {
    slug: 'exercises-for-snowboarders',
    id: '9XuJlyHwfeM',
    title: '3 muscle exercises for snowboarders',
    date: '2022-01-05',
    description:
      "Jamie Atlas's 9NEWS segment on three snowboard exercises: the kettlebell side lunge, single-leg calf raises and quick-feet power work. Full transcript.",
    transcript: [
      { speaker: J, text: `Snow is here, which means that if you're a snowboarder like I am, here are three favorite exercises you need to do to make sure your body and muscles are ready to go.` },
      { speaker: J, text: `Number one. We're going to take a kettlebell here, but that can be any weight or heavy dumbbell for you. I'm going to do a side lunge and bring it down and back together. Here's the key piece. If you think about snowboarding, snowboarding is a lot of front-to-back edge control. So if you watch, I'm coming into a side lunge. This thing is straight, and I'm drifting that forward. I want to drift that kettlebell forward so that the counterbalance is sinking me into the heels. That's number one.` },
      { speaker: J, text: `Number two. Anyone who's been out at the start of the season knows how bad those calves can burn. So we're going to do a calf raise right now. All I'm going to do is hang one foot off the edge of a stair and boom, boom, all the way up, all the way down. Really burn one out and then switch. Go back and forth until it feels really good.` },
      { speaker: J, text: `Next is going to be some power jumping stuff. Sometimes I need to be able to quickly move my feet to get my edges in front of me, in case there's someone in front of me. So we're going to go from here again. Hop, back, step. Boom, boom, boom, boom. Easy to do, you can do it anywhere. Minimal equipment. Get it done. Do yourself a favor, you'll be glad you did. For tips like these and more, go to 9news.com.` },
    ],
    afterword: [
      `Still my three. If you only do one, make it the calf raise: it's the easiest to do at home, and it answers the burn most riders feel on day one.`,
    ],
    related: [
      { href: '/resources/snowboard-conditioning', label: 'Snowboard conditioning' },
      { href: '/9news/skiers-and-boarders-ready-for-the-season', label: 'On 9NEWS, 2019: getting skiers and boarders ready' },
      { href: '/resources/ski-season-prep', label: 'Ski season prep: the complete Denver guide' },
      { href: '/for/skiers', label: 'Personal training for skiers and riders' },
    ],
  },
  {
    slug: 'exercising-after-knee-surgery',
    id: 'RgWHU2UVtOk',
    title: 'Exercising after surgery',
    date: '2018-12-17',
    description:
      'Jamie Atlas on 9NEWS with a host recovering from meniscus surgery: the three lanes of the knee, rotational calf raises and heel slides. Full transcript.',
    note2026: `The "three lanes of the knee" idea from this segment is still how I start with every knee: find the directions that feel good, train those, and the stiff lane usually follows. One thing I'd add now: if you've had surgery and been discharged but still don't trust the knee, that gap is normal, and it's most of what I work on.`,
    clipEndsEarly: true,
    transcript: [
      { speaker: 'Host', text: `On this Workout Wednesday, we're talking about knees. I'm here with Jamie Atlas. I recently had knee surgery, but you don't have to wait for knee surgery to do nice things for your knees.` },
      { speaker: J, text: `That's right. A lot of people have knee challenges. The way I want people to think about their knees: instead of saying, oh, a squat hurts or a deadlift hurts, that's it, I'm out, there's plenty of other ways to do it. Let's just do a small variation right now. Get your feet nice and wide. This is a way where you can really explore your own body and sort of feel what feels good and go with that.` },
      { speaker: 'Host', text: `Now, do you have to use a weight?` },
      { speaker: J, text: `Not at all. Just lightly. 10 pounds, nice and easy. So we're going to drift to the left. We mentioned three lanes of a knee highway, if you will. So I'm going to go straight down. That's one lane.` },
      { speaker: 'Host', text: `There's one.` },
      { speaker: J, text: `There's one. Now stay to the left. Now let's go to the inside, almost like you're trying to clean something off the inside of your right knee. There's two right there. And drift left again. Now go to the outside of the knee. So which of those highways felt easiest for you?` },
      { speaker: 'Host', text: `The straight-ahead one.` },
      { speaker: J, text: `The straight-ahead one. So what we know is that lane works; these two lanes don't. The important part is we play with those lanes while we're doing our movements to see what feels okay, because that gives us a good idea of how our knee is doing and progressing.` },
      { speaker: 'Host', text: `And this is something that, if you're at home, you can just stop and do for a couple of...` },
      { speaker: J, text: `10, 20 reps.` },
      { speaker: 'Host', text: `And move on.` },
      { speaker: J, text: `And then move on. It doesn't have to be a big to-do, blocking out time in your day. You walk over to the window, you're watching a commercial break: hey, let me work on the muscles that help stabilize my knee. And weight is purely optional. Face that way for me. I'm going to have you put a foot there. Now, a lot of us know this calf stretch. What I'm going to have you do is actually a calf raise for me, because I want flexibility. So right there, nice and easy. Good. Now, just like the knee, the calf needs to be able to go front to back, but also with a rotation. I want you to take that knee out about 45 degrees. Show me that.` },
      { speaker: 'Host', text: `Okay.` },
      { speaker: J, text: `So while you're doing that, have a feel of that. Now let's go the other way. Inside now. That's the lane we found not to go down.` },
      { speaker: 'Host', text: `The bad lane.` },
      { speaker: J, text: `This is the lane with all the potholes in it.` },
      { speaker: 'Host', text: `You have two good lanes.` },
      { speaker: J, text: `If you work on these two good lanes, what you'll find eventually is that third lane will start to come to work for you. Third exercise: lie on your back for me.` },
      { speaker: 'Host', text: `All right.` },
      { speaker: J, text: `I'm going to have you do an exercise you're very familiar with, because you had your meniscus surgery. Even if you don't have a meniscus challenge, this is good preventative maintenance. I'm going to have you slide that heel up and slide it down. Now, the important part is I'm going to put a hand here, and imagine you're crushing that hand.` },
      { speaker: 'Host', text: `Push down on that.` },
      { speaker: J, text: `Crush it. You're going to keep that toe up and then slide that back down. Beautiful. Just like that. If you do 20 to 30 reps of that every other day, that's a great way to make sure your knee has the structure to start to feel better, and also to protect it in case you slip on some ice, something accidentally happens, and that knee gets tested. If we look after our knees, our knees will look after us.` },
      { speaker: 'Host', text: `Even if you have one that feels good, do it on those...` },
    ],
    afterword: [
      `What the research added since this aired: knee findings on a scan are far more common than people expect. Culvenor and colleagues, in the <a href="https://bjsm.bmj.com/content/53/20/1268" target="_blank" rel="noopener">British Journal of Sports Medicine</a> (2019), pooled MRI studies of adults over 40 who had never injured a knee and had no knee pain: 19% had a meniscus tear. A tear on your report is not, on its own, the reason your knee hurts or the limit on what it can do.`,
      `That's why I start with what the knee will accept, the good lanes, and build from there. Below is Meghan, a client working back from an ACL tear. One person's result, not a promise.`,
    ],
    clientVideoId: 'nPUisex9g_s',
    related: [
      { href: '/this-is-you/cleared-but-not-ready', label: 'Cleared by your physical therapist, but not ready' },
      { href: '/what-i-work-with/knee-pain', label: 'Knee pain' },
      { href: '/what-i-work-with/post-surgical-return-to-sport', label: 'Returning to sport after surgery' },
    ],
  },
  {
    slug: 'shoulder-exercises-without-aggravation',
    id: 'GHTku-enqy0',
    title: "3 shoulder exercises that won't cause aggravation",
    date: '2020-01-01',
    description:
      "Jamie Atlas's 9NEWS segment on three gentle shoulder exercises, with a 2026 update on shoulder position and what rotator cuff findings on a scan mean.",
    note2026: `In 2020 I explained these through shoulder position: the arm rolls forward in the socket, so pull it back to neutral. I'd explain it differently now. Shoulder position on its own doesn't predict pain very well. The three exercises still help, because they get a sore shoulder moving and loading in ways it will accept. And if a scan has shown a rotator cuff tear, those are common in people with no shoulder pain at all.`,
    transcript: [
      { speaker: 'Anchor', text: `A new year means new goals. If some of your resolutions are to stay in shape, we have tips for you. We were talking about how to exercise and eat healthy. In today's edition of Workout Wednesday, Kylie shows us exercises to work on.` },
      { speaker: 'Kylie', text: `Welcome to Workout Wednesday. We're talking about shoulder health.` },
      { speaker: J, text: `Shoulder health. One of the things that happens out there with all the ice: people are slipping and falling. And when people want to get back to using the shoulder again, what I try to do with my clients is say, let's be kind to our shoulders, and not try to get just strength, because some of these movements tend to be aggravating. What I tend to do is say, okay, how do we get the shoulder active again in a way that is likely to be safe? Obviously, if you have real problems, go get it checked out by a medical professional. But if you feel like it's just not coming back the way you wanted it to, here are three exercises I recommend you do.` },
      { speaker: J, text: `Number one: think about the position of your shoulder. When we roll our shoulders forward, that upper arm in the socket starts to push forward, and what I want to do is get that back into a more neutral position. So the first thing we'll do is a chest stretch. Get that hand there, and I'll have you shuffle forward, left foot forward. So we're going to go right there. The key here is to relax the shoulder and drive forward with the chest for that nice deep stretch.` },
      { speaker: 'Kylie', text: `That feels good.` },
      { speaker: J, text: `If you work in an office, just do these while you're hanging out talking to people. Number two: once we've got that in the right place, the shoulder blade is back here, hanging around by the side. As this arm comes down, I want you to see the shoulder blade start to really line up. If we're going to have a happy shoulder, we need a happy shoulder blade. So let's do this exercise really quick. I'm going to have you step back there, and we're going to go straight up. When you pull down, I want you to move your hip to the side, point your shoulder blade down, and pull back and down. We want to really activate the shoulder blade muscles back in here, so do this movement in a way where we're being respectful of the shoulder blade. Good.` },
      { speaker: J, text: `And then I'll have you do one arm. Face me and stand at that side. What you're going to do is bend over 90 degrees right here and then go boom, boom. You're moving the shoulder blade, not just your arm. If you can do those three moves right there, you're on your way. As long as you're pain-free, there's no shame in doing air reps to get the shoulders moving.` },
      { speaker: 'Kylie', text: `Awesome, thank you so much.` },
    ],
    afterword: [
      `The research behind my change of mind: in a population screening study in Japan (<a href="https://www.orthobullets.com/evidence/21454096" target="_blank" rel="noopener">Minagawa and colleagues</a>), 65% of the full-thickness rotator cuff tears found by ultrasound were in shoulders with no symptoms at all. A tear can be there and not be the problem.`,
      `So today the job is less "fix the position" and more "find the movement the shoulder will accept, then load it." Below is Heather, a client who came in with shoulder nerve pain. One person's result, not a promise.`,
    ],
    clientVideoId: '31I4nnADI_s',
    related: [
      { href: '/resources/shoulder-exercises', label: 'Shoulder exercises' },
      { href: '/what-i-work-with/shoulder-pain', label: 'Shoulder pain' },
      { href: '/9news/posture-tips-at-work', label: 'On 9NEWS, 2021: 3 tips for better posture at work' },
    ],
  },
  {
    slug: 'balance-training',
    id: 'J7wGWcvBugw',
    title: 'Balance training',
    date: '2017-04-05',
    description:
      'Jamie Atlas on 9NEWS with balance board, BOSU and Core-Tex drills, the head-snap drill, and the question "training to perform or training to protect?" Full transcript.',
    note2026: `This aired in 2017, when my studio was called Bonza Bodies. Same studio at 1800 Glenarm, new name. The question I ask near the end, "are you training to perform or training to protect?", is still the first thing I ask anyone who wants better balance.`,
    transcript: [
      { speaker: 'Host', text: `All right, time now for our Workout Wednesday. Our 9NEWS fitness expert, Jamie Atlas with Bonza Bodies, is joining us. We're talking about balance training today.` },
      { speaker: J, text: `Balance training. It's an essential part, whether you want to be doing something between your sets so you're not just standing around watching the clock, or alternatively, if you say to yourself, okay, I'm playing a sport where I need to be able to control where I'm going, and maybe I sometimes get off balance and need to be able to recover. Or if you're just someone who's maybe getting to an age where you're starting to get worried about falls. Because let's face it, I can't count the number of clients I've had who have come in and said, man, I had a close shave on a step on the stairwell, or I stood on a patch of ice, and I was able to save myself, and I was really grateful for that. Because a fall at a certain age can mean you go into hospital, and sometimes you don't make it back out.` },
      { speaker: 'Host', text: `I love that it covers everyone from that end all the way to the other. This is great for athletes as well.` },
      { speaker: J, text: `Very much so. So let's start. We have three pieces of equipment right here. These two are very common. This one I have in my studio, and there's a few other places in Denver that have one. It's wild. You'll get to see it. So let's just stand on this, basically a balance board, right now. If you guys can see this, you'll notice that Cory is going side to side. As she goes side to side, I want you to think: if you're playing a sport and you're worried about lateral agility, then I need my ankles to be able to react and not roll over if something goes wrong. So Cory's doing that right now. Cory, give me a couple of squats right there. We'll basically train those ankles to be smart. Good. Nice. Now, the deeper she goes, the more athletic she goes, the harder that's going to be. Right there. Good. Nice.` },
      { speaker: J, text: `Now let's switch it up. Hop off for me. What I want you to do now is face me. You went side to side before; now you're going to go front to back. There's no wrong way to do it.` },
      { speaker: 'Cory', text: `Help me, help me. Oh, okay. Yeah, this is very different.` },
      { speaker: J, text: `Very different. Now, if you are someone who's worried about falling, or slipping, or missing a step on stairs or on ice, here's what I'll say. If you practice this kind of balancing on a balance board, then you're going to be great at being able to control that if you do get a foot suddenly slip away from you. Does that make sense?` },
      { speaker: 'Cory', text: `It does. Fantastic. I feel that all over.` },
      { speaker: J, text: `It's great. Even when we're standing still, there are all these stability muscles that kick in to help us stand in that position. Now, real quick before you get on: the BOSU ball is a really common piece of equipment you find at the gym. What I'll say is that some are more inflated than others, so what you're about to do will work for most, but it might not work for all. Just a point for those at home. I'm going to have you put one foot on there, find an edge, and then find the other edge, and then stand on there. Now all of a sudden we've got a game changer, because this BOSU ball can go anywhere. It can go forward, back, side to side, at any time.` },
      { speaker: J, text: `Now, what I love about this, personal trainers watching: if you want to do a squat assessment, put your client on a BOSU ball. It's a great way to find out where their body wants to go. Sometimes they'll lean to one side; sometimes their toes will roll forward. On the side shot right here, I see Cory's toes rolling forward a little bit. If I want to teach good squat mechanics, I want to teach her to put her weight a little bit more on the heels. Try that for me. Good. So off there.` },
      { speaker: J, text: `All right, so this one we have to check out. This is a Core-Tex. Now, as with any of these tools, they can be used in multiple ways. Today we're going to talk about the balance aspect of it. Now, in Colorado, snowboarders and skiers, it's coming up soon. And if you're lucky enough to be traveling to my country, you might be going surfing. That's what it feels like, surfing, to me. This guy can go anywhere. The difference is that one was teeter-tottering; this is translating. The ground's going to move from under you, so it's the closest thing to the real world I can get. So I'm going to have you grab both handles and just hop on.` },
      { speaker: 'Cory', text: `Okay. All right. Whoa, whoa, whoa.` },
      { speaker: J, text: `Just got real, right? Okay. So what I want you to do, real easy, is just give me a nice easy squat. Keep your hands just above the bar so you have it if you need it.` },
      { speaker: 'Cory', text: `I don't trust myself. I trust you, though.` },
      { speaker: J, text: `Stand up. Good. If you fall, it'll make great TV.` },
      { speaker: 'Cory', text: `Yeah, great, thanks.` },
      { speaker: J, text: `Don't worry about my face. Nice. So now let's make this a little bit more like snowboarding or skiing. Just take one hand off for me, so that way we've got less support. Give me a squat with a twist, and back up. Nice. And the other way. And all of a sudden, yeah, all of a sudden we've got balance. You're doing great.` },
      { speaker: 'Cory', text: `For the first time!` },
      { speaker: J, text: `Fantastic. So right now we've got something where we can do this exercise and it's going to look and feel like the sport I want to perform in. And here's the question: when you do your balance work, are you training to perform or training to protect? Because sometimes we're training to protect, to make sure we don't have an accident.` },
      { speaker: J, text: `So the last thing I'm going to show doesn't require any equipment at all. We're just going to stand on one foot. Standing on one leg is a common thing that we all think is our balance work. So we're going to stand on one leg and look straight ahead. Oftentimes when we say, hey, check out my balance, I can stand on one leg, we lock on a point in the background somewhere. Here's what I'll say: that's about as far from the real world as we can get. Oftentimes when we need that balance is when I'm walking and talking to someone, and all of a sudden I miss a step and my head does this snap thing, where I'm going from looking at whatever I was looking at to: holy cow, where's my foot going? So what we're going to do, it's kind of going to feel like a sobriety test. We're going to go one foot, and I'm going to have you look at one thumb. When I say snap, I want you to snap that head to the other side. So look at this thumb. Good. Check out that beautiful manicure right there. And then we're going to go snap, boom, hold it. And snap, boom, hold it. Good. Now we're going to double snap. Ready, go. Boom, boom. Freeze.` },
      { speaker: 'Cory', text: `This is harder than you think it is.` },
      { speaker: 'Host', text: `I love all of these tips. This was so great, for people just in daily life or athletes. Jamie Atlas from Bonza Bodies, thank you so much. We're going to put all the information on our website at 9news.com.` },
    ],
    afterword: [
      `The research has caught up with the "training to protect" side of this. A 2019 Cochrane review led by Sherrington (<a href="https://pedro.org.au/english/systematic-review-found-that-exercise-prevents-falls-in-older-people-living-in-the-community/" target="_blank" rel="noopener">summary on PEDro</a>) pooled 108 trials with more than 23,000 older adults living at home. Exercise cut the rate of falls by 23%, and most of the programs were built on balance and functional exercise.`,
      `The head-snap drill at the end is still in my programs. Real falls happen when your eyes are somewhere else, so that's where balance should be trained.`,
    ],
    related: [
      { href: '/resources/balance-training', label: 'Balance training: train the recovery, not just the legs' },
      { href: '/personal-trainer-denver/over-40', label: 'Personal training over 40, 50 and 60' },
      { href: '/resources/ski-season-prep', label: 'Ski season prep' },
    ],
  },
  {
    slug: 'posture-tips-at-work',
    id: 'f_SoiKUqHak',
    title: '3 tips for better posture at work',
    date: '2021-07-28',
    description:
      "Jamie Atlas's 9NEWS segment on three desk-day exercises, with a 2026 update on what the research says about posture and pain. Full transcript.",
    note2026: `In this one I talk about "correcting" posture. I'd say it differently now. The research hasn't shown that posture causes back or neck pain. These three moves still help, because a desk day leaves you stiff, and moving and strengthening feels better. The rule I use today: your next posture is your best posture.`,
    transcript: [
      { speaker: J, text: `If you want to know about posture, I've got three tips coming right up.` },
      { speaker: J, text: `I'm 9NEWS fitness expert Jamie Atlas, and today we're talking posture. A lot of us are coming back to the workplace, or just finding that our posture is starting to fall apart. So here are the three things you need to know. Number one is the angle of the hips: these hips are going to tighten at the front. Number two is the shoulder blades rounding forward. Number three is the weight of this head needs to be corrected.` },
      { speaker: J, text: `So, number one, really easy. All you need is a chair or a bench or whatever you have right there. You can put this leg up and really stretch forward to stretch the front of the back leg, and vice versa.` },
      { speaker: J, text: `Number two is how we correct the shoulder blades. To correct the shoulder blades, I'm going to take a resistance band, put one leg back, and pull. The emphasis in this exercise is pulling the shoulder blades back and really trying to undo that desk-like T. rex arm position.` },
      { speaker: J, text: `Number three is our reverse curl. We're going to hunch forward, bring your chest over the edge of a bench, drop down, bring it up. Give me 15 to 20 reps of that. And those are the three exercises you need to know: correct the pelvic tilt, correct the shoulder position, correct the strength in the neck.` },
    ],
    afterword: [
      `The research behind my change of mind: a 2020 review of 41 systematic reviews, by Swain and colleagues in the <a href="https://research.monash.edu/en/publications/no-consensus-on-causality-of-spine-postures-or-physical-exposure-/" target="_blank" rel="noopener">Journal of Biomechanics</a>, found "no consensus regarding causality of physical exposure to LBP" (low back pain). Sitting and posture show up as associations. Nobody has shown they are the cause.`,
      `So keep the three moves, drop the guilt about how you sit. Below is Sandy, a client who had lived with neck pain for three years. One person's result, not a promise.`,
    ],
    clientVideoId: '-gdriOBWpS0',
    related: [
      { href: '/resources/desk-posture', label: 'Desk posture: your next posture is your best posture' },
      { href: '/for/desk-workers', label: 'Personal training for desk workers' },
      { href: '/what-i-work-with/neck-pain', label: 'Neck pain' },
      { href: '/9news/posture-exercises-returning-to-work', label: 'On 9NEWS, 2021: posture exercises for returning to the workplace' },
    ],
  },
  {
    slug: 'posture-exercises-returning-to-work',
    id: 'eCYSIo1lKuY',
    title: 'Posture exercises for returning to the workplace',
    date: '2021-08-11',
    description:
      'Jamie Atlas on 9NEWS with four upper-back and neck moves for desk workers, plus a 2026 update on stiffness, sitting and neck pain. Full transcript.',
    note2026: `I open this one by saying sitting "cranks up" the neck and these moves "take the pressure off". I wouldn't explain it that way now. A stiff upper back and a sore neck after a long desk day are common, and they aren't a sign your spine is being damaged. These moves are still worth doing, because they feel good and get you moving. If neck pain has stuck around for months, that's a different conversation.`,
    transcript: [
      { speaker: J, text: `The human spine: a fascinating piece of equipment that we need to stand tall. Unfortunately, the cervical spine... If you can imagine the natural curves of the spine, the cervical spine here can sometimes get a little cranked up as we sit all day. The important part to remember is that this thoracic spine here, this upper back, can really get rounded. So we need something to open it up, to take the pressure off that cervical spine.` },
      { speaker: J, text: `First move. I'm going to take a rolled-up towel or yoga mat. I want to put this across my shoulder blades, right here, arms wide, and I'm just going to roll the knees left to right. That rolling is going to provide some gentle massage and opening of that thoracic spine.` },
      { speaker: J, text: `Number two. Now, you'll notice I'm not picking up my head. I'm really trying to let gravity weigh me down, drawing open either side of my neck as I'm going. You can do both those moves for three to five minutes and you'll feel amazing.` },
      { speaker: J, text: `Last one, if you're sitting at a desk and you don't have a chance to get down. I'm going to take my hand, wrap it under the edge of the seat, sitting nice and tall. And then I'm going to take my head slightly to the right and tilt it down, and you will feel this deep, delicious stretch right through the upper trapezius on your left-hand side.` },
      { speaker: J, text: `One more move to do. It's over here. I'm going to take a yoga block again. You can use whatever you'd like, but this move right here I call "head steady, chest moving." The more I move my feet away from the wall, the harder it's going to get. So now I'm going to collapse, and then drive the chest forward. Now, you'll notice I'm not bringing my head up; my head is dead level. What's happening right now is I'm having to use these neck muscles to drive my chest up. Do 15 to 20 reps of these anywhere you want, and you'll find yourself standing taller, free of neck pain. For more spots like this, go to 9news.com.` },
    ],
    afterword: [
      `"Free of neck pain" was TV shorthand. Today I'd say these moves ease desk-day stiffness, and that neck pain which hangs on for months usually needs more than stretches: it needs someone to look at what the neck will and won't accept, and build from there.`,
      `Below is Monique, a client who came in with four weeks of neck pain. One person's result, not a promise.`,
    ],
    clientVideoId: 'X5EquRG2d24',
    related: [
      { href: '/what-i-work-with/neck-pain', label: 'Neck pain' },
      { href: '/resources/desk-posture', label: 'Desk posture' },
      { href: '/9news/posture-tips-at-work', label: 'On 9NEWS, 2021: 3 tips for better posture at work' },
      { href: '/for/desk-workers', label: 'Personal training for desk workers' },
    ],
  },
  {
    slug: 'returning-to-the-gym',
    id: 'JBwMREKugq0',
    title: '3 exercises for returning to the gym',
    date: '2021-06-30',
    description:
      "Jamie Atlas's 9NEWS tips for coming back to the gym after a break: multi-joint lifts, a reduced range of motion and breathing. Full transcript.",
    note2026: `This aired in June 2021, as gyms reopened after COVID. The advice holds for coming back after any break, whether it's an injury, a busy year or a new baby: big multi-joint lifts, a shorter range of motion for the first few weeks, and breathe.`,
    clipEndsEarly: true,
    transcript: [
      { speaker: J, text: `Coming back to the gym after your COVID break? I'll have three tips coming up.` },
      { speaker: J, text: `Hi, I'm 9NEWS fitness expert Jamie Atlas. If you're back in the gym, here are three things you need to know. One: pick multi-joint exercises. This exercise I'm doing, everyone knows, but it's not where I'd have you stop. I much prefer multi-joint exercises like bench press, lat pulldown, squat and press. They're great exercises where you're using multiple joints.` },
      { speaker: J, text: `Now, when you see people doing a bench press, they'll come all the way down here. When we're starting, just give me a reduced range of motion. And most importantly, make sure you breathe through it. When we return to the gym, we lose all these small technique tips. So there you have it: breathe, reduced range of motion, and multi-joint exercises, to give yourself the best re-entry into the gym.` },
    ],
    afterword: [
      `The trap after a break is usually not weakness. It's the second week: the first sessions feel fine, so the load jumps, and something old wakes up. Keep the shorter range and the lighter weights for two weeks longer than you think you need.`,
      `If an old injury is the reason you stopped in the first place, the pages below are where to go next.`,
    ],
    related: [
      { href: '/this-is-you/worried-about-reinjury', label: 'You want to train without getting hurt again' },
      { href: '/personal-trainer-denver/over-40', label: 'Personal training over 40, 50 and 60' },
      { href: '/resources/resistance-band-training', label: 'Resistance band training at home' },
    ],
  },
];
