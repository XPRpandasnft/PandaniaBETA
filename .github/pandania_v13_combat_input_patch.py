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
(function(){'use strict';
const critStats={
 'Wooden Sword':{chance:.05,bonus:.05},'Bamboo Sword':{chance:.08,bonus:.06},'Iron Sword':{chance:.12,bonus:.08},
 'Goblin Saber':{chance:.15,bonus:.10},'XPR Lens':{chance:.18,bonus:.12},'Spiked Twin Blade':{chance:.22,bonus:.14},
 'Purple Ice Blade':{chance:.27,bonus:.15},'Diamond staff':{chance:.32,bonus:.16},'Golden Beacon Staff':{chance:.40,bonus:.18},
 'Thunderma':{chance:.45,bonus:.19},'Purplereign':{chance:.50,bonus:.20}
};
window.__pandaniaWeaponCritStatsV13=critStats;
const isMobile=()=>matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches;
/* Screen taps are never movement on desktop or mobile. */
function blockMove(e){if(e.target!==canvas)return;if(!gameStarted&&!gameWrap.classList.contains('pandaniaStarted'))return;e.preventDefault();e.stopImmediatePropagation()}
['pointerdown','pointerup','mousedown','mouseup','click','dblclick','contextmenu'].forEach(t=>canvas.addEventListener(t,blockMove,true));
function weaponName(){return(window.__pandaniaEquipment&&window.__pandaniaEquipment.weapon)||'Wooden Sword'}
function weaponRange(n){const r=window.__pandaniaWeaponStats||{};return r[n]||r['Wooden Sword']||{min:8,max:12}}
/* One authoritative attack function: individual chance + individual bonus. */
window.swordAttack=function(target){
 if(player.attackCooldown>0)return;player.attackCooldown=22;player.swordSwing=12;
 if(!target){let c=null,d0=Infinity;for(const m of monsters){const vx=m.x-player.x,vy=m.y-player.y,d=Math.hypot(vx,vy);if(d>95||d<1)continue;const dot=(vx*(player.facingX||0)+vy*(player.facingY||0))/d;if(dot>=.15&&d<d0){c=m;d0=d}}if(!c)for(const m of monsters){const d=Math.hypot(m.x-player.x,m.y-player.y);if(d<82&&d<d0){c=m;d0=d}}target=c}
 if(!target){showMessage('⚔️ Sword swing!');return}if(Math.hypot(target.x-player.x,target.y-player.y)>88)return;
 const n=weaponName(),r=weaponRange(n),s=critStats[n]||critStats['Wooden Sword'];let damage=Math.floor(Math.random()*(r.max-r.min+1))+r.min;damage=Math.max(1,damage-(target.defense||0));const crit=Math.random()<s.chance;if(crit)damage=Math.max(1,Math.round(damage*(1+s.bonus)));target.hp-=damage;addDamageNumber(target.x,target.y-38,damage,'#fff',crit);target.hitFlash=8;showMessage(crit?'💥 CRITICAL! '+target.name+' for '+damage+' damage!':'⚔️ Hit '+target.name+' for '+damage+' damage!');if(target.hp<=0)killMonster(target)
};
/* Damage text: normal white; critical large yellow + neon-red glow. */
window.drawDamageNumbers=function(){for(const d of damageNumbers){ctx.save();ctx.globalAlpha=Math.max(0,d.life/d.maxLife);ctx.textAlign='center';if(d.crit){ctx.font='900 36px Arial';ctx.fillStyle='#ffe94a';ctx.shadowColor='#ff102b';ctx.shadowBlur=26;ctx.lineWidth=3;ctx.strokeStyle='#ff1835';ctx.strokeText(String(d.amount),d.x,d.y);ctx.fillText(String(d.amount),d.x,d.y)}else{ctx.font='900 20px Arial';ctx.fillStyle='#fff';ctx.shadowColor='#000';ctx.shadowBlur=4;ctx.fillText(String(d.amount),d.x,d.y)}ctx.restore()}};
/* Inventory green box: ATK range + per-weapon crit chance + crit damage. */
function refreshWeaponStats(){document.querySelectorAll('#bagItems .itemCard').forEach(card=>{const e=card.querySelector('.itemName');if(!e)return;const n=e.textContent.trim(),s=critStats[n];if(!s)return;card.querySelectorAll('.pandaniaCritStat').forEach(x=>x.remove());let b=card.querySelector('.pandaniaWeaponGreenStats');if(!b){b=document.createElement('div');b.className='pandaniaWeaponGreenStats';card.appendChild(b)}const r=weaponRange(n);b.innerHTML='ATK '+r.min+'–'+r.max+' · CRIT <span class="critChance">'+Math.round(s.chance*100)+'%</span> · CRIT DMG <span class="critDamage">+'+Math.round(s.bonus*100)+'%</span>'})}
window.__pandaniaRefreshWeaponStats=refreshWeaponStats;
new MutationObserver(refreshWeaponStats).observe(document.body,{childList:true,subtree:true});setInterval(refreshWeaponStats,500);setTimeout(refreshWeaponStats,50);
/* Mobile-only monster width: overlay the monster icon 15% wider; hitboxes unchanged. */
const baseDraw=window.draw;if(typeof baseDraw==='function'&&!window.__pandaniaWideDraw){window.draw=function(){baseDraw();if(isMobile()){const z=typeof pandaniaMobileZoom==='function'?pandaniaMobileZoom():1,vw=W/z,vh=H/z;for(const m of monsters){const sx=(m.x-camera.x-vw/2)*z+W/2,sy=(m.y-camera.y-vh/2)*z+H/2;ctx.save();ctx.translate(sx,sy);ctx.scale(1.15,1);ctx.font='40px Arial';ctx.textAlign='center';ctx.fillText(m.icon||'👹',0,0);ctx.restore()}}};window.__pandaniaWideDraw=true}
window.__pandaniaV13=true;
})();
</script>
<!-- ===== END PANDANIA V13 COMBAT/INPUT PATCH ===== -->'''
text=text.replace('</body>',patch+'\n</body>',1)
path.write_text(text,encoding='utf-8')
