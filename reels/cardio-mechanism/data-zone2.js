window.VIDEO = {
  kicker: 'MECHANISM · CARDIO · ZONE 2',
  title: 'What 300 minutes a week of zone 2 builds',
  accent: '#a3232d',
  rowH: 79,
  sources: 'Egan 2010 · Phillips 1996 · Venables 2008 · Meinild Lundby 2018 · Hoier 2012 · Ingjer 1979 · Davis 1979 · Montero & Lundby 2017 · Ross 2015 · Scharhag-Rosenberger 2009',
  axis: [{label:'start',day:0},{label:'1 week',day:7},{label:'4 weeks',day:28},{label:'12 weeks',day:84},{label:'24 weeks',day:168}],
  phases: [
    {day:0, hold:4.5, chip:'START', sub:'Five easy hours a week, at a pace where you can still talk. What that builds, and how slowly.',
      caption:'ONE SESSION · 60 MIN AT 60–70% OF MAX HEART RATE', credit:'Heart-rate trace · schematic',
      illo:{kind:'protocol',blocks:[[5,0.55],[55,0.67],[5,0.55]],zone:[0.6,0.7],zoneLabel:'zone 2',zoneColor:'#1baf7a',color:'#5ad7a3',tick:10,sweep:(d,t)=>Math.min(1,t/3.6)}},
    {day:7, hold:7, chip:'WEEK 1 · 5 SESSIONS', sub:'One session only nudges the mitochondria gene. You do five. Fat burning is up 10% by day five.',
      caption:'ONE FIBRE · NUCLEI SENDING SMALL BUILD ORDERS', illo:{kind:'signal',level:0.45,mito:0.35}, highlight:['signal','fat']},
    {day:28, hold:7.5, chip:'WEEK 4 · 20 SESSIONS', sub:'Mitochondria are growing in volume. Capillaries up a fifth. Fat burning at easy pace up 44%.',
      caption:'THIGH MUSCLE · GREEN: MITOCHONDRIA · RED: CAPILLARIES', illo:{kind:'fibres',mito:(d)=>Math.min(1,(d-3)/40),cap:(d)=>Math.min(1,(d-10)/20)}, highlight:['mito','cap']},
    {day:84, hold:7.5, chip:'WEEK 12 · 60 SESSIONS', sub:'The pace you can hold before the burn is up about 15%. Resting heart rate is down a few beats.',
      caption:'LEFT VENTRICLE · MORE BLOOD PER BEAT, FEWER BEATS', illo:{kind:'heart',sv:(d)=>Math.min(1,(d-7)/100),hr:(d)=>1-0.15*Math.min(1,d/168)}, highlight:['lt','rhr']},
    {day:168, hold:8, chip:'WEEK 24 · 120 SESSIONS', sub:'VO₂max up around 15%, and at this dose almost nobody fails to respond. Waist down about 4.6 cm.',
      caption:'LEFT VENTRICLE · MORE BLOOD PER BEAT, FEWER BEATS', illo:{kind:'heart',sv:(d)=>Math.min(1,(d-7)/100),hr:(d)=>1-0.15*Math.min(1,d/168)}, highlight:['fit']},
    {day:168, travel:0.5, hold:6, chip:'WEEK 24 · 120 SESSIONS', sub:'Zone 2 pays by the hour. Five hours a week beats three, and the gap only opens after month four.',
      caption:'LEFT VENTRICLE · MORE BLOOD PER BEAT, FEWER BEATS', illo:{kind:'heart',sv:1,hr:0.85}, highlight:['fit']}
  ],
  rows: [
    {key:'signal',label:'SIGNAL',sub:'PGC-1α, per session',color:'#2a78d6',segments:[{kind:'dot',at:0.15,value:'×3 to ×4'}]},
    {key:'mito',label:'MITOCHONDRIA',sub:'total volume',color:'#eb6834',segments:[{kind:'bar',from:3,to:42,value:'+40–55%'}]},
    {key:'fat',label:'FAT BURNING',sub:'at easy pace',color:'#008300',segments:[{kind:'bar',from:2,to:5,value:'+10%'},{kind:'bar',from:5,to:28,value:'+44%'}]},
    {key:'cap',label:'CAPILLARIES',sub:'new blood vessels',color:'#e87ba4',segments:[{kind:'bar',from:10,to:28,value:'+23%'},{kind:'bar',from:28,to:168,light:true,value:'+29%',anchor:'end'}]},
    {key:'lt',label:'THRESHOLD',sub:'pace before the burn',color:'#4a3aa7',segments:[{kind:'bar',from:14,to:63,value:'+15% of max'}]},
    {key:'rhr',label:'RESTING PULSE',sub:'beats per minute',color:'#1baf7a',segments:[{kind:'bar',from:14,to:168,value:'−5 to −9 bpm',anchor:'end'}]},
    {key:'fit',label:'FITNESS',sub:'VO₂max',sub2:'non-responders at this dose: 0%',big:true,color:'#e34948',segments:[{kind:'ring',at:3,value:'no change'},{kind:'bar',from:6,to:84,value:'~+10%',small:true,labelPos:'mid'},{kind:'bar',from:84,to:168,value:'~+15%',bigValue:true,anchor:'end'}]}
  ]
};
