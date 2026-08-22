from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

# Replace any previous copy of this patch so the workflow is idempotent.
text = re.sub(
    r'<!-- ===== PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->.*?<!-- ===== END PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->',
    '',
    text,
    flags=re.S,
)

# The camera already has a mobile-specific zoom function.  Values below 1 zoom
# out; values above 1 zoom in.  Give mobile a modest, deliberate zoom-in.
text = re.sub(
    r'(function pandaniaMobileZoom\(\)\{.*?return window\.matchMedia\("\(orientation:landscape\)"\)\.matches \? )\.94( : )\.88(;)'
    , r'\g<1>1.08\g<2>1.12\g<3>',
    text,
    count=1,
    flags=re.S,
)

patch = r'''<!-- ===== PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->
<script>
(function(){
  'use strict';

  /* ---------------------------------------------------------
     MOBILE ZOOM + UI SCALING
     The game camera is zoomed in slightly on phones while the
     overlay controls/HUD are scaled with it so the interface
     remains visually balanced.
  --------------------------------------------------------- */
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

  /* ---------------------------------------------------------
     MOBILE MOVEMENT RULE
     A tap on the game world can NEVER set a movement target on
     mobile. The joystick remains the only movement input.

     Ground-item taps are the exception: a generous pickup radius
     lets players collect an item without needing pixel-perfect taps.
  --------------------------------------------------------- */
  function zoomAwareWorldPoint(e){
    const rect=canvas.getBoundingClientRect();
    const sx=(e.clientX-rect.left)*(W/rect.width);
    const sy=(e.clientY-rect.top)*(H/rect.height);
    const z=(typeof pandaniaMobileZoom==='function'&&isMobileDevice()) ? pandaniaMobileZoom() : 1;
    if(z!==1){
      const viewW=W/z, viewH=H/z;
      return {
        x:camera.x+viewW/2+(sx-W/2)/z,
        y:camera.y+viewH/2+(sy-H/2)/z
      };
    }
    return {x:sx+camera.x,y:sy+camera.y};
  }

  function pickupGroundItemAt(p){
    if(!Array.isArray(groundDrops)||!groundDrops.length)return false;
    let bestIndex=-1,bestDistance=Infinity;
    for(let i=groundDrops.length-1;i>=0;i--){
      const d=groundDrops[i];
      const dist=Math.hypot(p.x-d.x,p.y-d.y);
      if(dist<110 && dist<bestDistance){bestDistance=dist;bestIndex=i;}
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

  if(typeof canvas!=='undefined'){
    canvas.addEventListener('pointerdown',function(e){
      if(!isMobileDevice() || !gameStarted)return;
      const p=zoomAwareWorldPoint(e);
      /* First priority on mobile: collect anything reasonably near the tap. */
      if(pickupGroundItemAt(p)){
        e.preventDefault();
        e.stopImmediatePropagation();
        return;
      }
      /* No world tapping movement on mobile. */
      e.preventDefault();
      e.stopImmediatePropagation();
    },true);
  }

  /* ---------------------------------------------------------
     WEAPON CRIT STATS
     Every weapon has a 20% crit chance. A critical hit increases
     that weapon's rolled attack damage by 5%.
  --------------------------------------------------------- */
  const weaponCritStats={
    'Wooden Sword':{critChance:.20,critBonus:.05},
    'Bamboo Sword':{critChance:.20,critBonus:.05},
    'Iron Sword':{critChance:.20,critBonus:.05},
    'Goblin Saber':{critChance:.20,critBonus:.05},
    'XPR Lens':{critChance:.20,critBonus:.05},
    'Spiked Twin Blade':{critChance:.20,critBonus:.05},
    'Purple Ice Blade':{critChance:.20,critBonus:.05},
    'Thunderma':{critChance:.20,critBonus:.05},
    'Diamond staff':{critChance:.20,critBonus:.05},
    'Golden Beacon Staff':{critChance:.20,critBonus:.05},
    'Purplereign':{critChance:.20,critBonus:.05}
  };
  window.__pandaniaWeaponCritStats=weaponCritStats;

  if(Array.isArray(window.weaponDrops)){
    window.weaponDrops.forEach(w=>{
      if(weaponCritStats[w.name]){
        w.critChance=.20;
        w.critBonus=.05;
      }
    });
  }

  function equippedWeaponName(){
    const s=window.__pandaniaEquipment;
    return s&&s.weapon ? s.weapon : 'Wooden Sword';
  }

  /* ---------------------------------------------------------
     CRITICAL DAMAGE NUMBERS
     Critical numbers remain white, become larger, and receive a
     strong neon-red glow as requested.
  --------------------------------------------------------- */
  window.addDamageNumber=function(x,y,amount,color,crit){
    damageNumbers.push({x,y,amount,color:color||'#fff',crit:!!crit,life:55,maxLife:55});
  };

  window.drawDamageNumbers=function(){
    for(const d of damageNumbers){
      ctx.save();
      ctx.globalAlpha=d.life/d.maxLife;
      ctx.textAlign='center';
      if(d.crit){
        ctx.fillStyle='#fff';
        ctx.font='900 31px Arial';
        ctx.shadowColor='#ff102b';
        ctx.shadowBlur=20;
        ctx.lineWidth=2;
        ctx.strokeStyle='rgba(255,0,32,.55)';
        ctx.strokeText(String(d.amount),d.x,d.y);
        ctx.fillText(String(d.amount),d.x,d.y);
      }else{
        ctx.fillStyle=d.color;
        ctx.font='900 20px Arial';
        ctx.shadowColor='#000';
        ctx.shadowBlur=4;
        ctx.fillText(String(d.amount),d.x,d.y);
      }
      ctx.restore();
    }
  };

  /* ---------------------------------------------------------
     FINAL WEAPON ATTACK HANDLER
     This keeps the existing weapon ranges and adds the crit roll
     without relying on inventory quantity to determine damage.
  --------------------------------------------------------- */
  const weaponRanges=window.__pandaniaWeaponStats||{
    'Wooden Sword':{min:8,max:12},
    'Bamboo Sword':{min:8,max:12},
    'Iron Sword':{min:25,max:35},
    'Goblin Saber':{min:8,max:12},
    'XPR Lens':{min:165,max:180},
    'Spiked Twin Blade':{min:75,max:90},
    'Purple Ice Blade':{min:50,max:65},
    'Thunderma':{min:200,max:250},
    'Diamond staff':{min:105,max:125},
    'Golden Beacon Staff':{min:130,max:155},
    'Purplereign':{min:190,max:230}
  };

  window.swordAttack=function(target=null){
    if(player.attackCooldown>0)return;
    player.attackCooldown=22;
    player.swordSwing=12;
    if(typeof swordSound==='function')swordSound();

    if(!target){
      let closest=null,distance=Infinity;
      for(const m of monsters){
        const vx=m.x-player.x,vy=m.y-player.y,d=Math.hypot(vx,vy);
        if(d>95||d<1)continue;
        const dot=(vx*(player.facingX||0)+vy*(player.facingY||0))/d;
        if(dot>=0.15&&d<distance){closest=m;distance=d;}
      }
      if(!closest){
        for(const m of monsters){
          const d=Math.hypot(m.x-player.x,m.y-player.y);
          if(d<82&&d<distance){closest=m;distance=d;}
        }
      }
      target=closest;
    }

    if(!target){
      if(typeof showMessage==='function')showMessage('⚔️ Sword swing!');
      return;
    }

    const d=Math.hypot(target.x-player.x,target.y-player.y);
    if(d>88)return;

    const name=equippedWeaponName();
    const range=weaponRanges[name]||weaponRanges['Wooden Sword'];
    const rolled=Math.floor(Math.random()*(range.max-range.min+1))+range.min;
    const defense=target.defense||0;
    let damage=Math.max(1,rolled-defense);
    const critInfo=weaponCritStats[name]||{critChance:.20,critBonus:.05};
    const critical=Math.random()<critInfo.critChance;
    if(critical)damage=Math.max(1,Math.round(damage*(1+critInfo.critBonus)));

    target.hp-=damage;
    addDamageNumber(target.x,target.y-38,damage,'#fff',critical);
    target.hitFlash=8;
    if(typeof hitSound==='function')hitSound();

    if(typeof showMessage==='function'){
      showMessage(
        critical
          ? '💥 CRITICAL! '+target.name+' for '+damage+' damage!'
          : '⚔️ Hit '+target.name+' for '+damage+' damage!'
      );
    }

    if(target.hp<=0 && typeof killMonster==='function')killMonster(target);
  };

  /* ---------------------------------------------------------
     SHOW CRIT CHANCE ON WEAPON ITEMS
  --------------------------------------------------------- */
  function decorateWeaponCards(){
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const nameEl=card.querySelector('.itemName');
      if(!nameEl)return;
      const name=nameEl.textContent.trim();
      if(!weaponCritStats[name])return;
      if(card.querySelector('.pandaniaCritStat'))return;
      const range=weaponRanges[name]||{};
      const stat=document.createElement('div');
      stat.className='pandaniaCritStat';
      stat.innerHTML='ATK '+(range.min??'?')+'–'+(range.max??'?')+' · CRIT 20% <span>(+5%)</span>';
      card.appendChild(stat);
    });
  }

  const critCardStyle=document.createElement('style');
  critCardStyle.textContent=`
    .pandaniaCritStat{margin-top:5px;color:#ffdc70;font-size:10px;font-weight:bold;line-height:1.25;text-align:center;text-shadow:0 0 5px rgba(255,216,80,.2)}
    .pandaniaCritStat span{color:#ff6878}
  `;
  document.head.appendChild(critCardStyle);

  const bagCritObserver=new MutationObserver(()=>decorateWeaponCards());
  bagCritObserver.observe(document.body,{childList:true,subtree:true});
  setTimeout(decorateWeaponCards,250);

  window.__pandaniaMobileCritZoomV12=true;
})();
</script>
<!-- ===== END PANDANIA MOBILE CRIT/ZOOM PATCH v12 ===== -->'''

# Append after the game's scripts so it becomes the final input/combat layer.
if '</body>' in text:
    text=text.replace('</body>', patch+'\n</body>', 1)
elif '</html>' in text:
    text=text.replace('</html>', patch+'\n</html>', 1)
else:
    text += '\n' + patch + '\n'

path.write_text(text, encoding='utf-8')
