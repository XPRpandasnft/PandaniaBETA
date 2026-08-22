from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')

# Remove prior V14 if present.
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)

patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
/* Mobile minimap: top-right, smaller, more transparent. */
@media (max-width:700px),(pointer:coarse){
  #minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important;transform:none!important}
  #stats{width:205px!important;padding:7px!important;opacity:.72!important;transform:scale(.88);transform-origin:top left}
  /* Give the paper doll a dedicated weapon slot with no overlap from the panda. */
  #paperDoll{position:relative!important;overflow:visible!important}
  #paperDoll .equippedWeapon,#paperDoll .weaponSlot,#equippedWeapon,#equippedWeaponSlot{z-index:20!important;position:relative!important;min-width:72px!important;min-height:72px!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:visible!important}
  #paperDoll .equippedWeapon img,#paperDoll .weaponSlot img,#equippedWeapon img,#equippedWeaponSlot img{width:64px!important;height:64px!important;object-fit:contain!important;position:relative!important;z-index:30!important}
}
/* Desktop too: never clip the equipped weapon image. */
#paperDoll .equippedWeapon,#paperDoll .weaponSlot,#equippedWeapon,#equippedWeaponSlot{overflow:visible!important}
</style>
<script>
(function(){
'use strict';

/* ---------- Mana potion: double-click = +5 mana ---------- */
function tryManaPotion(){
  if(typeof player==='undefined'||!player)return false;
  const before=Number(player.mana)||0;
  const max=Number(player.maxMana)||100;
  if(before>=max)return false;
  player.mana=Math.min(max,before+5);
  if(typeof updateUI==='function')try{updateUI()}catch(e){}
  if(typeof showMessage==='function')showMessage('🧪 +5 Mana');
  return true;
}
function isManaCard(card){
  const t=(card?.textContent||'').toLowerCase();
  return t.includes('mana potion')||t.includes('mana potion');
}
function bindManaPotion(){
  document.querySelectorAll('#bagItems .itemCard').forEach(card=>{
    if(!isManaCard(card)||card.__manaBound)return;
    card.__manaBound=true;
    card.addEventListener('dblclick',function(e){
      e.preventDefault();e.stopPropagation();
      tryManaPotion();
    },true);
  });
}
window.__pandaniaManaPotionV14=tryManaPotion;
setTimeout(bindManaPotion,150);
const oldOpen=window.openBag;
if(typeof oldOpen==='function'&&!window.__manaOpenWrapped){
  window.openBag=function(){const r=oldOpen.apply(this,arguments);setTimeout(bindManaPotion,30);return r};
  window.__manaOpenWrapped=true;
}

/* ---------- Paper doll equipped weapon: image-first, no emoji fallback ---------- */
function fixEquippedWeapon(){
  const selectors=['#equippedWeapon','#equippedWeaponSlot','#paperDoll .equippedWeapon','#paperDoll .weaponSlot'];
  let slot=null;
  for(const sel of selectors){const el=document.querySelector(sel);if(el){slot=el;break}}
  if(!slot)return;
  slot.style.overflow='visible';slot.style.zIndex='30';
  const img=slot.querySelector('img');
  if(img){img.style.display='block';img.style.visibility='visible';img.style.opacity='1';img.style.width='64px';img.style.height='64px';img.style.objectFit='contain';img.style.zIndex='40';return}
  /* If unequipped, explicitly clear legacy emoji/text placeholder. */
  const txt=(slot.textContent||'').trim();
  if(/^[^\w\s]{1,4}$/.test(txt)||txt==='🗡️'||txt==='⚔️'||txt==='📦')slot.textContent='';
}
window.__pandaniaFixEquippedWeaponV14=fixEquippedWeapon;
setTimeout(fixEquippedWeapon,100);
setTimeout(fixEquippedWeapon,500);

/* ---------- Mobile minimap ---------- */
function fixMiniMap(){
  const map=document.querySelector('#minimap');
  if(!map)return;
  if(matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches){
    map.style.setProperty('left','auto','important');
    map.style.setProperty('right','10px','important');
    map.style.setProperty('bottom','auto','important');
    map.style.setProperty('top','72px','important');
    map.style.setProperty('width','105px','important');
    map.style.setProperty('height','105px','important');
    map.style.setProperty('opacity','.48','important');
  }
}
window.__pandaniaFixMiniMapV14=fixMiniMap;
setTimeout(fixMiniMap,50);setTimeout(fixMiniMap,500);setTimeout(fixMiniMap,1500);

})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->'''

s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')
