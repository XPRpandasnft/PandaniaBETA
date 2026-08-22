from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)
patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
@media (max-width:700px),(pointer:coarse){
#minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important}
#stats{width:205px!important;padding:7px!important;opacity:.72!important;transform:scale(.88);transform-origin:top left}
#paperDoll{position:relative!important;overflow:visible!important}
#paperDoll .equippedWeapon,#paperDoll .weaponSlot,#equippedWeapon,#equippedWeaponSlot{z-index:20!important;position:relative!important;min-width:72px!important;min-height:72px!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:visible!important}
#paperDoll .equippedWeapon img,#paperDoll .weaponSlot img,#equippedWeapon img,#equippedWeaponSlot img{width:64px!important;height:64px!important;object-fit:contain!important;position:relative!important;z-index:30!important}
/* Much smaller mobile panda placeholder/emoji so the equipped weapon has room. */
#paperDoll .pandaEmoji,#paperDoll .panda,#paperDoll .paperDollPanda,#paperDoll .playerEmoji,#paperDoll .characterEmoji{font-size:26px!important;line-height:1!important;transform:scale(.45)!important;transform-origin:center center!important;max-width:36px!important;max-height:36px!important}
}
#paperDoll .equippedWeapon,#paperDoll .weaponSlot,#equippedWeapon,#equippedWeaponSlot{overflow:visible!important}
</style>
<script>
(function(){'use strict';
function tryManaPotion(){if(typeof player==='undefined'||!player)return false;const before=Number(player.mana)||0,max=Number(player.maxMana)||100;if(before>=max)return false;player.mana=Math.min(max,before+5);if(typeof updateUI==='function')try{updateUI()}catch(e){}if(typeof showMessage==='function')showMessage('🧪 +5 Mana');return true}
function isManaCard(card){return(card?.textContent||'').toLowerCase().includes('mana potion')}
function bindManaPotion(){document.querySelectorAll('#bagItems .itemCard').forEach(card=>{if(!isManaCard(card)||card.__manaBound)return;card.__manaBound=true;card.addEventListener('dblclick',function(e){e.preventDefault();e.stopPropagation();tryManaPotion()},true)})}
window.__pandaniaManaPotionV14=tryManaPotion;setTimeout(bindManaPotion,150);const oldOpen=window.openBag;if(typeof oldOpen==='function'&&!window.__manaOpenWrapped){window.openBag=function(){const r=oldOpen.apply(this,arguments);setTimeout(bindManaPotion,30);return r};window.__manaOpenWrapped=true}
function fixEquippedWeapon(){const selectors=['#equippedWeapon','#equippedWeaponSlot','#paperDoll .equippedWeapon','#paperDoll .weaponSlot'];let slot=null;for(const sel of selectors){const el=document.querySelector(sel);if(el){slot=el;break}}if(!slot)return;slot.style.overflow='visible';slot.style.zIndex='30';const img=slot.querySelector('img');if(img){img.style.display='block';img.style.visibility='visible';img.style.opacity='1';img.style.width='64px';img.style.height='64px';img.style.objectFit='contain';img.style.zIndex='40';return}const txt=(slot.textContent||'').trim();if(/^[^\w\s]{1,4}$/.test(txt)||txt==='🗡️'||txt==='⚔️'||txt==='📦')slot.textContent=''}
function shrinkPandaBox(){if(!(matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches))return;const root=document.querySelector('#paperDoll');if(!root)return;root.querySelectorAll('.pandaEmoji,.panda,.paperDollPanda,.playerEmoji,.characterEmoji').forEach(el=>{el.style.setProperty('font-size','26px','important');el.style.setProperty('line-height','1','important');el.style.setProperty('transform','scale(.45)','important');el.style.setProperty('transform-origin','center center','important');el.style.setProperty('max-width','36px','important');el.style.setProperty('max-height','36px','important')})}
function fixMiniMap(){const map=document.querySelector('#minimap');if(!map)return;if(matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches){map.style.setProperty('left','auto','important');map.style.setProperty('right','10px','important');map.style.setProperty('bottom','auto','important');map.style.setProperty('top','72px','important');map.style.setProperty('width','105px','important');map.style.setProperty('height','105px','important');map.style.setProperty('opacity','.48','important')}}
window.__pandaniaFixMiniMapV14=fixMiniMap;window.__pandaniaFixEquippedWeaponV14=fixEquippedWeapon;
setTimeout(fixEquippedWeapon,100);setTimeout(fixEquippedWeapon,500);setTimeout(shrinkPandaBox,100);setTimeout(shrinkPandaBox,500);setTimeout(fixMiniMap,50);setTimeout(fixMiniMap,500);setTimeout(fixMiniMap,1500);
})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->'''
s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')
