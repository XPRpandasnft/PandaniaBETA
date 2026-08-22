from pathlib import Path
import re

path=Path('Adventures Of Pandania The Lost Realms/index.html')
text=path.read_text(encoding='utf-8')
text=re.sub(r'<!-- ===== PANDANIA V14 POLISH PATCH ===== -->.*?<!-- ===== END PANDANIA V14 POLISH PATCH ===== -->','',text,flags=re.S)

# Replace the source updateMonsters function with a collision-safe version.
def replace_function(src,name,new_body):
    marker='function '+name+'('
    start=src.find(marker)
    if start<0:return src,False
    brace=src.find('{',start)
    if brace<0:return src,False
    depth=0; i=brace; quote=None; esc=False; line_comment=False; block_comment=False
    while i<len(src):
        c=src[i]; n=src[i+1] if i+1<len(src) else ''
        if line_comment:
            if c=='\n': line_comment=False
        elif block_comment:
            if c=='*' and n=='/': block_comment=False;i+=1
        elif quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
        elif c in "'\"`": quote=c
        elif c=='/' and n=='/': line_comment=True;i+=1
        elif c=='/' and n=='*': block_comment=True;i+=1
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                return src[:start]+new_body+src[i+1:],True
        i+=1
    return src,False

new_update=r'''function updateMonsters(){
    if(inHouse) return;
    for(const m of monsters){
        if(m.attackCooldown>0)m.attackCooldown--;
        if(m.hitFlash>0)m.hitFlash--;
        if(m.type==="boss1"&&m.bossFireCooldown>0)m.bossFireCooldown--;
        if(m.type==="boss1"&&m.bossFireCooldown<=0){
            for(const dir of [{x:1,y:0},{x:-1,y:0},{x:0,y:1},{x:0,y:-1}])bossFireShots.push({x:m.x,y:m.y,vx:dir.x*5.2,vy:dir.y*5.2,life:150,damage:28});
            m.bossFireCooldown=600;
            if(typeof bossSound==='function')bossSound();
            if(typeof showMessage==='function')showMessage("🔥 FLAMEOZN casts a four-way Fire Burst!");
        }
        const dx=player.x-m.x,dy=player.y-m.y,d=Math.hypot(dx,dy)||.001;
        const attackRange=m.boss?Math.max(68,(m.r||18)+(player.r||14)+10):Math.max(52,(m.r||18)+(player.r||14)+4);
        if(d<m.chaseDistance){
            /* Never let a boss physically overlap/push the player. Once inside
               attack range it stops and performs a real timed melee hit. */
            if(d>attackRange){
                const nx=m.x+(dx/d)*m.speed,ny=m.y+(dy/d)*m.speed;
                if(!blocked(nx,m.y,m.r))m.x=nx;
                if(!blocked(m.x,ny,m.r))m.y=ny;
            }else if(m.attackCooldown<=0&&player.invincible<=0){
                const dmg=Math.max(1,Number(m.damage)||1);
                player.hp-=dmg;
                addDamageNumber(player.x,player.y-38,dmg,"#f33");
                player.invincible=30;
                m.attackCooldown=m.boss?80:(m.type==="monster6"?50:(m.type==="monster7"?40:70));
                if(typeof hitSound==='function')hitSound();
                if(m.boss&&typeof bossSound==='function')bossSound();
                if(typeof showMessage==='function')showMessage("💥 "+m.name+" hit you for "+dmg+" damage!");
                if(player.hp<=0&&typeof respawnPlayer==='function')respawnPlayer();
            }
        }
    }
}'''
text,ok=replace_function(text,'updateMonsters',new_update)

patch=r'''<!-- ===== PANDANIA V14 POLISH PATCH ===== -->
<style>
/* Paper-doll: reserve a real weapon slot so the panda avatar cannot crush it. */
#paperDoll,#paperDollWindow,.paperDoll,.paper-doll{position:relative}
#paperDoll .weaponSlot,#paperDoll .equippedWeapon,#paperDoll .weapon,
#paperDollWindow .weaponSlot,#paperDollWindow .equippedWeapon,
.paperDoll .weaponSlot,.paper-doll .weaponSlot{min-width:72px!important;min-height:72px!important;width:72px!important;height:72px!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:visible!important;position:relative!important;z-index:4!important}
#paperDoll .weaponSlot img,#paperDoll .equippedWeapon img,#paperDollWindow .weaponSlot img,#paperDollWindow .equippedWeapon img{max-width:62px!important;max-height:62px!important;object-fit:contain!important;position:relative!important;z-index:6!important}
@media(max-width:700px),(pointer:coarse){
 #paperDoll,#paperDollWindow,.paperDoll,.paper-doll{min-width:300px!important}
 #paperDoll .weaponSlot,#paperDoll .equippedWeapon,#paperDoll .weapon,#paperDollWindow .weaponSlot,#paperDollWindow .equippedWeapon,.paperDoll .weaponSlot,.paper-doll .weaponSlot{min-width:82px!important;min-height:82px!important;width:82px!important;height:82px!important}
 #paperDoll .weaponSlot img,#paperDoll .equippedWeapon img,#paperDollWindow .weaponSlot img,#paperDollWindow .equippedWeapon img{max-width:72px!important;max-height:72px!important}
 #mapCanvas,#miniMap,#minimap,.miniMap,.mini-map{top:10px!important;right:10px!important;bottom:auto!important;left:auto!important;width:110px!important;height:82px!important;opacity:.42!important;transform:none!important}
 #hud,#statusBar,#playerStats,.playerStats,.statusBar{opacity:.68!important}
}
/* Never show the placeholder weapon emoji after unequip. */
.weaponSlot.unequipped,.equippedWeapon.unequipped{font-size:0!important}
.weaponSlot.unequipped::before,.equippedWeapon.unequipped::before{content:''!important}
</style>
<script>
(function(){
'use strict';

/* Remove common weapon-placeholder emoji text without touching the panda avatar. */
function cleanUnequippedWeaponSlots(){
 document.querySelectorAll('.weaponSlot,.equippedWeapon').forEach(el=>{
  const t=(el.textContent||'').trim();
  if(!el.querySelector('img') && /^(⚔️|🗡️|🪓|🔪|🛡️|🗡|⚔)$/.test(t)){el.textContent='';el.classList.add('unequipped')}
 });
}
window.__pandaniaCleanWeaponSlots=cleanUnequippedWeaponSlots;

/* Safe fish double-click: any visible ground fish restores at least 5 HP. */
function fishDoubleClick(e){
 if(!Array.isArray(groundDrops)||!groundDrops.length)return;
 const rect=canvas.getBoundingClientRect();
 const sx=(e.clientX-rect.left)*(W/rect.width),sy=(e.clientY-rect.top)*(H/rect.height);
 const z=(typeof pandaniaMobileZoom==='function'&&((matchMedia('(pointer:coarse)').matches)||matchMedia('(max-width:700px)').matches))?pandaniaMobileZoom():1;
 const vw=W/z,vh=H/z;
 const p=z!==1?{x:camera.x+vw/2+(sx-W/2)/z,y:camera.y+vh/2+(sy-H/2)/z}:{x:sx+camera.x,y:sy+camera.y};
 for(let i=groundDrops.length-1;i>=0;i--){
  const d=groundDrops[i];if(!d)continue;
  const name=String(d.name||d.item||d.type||'').toLowerCase();
  if(!name.includes('fish'))continue;
  if(Math.hypot(p.x-d.x,p.y-d.y)>125)continue;
  player.hp=Math.min(player.maxHp,player.hp+5);
  if(typeof showMessage==='function')showMessage('🐟 Fish restored +5 HP!');
  if(typeof updateUI==='function')updateUI();
  groundDrops.splice(i,1);
  e.preventDefault();e.stopImmediatePropagation();
  return;
 }
}
canvas.addEventListener('dblclick',fishDoubleClick,true);

/* Refresh after inventory/paper-doll changes, but never use a MutationObserver. */
setTimeout(cleanUnequippedWeaponSlots,200);
setInterval(cleanUnequippedWeaponSlots,1000);
window.__pandaniaV14=true;
})();
</script>
<!-- ===== END PANDANIA V14 POLISH PATCH ===== -->'''
text=text.replace('</body>',patch+'\n</body>',1) if '</body>' in text else text+'\n'+patch+'\n'
path.write_text(text,encoding='utf-8')
