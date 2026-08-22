from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

# Remove an older copy if this workflow is re-run.
text = re.sub(r'<!-- ===== PANDANIA V13 COMBAT/INPUT PATCH ===== -->.*?<!-- ===== END PANDANIA V13 COMBAT/INPUT PATCH ===== -->', '', text, flags=re.S)

patch = r'''<!-- ===== PANDANIA V13 COMBAT/INPUT PATCH ===== -->
<script>
(function(){
  'use strict';

  /* =========================================================
     V13 WEAPON CRITICAL STATS
     Each weapon has its own chance (5%-50%) and bonus (5%-20%).
  ========================================================= */
  const critStats={
    'Wooden Sword':      {chance:.05, bonus:.05},
    'Bamboo Sword':      {chance:.08, bonus:.06},
    'Iron Sword':        {chance:.12, bonus:.08},
    'Goblin Saber':      {chance:.15, bonus:.10},
    'XPR Lens':          {chance:.18, bonus:.12},
    'Spiked Twin Blade': {chance:.22, bonus:.14},
    'Purple Ice Blade':  {chance:.27, bonus:.15},
    'Diamond staff':     {chance:.32, bonus:.16},
    'Golden Beacon Staff':{chance:.40, bonus:.18},
    'Thunderma':         {chance:.45, bonus:.19},
    'Purplereign':       {chance:.50, bonus:.20}
  };
  window.__pandaniaWeaponCritStatsV13=critStats;

  /* =========================================================
     NO SCREEN-TAP MOVEMENT — DESKTOP + MOBILE
     A click/tap on the game canvas is never a movement command.
     Keyboard movement remains WASD/arrows; mobile remains joystick.
     Ground-item pickup is intentionally preserved by the earlier
     pickup handler and is not treated as movement.
  ========================================================= */
  function blockCanvasMovementInput(e){
    if(!window.gameStarted && !document.getElementById('gameWrap')?.classList.contains('pandaniaStarted')) return;
    const t=e.target;
    if(t!==canvas) return;
    /* Stop both bubbling and later handlers attached to canvas/document. */
    e.preventDefault();
    e.stopImmediatePropagation();
  }
  if(typeof canvas!=='undefined'){
    ['pointerdown','pointerup','mousedown','mouseup','click','dblclick','contextmenu'].forEach(type=>{
      canvas.addEventListener(type,blockCanvasMovementInput,true);
    });
  }

  /* =========================================================
     CRITICAL ATTACKS
     Normal damage numbers = white.
     Critical damage numbers = larger yellow + neon-red glow.
  ========================================================= */
  function weaponName(){
    return (window.__pandaniaEquipment&&window.__pandaniaEquipment.weapon) || 'Wooden Sword';
  }
  function attackRange(name){
    const ranges=window.__pandaniaWeaponStats||{};
    return ranges[name]||ranges['Wooden Sword']||{min:8,max:12};
  }

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
        if(dot>=.15&&d<distance){closest=m;distance=d;}
      }
      if(!closest){
        for(const m of monsters){
          const d=Math.hypot(m.x-player.x,m.y-player.y);
          if(d<82&&d<distance){closest=m;distance=d;}
        }
      }
      target=closest;
    }
    if(!target){if(typeof showMessage==='function')showMessage('⚔️ Sword swing!');return;}
    if(Math.hypot(target.x-player.x,target.y-player.y)>88)return;

    const name=weaponName();
    const r=attackRange(name);
    const rolled=Math.floor(Math.random()*(r.max-r.min+1))+r.min;
    let damage=Math.max(1,rolled-(target.defense||0));
    const stat=critStats[name]||critStats['Wooden Sword'];
    const critical=Math.random()<stat.chance;
    if(critical)damage=Math.max(1,Math.round(damage*(1+stat.bonus)));

    target.hp-=damage;
    addDamageNumber(target.x,target.y-38,damage,'#fff',critical);
    target.hitFlash=8;
    if(typeof hitSound==='function')hitSound();
    if(typeof showMessage==='function')showMessage(critical?'💥 CRITICAL! '+target.name+' for '+damage+' damage!':'⚔️ Hit '+target.name+' for '+damage+' damage!');
    if(target.hp<=0&&typeof killMonster==='function')killMonster(target);
  };

  /* Replace the damage-number renderer with the requested visual distinction. */
  window.drawDamageNumbers=function(){
    for(const d of damageNumbers){
      ctx.save();
      ctx.globalAlpha=d.life/d.maxLife;
      ctx.textAlign='center';
      if(d.crit){
        ctx.font='900 34px Arial';
        ctx.fillStyle='#ffe94a';
        ctx.shadowColor='#ff102b';
        ctx.shadowBlur=24;
        ctx.lineWidth=3;
        ctx.strokeStyle='rgba(255,20,40,.72)';
        ctx.strokeText(String(d.amount),d.x,d.y);
        ctx.fillText(String(d.amount),d.x,d.y);
      }else{
        ctx.font='900 20px Arial';
        ctx.fillStyle='#fff';
        ctx.shadowColor='#000';
        ctx.shadowBlur=4;
        ctx.fillText(String(d.amount),d.x,d.y);
      }
      ctx.restore();
    }
  };

  /* =========================================================
     GREEN WEAPON STAT BOX
     ATK range + individual CRIT chance + CRIT damage bonus.
  ========================================================= */
  const statStyle=document.createElement('style');
  statStyle.textContent=`
    .pandaniaWeaponGreenStats{
      margin-top:6px;padding:5px 4px;border-radius:5px;
      background:rgba(13,65,32,.92);
      border:1px solid #25e86e;
      color:#69ff9a;
      font-size:10px;font-weight:800;line-height:1.45;
      text-align:center;
      box-shadow:0 0 6px rgba(37,232,110,.22);
      text-shadow:0 0 5px rgba(74,255,139,.25);
    }
    .pandaniaWeaponGreenStats .critChance{color:#7dffad}
    .pandaniaWeaponGreenStats .critDamage{color:#ffe66b}
    @media(max-width:700px),(pointer:coarse){
      .pandaniaWeaponGreenStats{font-size:9px;padding:4px 2px}
    }
  `;
  document.head.appendChild(statStyle);

  function decorateWeaponCardsV13(){
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const nameEl=card.querySelector('.itemName');
      if(!nameEl)return;
      const name=nameEl.textContent.trim();
      if(!critStats[name])return;
      const old=card.querySelectorAll('.pandaniaCritStat');
      old.forEach(el=>el.remove());
      let box=card.querySelector('.pandaniaWeaponGreenStats');
      if(!box){box=document.createElement('div');box.className='pandaniaWeaponGreenStats';card.appendChild(box)}
      const r=attackRange(name),s=critStats[name];
      box.innerHTML='ATK '+r.min+'–'+r.max+' · CRIT <span class="critChance">'+Math.round(s.chance*100)+'%</span> · CRIT DMG <span class="critDamage">+'+Math.round(s.bonus*100)+'%</span>';
    });
  }

  /* Existing renderBag is preserved; observer adds stats after each render. */
  const observer=new MutationObserver(decorateWeaponCardsV13);
  observer.observe(document.body,{childList:true,subtree:true});
  setTimeout(decorateWeaponCardsV13,250);

  /* =========================================================
     MOBILE MONSTER WIDTH
     Scale monster drawing horizontally by 15% on mobile only.
     This patches the existing draw source so sprites/icons are
     actually wider rather than changing their height.
  ========================================================= */
  try{
    const source=Function.prototype.toString.call(window.draw);
    if(source.includes("ctx.font='40px Arial';ctx.fillText(m.icon||'👹',m.x,m.y)") && !source.includes('__pandaniaMonsterWideV13')){
      const replacement="if((window.matchMedia('(pointer:coarse)').matches||window.matchMedia('(max-width:700px)').matches)){ctx.save();ctx.translate(m.x,m.y);ctx.scale(1.15,1);ctx.font='40px Arial';ctx.fillText(m.icon||'👹',0,0);ctx.restore();}else{ctx.font='40px Arial';ctx.fillText(m.icon||'👹',m.x,m.y)}";
      const patched=source.replace("ctx.font='40px Arial';ctx.fillText(m.icon||'👹',m.x,m.y)",replacement+'/*__pandaniaMonsterWideV13*/');
      if(patched!==source){
        /* Rebuild only when the exact compact draw pattern is present. */
        window.draw=Function('return '+patched)();
      }
    }
  }catch(e){console.warn('Pandania mobile monster width patch skipped:',e)}

  window.__pandaniaV13=true;
})();
</script>
<!-- ===== END PANDANIA V13 COMBAT/INPUT PATCH ===== -->'''

text=text.replace('</body>',patch+'\n</body>',1) if '</body>' in text else text+'\n'+patch+'\n'
path.write_text(text,encoding='utf-8')
