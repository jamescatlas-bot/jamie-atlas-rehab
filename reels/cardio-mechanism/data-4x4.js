window.VIDEO = {
  kicker: 'MECHANISM · CARDIO · NORWEGIAN 4×4',
  title: 'What 4x4 intervals do, and when',
  accent: '#a3232d',
  sources: 'Helgerud 2007 · Egan 2010 · Perry 2010 · Talanian 2007 · Støren 2017 · Tjønna 2008, 2013 · Rognmo 2004 · Wisløff 2007 · Ramos 2015',
  axis: [{label:'start',day:0},{label:'1 day',day:1},{label:'1 week',day:7},{label:'4 weeks',day:28},{label:'8 weeks',day:56},{label:'16 weeks',day:112}],
  phases: [
    {day:0, hold:4.5, chip:'START', sub:'Four minutes hard, three easy, four times over. Three days a week. Here is what it does, and when.',
      caption:'ONE SESSION · 4 × 4 MIN AT 90–95% OF MAX HEART RATE', credit:'Heart-rate trace · schematic',
      illo:{kind:'protocol',blocks:[[8,0.62],[4,0.93],[3,0.7],[4,0.93],[3,0.7],[4,0.93],[3,0.7],[4,0.93],[5,0.6]],zone:[0.88,0.97],zoneLabel:'4×4 zone',zoneColor:'#e34948',tick:10,sweep:(d,t)=>Math.min(1,t/3.6)}},
    {day:1, hold:6.5, chip:'DAY 1 · SESSION 1', sub:'One hard session flips the mitochondria gene on about ten times over. An easy jog manages four.',
      caption:'ONE FIBRE · NUCLEI SENDING BUILD ORDERS', illo:{kind:'signal',level:1,mito:0.3}, highlight:['signal']},
    {day:7, hold:6.5, chip:'WEEK 1 · 3 SESSIONS', sub:'Three sessions in, the enzymes that burn fuel with oxygen are already up. You cannot feel it yet.',
      caption:'THIGH MUSCLE · GREEN: MITOCHONDRIA', illo:{kind:'fibres',mito:(d)=>Math.min(1,(d-1)/16),cap:0}, highlight:['mito']},
    {day:28, hold:7, chip:'WEEK 4 · 12 SESSIONS', sub:'By week two, fat burning at easy pace is up a third. Inside the muscle, most of the change is done.',
      caption:'THIGH MUSCLE · GREEN: MITOCHONDRIA · RED: CAPILLARIES', illo:{kind:'fibres',mito:(d)=>Math.min(1,(d-1)/16),cap:(d)=>Math.min(1,(d-10)/40)}, highlight:['fat','mito']},
    {day:56, hold:8, chip:'WEEK 8 · 24 SESSIONS', sub:'Now the heart: 10% more blood per beat. VO₂max up 7 to 13%. Same work at 70% effort moved it 0%.',
      caption:'LEFT VENTRICLE · MORE BLOOD PER BEAT', illo:{kind:'heart',sv:(d)=>Math.min(1,(d-7)/49)}, highlight:['heart','fit']},
    {day:112, hold:7, chip:'WEEK 16 · 48 SESSIONS', sub:'Keep going and the artery lining responds too. Unfit starters have gained up to 35% by now.',
      caption:'ARTERY · WIDENS MORE WHEN ASKED (FMD)', illo:{kind:'blood',plasma:(d)=>Math.min(1,(d-28)/84),rbc:0.5}, highlight:['vessel','fit']},
    {day:112, travel:0.5, hold:6, chip:'WEEK 16 · 48 SESSIONS', sub:'The dose is 24 sessions, not one. If week two feels like nothing happened, that is on schedule.',
      caption:'ARTERY · WIDENS MORE WHEN ASKED (FMD)', illo:{kind:'blood',plasma:1,rbc:0.5}, highlight:['fit']}
  ],
  rows: [
    {key:'signal',label:'SIGNAL',sub:'PGC-1α, per session',color:'#2a78d6',segments:[{kind:'dot',at:0.15,value:'×10'}]},
    {key:'mito',label:'MITOCHONDRIA',sub:'enzymes, then volume',color:'#eb6834',segments:[{kind:'bar',from:1,to:14,value:'+20–30%'}]},
    {key:'fat',label:'FAT BURNING',sub:'at easy pace',color:'#008300',segments:[{kind:'bar',from:3,to:14,value:'+36%',labelPos:'end'}]},
    {key:'heart',label:'HEART',sub:'blood per beat',color:'#4a3aa7',segments:[{kind:'bar',from:7,to:56,value:'+10%'}]},
    {key:'vessel',label:'ARTERIES',sub:'how well they widen',color:'#e87ba4',segments:[{kind:'bar',from:28,to:112,value:'+9% (steady +5%)',small:true,anchor:'end'}]},
    {key:'fit',label:'FITNESS',sub:'VO₂max',sub2:'same work at 70%: 0%',big:true,color:'#e34948',segments:[{kind:'bar',from:4,to:56,value:'+7–13%',bigValue:true},{kind:'bar',from:56,to:112,light:true,value:'up to +35% if unfit',small:true,below:true,anchor:'end'}]}
  ]
};
