window.VIDEO = {
  kicker: 'MECHANISM · CARDIO · STEADY STATE',
  title: 'Why cardio fitness takes weeks to show',
  accent: '#a3232d',
  sources: 'Egan 2010 · Gillen 1991 · Montero 2017 · Hoier 2012 · Meinild Lundby 2018 · Hoppeler 1985 · Helgerud 2007 · Murias 2010 · Scharhag-Rosenberger 2009',
  axis: [{label:'start',day:0},{label:'1 day',day:1},{label:'1 week',day:7},{label:'4 weeks',day:28},{label:'12 weeks',day:84}],
  phases: [
    {day:0, hold:4.5, chip:'START', sub:'Forty steady minutes, three times a week. What one session sets off, and how long each part takes.',
      caption:'ONE SESSION · 40 MIN AT ABOUT 70% OF MAX HEART RATE', credit:'Heart-rate trace · schematic',
      illo:{kind:'protocol',blocks:[[5,0.6],[30,0.72],[5,0.58]],zone:[0.65,0.77],zoneLabel:'steady state',zoneColor:'#e34948',tick:10,sweep:(d,t)=>Math.min(1,t/3.6)}},
    {day:1, hold:6.5, chip:'DAY 1', sub:'Within hours the mitochondria gene flips on, 4 to 10 times over. By tomorrow it is off again.',
      caption:'ONE FIBRE · NUCLEI SENDING BUILD ORDERS', illo:{kind:'signal',level:1,mito:0.3}, highlight:['signal']},
    {day:7, hold:6.5, chip:'WEEK 1 · 3 SESSIONS', sub:'Blood plasma expands first. Up to a fifth more fluid within weeks, before anything new is built.',
      caption:'BLOOD VESSEL · MORE PLASMA, SAME RED CELLS', illo:{kind:'blood',plasma:(d)=>Math.min(1,d/21),rbc:0}, highlight:['blood']},
    {day:28, hold:7, chip:'WEEK 4 · 12 SESSIONS', sub:'Mitochondria multiply in the fibres. Capillaries grow around them. Test scores: up a few percent.',
      caption:'THIGH MUSCLE · GREEN: MITOCHONDRIA · RED: CAPILLARIES', illo:{kind:'fibres',mito:(d)=>Math.min(1,(d-2)/40),cap:(d)=>Math.min(1,(d-10)/32)}, highlight:['mito','cap']},
    {day:84, hold:8, chip:'WEEK 12 · 36 SESSIONS', sub:'Red cells catch up. The heart pumps more per beat. VO₂max lands 10 to 18% higher than it started.',
      caption:'LEFT VENTRICLE · MORE BLOOD PER BEAT', illo:{kind:'heart',sv:(d)=>Math.min(1,(d-7)/77)}, highlight:['heart','fit']},
    {day:84, travel:0.5, hold:6, chip:'WEEK 12 · 36 SESSIONS', sub:'Judge a cardio plan at week eight, not week two. The early work is real. It is just invisible.',
      caption:'LEFT VENTRICLE · MORE BLOOD PER BEAT', illo:{kind:'heart',sv:1}, highlight:['fit']}
  ],
  rows: [
    {key:'signal',label:'SIGNAL',sub:'PGC-1α, per session',color:'#2a78d6',segments:[{kind:'dot',at:0.15,value:'×4 to ×10'}]},
    {key:'blood',label:'BLOOD',sub:'plasma, then red cells',color:'#1baf7a',segments:[{kind:'bar',from:0.3,to:28,value:'+20% plasma',labelPos:'mid'},{kind:'bar',from:28,to:84,light:true,value:'red cells +12%',small:true,anchor:'end'}]},
    {key:'mito',label:'MITOCHONDRIA',sub:'the power plants',color:'#eb6834',segments:[{kind:'bar',from:2,to:42,value:'+40%'}]},
    {key:'cap',label:'CAPILLARIES',sub:'new blood vessels',color:'#e87ba4',segments:[{kind:'bar',from:10,to:42,value:'+20%'}]},
    {key:'heart',label:'HEART',sub:'blood per beat',color:'#4a3aa7',segments:[{kind:'bar',from:7,to:56,value:'+10%'}]},
    {key:'fit',label:'FITNESS',sub:'VO₂max',sub2:'the number you can test',big:true,color:'#e34948',segments:[{kind:'ring',at:1,value:'no change'},{kind:'bar',from:5,to:84,value:'+10 to 18%',bigValue:true,anchor:'end'}]}
  ]
};
