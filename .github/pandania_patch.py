from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')

# Keep the paper-doll UI from v4 exactly as the base and replace only the
# gameplay layer. This removes earlier experimental layers so they cannot
# override the final behavior.
for version in ('v2','v3','v4','v5'):
    text = re.sub(rf'/\* ===== PANDANIA GAMEPLAY PATCH {version} ===== \*/.*?/\* ===== END PANDANIA GAMEPLAY PATCH {version} ===== \*/', '', text, flags=re.S)

new_patch = r'''/* ===== PANDANIA GAMEPLAY PATCH v5 ===== */
(function(){
  const state=window.__pandaniaEquipment||(window.__pandaniaEquipment={weapon:'Wooden Sword',armor:null,tool:null,dir:'down',dirX:0,dirY:1});

  function face(dir){
    state.dir=dir;
    if(dir==='left'){state.dirX=-1;state.dirY=0}
    if(dir==='right'){state.dirX=1;state.dirY=0}
    if(dir==='up'){state.dirX=0;state.dirY=-1}
    if(dir==='down'){state.dirX=0;state.dirY=1}
    player.attackDX=state.dirX; player.attackDY=state.dirY;
  }
  function keyDir(k){
    if(k==='a'||k==='arrowleft')return'left';
    if(k==='d'||k==='arrowright')return'right';
    if(k==='w'||k==='arrowup')return'up';
    if(k==='s'||k==='arrowdown')return'down';
    return null;
  }

  window.addEventListener('keydown',e=>{const d=keyDir(e.key.toLowerCase());if(d)face(d)},true);
  const oldUpdate=updatePlayer;
  updatePlayer=function(){
    const oldX=player.x,oldY=player.y;
    oldUpdate();
    let dx=0,dy=0;
    if(keys['a']||keys['arrowleft'])dx--;
    if(keys['d']||keys['arrowright'])dx++;
    if(keys['w']||keys['arrowup'])dy--;
    if(keys['s']||keys['arrowdown'])dy++;
    if(dx||dy){face(Math.abs(dx)>=Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down'))}
    /* Monsters are solid: if the movement step enters a monster radius,
       restore the previous position. */
    for(const m of monsters){
      if(m.dead)continue;
      const r=(m.collisionRadius||28)+18;
      if(Math.hypot(player.x-m.x,player.y-m.y)<r){player.x=oldX;player.y=oldY;break}
    }
  };

  /* Single sprite, four clean orientations. We mirror for horizontal travel
     and flip vertically for the rear-facing view; no sideways 90-degree spin. */
  drawPlayer=function(){
    const img=images['player1'];
    const bob=player.moving?Math.abs(Math.sin(player.walkTime))*2:0;
    ctx.save();
    ctx.globalAlpha=(player.invincible>0&&Math.floor(player.invincible/4)%2===0)?.3:1;
    if(img){
      ctx.translate(player.x,player.y+bob);
      if(state.dir==='left')ctx.scale(-1,1);
      if(state.dir==='up')ctx.scale(1,-1);
      ctx.imageSmoothingEnabled=false;
      ctx.drawImage(img,-38,-100,76,100);
    }
    ctx.restore();
    if(typeof drawPlayerEffects==='function')drawPlayerEffects();
  };

  /* Guaranteed monster HP update. */
  swordAttack=function(target=null){
    if(player.attackCooldown>0)return;
    player.attackCooldown=22; player.swordSwing=12; swordSound();
    if(target&&!monsters.includes(target))target=null;
    if(!target){
      let best=null,score=-999;
      for(const m of monsters){
        if(m.dead)continue;
        const dx=m.x-player.x,dy=m.y-player.y,d=Math.hypot(dx,dy);
        if(!d||d>110)continue;
        const dot=(dx/d)*state.dirX+(dy/d)*state.dirY;
        if(dot<.15)continue;
        const s=dot*4-d/110;if(s>score){score=s;best=m}
      }
      target=best;
    }
    if(!target){showMessage('⚔️ Swing!');return}
    const d=Math.hypot(target.x-player.x,target.y-player.y);
    if(d>110){showMessage('⚔️ Too far away!');return}
    const wd={'Wooden Sword':8,'Weapon 1':22,'Weapon 2':30,'Weapon 3':42}[state.weapon]||8;
    const damage=15+(Number(player.level)||1)*3+wd;
    target.hp=Math.max(0,(Number(target.hp)||0)-damage);
    target.hitFlash=8;hitSound();
    showMessage('⚔️ Hit '+target.name+' for '+damage+' damage!');
    if(target.hp<=0)killMonster(target);
  };

  /* Use the existing paper doll created by v4; do not replace its markup.
     Make equipping transfer the selected item out of the bag count and into
     the equipment state. Unequip returns one copy to the bag. */
  function equipmentPanel(){return document.getElementById('pandaniaEquipment')}
  function setInventoryCount(name,count){
    if(!inventory[name])inventory[name]={count:0};
    inventory[name].count=Math.max(0,count);
    if(inventory[name].count===0)delete inventory[name];
  }
  function equip(name){
    if(!inventory[name]||Number(inventory[name].count)<1)return;
    if(/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3)$/.test(name)){if(state.weapon&&state.weapon!==name)setInventoryCount(state.weapon,(inventory[state.weapon]?.count||0)+1);state.weapon=name}
    else if(name==='Iron Armor'){if(state.armor)setInventoryCount(state.armor,(inventory[state.armor]?.count||0)+1);state.armor=name}
    else if(/^(Woodcutting Axe|Fishing Rod)$/.test(name)){if(state.tool)setInventoryCount(state.tool,(inventory[state.tool]?.count||0)+1);state.tool=name}
    setInventoryCount(name,(inventory[name]?.count||1)-1);
    refreshEquipment();showMessage('✅ '+name+' equipped!');
  }
  function unequipSlot(kind){
    const name=kind==='weapon'?state.weapon:kind==='armor'?state.armor:state.tool;
    if(!name)return;
    setInventoryCount(name,(inventory[name]?.count||0)+1);
    if(kind==='weapon')state.weapon='';
    if(kind==='armor')state.armor=null;
    if(kind==='tool')state.tool=null;
    refreshEquipment();showMessage('↩️ '+name+' unequipped.');
  }
  function refreshEquipment(){
    const panel=equipmentPanel();if(!panel)return;
    const w=document.getElementById('equipWeapon'),a=document.getElementById('equipArmor'),t=document.getElementById('equipTool');
    if(!w||!a||!t)return;
    const put=(el,icon,label,item,kind)=>{
      el.innerHTML='<div style="color:#e7bd73;font-weight:bold">'+icon+' '+label+'</div><div style="margin:6px 0;color:'+(item?'#fff':'#777')+'">'+(item||'Empty')+'</div>'+(item?'<button type="button" class="unequipButton" style="border:1px solid #b55c4c;background:#4a251f;color:#fff;border-radius:5px;padding:4px 9px;cursor:pointer">Unequip</button>':'');
      el.style.cssText='padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center;min-height:68px;cursor:pointer;';
      const b=el.querySelector('.unequipButton');if(b)b.onclick=e=>{e.stopPropagation();unequipSlot(kind)};
    };
    put(w,'⚔️','Weapon',state.weapon,'weapon');put(a,'🛡️','Armor',state.armor,'armor');put(t,'🛠️','Tool',state.tool,'tool');
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const n=card.querySelector('.itemName');if(!n)return;const name=n.textContent.trim();
      if(!/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3|Iron Armor|Woodcutting Axe|Fishing Rod)$/.test(name))return;
      card.ondblclick=e=>{e.preventDefault();e.stopPropagation();equip(name)};
    });
  }
  const oldBag=renderBag;
  renderBag=function(){oldBag();refreshEquipment()};
  setTimeout(refreshEquipment,100);

  /* PDA artwork: use the new image from images/pda instead of an invisible
     token graphic. We support both .png and .webp without changing markup. */
  function loadPDA(){
    const srcs=['images/pda.png','images/pda.webp','images/pda.jpg'];
    const img=new Image();let i=0;
    img.onload=function(){
      document.querySelectorAll('*').forEach(el=>{
        if(el.dataset&&el.dataset.pda==='true')el.style.backgroundImage='url("'+img.src+'")';
      });
      window.pdaImage=img;
    };
    img.onerror=function(){i++;if(i<srcs.length)img.src=srcs[i]};img.src=srcs[0];
  }
  loadPDA();

  /* Subtle original fantasy ambience. Web Audio starts only after the player's
     first interaction, so browsers will not block autoplay. */
  let audioStarted=false,audioCtx,master;
  function startMusic(){
    if(audioStarted)return;audioStarted=true;
    try{
      audioCtx=new(window.AudioContext||window.webkitAudioContext)();
      master=audioCtx.createGain();master.gain.value=.035;master.connect(audioCtx.destination);
      const notes=[196,220,261.63,293.66,261.63,220,174.61,196];let step=0;
      function tone(){
        if(!audioCtx||audioCtx.state==='suspended')audioCtx.resume();
        const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='sine';o.frequency.value=notes[step++%notes.length];g.gain.setValueAtTime(.0001,audioCtx.currentTime);g.gain.exponentialRampToValueAtTime(.12,audioCtx.currentTime+.25);g.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+2.2);o.connect(g);g.connect(master);o.start();o.stop(audioCtx.currentTime+2.3);
      }
      tone();setInterval(tone,2200);
    }catch(e){}
  }
  ['keydown','pointerdown','touchstart'].forEach(ev=>window.addEventListener(ev,startMusic,{once:true,passive:true}));

  window.__pandaniaGameplayV5=true;
})();
/* ===== END PANDANIA GAMEPLAY PATCH v5 ===== */'''

marker='</script>'
if marker not in text:raise SystemExit('Missing closing script tag')
text=text.replace(marker,'\n'+new_patch.strip()+'\n'+marker,1)
path.write_text(text,encoding='utf-8')
