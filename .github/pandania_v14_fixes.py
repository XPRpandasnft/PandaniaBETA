from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)
s=s.replace("if(typeof window.imageFiles==='object'&&window.imageFiles[ref])return window.imageFiles[ref];","if(typeof imageFiles!='undefined'&&imageFiles&&imageFiles[ref])return imageFiles[ref];")

patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
#pandaniaEquipment{position:relative;box-sizing:border-box;overflow:visible!important}
#pandaniaEquipment #equipWeapon{position:relative;box-sizing:border-box;overflow:visible!important;min-width:0}
.paperDollWeaponArt{height:72px;display:flex;align-items:center;justify-content:center;overflow:visible;margin:0 auto 3px;position:relative;z-index:5}
.paperDollEquipImage{display:block;width:72px;height:72px;max-width:72px;max-height:72px;object-fit:contain;margin:0 auto 3px;image-rendering:auto;position:relative;z-index:10;visibility:visible;opacity:1}
@media(max-width:700px),(pointer:coarse){
#stats{width:185px!important;padding:5px 6px!important;opacity:1!important;background:rgba(10,10,10,.94)!important;transform:scale(.82);transform-origin:top left}
#minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important}
#pandaniaMobileControls{display:none!important}#gameWrap.pandaniaStarted #pandaniaMobileControls{display:flex!important}
#pandaniaEquipment{width:100%!important;max-width:94vw!important;padding:10px!important;overflow:visible!important}
#pandaniaEquipment>div:nth-child(2){display:grid!important;grid-template-columns:minmax(0,1fr) 92px minmax(0,1fr)!important;gap:6px!important;align-items:center!important;width:100%!important;overflow:visible!important}
#pandaniaEquipment>div:nth-child(2)>#equipWeapon,#pandaniaEquipment>div:nth-child(2)>#equipArmor{min-width:0!important;width:100%!important;padding:6px!important;overflow:visible!important;word-break:break-word!important}
#pandaniaEquipment>div:nth-child(2)>div:nth-child(2){width:92px!important;min-width:92px!important;height:110px!important;font-size:48px!important;overflow:visible!important}
.paperDollWeaponArt{height:60px!important;width:100%!important;overflow:visible!important}.paperDollEquipImage{width:60px!important;height:60px!important;max-width:60px!important;max-height:60px!important;display:block!important;visibility:visible!important;opacity:1!important;object-fit:contain!important;z-index:50!important}
}
</style>
<script>
(function(){'use strict';
function refreshSameRenderer(){try{if(typeof window.renderBag==='function')window.renderBag();}catch(e){console.warn('Pandania equipment refresh skipped:',e);}}
window.__pandaniaFixEquippedWeaponV14=refreshSameRenderer;window.__pandaniaFinalFixV11=true;
document.addEventListener('click',function(e){const t=e.target;if(t&&((t.id==='playButton')||(t.closest&&t.closest('#bagWindow'))))setTimeout(refreshSameRenderer,50);},true);
window.addEventListener('resize',function(){setTimeout(refreshSameRenderer,50)},{passive:true});window.addEventListener('orientationchange',function(){setTimeout(refreshSameRenderer,100)},{passive:true});})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->

<!-- ===== PANDANIA FINAL BOSS4 / STAIRS / GROUNDING FIX ===== -->
<script>
(function(){'use strict';
window.__boss4EarthquakeFrames=window.__boss4EarthquakeFrames||0;window.__boss4EarthquakeStrength=4.5;
const priorMonsterUpdate=updateMonsters;
updateMonsters=function(){
  priorMonsterUpdate();
  if(!inDungeon){window.__boss4EarthquakeFrames=0;if(Array.isArray(window.__stableMetalMeteors))window.__stableMetalMeteors.length=0;return;}
  if(typeof dungeonLevel!=='undefined'&&dungeonLevel===4){
    for(const m of monsters){if(m.type!=='boss4')continue;const cd=m.__stableMeteorCooldown;if(typeof cd==='number'&&cd>0&&cd<=60&&!m.__boss4ShakeWarned){m.__boss4ShakeWarned=true;window.__boss4EarthquakeFrames=24;if(typeof showMessage==='function')showMessage('🌋 The dungeon begins to shake...');}if(typeof cd==='number'&&cd>60)m.__boss4ShakeWarned=false;}
    if(Array.isArray(window.__stableMetalMeteors)){
      const z=typeof pandaniaMobileZoom==='function'?pandaniaMobileZoom():1,visibleH=H/Math.max(.1,z),ceilingY=Math.max(90,(camera.y-visibleH/2)-110);
      for(const q of window.__stableMetalMeteors){if(!q.__ceilingSpawnFixed){q.__ceilingSpawnFixed=true;q.x=Math.max(95,Math.min(dungeon.width-95,q.x));q.y=ceilingY-Math.random()*80;q.life=220;q.dropSpeed=12.5;}if(q.dropSpeed)q.y+=q.dropSpeed-9.5;}
    }
  }else if(Array.isArray(window.__stableMetalMeteors))window.__stableMetalMeteors.length=0;
  if(window.__boss4EarthquakeFrames>0)window.__boss4EarthquakeFrames--;
};
window.__pandaniaFloorBossSpawned=window.__pandaniaFloorBossSpawned||false;
const priorSpawnDungeonLevel=spawnDungeonLevel;
spawnDungeonLevel=function(level){dungeonStairOpen=false;window.__pandaniaFloorBossSpawned=true;window.__boss4EarthquakeFrames=0;if(Array.isArray(window.__stableMetalMeteors))window.__stableMetalMeteors.length=0;return priorSpawnDungeonLevel(level);};
const priorPlayerUpdate=updatePlayer;
updatePlayer=function(){
  priorPlayerUpdate();if(!inDungeon||!window.__pandaniaFloorBossSpawned||dungeonStairOpen)return;
  if(!monsters.some(m=>m.boss&&(m.dungeonLevel||1)===dungeonLevel)){dungeonStairOpen=true;if(typeof showMessage==='function')showMessage(dungeonLevel<4?'⬇️ The downward stairs have opened!':'🏆 Metal Monster defeated! The dungeon stairs are now visible.');}
};
function renderGroundedMonster(m){
  const floating=m.type==='boss3'||m.type==='roamer1',size=m.type==='roamer1'?110:(m.boss?120:65),off=floating?0:12;
  if(floating){ctx.save();ctx.fillStyle='rgba(0,0,0,.35)';ctx.beginPath();ctx.ellipse(m.x,m.y+5,m.r+5,8,0,0,Math.PI*2);ctx.fill();ctx.restore();}
  const drawn=drawSprite(m.image,m.x,m.y+off,size,size,false,1);
  if(!drawn){ctx.fillStyle=m.boss?'#5b1d32':'#75a83f';ctx.beginPath();ctx.arc(m.x,m.y+off-25,m.boss?40:22,0,Math.PI*2);ctx.fill();}
  const bw=(m.boss||m.type==='roamer1')?110:50;ctx.fillStyle='#191919';ctx.fillRect(m.x-bw/2,m.y+off-size-8,bw,7);ctx.fillStyle=m.boss?'#d7263d':'#e74c3c';ctx.fillRect(m.x-bw/2,m.y+off-size-8,bw*Math.max(0,m.hp/m.maxHp),7);ctx.fillStyle='#fff';ctx.font=m.boss?'bold 13px Arial':'9px Arial';ctx.textAlign='center';ctx.fillText(m.name,m.x,m.y+off-size-12);if(m.boss){ctx.fillStyle='#ffd36b';ctx.font='bold 11px Arial';ctx.fillText('BOSS',m.x,m.y+off-size-27);}if(m.hitFlash){ctx.fillStyle='rgba(255,70,70,.35)';ctx.beginPath();ctx.arc(m.x,m.y+off-30,size*.45,0,Math.PI*2);ctx.fill();}
}
drawMonster=function(m){renderGroundedMonster(m);};drawStableMonster=function(m){renderGroundedMonster(m);};
const priorStableDungeonRenderer=drawStableDungeon;
drawStableDungeon=function(){
  if(window.__boss4EarthquakeFrames>0&&typeof dungeonLevel!=='undefined'&&dungeonLevel===4){const ox=camera.x,oy=camera.y,s=window.__boss4EarthquakeStrength;camera.x=ox+(Math.random()*2-1)*s;camera.y=oy+(Math.random()*2-1)*s;try{priorStableDungeonRenderer();}finally{camera.x=ox;camera.y=oy;}}else priorStableDungeonRenderer();
};
window.__pandaniaFinalBoss4DungeonFix=true;
})();
</script>
<!-- ===== END PANDANIA FINAL BOSS4 / STAIRS / GROUNDING FIX ===== -->'''

s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')

# Final Boss4 telegraph override: preserve existing game systems but make the
# authoritative meteor layer show a 1-second warning at the exact impact point.
telegraph=r'''<!-- ===== BOSS4 METEOR TELEGRAPH / IMAGE TIMING FIX ===== -->
<script>
(function(){'use strict';
if(typeof window.__finalBoss4Meteors==='undefined')window.__finalBoss4Meteors=[];
window.__boss4TelegraphVersion='v2';
const oldFinalBoss4Tick=window.__finalBoss4Tick;
if(typeof oldFinalBoss4Tick!=='function')return;
window.__finalBoss4Tick=function(){
  const now=performance.now();
  oldFinalBoss4Tick();
  const list=window.__finalBoss4Meteors;
  for(const q of list){
    if(q.warningUntil===undefined){q.warningUntil=now+1000;q.dropAt=q.warningUntil;q.active=false;q.impacted=false;}
  }
};
const oldFinalBoss4DrawWorld=window.__finalBoss4DrawWorld;
window.__finalBoss4DrawWorld=function(){
  if(typeof oldFinalBoss4DrawWorld!=='function')return;
  if(!(inDungeon&&typeof dungeonLevel!=='undefined'&&dungeonLevel===4))return;
  const now=performance.now();
  const list=window.__finalBoss4Meteors||[];
  for(const q of list){
    if(q.warningUntil!==undefined&&now<q.warningUntil){
      ctx.save();
      ctx.globalAlpha=.72+Math.sin(now/100)*.12;
      ctx.fillStyle='rgba(0,0,0,.62)';
      ctx.shadowColor='rgba(0,0,0,.9)';ctx.shadowBlur=8;
      ctx.beginPath();ctx.arc(q.x,q.targetY,24,0,Math.PI*2);ctx.fill();
      ctx.shadowBlur=0;
      ctx.strokeStyle='rgba(255,255,255,.55)';ctx.lineWidth=2;
      ctx.beginPath();ctx.arc(q.x,q.targetY,23,0,Math.PI*2);ctx.stroke();
      ctx.restore();
    }
  }
  oldFinalBoss4DrawWorld();
};
})();
</script>
<!-- ===== END BOSS4 METEOR TELEGRAPH / IMAGE TIMING FIX ===== -->'''
s=s.replace('</body>',telegraph+'\n</body>',1) if '</body>' in s else s+'\n'+telegraph
p.write_text(s,encoding='utf-8')
