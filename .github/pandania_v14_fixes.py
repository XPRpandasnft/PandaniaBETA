from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)

# Keep the existing V11/V7 paper-doll renderer as the ONLY renderer, but restore
# the original working asset lookup directly through imageFiles. Do not create
# a second weapon renderer or an overlay.
s=s.replace(
    "if(typeof window.imageFiles==='object'&&window.imageFiles[ref])return window.imageFiles[ref];",
    "if(typeof imageFiles!='undefined'&&imageFiles&&imageFiles[ref])return imageFiles[ref];"
)

patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
/* SINGLE paper-doll renderer: only control its existing weapon slot. */
#pandaniaEquipment{position:relative;box-sizing:border-box;overflow:visible!important}
#pandaniaEquipment #equipWeapon{position:relative;box-sizing:border-box;overflow:visible!important;min-width:0}
.paperDollWeaponArt{height:72px;display:flex;align-items:center;justify-content:center;overflow:visible;margin:0 auto 3px;position:relative;z-index:5}
.paperDollEquipImage{display:block;width:72px;height:72px;max-width:72px;max-height:72px;object-fit:contain;margin:0 auto 3px;image-rendering:auto;position:relative;z-index:10;visibility:visible;opacity:1}
@media(max-width:700px),(pointer:coarse){
  #stats{width:185px!important;padding:5px 6px!important;opacity:1!important;background:rgba(10,10,10,.94)!important;transform:scale(.82);transform-origin:top left}
  #minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important}
  #pandaniaMobileControls{display:none!important}
  #gameWrap.pandaniaStarted #pandaniaMobileControls{display:flex!important}

  /* The original equipment panel uses a 1fr / 130px / 1fr grid. On a
     phone the 130px center panda can collapse the weapon column. Keep the
     same paper-doll, but give its existing grid a mobile-safe center width. */
  #pandaniaEquipment{width:100%!important;max-width:94vw!important;padding:10px!important;overflow:visible!important}
  #pandaniaEquipment>div:nth-child(2){
    display:grid!important;
    grid-template-columns:minmax(0,1fr) 92px minmax(0,1fr)!important;
    gap:6px!important;
    align-items:center!important;
    width:100%!important;
    overflow:visible!important;
  }
  #pandaniaEquipment>div:nth-child(2)>#equipWeapon,
  #pandaniaEquipment>div:nth-child(2)>#equipArmor{
    min-width:0!important;width:100%!important;padding:6px!important;overflow:visible!important;
    word-break:break-word!important;
  }
  #pandaniaEquipment>div:nth-child(2)>div:nth-child(2){
    width:92px!important;min-width:92px!important;height:110px!important;font-size:48px!important;overflow:visible!important;
  }
  .paperDollWeaponArt{height:60px!important;width:100%!important;overflow:visible!important}
  .paperDollEquipImage{width:60px!important;height:60px!important;max-width:60px!important;max-height:60px!important;display:block!important;visibility:visible!important;opacity:1!important;object-fit:contain!important;z-index:50!important}
}
</style>
<script>
(function(){
'use strict';
/* SINGLE RENDERER ONLY: the existing V11/V7 paper-doll renderer owns #equipWeapon. */
function refreshSameRenderer(){
  try{ if(typeof window.renderBag==='function') window.renderBag(); }
  catch(e){ console.warn('Pandania equipment refresh skipped:',e); }
}
window.__pandaniaFixEquippedWeaponV14=refreshSameRenderer;
window.__pandaniaFinalFixV11=true;
document.addEventListener('click',function(e){
  const t=e.target;
  if(t&&((t.id==='playButton')||(t.closest&&t.closest('#bagWindow'))))setTimeout(refreshSameRenderer,50);
},true);
window.addEventListener('resize',function(){setTimeout(refreshSameRenderer,50)},{passive:true});
window.addEventListener('orientationchange',function(){setTimeout(refreshSameRenderer,100)},{passive:true});
})();
</script>
<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->'''

s=s.replace('</body>',patch+'\n</body>',1) if '</body>' in s else s+'\n'+patch
p.write_text(s,encoding='utf-8')
