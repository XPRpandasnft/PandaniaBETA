from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

# Remove every copy of the old v2 patch. The repository currently contains it twice.
text = re.sub(
    r'/\* ===== PANDANIA GAMEPLAY PATCH v2 ===== \*/.*?/\* ===== END PANDANIA GAMEPLAY PATCH v2 ===== \*/',
    '',
    text,
    flags=re.S,
)
# Remove any previous v3 copy so this script is safe to run again.
text = re.sub(
    r'/\* ===== PANDANIA GAMEPLAY PATCH v3 ===== \*/.*?/\* ===== END PANDANIA GAMEPLAY PATCH v3 ===== \*/',
    '',
    text,
    flags=re.S,
)

new_patch = r'''/* ===== PANDANIA GAMEPLAY PATCH v3 ===== */
(function(){
  'use strict';

  /* ---------- Direction / movement ---------- */
  player.attackDX = player.attackDX || 0;
  player.attackDY = player.attackDY || 1;
  player.facingX = player.facingX || 0;
  player.facingY = player.facingY || 1;

  function setPlayerDirection(dx,dy){
    if(!dx && !dy) return;
    const len=Math.hypot(dx,dy)||1;
    player.attackDX=dx/len;
    player.attackDY=dy/len;
    player.facingX=player.attackDX;
    player.facingY=player.attackDY;
    if(dx<0) player.facing=-1;
    if(dx>0) player.facing=1;
  }

  window.addEventListener('keydown',function(e){
    const k=e.key.toLowerCase();
    const d={
      w:[0,-1],arrowup:[0,-1],
      s:[0,1],arrowdown:[0,1],
      a:[-1,0],arrowleft:[-1,0],
      d:[1,0],arrowright:[1,0]
    }[k];
    if(d) setPlayerDirection(d[0],d[1]);
  },true);

  const baseUpdatePlayer=updatePlayer;
  updatePlayer=function(){
    baseUpdatePlayer();
    let dx=0,dy=0;
    if(keys['a']||keys['arrowleft']) dx--;
    if(keys['d']||keys['arrowright']) dx++;
    if(keys['w']||keys['arrowup']) dy--;
    if(keys['s']||keys['arrowdown']) dy++;
    if(dx||dy) setPlayerDirection(dx,dy);
  };

  /* ---------- Directional sword combat ---------- */
  swordAttack=function(target=null){
    if(player.attackCooldown>0) return;
    player.attackCooldown=22;
    player.swordSwing=12;
    swordSound();

    if(target && monsters.includes(target)){
      const tx=target.x-player.x,ty=target.y-player.y;
      setPlayerDirection(tx,ty);
    }else{
      const ax=player.attackDX||0,ay=player.attackDY||1;
      let best=null,bestScore=-Infinity;
      for(const m of monsters){
        const dx=m.x-player.x,dy=m.y-player.y;
        const dist=Math.hypot(dx,dy);
        if(!dist || dist>110) continue;
        const dot=(dx/dist)*ax+(dy/dist)*ay;
        if(dot<0.25) continue;
        const score=dot*3-(dist/110);
        if(score>bestScore){bestScore=score;best=m;}
      }
      target=best;
    }

    if(!target){
      showMessage('⚔️ Swinging '+(equippedWeapon||'Wooden Sword')+' toward your facing!');
      return;
    }

    const dist=Math.hypot(target.x-player.x,target.y-player.y);
    if(dist>110){
      showMessage('⚔️ Too far away!');
      return;
    }

    const weaponDamage={
      'Wooden Sword':8,
      'Weapon 1':22,
      'Weapon 2':30,
      'Weapon 3':42
    }[equippedWeapon||'Wooden Sword']||8;
    const damage=15+player.level*3+weaponDamage;
    target.hp-=damage;
    target.hitFlash=8;
    hitSound();
    showMessage('⚔️ '+(equippedWeapon||'Wooden Sword')+' hit '+target.name+' for '+damage+' damage!');
    if(target.hp<=0) killMonster(target);
  };

  /* ---------- Keep monster images proportional ---------- */
  drawMonster=function(m){
    ctx.save();
    const img=images[m.image];
    const h=m.boss?126:96;
    const w=(img&&img.naturalWidth&&img.naturalHeight)
      ?Math.max(1,Math.round(h*(img.naturalWidth/img.naturalHeight)))
      :h;
    ctx.fillStyle='rgba(0,0,0,.32)';
    ctx.beginPath();
    ctx.ellipse(m.x,m.y+5,Math.max(18,w*.34),8,0,0,Math.PI*2);
    ctx.fill();
    if(img){
      ctx.imageSmoothingEnabled=false;
      ctx.drawImage(img,Math.round(m.x-w/2),Math.round(m.y-h),w,h);
    }else{
      ctx.fillStyle=m.boss?'#5b1d32':'#75a83f';
      ctx.beginPath();
      ctx.arc(m.x,m.y-h*.45,m.boss?42:30,0,Math.PI*2);
      ctx.fill();
    }
    const bw=m.boss?Math.min(170,Math.max(100,w+25)):Math.min(105,Math.max(62,w+10));
    const by=m.y-h-10;
    ctx.fillStyle='#191919';
    ctx.fillRect(m.x-bw/2,by,bw,8);
    ctx.fillStyle=m.boss?'#d7263d':'#e74c3c';
    ctx.fillRect(m.x-bw/2,by,bw*Math.max(0,m.hp/m.maxHp),8);
    ctx.fillStyle='#fff';
    ctx.font=m.boss?'bold 13px Arial':'bold 10px Arial';
    ctx.textAlign='center';
    ctx.fillText(m.name,m.x,by-5);
    if(m.boss){
      ctx.fillStyle='#ffd36b';
      ctx.font='bold 11px Arial';
      ctx.fillText('BOSS',m.x,by-20);
    }
    if(m.hitFlash){
      ctx.fillStyle='rgba(255,70,70,.32)';
      ctx.beginPath();
      ctx.arc(m.x,m.y-h*.48,Math.max(25,w*.38),0,Math.PI*2);
      ctx.fill();
    }
    ctx.restore();
  };

  /* ---------- NPC cleanup ---------- */
  npcs.splice(0,npcs.length,
    {x:760,y:420,name:'Panda Guard',image:'npc1',wander:false,quest:false},
    {x:1000,y:350,name:'King Pandee',image:'npc2',wander:false,quest:true},
    {x:520,y:690,name:'Panda Guard',image:'npc1',wander:true,quest:false},
    {x:1490,y:840,name:'Panda Guard',image:'npc1',wander:true,quest:false},
    {x:1940,y:560,name:'Panda Guard',image:'npc1',wander:false,quest:false},
    {x:900,y:620,name:'Panda Guard',image:'npc1',wander:true,quest:false},
    {x:1250,y:480,name:'Panda Guard',image:'npc1',wander:true,quest:false}
  );
  npcs.forEach(n=>{
    n.homeX=n.x;n.homeY=n.y;n.targetX=n.x;n.targetY=n.y;n.walkTimer=0;
  });

  /* ---------- Equipment / paper doll ---------- */
  equippedWeapon=equippedWeapon||'Wooden Sword';
  equippedArmor=equippedArmor||null;
  equippedTool=equippedTool||null;

  function ensureEquipmentUI(){
    const bag=document.getElementById('bagWindow');
    const bagItems=document.getElementById('bagItems');
    if(!bag || !bagItems || document.getElementById('pandaniaEquipment')) return;
    bagItems.insertAdjacentHTML('beforebegin',`
      <div id="pandaniaEquipment" style="margin:0 0 16px;padding:14px;border:1px solid #6b5130;border-radius:12px;background:linear-gradient(180deg,#21170f,#100d09);">
        <div style="text-align:center;color:#ffd86a;font-size:18px;font-weight:bold;margin-bottom:10px;">🧍 Pandee's Equipment</div>
        <div style="display:grid;grid-template-columns:1fr 120px 1fr;gap:10px;align-items:center;max-width:620px;margin:auto;">
          <div style="display:flex;flex-direction:column;gap:8px;">
            <div class="equipSlot" data-slot="weapon" id="equipWeapon" style="padding:9px;border:1px solid #705333;border-radius:8px;background:#17120d;text-align:center;">⚔️ Weapon</div>
            <div class="equipSlot" data-slot="tool" id="equipTool" style="padding:9px;border:1px solid #705333;border-radius:8px;background:#17120d;text-align:center;">🛠️ Tool</div>
          </div>
          <div style="height:130px;border:2px solid #8b683e;border-radius:12px;background:#0b0b0b;display:flex;align-items:center;justify-content:center;font-size:64px;">🐼</div>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <div class="equipSlot" data-slot="armor" id="equipArmor" style="padding:9px;border:1px solid #705333;border-radius:8px;background:#17120d;text-align:center;">🛡️ Armor</div>
            <div style="padding:9px;border:1px solid #705333;border-radius:8px;background:#17120d;text-align:center;color:#a9977d;font-size:12px;">Double-click an item below to equip it.</div>
          </div>
        </div>
      </div>`);
  }

  function slotHTML(label,icon,item){
    const safe=item||'Empty';
    return `<div style="font-weight:bold;color:#e7bd73;">${icon} ${label}</div><div class="slotItem" style="margin:5px 0;color:${item?'#fff':'#777'};">${safe}</div>${item?'<button type="button" class="unequipBtn" style="border:1px solid #a75b4b;background:#49251f;color:#fff;border-radius:5px;padding:4px 8px;cursor:pointer;">Unequip</button>':''}`;
  }

  function renderEquipment(){
    ensureEquipmentUI();
    const w=document.getElementById('equipWeapon');
    const a=document.getElementById('equipArmor');
    const t=document.getElementById('equipTool');
    if(!w||!a||!t) return;
    w.innerHTML=slotHTML('Weapon','⚔️',equippedWeapon);
    a.innerHTML=slotHTML('Armor','🛡️',equippedArmor);
    t.innerHTML=slotHTML('Tool','🛠️',equippedTool);
    [[w,equippedWeapon],[a,equippedArmor],[t,equippedTool]].forEach(([slot,item])=>{
      const btn=slot.querySelector('.unequipBtn');
      if(btn) btn.onclick=function(e){e.stopPropagation();unequipItem(item);};
      slot.ondblclick=function(){if(item) unequipItem(item);};
    });
  }

  function equipFromBag(name){
    const item=inventory[name];
    if(!item || !item.count) return;
    if(/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3)$/.test(name)) equippedWeapon=name;
    else if(name==='Iron Armor') equippedArmor=name;
    else if(/^(Woodcutting Axe|Fishing Rod)$/.test(name)) equippedTool=name;
    else {showMessage('That item cannot be equipped.');return;}
    renderEquipment();
    updateUI();
    showMessage('⚔️ '+name+' equipped!');
  }

  function unequipItem(name){
    if(equippedWeapon===name) equippedWeapon='';
    if(equippedArmor===name) equippedArmor=null;
    if(equippedTool===name) equippedTool=null;
    renderEquipment();
    updateUI();
    showMessage('↩️ '+name+' unequipped.');
  }

  function bindEquipmentInteractions(){
    ensureEquipmentUI();
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const name=card.querySelector('.itemName')?.textContent?.trim();
      if(!name) return;
      if(!/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3|Iron Armor|Woodcutting Axe|Fishing Rod)$/.test(name)) return;
      card.ondblclick=function(e){e.preventDefault();equipFromBag(name);};
    });
  }

  const baseRenderBag=renderBag;
  renderBag=function(){
    baseRenderBag();
    ensureEquipmentUI();
    renderEquipment();
    bindEquipmentInteractions();
  };

  /* Prevent interaction with King Pandee from selecting a target to walk into. */
  const baseInteract=interact;
  interact=function(){
    const king=npcs.find(n=>n.quest&&n.name==='King Pandee');
    if(king && Math.hypot(player.x-king.x,player.y-king.y)<100){
      player.targetX=null;player.targetY=null;player.targetMonster=null;
    }
    return baseInteract();
  };

  ensureEquipmentUI();
  window.PandaniaGameplayV3=true;
})();
/* ===== END PANDANIA GAMEPLAY PATCH v3 ===== */'''

insert='\n'+new_patch.strip()+'\n'
marker='</script>'
if marker not in text:
    raise SystemExit('Could not find closing script tag')
text=text.replace(marker,insert+marker,1)
path.write_text(text,encoding='utf-8')
print('Pandania gameplay patch rebuilt as v3')
