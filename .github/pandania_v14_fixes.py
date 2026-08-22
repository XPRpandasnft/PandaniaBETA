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
#paperDoll{overflow:visible!important;isolation:isolate!important}
#paperDoll>*{overflow:visible!important}
#paperDoll .pandaEmoji,#paperDoll .panda,#paperDoll .paperDollPanda,#paperDoll .playerEmoji,#paperDoll .characterEmoji{z-index:1!important;font-size:26px!important;transform:scale(.45)!important;max-width:36px!important;max-height:36px!important}
#pandaniaMobileWeaponOverlay{position:fixed!important;display:none!important;pointer-events:none!important;z-index:2147483647!important;object-fit:contain!important;max-width:none!important;max-height:none!important}
#pandaniaMobileWeaponOverlay.pandaniaVisible{display:block!important}
}
#paperDoll,#paperDoll>*{overflow:visible!important}
</style>
<script>
(function(){'use strict';
function getSlot(){const root=document.querySelector('#paperDoll');if(!root)return null;for(const q of ['.equippedWeapon','.weaponSlot','#equippedWeapon','#equippedWeaponSlot']){const e=root.querySelector(q);if(e)return e}return null}
function weapon(){const slot=getSlot();if(!slot)return null;return slot.querySelector('img')}
function paint(){const img=weapon();if(!img||!img.src){const old=document.getElementById('pandaniaMobileWeaponOverlay');if(old)old.classList.remove('pandaniaVisible');return}
 let o=document.getElementById('pandaniaMobileWeaponOverlay');if(!o){o=document.createElement('img');o.id='pandaniaMobileWeaponOverlay';document.body.appendChild(o)}
 o.src=img.currentSrc||img.src;
 const portrait=window.innerWidth<window.innerHeight;
 /* Deliberately use a fixed viewport position instead of the paper-doll's
    percentage/flex layout. This prevents portrait CSS from shrinking/clipping it. */
 const size=portrait?Math.min(72,Math.max(58,window.innerWidth*.20)):76;
 const left=portrait?Math.round(window.innerWidth*.70):Math.round(window.innerWidth*.72);
 const top=portrait?Math.round(window.innerHeight*.34):Math.round(window.innerHeight*.36);
 o.style.width=size+'px';o.style.height=size+'px';o.style.left=Math.max(4,Math.min(left,window.innerWidth-size-4))+'px';o.style.top=Math.max(4,Math.min(top,window.innerHeight-size-4))+'px';o.classList.add('pandaniaVisible');
}
window.__pandaniaFixEquippedWeaponV14=paint;
setTimeout(paint,100);setTimeout(paint,500);setTimeout(paint,1200);setInterval(paint,500);window.addEventListener('resize',()=>setTimeout(paint,50),{passive:true});window.addEventListener('orientationchange',()=>setTimeout(paint,100),{passive:true});
})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->'''
s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')