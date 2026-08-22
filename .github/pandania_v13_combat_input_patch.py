from pathlib import Path
import re

path=Path('Adventures Of Pandania The Lost Realms/index.html')
text=path.read_text(encoding='utf-8')
text=re.sub(r'<!-- ===== PANDANIA V13 COMBAT/INPUT PATCH ===== -->.*?<!-- ===== END PANDANIA V13 COMBAT/INPUT PATCH ===== -->','',text,flags=re.S)

patch=r'''<!-- ===== PANDANIA V13 COMBAT/INPUT PATCH ===== -->
<style>
.pandaniaWeaponGreenStats{margin-top:6px;padding:5px 4px;border-radius:5px;background:#0d4120;border:1px solid #25e86e;color:#69ff9a;font-size:10px;font-weight:800;line-height:1.45;text-align:center;box-shadow:0 0 6px rgba(37,232,110,.22)}
.pandaniaWeaponGreenStats .critChance{color:#7dffad}.pandaniaWeaponGreenStats .critDamage{color:#ffe66b}
@media(max-width:700px),(pointer:coarse){.pandaniaWeaponGreenStats{font-size:9px;padding:4px 2px}}
</style>
<script>
(function(){
'use strict';

/* Per-weapon critical stats. */
const critStats={
 'Wooden Sword':{chance:.05,bonus:.05},
 'Bamboo Sword':{chance:.08,bonus:.06},
 'Iron Sword':{chance:.12,bonus:.08},
 'Goblin Saber':{chance:.15,bonus:.10},
 'XPR Lens':{chance:.18,bonus:.12},
 'Spiked Twin Blade':{chance:.22,bonus:.14},
 'Purple Ice Blade':{chance:.27,bonus:.15},
 'Diamond staff':{chance:.32,bonus:.16},
 'Golden Beacon Staff':{chance:.40,bonus:.18},
 'Thunderma':{chance:.45,bonus:.19},
 'Purplereign':{chance:.50,bonus:.20}
};
window.__pandaniaWeaponCritStatsV13=critStats;

function isMobile(){try{return matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches}catch(e){return false}}
function weaponName(){return(window.__pandaniaEquipment&&window.__pandaniaEquipment.weapon)||'Wooden Sword'}
function weaponRange(n){const r=window.__pandaniaWeaponStats||{};return r[n]||r['Wooden Sword']||{min:8,max:12}}

/* ---------------------------------------------------------
   SAFE WORLD CLICK HANDLING
   Desktop + mobile: screen clicks/taps cannot move the player.
   Ground drops are the one exception: clicking a visible item
   attempts pickup with a generous radius. Nothing calls renderBag
   unless the pickup actually succeeds, and all UI refreshes are guarded.
--------------------------------------------------------- */
function worldPoint(e){
 const rect=canvas.getBoundingClientRect();
 const sx=(e.clientX-rect.left)*(W/rect.width);
 const sy=(e.clientY-rect.top)*(H/rect.height);
 const z=isMobile()&&typeof pandaniaMobileZoom==='function'?pandaniaMobileZoom():1;
 if(z!==1){
   const vw=W/z,vh=H/z;
   return{x:camera.x+vw/2+(sx-W/2)/z,y:camera.y+vh/2+(sy-H/2)/z};
 }
 return{x:sx+camera.x,y:sy+camera.y};
}
function safePickupAt(p){
 if(!Array.isArray(groundDrops)||!groundDrops.length)return false;
 let index=-1,best=Infinity;
 for(let i=groundDrops.length-1;i>=0;i--){
   const d=groundDrops[i];
   if(!d||!Number.isFinite(d.x)||!Number.isFinite(d.y))continue;
   const dist=Math.hypot(p.x-d.x,p.y-d.y);
   if(dist<125&&dist<best){best=dist;index=i;}
 }
 if(index<0)return false;
 const drop=groundDrops[index];
 if(typeof collectDrop!=='function')return false;
 let ok=false;
 try{ok=collectDrop(drop)===true}catch(err){console.error('Pandania pickup error:',err);return false}
 if(!ok)return true;
 groundDrops.splice(index,1);
 try{updateUI()}catch(err){console.warn('Pickup UI refresh skipped:',err)}
 /* Do NOT force a bag render here. This was one of the freeze paths. */
 return true;
}

function blockWorldMovement(e){
 if(e.target!==canvas||!gameStarted)return;
 const p=worldPoint(e);
 if(safePickupAt(p)){e.preventDefault();e.stopImmediatePropagation();return;}
 /* All other screen clicks are ignored for movement. */
 e.preventDefault();e.stopImmediatePropagation();
}
['pointerdown','mousedown','click','dblclick','contextmenu'].forEach(type=>{
 canvas.addEventListener(type,blockWorldMovement,true);
});

/* ---------------------------------------------------------
   CRITICAL COMBAT
--------------------------------------------------------- */
window.swordAttack=function(target=null){
 if(player.attackCooldown>0)return;
 player.attackCooldown=22;player.swordSwing=12;
 if(typeof swordSound==='function')swordSound();
 if(!target){
  let closest=null,distance=Infinity;
  for(const m of monsters){
   const vx=m.x-player.x,vy=m.y-player.y,d=Math.hypot(vx,vy);
   if(d>95||d<1)continue;
   const dot=(vx*(player.facingX||0)+vy*(player.facingY||0))/d;
   if(dot>=.15&&d<distance){closest=m;distance=d}
  }
  if(!closest)for(const m of monsters){const d=Math.hypot(m.x-player.x,m.y-player.y);if(d<82&&d<distance){closest=m;distance=d}}
  target=closest;
 }
 if(!target){if(typeof showMessage==='function')showMessage('⚔️ Sword swing!');return}
 if(Math.hypot(target.x-player.x,target.y-player.y)>88)return;
 const n=weaponName(),r=weaponRange(n),s=critStats[n]||critStats['Wooden Sword'];
 let damage=Math.floor(Math.random()*(r.max-r.min+1))+r.min;
 damage=Math.max(1,damage-(target.defense||0));
 const crit=Math.random()<s.chance;
 if(crit)damage=Math.max(1,Math.round(damage*(1+s.bonus)));
 target.hp-=damage;
 addDamageNumber(target.x,target.y-38,damage,'#fff',crit);
 target.hitFlash=8;
 if(typeof hitSound==='function')hitSound();
 if(typeof showMessage==='function')showMessage(crit?'💥 CRITICAL! '+target.name+' for '+damage+' damage!':'⚔️ Hit '+target.name+' for '+damage+' damage!');
 if(target.hp<=0&&typeof killMonster==='function')killMonster(target);
};

/* ---------------------------------------------------------
   DAMAGE NUMBERS
--------------------------------------------------------- */
window.drawDamageNumbers=function(){
 for(const d of damageNumbers){
  ctx.save();
  ctx.globalAlpha=Math.max(0,d.life/d.maxLife);
  ctx.textAlign='center';
  if(d.crit){
   ctx.font='900 36px Arial';
   ctx.fillStyle='#ffe94a';
   ctx.shadowColor='#ff102b';
   ctx.shadowBlur=26;
   ctx.lineWidth=3;
   ctx.strokeStyle='#ff1835';
   ctx.strokeText(String(d.amount),d.x,d.y);
   ctx.fillText(String(d.amount),d.x,d.y);
  }else{
   ctx.font='900 20px Arial';
   ctx.fillStyle='#fff';
   ctx.shadowColor='#000';
   ctx.shadowBlur=4;
   ctx.fillText(String(d.amount),d.x,d.y);
  }
  ctx.restore();
 }
};

/* ---------------------------------------------------------
   WEAPON INVENTORY STATS
   No MutationObserver and no interval: those caused the bag
   freeze by repeatedly mutating the DOM while observing it.
--------------------------------------------------------- */
function refreshWeaponStats(){
 try{
  document.querySelectorAll('#bagItems .itemCard').forEach(card=>{
   const e=card.querySelector('.itemName');if(!e)return;
   const n=e.textContent.trim(),s=critStats[n];if(!s)return;
   let b=card.querySelector('.pandaniaWeaponGreenStats');
   if(!b){b=document.createElement('div');b.className='pandaniaWeaponGreenStats';card.appendChild(b)}
   const r=weaponRange(n);
   b.innerHTML='ATK '+r.min+'–'+r.max+' · CRIT <span class="critChance">'+Math.round(s.chance*100)+'%</span> · CRIT DMG <span class="critDamage">+'+Math.round(s.bonus*100)+'%</span>';
  });
 }catch(err){console.warn('Weapon stat refresh skipped:',err)}
}
window.__pandaniaRefreshWeaponStats=refreshWeaponStats;

/* Refresh only when the bag is actually opened, never continuously. */
const originalOpenBag=window.openBag;
if(typeof originalOpenBag==='function'&&!window.__pandaniaSafeOpenBagV13){
 window.openBag=function(){
  try{originalOpenBag.apply(this,arguments)}catch(err){console.error('Pandania bag open recovered:',err);return}
  setTimeout(refreshWeaponStats,0);
 };
 window.__pandaniaSafeOpenBagV13=true;
}
setTimeout(refreshWeaponStats,150);

/* ---------------------------------------------------------
   REMOVE THE OLD V13 MONSTER-EMOJI OVERLAY.
   The real image renderer already draws the monster artwork.
--------------------------------------------------------- */
window.__pandaniaWideDraw=false;

/* Mobile-only monster width: modify the sprite draw itself, not the
   entire game draw pass, so opening UI cannot trigger a second renderer. */
try{
 const originalSprite=window.drawSprite;
 if(typeof originalSprite==='function'&&!window.__pandaniaWideSpriteV13){
  const monsterImages=new Set(['monster1','monster2','monster3','monster4','monster5','monster6','monster7','boss1','boss2','boss3','roamer1']);
  window.drawSprite=function(imageKey,x,y,width,height,flip=false,alpha=1){
   if(!isMobile()||!monsterImages.has(imageKey))return originalSprite.apply(this,arguments);
   const img=images[imageKey];if(!img)return originalSprite.apply(this,arguments);
   ctx.save();ctx.globalAlpha=alpha;ctx.translate(x,y);if(flip)ctx.scale(-1,1);ctx.scale(1.15,1);ctx.imageSmoothingEnabled=false;ctx.drawImage(img,-width/2,-height,width,height);ctx.restore();return true;
  };
  window.__pandaniaWideSpriteV13=true;
 }
}catch(err){console.warn('Mobile monster width patch skipped:',err)}

window.__pandaniaV13=true;
window.__pandaniaPickupFixV13=true;
})();
</script>
<!-- ===== END PANDANIA V13 COMBAT/INPUT PATCH ===== -->'''

text=text.replace('</body>',patch+'\n</body>',1) if '</body>' in text else text+'\n'+patch+'\n'
path.write_text(text,encoding='utf-8')
