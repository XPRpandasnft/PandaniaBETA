from pathlib import Path

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

start_marker = '/* ===== PANDANIA EQUIPMENT PATCH v1 ===== */'
end_marker = '/* ===== END PANDANIA EQUIPMENT PATCH v1 ===== */'
new_patch = '''/* ===== PANDANIA GAMEPLAY PATCH v2 ===== */
(function(){
  'use strict';

  player.attackDX = 0;
  player.attackDY = 1;
  player.facingX = 0;
  player.facingY = 1;

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
    const d={w:[0,-1],arrowup:[0,-1],s:[0,1],arrowdown:[0,1],a:[-1,0],arrowleft:[-1,0],d:[1,0],arrowright:[1,0]}[k];
    if(d) setPlayerDirection(d[0],d[1]);
  },true);

  const oldUpdatePlayerV2=updatePlayer;
  updatePlayer=function(){
    oldUpdatePlayerV2();
    let dx=0,dy=0;
    if(keys['a']||keys['arrowleft']) dx--;
    if(keys['d']||keys['arrowright']) dx++;
    if(keys['w']||keys['arrowup']) dy--;
    if(keys['s']||keys['arrowdown']) dy++;
    if(dx||dy) setPlayerDirection(dx,dy);
  };

  swordAttack=function(target=null){
    if(player.attackCooldown>0) return;
    player.attackCooldown=22;
    player.swordSwing=12;
    swordSound();

    if(target && monsters.includes(target)){
      const dx=target.x-player.x,dy=target.y-player.y,d=Math.hypot(dx,dy)||1;
      setPlayerDirection(dx,dy);
    } else {
      const ax=player.attackDX||0,ay=player.attackDY||1;
      let best=null,bestScore=-Infinity;
      for(const m of monsters){
        const dx=m.x-player.x,dy=m.y-player.y,d=Math.hypot(dx,dy);
        if(!d || d>105) continue;
        const dot=(dx/d)*ax+(dy/d)*ay;
        if(dot<0.15) continue;
        const score=dot*3-(d/105);
        if(score>bestScore){bestScore=score;best=m;}
      }
      target=best;
    }

    if(!target){showMessage('⚔️ Swinging '+(equippedWeapon||'Wooden Sword')+' toward your facing!');return;}
    const d=Math.hypot(target.x-player.x,target.y-player.y);
    if(d>105){showMessage('⚔️ Too far away!');return;}

    const weaponDamage={'Wooden Sword':8,'Weapon 1':22,'Weapon 2':30,'Weapon 3':42}[equippedWeapon||'Wooden Sword']||8;
    const damage=15+player.level*3+weaponDamage;
    target.hp-=damage;
    target.hitFlash=8;
    hitSound();
    showMessage('⚔️ '+(equippedWeapon||'Wooden Sword')+' hit '+target.name+' for '+damage+' damage!');
    if(target.hp<=0) killMonster(target);
  };

  drawMonster=function(m){
    ctx.save();
    const img=images[m.image];
    const baseH=m.boss?126:96;
    let w=baseH;
    if(img && img.naturalWidth && img.naturalHeight) w=Math.max(1,Math.round(baseH*(img.naturalWidth/img.naturalHeight)));
    ctx.fillStyle='rgba(0,0,0,.32)';
    ctx.beginPath();ctx.ellipse(m.x,m.y+5,Math.max(18,w*.34),8,0,0,Math.PI*2);ctx.fill();
    if(img){ctx.imageSmoothingEnabled=false;ctx.drawImage(img,Math.round(m.x-w/2),Math.round(m.y-baseH),w,baseH);}
    else{ctx.fillStyle=m.boss?'#5b1d32':'#75a83f';ctx.beginPath();ctx.arc(m.x,m.y-baseH*.45,m.boss?42:30,0,Math.PI*2);ctx.fill();}
    const bw=m.boss?Math.min(170,Math.max(100,w+25)):Math.min(105,Math.max(62,w+10));
    const by=m.y-baseH-10;
    ctx.fillStyle='#191919';ctx.fillRect(m.x-bw/2,by,bw,8);
    ctx.fillStyle=m.boss?'#d7263d':'#e74c3c';ctx.fillRect(m.x-bw/2,by,bw*Math.max(0,m.hp/m.maxHp),8);
    ctx.fillStyle='#fff';ctx.font=m.boss?'bold 13px Arial':'bold 10px Arial';ctx.textAlign='center';ctx.fillText(m.name,m.x,by-5);
    if(m.boss){ctx.fillStyle='#ffd36b';ctx.font='bold 11px Arial';ctx.fillText('BOSS',m.x,by-20);}
    if(m.hitFlash){ctx.fillStyle='rgba(255,70,70,.32)';ctx.beginPath();ctx.arc(m.x,m.y-baseH*.48,Math.max(25,w*.38),0,Math.PI*2);ctx.fill();}
    ctx.restore();
  };

  /* npc1 is the Panda Guard; npc2 is King Pandee. There is only one King. */
  npcs.splice(0,npcs.length,
    {x:760,y:420,name:'Panda Guard',image:'npc1',wander:false,quest:false},
    {x:1000,y:350,name:'King Pandee',image:'npc2',wander:false,quest:true},
    {x:520,y:690,name:'Panda Guard',image:'npc1',wander:true,quest:false},
    {x:1490,y:840,name:'Panda Guard',image:'npc1',wander:true,quest:false},
    {x:1940,y:560,name:'Panda Guard',image:'npc1',wander:false,quest:false},
    {x:900,y:620,name:'Panda Guard',image:'npc1',wander:true,quest:false},
    {x:1250,y:480,name:'Panda Guard',image:'npc1',wander:true,quest:false}
  );
  npcs.forEach(n=>{n.homeX=n.x;n.homeY=n.y;n.targetX=n.x;n.targetY=n.y;n.walkTimer=0;});

  equippedWeapon=equippedWeapon||'Wooden Sword';
  equippedArmor=equippedArmor||null;
  equippedTool=equippedTool||null;

  function equipFromBag(name){
    const item=inventory[name];
    if(!item || !item.count) return;
    if(name==='Wooden Sword'||name==='Weapon 1'||name==='Weapon 2'||name==='Weapon 3') equippedWeapon=name;
    else if(name==='Iron Armor') equippedArmor=name;
    else if(name==='Woodcutting Axe'||name==='Fishing Rod') equippedTool=name;
    renderEquipment();updateUI();showMessage('⚔️ '+name+' equipped!');
  }
  function unequipItem(name){
    if(equippedWeapon===name) equippedWeapon='';
    if(equippedArmor===name) equippedArmor=null;
    if(equippedTool===name) equippedTool=null;
    renderEquipment();updateUI();showMessage('↩️ '+name+' unequipped.');
  }

  function bindEquipmentInteractions(){
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const name=card.querySelector('.itemName')?.textContent?.trim();
      if(!name || !/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3|Iron Armor|Woodcutting Axe|Fishing Rod)$/.test(name)) return;
      card.setAttribute('draggable','true');
      card.ondblclick=e=>{e.preventDefault();equipFromBag(name);};
      card.ondragstart=e=>{e.dataTransfer.setData('text/pandania-item',name);e.dataTransfer.effectAllowed='move';};
    });
    document.querySelectorAll('#pandaniaSlots .equipSlot').forEach(slot=>{
      slot.ondragover=e=>{e.preventDefault();slot.style.outline='2px solid #d7a55a';};
      slot.ondragleave=()=>slot.style.outline='';
      slot.ondrop=e=>{
        e.preventDefault();slot.style.outline='';
        const name=e.dataTransfer.getData('text/pandania-item');if(!name)return;
        const weapon=/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3)$/.test(name),armor=name==='Iron Armor',tool=/^(Woodcutting Axe|Fishing Rod)$/.test(name);
        const label=(slot.textContent||'').toLowerCase();
        if((weapon&&label.includes('weapon'))||(armor&&label.includes('armor'))||(tool&&label.includes('tool'))) equipFromBag(name);
        else showMessage('That item does not fit this equipment slot.');
      };
      slot.ondblclick=()=>{const text=slot.querySelector('.slotItem')?.textContent||'';if(text&&text!=='Empty')unequipItem(text);};
    });
  }
  const oldRenderEquipment=renderEquipment;
  renderEquipment=function(){oldRenderEquipment();bindEquipmentInteractions();};
  document.addEventListener('dblclick',e=>{const card=e.target.closest('#bagWindow .itemCard');if(!card)return;const name=card.querySelector('.itemName')?.textContent?.trim();if(name) equipFromBag(name);});

  const oldInteract=interact;
  interact=function(){
    const king=npcs.find(n=>n.quest&&n.name==='King Pandee');
    if(king && Math.hypot(player.x-king.x,player.y-king.y)<100){player.targetX=null;player.targetY=null;player.targetMonster=null;}
    return oldInteract();
  };

  window.PandaniaGameplayV2=true;
})();
/* ===== END PANDANIA GAMEPLAY PATCH v2 ===== */'''

if start_marker not in text or end_marker not in text:
    raise SystemExit('Existing v1 patch markers not found')

start=text.index(start_marker)
end=text.index(end_marker,start)+len(end_marker)
text=text[:start]+new_patch.strip()+text[end:]
path.write_text(text,encoding='utf-8')
print('Pandania gameplay patch upgraded to v2')
