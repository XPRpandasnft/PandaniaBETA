from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

# Remove all prior gameplay patch generations before installing the corrected one.
for version in ('v2','v3','v4'):
    text = re.sub(
        rf'/\* ===== PANDANIA GAMEPLAY PATCH {version} ===== \*/.*?/\* ===== END PANDANIA GAMEPLAY PATCH {version} ===== \*/',
        '', text, flags=re.S
    )

new_patch = r'''/* ===== PANDANIA GAMEPLAY PATCH v4 ===== */
(function(){
  /* This patch deliberately avoids strict-mode undeclared globals. */
  const state = window.__pandaniaEquipment || (window.__pandaniaEquipment = {
    weapon: 'Wooden Sword', armor: null, tool: null,
    dirX: 0, dirY: 1, facing: 'down'
  });

  function setDirection(dx,dy){
    if(!dx && !dy) return;
    if(Math.abs(dx) >= Math.abs(dy)){
      state.dirX = dx < 0 ? -1 : 1; state.dirY = 0;
      state.facing = dx < 0 ? 'left' : 'right';
    }else{
      state.dirX = 0; state.dirY = dy < 0 ? -1 : 1;
      state.facing = dy < 0 ? 'up' : 'down';
    }
    player.attackDX=state.dirX;
    player.attackDY=state.dirY;
    player.facing = state.facing === 'left' ? -1 : 1;
  }

  const oldUpdatePlayer = updatePlayer;
  updatePlayer = function(){
    oldUpdatePlayer();
    let dx=0,dy=0;
    if(keys['a']||keys['arrowleft']) dx--;
    if(keys['d']||keys['arrowright']) dx++;
    if(keys['w']||keys['arrowup']) dy--;
    if(keys['s']||keys['arrowdown']) dy++;
    if(dx||dy) setDirection(dx,dy);
  };

  window.addEventListener('keydown',function(e){
    const k=e.key.toLowerCase();
    if(k==='a'||k==='arrowleft') setDirection(-1,0);
    if(k==='d'||k==='arrowright') setDirection(1,0);
    if(k==='w'||k==='arrowup') setDirection(0,-1);
    if(k==='s'||k==='arrowdown') setDirection(0,1);
  },true);

  /* Four-direction player rendering: down=normal, up=180 degrees,
     left/right=mirrored. This works with the existing single player sprite. */
  drawPlayer = function(){
    const bob = player.moving ? Math.abs(Math.sin(player.walkTime))*3 : Math.sin(Date.now()/700)*.35;
    const alpha = player.invincible>0 && Math.floor(player.invincible/4)%2===0 ? .25 : 1;
    const img=images['player1'];
    if(img){
      ctx.save();
      ctx.globalAlpha=alpha;
      ctx.translate(player.x,player.y+bob);
      if(state.facing==='left') ctx.scale(-1,1);
      if(state.facing==='up') ctx.rotate(Math.PI);
      ctx.imageSmoothingEnabled=false;
      ctx.drawImage(img,-38,-100,76,100);
      ctx.restore();
    }else{
      drawFallbackPlayer();
    }
    ctx.save();
    ctx.fillStyle='rgba(255,255,255,.95)';
    ctx.font='bold 10px Arial';
    ctx.textAlign='center';
    ctx.fillText('Pandee',player.x,player.y-108);
    ctx.restore();
    drawPlayerEffects();
  };

  /* Attack uses the selected facing direction and always applies damage to the
     selected monster. Clicking a monster still targets it, but the player must
     be within sword range. */
  swordAttack = function(target=null){
    if(player.attackCooldown>0) return;
    player.attackCooldown=22;
    player.swordSwing=12;
    swordSound();

    if(target && monsters.includes(target)){
      const dx=target.x-player.x,dy=target.y-player.y;
      setDirection(dx,dy);
    }else{
      let best=null,bestScore=-Infinity;
      const ax=state.dirX||0, ay=state.dirY||1;
      for(const m of monsters){
        const dx=m.x-player.x,dy=m.y-player.y;
        const d=Math.hypot(dx,dy);
        if(!d || d>105) continue;
        const dot=(dx/d)*ax+(dy/d)*ay;
        if(dot < .2) continue;
        const score=dot*4-d/105;
        if(score>bestScore){bestScore=score;best=m;}
      }
      target=best;
    }

    if(!target){ showMessage('⚔️ Sword swing!'); return; }
    const d=Math.hypot(target.x-player.x,target.y-player.y);
    if(d>105){ showMessage('⚔️ Too far away!'); return; }

    const weaponDamage={
      'Wooden Sword':8,'Weapon 1':22,'Weapon 2':30,'Weapon 3':42
    }[state.weapon] || 8;
    const damage=15+(Number(player.level)||1)*3+weaponDamage;
    const before=Number(target.hp)||0;
    target.hp=Math.max(0,before-damage);
    target.hitFlash=8;
    hitSound();
    showMessage('⚔️ '+state.weapon+' hit '+target.name+' for '+damage+' damage!');
    if(target.hp<=0) killMonster(target);
  };

  /* Paper doll is built directly into the bag every time it opens. */
  function ensureEquipment(){
    const bag=document.getElementById('bagWindow');
    const items=document.getElementById('bagItems');
    if(!bag || !items) return null;
    let panel=document.getElementById('pandaniaEquipment');
    if(!panel){
      panel=document.createElement('div');
      panel.id='pandaniaEquipment';
      panel.style.cssText='margin:0 0 16px;padding:14px;border:2px solid #8b683e;border-radius:12px;background:#15100c;color:#fff;';
      panel.innerHTML='<div style="text-align:center;color:#ffd86a;font-size:19px;font-weight:bold;margin-bottom:10px">🧍 PANDEE — EQUIPMENT</div>'+
        '<div style="display:grid;grid-template-columns:1fr 130px 1fr;gap:10px;align-items:center">'+
        '<div style="display:flex;flex-direction:column;gap:8px">'+
        '<div id="equipWeapon" class="equipSlot"></div><div id="equipTool" class="equipSlot"></div></div>'+
        '<div style="height:145px;border:2px solid #6f5333;border-radius:10px;background:#090909;display:flex;align-items:center;justify-content:center;font-size:70px">🐼</div>'+
        '<div style="display:flex;flex-direction:column;gap:8px"><div id="equipArmor" class="equipSlot"></div><div style="font-size:11px;color:#b9a78d;text-align:center">Double-click an inventory item to equip it.</div></div></div>';
      items.parentNode.insertBefore(panel,items);
    }
    return panel;
  }

  function slot(el,icon,label,item,canEquip){
    el.style.cssText='padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center;min-height:68px;cursor:pointer;';
    el.innerHTML='<div style="color:#e7bd73;font-weight:bold">'+icon+' '+label+'</div><div style="margin:6px 0;color:'+(item?'#fff':'#777')+'">'+(item||'Empty')+'</div>'+(item?'<button type="button" class="unequipButton" style="border:1px solid #b55c4c;background:#4a251f;color:#fff;border-radius:5px;padding:4px 9px;cursor:pointer">Unequip</button>':'');
    const b=el.querySelector('.unequipButton');
    if(b) b.onclick=function(e){e.stopPropagation(); if(label==='Weapon') state.weapon=''; if(label==='Armor') state.armor=null; if(label==='Tool') state.tool=null; renderEquipment();};
  }

  function renderEquipment(){
    ensureEquipment();
    slot(document.getElementById('equipWeapon'),'⚔️','Weapon',state.weapon,true);
    slot(document.getElementById('equipArmor'),'🛡️','Armor',state.armor,true);
    slot(document.getElementById('equipTool'),'🛠️','Tool',state.tool,true);
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const nameEl=card.querySelector('.itemName');
      if(!nameEl) return;
      const name=nameEl.textContent.trim();
      const equippable=/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3|Iron Armor|Woodcutting Axe|Fishing Rod)$/.test(name);
      if(!equippable) return;
      card.style.cursor='pointer';
      card.title='Double-click to equip '+name;
      card.ondblclick=function(e){
        e.preventDefault();e.stopPropagation();
        if(!inventory[name] || Number(inventory[name].count)<=0) return;
        if(/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3)$/.test(name)) state.weapon=name;
        else if(name==='Iron Armor') state.armor=name;
        else state.tool=name;
        renderEquipment();
        showMessage('✅ '+name+' equipped!');
      };
    });
  }

  const oldRenderBag=renderBag;
  renderBag=function(){ oldRenderBag(); renderEquipment(); };

  /* Render immediately if the bag is already open. */
  if(document.getElementById('bagWindow')?.style.display==='block') renderEquipment();

  window.__pandaniaGameplayV4=true;
})();
/* ===== END PANDANIA GAMEPLAY PATCH v4 ===== */'''

marker='</script>'
if marker not in text:
    raise SystemExit('Missing closing script tag')
text=text.replace(marker,'\n'+new_patch.strip()+'\n'+marker,1)
path.write_text(text,encoding='utf-8')
print('Pandania gameplay v4 installed')
