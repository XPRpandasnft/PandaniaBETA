from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)

patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
@media(max-width:700px),(pointer:coarse){
  #stats{width:185px!important;padding:5px 6px!important;opacity:1!important;background:rgba(10,10,10,.94)!important;transform:scale(.82);transform-origin:top left}
  #minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important}
  #pandaniaMobileControls{display:none!important}
  #gameWrap.pandaniaStarted #pandaniaMobileControls{display:flex!important}
  .paperDollWeaponArt{height:58px;display:flex;align-items:center;justify-content:center;overflow:hidden;margin:0 auto 3px}
  .paperDollEquipImage{display:block;width:58px!important;height:58px!important;max-width:58px!important;max-height:58px!important;object-fit:contain;margin:0 auto 3px;image-rendering:auto}
}
.paperDollWeaponArt{height:72px;display:flex;align-items:center;justify-content:center;overflow:hidden;margin:0 auto 3px}
.paperDollEquipImage{display:block;width:72px;height:72px;max-width:72px;max-height:72px;object-fit:contain;margin:0 auto 3px;image-rendering:auto}
</style>
<script>
(function(){
'use strict';
/* Restore the previously working paper-doll equipment rendering. */
const wrap=document.getElementById('gameWrap');
const play=document.getElementById('playButton');
if(play&&wrap)play.addEventListener('click',()=>wrap.classList.add('pandaniaStarted'),true);
function syncStart(){
  if(wrap&&typeof gameStarted!=='undefined'&&gameStarted)wrap.classList.add('pandaniaStarted');
  else if(wrap){const start=document.getElementById('startScreen');if(!start||start.style.display!=='none')wrap.classList.remove('pandaniaStarted')}
}
syncStart();setInterval(syncStart,250);

function weaponImageSrc(name){
  if(!name)return '';
  let d=Array.isArray(window.weaponDrops)&&window.weaponDrops.find(w=>w&&w.name===name);
  if(!d&&window.inventory&&window.inventory[name]&&window.inventory[name].image)d={name:name,image:window.inventory[name].image};
  const aliases={'Proton Lens':'XPR Lens','XPR Lens':'Proton Lens'};
  if(!d&&aliases[name]){
    const a=aliases[name];
    d=Array.isArray(window.weaponDrops)&&window.weaponDrops.find(w=>w&&w.name===a);
    if(!d&&window.inventory&&window.inventory[a]&&window.inventory[a].image)d={name:a,image:window.inventory[a].image};
  }
  if(!d||!d.image)return '';
  const ref=d.image;
  if(typeof ref==='string'&&ref.startsWith('data:'))return ref;
  /* IMPORTANT: imageFiles is the original working asset map and is a local
     lexical variable in the game source, not necessarily window.imageFiles. */
  if(typeof imageFiles!=='undefined'&&imageFiles&&imageFiles[ref])return imageFiles[ref];
  if(typeof window.imageFiles==='object'&&window.imageFiles&&window.imageFiles[ref])return window.imageFiles[ref];
  if(typeof window.images==='object'&&window.images&&window.images[ref]&&window.images[ref].src)return window.images[ref].src;
  if(typeof ref==='string'){
    if(/^https?:|^data:|^blob:|^\//.test(ref))return ref;
    const folder=(typeof window.IMAGE_FOLDER==='string'?window.IMAGE_FOLDER:'./images/');
    return folder+ref+'.png';
  }
  return '';
}
function refreshPaperDoll(){
  const el=document.getElementById('equipWeapon');
  const state=window.__pandaniaEquipment;
  if(!el||!state)return;
  const item=state.weapon||'';
  const src=weaponImageSrc(item);
  let art='';
  if(item&&src){
    art='<div class="paperDollWeaponArt"><img class="paperDollEquipImage" src="'+src.replace(/"/g,'&quot;')+'" alt="'+String(item).replace(/"/g,'&quot;')+'"></div>';
  }
  el.innerHTML=art+'⚔️ Weapon<br><strong>'+String(item||'Empty')+'</strong>'+(item?'<br><button class="pdUnequip" type="button">Unequip</button>':'');
  const b=el.querySelector('.pdUnequip');
  if(b)b.onclick=function(e){
    e.preventDefault();e.stopPropagation();
    if(typeof window.setInv==='function')window.setInv(item,(window.inventory&&window.inventory[item]&&window.inventory[item].count||0)+1);
    state.weapon='';
    refreshPaperDoll();
    if(typeof window.renderBag==='function')window.renderBag();
  };
}
const oldOpenBag=window.openBag;
if(typeof oldOpenBag==='function'&&!window.__pandaniaV11OpenBagWrapped){
  window.openBag=function(){const r=oldOpenBag.apply(this,arguments);setTimeout(refreshPaperDoll,0);return r};
  window.__pandaniaV11OpenBagWrapped=true;
}
setInterval(refreshPaperDoll,400);
window.__pandaniaFinalFixV11=true;
window.__pandaniaFixEquippedWeaponV14=refreshPaperDoll;
})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->'''

s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')
