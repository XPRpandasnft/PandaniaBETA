from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

# Replace any previous copy of this patch so the workflow is idempotent.
text = re.sub(
    r'<!-- ===== PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->.*?<!-- ===== END PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->',
    '', text, flags=re.S
)

# Force the actual camera zoom function to the requested mobile zoom values.
# This intentionally replaces the whole function body instead of trying to
# match a particular older implementation, preventing later source changes
# from silently defeating the mobile zoom.
text, zoom_count = re.subn(
    r'function\s+pandaniaMobileZoom\s*\(\)\s*\{.*?\}',
    "function pandaniaMobileZoom(){if(!((window.matchMedia&&window.matchMedia('(pointer:coarse)').matches)||(window.matchMedia&&window.matchMedia('(max-width:700px)').matches)))return 1;return window.matchMedia('(orientation:landscape)').matches ? 1.08 : 1.12;}",
    text, count=1, flags=re.S
)
if zoom_count == 0:
    # If the source does not currently define it, add a stable global helper.
    marker = '</head>' if '</head>' in text else '<body>'
    helper = "<script>function pandaniaMobileZoom(){if(!((window.matchMedia&&window.matchMedia('(pointer:coarse)').matches)||(window.matchMedia&&window.matchMedia('(max-width:700px)').matches)))return 1;return window.matchMedia('(orientation:landscape)').matches ? 1.08 : 1.12;}</script>\n"
    text = text.replace(marker, helper + marker, 1)

patch = r'''<!-- ===== PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->
<script>
(function(){
  'use strict';

  /* MOBILE CAMERA + UI ZOOM: 8% landscape / 12% portrait. */
  const mobileZoomStyle=document.createElement('style');
  mobileZoomStyle.textContent=`
    @media (max-width:700px),(pointer:coarse){
      #hud,#zoneLabel,#message,#controls,#buttons,#spellBar,#dialogue,
      #bagWindow,#exchangeWindow,#friendsWindow,#mailWindow,
      #pandaniaMobileControls{zoom:1.08;}
      #pandaniaMobileControls{transform-origin:center bottom;}
    }
  `;
  document.head.appendChild(mobileZoomStyle);

  const isMobileDevice=()=>{
    try{return matchMedia('(pointer:coarse)').matches||matchMedia('(max-width:700px)').matches;}
    catch(e){return false;}
  };

  /* Mobile world taps are pickup-only; they can never create movement. */
  function zoomAwareWorldPoint(e){
    const rect=canvas.getBoundingClientRect();
    const sx=(e.clientX-rect.left)*(W/rect.width);
    const sy=(e.clientY-rect.top)*(H/rect.height);
    const z=(typeof pandaniaMobileZoom==='function'&&isMobileDevice()) ? pandaniaMobileZoom() : 1;
    if(z!==1){
      const viewW=W/z, viewH=H/z;
      return {x:camera.x+viewW/2+(sx-W/2)/z,y:camera.y+viewH/2+(sy-H/2)/z};
    }
    return {x:sx+camera.x,y:sy+camera.y};
  }

  function pickupGroundItemAt(p){
    if(!Array.isArray(groundDrops)||!groundDrops.length)return false;
    let bestIndex=-1,bestDistance=Infinity;
    for(let i=groundDrops.length-1;i>=0;i--){
      const d=groundDrops[i],dist=Math.hypot(p.x-d.x,p.y-d.y);
      if(dist<110&&dist<bestDistance){bestDistance=dist;bestIndex=i;}
    }
    if(bestIndex<0)return false;
    const drop=groundDrops[bestIndex];
    if(typeof collectDrop!=='function')return false;
    if(!collectDrop(drop))return true;
    groundDrops.splice(bestIndex,1);
    try{updateUI();}catch(e){}
    try{renderBag();}catch(e){}
    return true;
  }

  if(typeof canvas!=='undefined')canvas.addEventListener('pointerdown',function(e){
    if(!isMobileDevice()||!gameStarted)return;
    const p=zoomAwareWorldPoint(e);
    if(pickupGroundItemAt(p)){e.preventDefault();e.stopImmediatePropagation();return;}
    e.preventDefault();e.stopImmediatePropagation();
  },true);

  const weaponCritStats={
    'Wooden Sword':{critChance:.20,critBonus:.05},'Bamboo Sword':{critChance:.20,critBonus:.05},
    'Iron Sword':{critChance:.20,critBonus:.05},'Goblin Saber':{critChance:.20,critBonus:.05},
    'XPR Lens':{critChance:.20,critBonus:.05},'Spiked Twin Blade':{critChance:.20,critBonus:.05},
    'Purple Ice Blade':{critChance:.20,critBonus:.05},'Thunderma':{critChance:.20,critBonus:.05},
    'Diamond staff':{critChance:.20,critBonus:.05},'Golden Beacon Staff':{critChance:.20,critBonus:.05},
    'Purplereign':{critChance:.20,critBonus:.05}
  };
  window.__pandaniaWeaponCritStats=weaponCritStats;

  /* Critical visual: white number, larger size, neon-red glow. */
  window.addDamageNumber=function(x,y,amount,color,crit){
    damageNumbers.push({x,y,amount,color:color||'#fff',crit:!!crit,life:55,maxLife:55});
  };

  const weaponRanges=window.__pandaniaWeaponStats||{
    'Wooden Sword':{min:8,max:12},'Bamboo Sword':{min:8,max:12},'Iron Sword':{min:25,max:35},
    'Goblin Saber':{min:8,max:12},'XPR Lens':{min:165,max:180},'Spiked Twin Blade':{min:75,max:90},
    'Purple Ice Blade':{min:50,max:65},'Thunderma':{min:200,max:250},'Diamond staff':{min:105,max:125},
    'Golden Beacon Staff':{min:130,max:155},'Purplereign':{min:190,max:230}
  };

  function equippedWeaponName(){const s=window.__pandaniaEquipment;return s&&s.weapon?s.weapon:'Wooden Sword';}

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
        if(dot>=.15&&d<distance){closest=m;distance=d;}
      }
      if(!closest)for(const m of monsters){const d=Math.hypot(m.x-player.x,m.y-player.y);if(d<82&&d<distance){closest=m;distance=d;}}
      target=closest;
    }
    if(!target){if(typeof showMessage==='function')showMessage('⚔️ Sword swing!');return;}
    if(Math.hypot(target.x-player.x,target.y-player.y)>88)return;
    const name=equippedWeaponName(),range=weaponRanges[name]||weaponRanges['Wooden Sword'];
    const rolled=Math.floor(Math.random()*(range.max-range.min+1))+range.min;
    let damage=Math.max(1,rolled-(target.defense||0));
    const info=weaponCritStats[name]||{critChance:.20,critBonus:.05};
    const critical=Math.random()<info.critChance;
    if(critical)damage=Math.max(1,Math.round(damage*(1+info.critBonus)));
    target.hp-=damage;addDamageNumber(target.x,target.y-38,damage,'#fff',critical);target.hitFlash=8;
    if(typeof hitSound==='function')hitSound();
    if(typeof showMessage==='function')showMessage(critical?'💥 CRITICAL! '+target.name+' for '+damage+' damage!':'⚔️ Hit '+target.name+' for '+damage+' damage!');
    if(target.hp<=0&&typeof killMonster==='function')killMonster(target);
  };

  /* Make CRIT 20% visible on weapon cards without touching existing cards twice. */
  function decorateWeaponCards(){
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const nameEl=card.querySelector('.itemName');if(!nameEl)return;
      const name=nameEl.textContent.trim();if(!weaponCritStats[name]||card.querySelector('.pandaniaCritStat'))return;
      const range=weaponRanges[name]||{};const stat=document.createElement('div');stat.className='pandaniaCritStat';
      stat.innerHTML='ATK '+(range.min??'?')+'–'+(range.max??'?')+' · CRIT 20% <span>(+5%)</span>';card.appendChild(stat);
    });
  }
  const critCardStyle=document.createElement('style');critCardStyle.textContent=`.pandaniaCritStat{margin-top:5px;color:#ffdc70;font-size:10px;font-weight:bold;line-height:1.25;text-align:center;text-shadow:0 0 5px rgba(255,216,80,.2)}.pandaniaCritStat span{color:#ff6878}`;document.head.appendChild(critCardStyle);
  new MutationObserver(decorateWeaponCards).observe(document.body,{childList:true,subtree:true});
  setTimeout(decorateWeaponCards,250);
  window.__pandaniaMobileCritZoomV12=true;
})();
</script>
<!-- ===== END PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->'''

text=text.replace('</body>',patch+'\n</body>',1) if '</body>' in text else text+'\n'+patch+'\n'
path.write_text(text,encoding='utf-8')
