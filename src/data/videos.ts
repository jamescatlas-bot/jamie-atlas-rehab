// YouTube videos, supplied by Jamie 2026-07-30.
// Press clips are official 9NEWS channel segments featuring Jamie (except the raw boxing spot).

export interface Video {
  id: string; // YouTube video ID
  title: string;
}

export const PRESS_VIDEOS: Video[] = [
  { id: 'ji3xvNk3T4M', title: '3 glute exercises to add to your workout (9NEWS)' },
  { id: 'NUTTTyyo8qE', title: 'Wellness Wednesday: Stretches and exercises for hiking (9NEWS)' },
  { id: '5EhGpjWFBgU', title: 'Workouts and stretches to help your golf game (9NEWS)' },
  { id: 'f_SoiKUqHak', title: '3 tips for better posture in the workplace (9NEWS)' },
  { id: 'eCYSIo1lKuY', title: 'Posture exercises for returning to the workplace (9NEWS)' },
  { id: '8ALP3EhbWN0', title: 'Wellness Wednesday: Ways to improve your balance (9NEWS)' },
  { id: '3pjgcMCT0rQ', title: '9NEWS boxing spot (raw footage)' },
];

export const TESTIMONIAL_VIDEOS: Video[] = [
  { id: 'jj9HW5h-Myc', title: '2 years of back pain gone in 20 minutes' },
  { id: 'cjvA1_s356I', title: '2-day back pain recovery' },
  { id: 'wX7ayi3Qm-g', title: 'Video testimonial — Tom H.' },
];
