from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)
patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
@media (max-width:700px),(pointer:coarse){
  /* Mobile HUD: solid, smaller HP/Mana/XP panel. */
  #stats{width:185px!important;padding:5px 6px!important;opacity:1!important;background:rgba(10,10,10,.94)!important;transform:scale(.82);transform-origin:top left}
  #minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important}

  /* Paper doll: the panda container must never paint over the equipped weapon. */
  #paperDoll{position:relative!important;overflow:visible!important;isolation:isolate!important}
  #paperDoll>*{overflow:visible!important}
  #paperDoll .equippedWeapon,#paperDoll .weaponSlot,#equippedWeapon,#equippedWeaponSlot{
    position:relative!important;z-index:1000!important;overflow:visible!important;
    min-width:78px!important;min-height:78px!important;
    display:flex!important;align-items:center!important;justify-content:center!important;
    flex:none!important;pointer-events:auto!important
  }
  #paperDoll .equippedWeapon img,#paperDoll .weaponSlot img,#equippedWeapon img,#equippedWeaponSlot img{
    position:relative!important;z-index:1100!important;display:block!important;visibility:visible!important;opacity:1!important;
    width:76px!important;height:76px!important;max-width:none!important;max-height:none!important;
    object-fit:contain!important;overflow:visible!important
  }
  /* The panda placeholder stays behind the weapon and is much smaller. */
  #paperDoll .pandaEmoji,#paperDoll .panda,#paperDoll .paperDollPanda,#paperDoll .playerEmoji,#paperDoll .characterEmoji{
    position:relative!important;z-index:1!important;font-size:26px!important;line-height:1!important;
    transform:scale(.45)!important;transform-origin:center center!important;max-width:36px!important;max-height:36px!important
  }
}
#paperDoll,#paperDoll>*{overflow:visible!important}
#paperDoll .equippedWeapon,#paperDoll .weaponSlot,#equippedWeapon,#equippedWeaponSlot{overflow:visible!important;z-index:1000!important}
#paperDoll .equippedWeapon img,#paperDoll .weaponSlot img,#equippedWeapon img,#equippedWeaponSlot img{z-index:1100!important;object-fit:contain!important}
</style>
<script>
(function(){'use strict';
function tryManaPotion(){if(typeof player==='undefined'||!player)return false;const before=Number(player.mana)||0,max=Number(player.maxMana)||100;if(before>=max)return false;player.mana=Math.min(max,before+5);if(typeof updateUI==='function')try{updateUI()}catch(e){}if(typeof showMessage==='function')showMessage('🧪 +5 Mana');return true}
function isManaCard(card){return(card?.textContent||'').toLowerCase().includes('mana potion')}
function bindManaPotion(){document.querySelectorAll('#bagItems .itemCard').forEach(card=>{if(!isManaCard(card)||card.__manaBound)return;card.__manaBound=true;card.addEventListener('dblclick',function(e){e.preventDefault();e.stopPropagation();tryManaPotion()},true)})}
window.__pandaniaManaPotionV14=tryManaPotion;setTimeout(bindManaPotion,150);const oldOpen=window.openBag;if(typeof oldOpen==='function'&&!window.__manaOpenWrapped){window.openBag=function(){const r=oldOpen.apply(this,arguments);setTimeout(bindManaPotion,30);return r};window.__manaOpenWrapped=true}
function forcePaperDollWeapon(){
 const root=document.querySelector('#paperDoll');if(!root)return;
 root.style.setProperty('overflow','visible','important');
 root.querySelectorAll('*').forEach(el=>el.style.setProperty('overflow','visible','important'));
 const slots=root.querySelectorAll('.equippedWeapon,.weaponSlot,#equippedWeapon,#equippedWeaponSlot');
 slots.forEach(slot=>{slot.style.setProperty('position','relative','important');slot.style.setProperty('z-index','1000','important');slot.style.setProperty('overflow','visible','important');const img=slot.querySelector('img');if(img){img.style.setProperty('display','block','important');img.style.setProperty('visibility','visible','important');img.style.setProperty('opacity','1','important');img.style.setProperty('width','76px','important');img.style.setProperty('height','76px','important');img.style.setProperty('max-width','none','important');img.style.setProperty('max-height','none','important');img.style.setProperty('object-fit','contain','important');img.style.setProperty('position','relative','important');img.style.setProperty('z-index','1100','important');}});
 root.querySelectorAll('.pandaEmoji,.panda,.paperDollPanda,.playerEmoji,.characterEmoji').forEach(el=>{el.style.setProperty('z-index','1','important');el.style.setProperty('font-size','26px','important');el.style.setProperty('transform','scale(.45)','important');el.style.setProperty('max-width','36px','important');el.style.setProperty('max-height','36px','important')});
}
function fixMiniMap(){const map=document.querySelector('#minimap');if(!map)return;if(matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches){map.style.setProperty('left','auto','important');map.style.setProperty('right','10px','important');map.style.setProperty('bottom','auto','important');map.style.setProperty('top','72px','important');map.style.setProperty('width','105px','important');map.style.setProperty('height','105px','important');map.style.setProperty('opacity','.48','important')}}
window.__pandaniaFixMiniMapV14=fixMiniMap;window.__pandaniaFixEquippedWeaponV14=forcePaperDollWeapon;
setTimeout(forcePaperDollWeapon,100);setTimeout(forcePaperDollWeapon,500);setTimeout(forcePaperDollWeapon,1200);setTimeout(fixMiniMap,50);setTimeout(fixMiniMap,500);setTimeout(fixMiniMap,1500);
})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->'''
s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')
