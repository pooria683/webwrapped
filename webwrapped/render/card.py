"""JavaScript canvas share-card renderer embedded in the story."""
CANVAS_SCRIPT = r'''
function cardData(redact) {
  const top = DATA.top_sites.slice(0, 3).map((x,i) => redact ? `Favourite site #${i+1}` : x.site);
  return {top};
}
function downloadCard() {
  const c=document.createElement('canvas'); c.width=1080; c.height=1350; const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,1080,1350); g.addColorStop(0,'#6d28d9'); g.addColorStop(.5,'#db2777'); g.addColorStop(1,'#f97316'); x.fillStyle=g; x.fillRect(0,0,c.width,c.height);
  x.fillStyle='rgba(255,255,255,.12)'; x.beginPath(); x.arc(900,180,330,0,Math.PI*2); x.fill(); x.beginPath(); x.arc(120,1260,400,0,Math.PI*2); x.fill();
  x.fillStyle='#fff'; x.font='700 44px system-ui'; x.fillText('MY WEB, WRAPPED',80,110); x.font='900 180px system-ui'; x.fillText(String(DATA.year),72,285);
  x.font='900 155px system-ui'; x.fillText(DATA.total_visits.toLocaleString(),72,520); x.font='600 44px system-ui'; x.fillText('pages visited',80,580);
  x.font='800 44px system-ui'; x.fillText('MY TOP CORNERS OF THE WEB',80,745); const d=cardData(REDACT);
  d.top.forEach((s,i)=>{x.font='900 68px system-ui'; x.fillText(`${i+1}`,80,850+i*105); x.font='700 46px system-ui'; x.fillText(s.slice(0,31),150,850+i*105)});
  x.font='700 36px system-ui'; x.fillText(`${DATA.night_owl_score}% after midnight  •  ${DATA.longest_streak_days} day streak`,80,1200); x.font='600 30px system-ui'; x.fillText('Made locally with webwrapped — nothing uploaded',80,1280);
  const a=document.createElement('a'); a.download=`webwrapped-${DATA.year}.png`; a.href=c.toDataURL('image/png'); a.click();
}
'''
