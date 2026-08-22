from pathlib import Path
import re

p=Path('Adventures Of Pandania The Lost Realms/index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<!-- ===== PANDANIA V14 FINAL FIXES ===== -->.*?<!-- ===== END PANDANIA V14 FINAL FIXES ===== -->','',s,flags=re.S)

patch=r'''<!-- ===== PANDANIA V14 FINAL FIXES ===== -->
<style>
.paperDollWeaponArt{height:72px;display:flex;align-items:center;justify-content:center;overflow:hidden;margin:0 auto 3px}
.paperDollEquipImage{display:block;width:72px;height:72px;max-width:72px;max-height:72px;object-fit:contain;margin:0 auto 3px;image-rendering:auto}
@media(max-width:700px),(pointer:coarse){
  #stats{width:185px!important;padding:5px 6px!important;opacity:1!important;background:rgba(10,10,10,.94)!important;transform:scale(.82);transform-origin:top left}
  #minimap{left:auto!important;right:10px!important;bottom:auto!important;top:72px!important;width:105px!important;height:105px!important;opacity:.48!important}
  #pandaniaMobileControls{display:none!important}
  #gameWrap.pandaniaStarted #pandaniaMobileControls{display:flex!important}
  .paperDollWeaponArt{height:58px}
  .paperDollEquipImage{width:58px!important;height:58px!important;max-width:58px!important;max-height:58px!important}
}
</style>
<script>
(function(){
'use strict';
/* SINGLE RENDERER ONLY: the V11 paper-doll renderer owns #equipWeapon. */
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
