// Every 9NEWS segment featuring Jamie that is on 9NEWS's own YouTube channel,
// 2017 to 2022, compiled 22 Oct 2026. Three "likely" clips (calorie match Apr 2019,
// upper body Mar 2020, MMA self-defence Sep 2020) are left OUT until Jamie confirms
// it is him. Dates are the segment dates. Keep dates on /press only, never next to
// the present-tense "9NEWS fitness expert" badge.
export interface NineNewsSegment {
  id: string;
  title: string;
  date: string; // ISO
}

export const NINENEWS_SEGMENTS: NineNewsSegment[] = [
  { id: 'J7wGWcvBugw', title: 'Balance training', date: '2017-04-05' },
  { id: 'dOooZgwAlrI', title: 'Exercises you can do on the road', date: '2017-04-26' },
  { id: 'fD6yGf2hGbs', title: 'BOSU ball exercises', date: '2017-05-03' },
  { id: 'DQJzVJ5jCX4', title: 'Exercises for the perfect golf swing', date: '2017-05-31' },
  { id: 'DbKDhIfrPlM', title: 'Racquetball exercises', date: '2017-07-05' },
  { id: 'EIId6g04vm4', title: 'Park bench workout', date: '2017-07-26' },
  { id: '9gL8hxE2orA', title: 'Red Rocks workout for beginners', date: '2017-08-02' },
  { id: 'VsjHXG4MxvE', title: 'Dealing with soreness after a workout', date: '2017-08-23' },
  { id: 'RgWHU2UVtOk', title: 'Exercising after surgery', date: '2018-12-17' },
  { id: 'htEMRuYKYu8', title: 'Smash test of Super Bowl foods', date: '2019-01-23' },
  { id: '-wWXuS-rXpM', title: "Easy Valentine's Day workouts", date: '2019-02-13' },
  { id: 'Q5cSE2ZFhmM', title: 'Keeping kids active during the school year', date: '2019-08-07' },
  { id: 'knOOnKnnAc4', title: 'Getting skiers and boarders ready for the season', date: '2019-11-20' },
  { id: 'GHTku-enqy0', title: "3 shoulder exercises that won't cause aggravation", date: '2020-01-01' },
  { id: 'CPmssXowdtU', title: 'The importance of vegetables', date: '2020-02-05' },
  { id: 'x4iqbjC50Cw', title: 'Proper form for boxing', date: '2020-08-05' },
  { id: 'MQT-vEJoAIU', title: 'Getting in shape before hitting the slopes', date: '2020-10-28' },
  { id: 'DvbBrVoDC2I', title: 'At-home exercises with household items', date: '2020-12-09' },
  { id: '8ALP3EhbWN0', title: 'Ways to improve your balance', date: '2021-01-13' },
  { id: 'kRxsXEMl1Vk', title: 'Two exercises to improve hip mobility', date: '2021-02-26' },
  { id: '1Sd2bqiRIx8', title: 'A fun workout to do with your kids', date: '2021-03-10' },
  { id: '7mJMuFDhdto', title: 'Exercises with weight plates', date: '2021-05-12' },
  { id: 'JBwMREKugq0', title: '3 exercises for returning to the gym', date: '2021-06-30' },
  { id: 'f_SoiKUqHak', title: '3 tips for better posture at work', date: '2021-07-28' },
  { id: 'eCYSIo1lKuY', title: 'Posture exercises for returning to the workplace', date: '2021-08-11' },
  { id: '5Wc-YTnmmgE', title: 'Resistance band exercises at home', date: '2021-10-13' },
  { id: 'cRGFMTXOeGc', title: 'Getting ready for ski season', date: '2021-11-10' },
  { id: '9XuJlyHwfeM', title: '3 muscle exercises for snowboarders', date: '2022-01-05' },
  { id: 'dGovL4qR7Cg', title: "Valentine's Day workouts", date: '2022-02-09' },
  { id: 'ji3xvNk3T4M', title: '3 glute exercises', date: '2022-03-09' },
  { id: 'v4rXPkDZVIc', title: 'Exercises to improve mountain biking skills', date: '2022-05-25' },
];
