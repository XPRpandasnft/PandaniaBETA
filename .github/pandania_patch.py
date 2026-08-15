from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')
# Remove every experimental layer so the final layer is installed exactly once.
for version in ('v2','v3','v4','v5','v6','v7','v8'):
    text = re.sub(rf'/\* ===== PANDANIA GAMEPLAY PATCH {version} ===== \*/.*?/\* ===== END PANDANIA GAMEPLAY PATCH {version} ===== \*/', '', text, flags=re.S)
text = re.sub(r'/\* ===== PANDANIA PDA FIX v9 ===== \*/.*?/\* ===== END PANDANIA PDA FIX v9 ===== \*/', '', text, flags=re.S)

patch = r'''/* ===== PANDANIA FINAL STABLE PATCH v10 ===== */
(function(){
  'use strict';

  const state=window.__pandaniaEquipment||(window.__pandaniaEquipment={weapon:'',armor:null,tool:null,dir:'down',dirX:0,dirY:1});
  const dirFor=k=>({a:'left',arrowleft:'left',d:'right',arrowright:'right',w:'up',arrowup:'up',s:'down',arrowdown:'down'})[k]||null;
  function face(d){
    if(!d)return; state.dir=d;
    if(d==='left'){state.dirX=-1;state.dirY=0}
    if(d==='right'){state.dirX=1;state.dirY=0}
    if(d==='up'){state.dirX=0;state.dirY=-1}
    if(d==='down'){state.dirX=0;state.dirY=1}
    if(window.player){player.attackDX=state.dirX;player.attackDY=state.dirY}
  }
  window.addEventListener('keydown',e=>{const d=dirFor(e.key.toLowerCase());if(d){face(d)}},true);

  /* ---------- MOBILE CONTROLS ---------- */
  function addMobileControls(){
    if(document.getElementById('pandaniaMobileControls'))return;
    const box=document.createElement('div');box.id='pandaniaMobileControls';
    box.innerHTML='<div id="pmDpad"><button data-k="w">▲</button><div><button data-k="a">◀</button><button data-k="s">▼</button><button data-k="d">▶</button></div></div><div id="pmActions"><button id="pmAttack">⚔️</button><button id="pmInteract">💬</button><button id="pmBag">🎒</button></div>';
    document.body.appendChild(box);
    const style=document.createElement('style');style.textContent=`
      #pandaniaMobileControls{display:none;position:fixed;z-index:99999;left:0;right:0;bottom:10px;width:100%;padding:0 12px;box-sizing:border-box;pointer-events:none;justify-content:space-between;align-items:flex-end;font-family:Arial,sans-serif}
      #pandaniaMobileControls button{width:52px;height:52px;margin:3px;border:2px solid rgba(255,216,106,.78);border-radius:50%;background:rgba(20,14,10,.82);color:#fff;font-size:21px;line-height:1;touch-action:none;user-select:none;-webkit-user-select:none;-webkit-tap-highlight-color:transparent}
      #pmDpad{pointer-events:auto;display:flex;flex-direction:column;align-items:center;flex:0 0 auto}
      #pmDpad>div{display:flex;justify-content:center}
      #pmActions{pointer-events:auto;display:flex;flex-direction:column;align-items:center;gap:2px;flex:0 0 auto}
      #pmActions button{width:54px;height:54px;margin:2px}
      @media(max-width:700px),(pointer:coarse){#pandaniaMobileControls{display:flex}canvas{touch-action:none}}
    `;document.head.appendChild(style);
    const setKey=(key,on)=>{if(window.keys)keys[key]=on;face(dirFor(key));if(typeof window.startMusic==='function')window.startMusic()};
    box.querySelectorAll('[data-k]').forEach(btn=>{
      const key=btn.dataset.k;
      btn.addEventListener('pointerdown',e=>{e.preventDefault();btn.setPointerCapture?.(e.pointerId);setKey(key,true)},{passive:false});
      const stop=e=>{e.preventDefault();setKey(key,false)};
      btn.addEventListener('pointerup',stop,{passive:false});btn.addEventListener('pointercancel',stop,{passive:false});btn.addEventListener('lostpointercapture',()=>setKey(key,false));
    });
    const attack=document.getElementById('pmAttack');attack.addEventListener('pointerdown',e=>{e.preventDefault();if(typeof window.swordAttack==='function')window.swordAttack();},{passive:false});
    const interact=document.getElementById('pmInteract');interact.addEventListener('pointerdown',e=>{e.preventDefault();if(typeof window.interact==='function')window.interact();},{passive:false});
    const bagBtn=document.getElementById('pmBag');bagBtn.addEventListener('pointerdown',e=>{e.preventDefault();const b=document.getElementById('bagWindow');if(b){b.style.display=b.style.display==='none'?'block':'none';try{renderBag()}catch(err){console.warn('Bag render prevented:',err)}}},{passive:false});
  }
  addMobileControls();

  /* ---------- MOVEMENT + MONSTER COLLISION ---------- */
  if(typeof window.updatePlayer==='function'){
    const baseUpdate=window.updatePlayer;
    window.updatePlayer=function(){
      const ox=player.x,oy=player.y;baseUpdate();
      let dx=0,dy=0;if(keys.a||keys.arrowleft)dx--;if(keys.d||keys.arrowright)dx++;if(keys.w||keys.arrowup)dy--;if(keys.s||keys.arrowdown)dy++;
      if(dx||dy)face(Math.abs(dx)>=Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down'));
      if(Array.isArray(window.monsters))for(const m of monsters){if(m.dead)continue;const r=(m.collisionRadius||28)+18;if(Math.hypot(player.x-m.x,player.y-m.y)<r){player.x=ox;player.y=oy;break}}
    };
  }

  /* ---------- PAPER DOLL / EQUIPMENT ---------- */
  function ensureDoll(){
    const bag=document.getElementById('bagWindow'),items=document.getElementById('bagItems');if(!bag||!items||document.getElementById('pandaniaEquipment'))return;
    const p=document.createElement('div');p.id='pandaniaEquipment';p.style.cssText='margin:0 0 16px;padding:14px;border:2px solid #8b683e;border-radius:12px;background:#15100c;color:#fff';
    p.innerHTML='<div style="text-align:center;color:#ffd86a;font-size:19px;font-weight:bold;margin-bottom:10px">🧍 Pandee — Equipment</div><div style="display:grid;grid-template-columns:1fr 130px 1fr;gap:10px;align-items:center"><div id="equipWeapon" style="padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center">⚔️ Weapon<br><span>Empty</span></div><div style="height:145px;border:2px solid #6f5333;border-radius:10px;background:#090909;display:flex;align-items:center;justify-content:center;font-size:70px">🐼</div><div id="equipArmor" style="padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center">🛡️ Armor<br><span>Empty</span></div></div><div id="equipTool" style="margin:8px auto 0;max-width:220px;padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center">🛠️ Tool<br><span>Empty</span></div>';
    items.parentNode.insertBefore(p,items);
  }
  function invSet(name,count){
    if(typeof inventory!=='object')return;
    if(!inventory[name]&&count>0)inventory[name]={count:0};
    if(inventory[name])inventory[name].count=Math.max(0,count);
    if(inventory[name]&&inventory[name].count===0)delete inventory[name];
  }
  function refreshDoll(){
    ensureDoll();
    const vals=[['equipWeapon','⚔️','Weapon',state.weapon,'weapon'],['equipArmor','🛡️','Armor',state.armor,'armor'],['equipTool','🛠️','Tool',state.tool,'tool']];
    vals.forEach(([id,ic,label,item,kind])=>{
      const el=document.getElementById(id);if(!el)return;
      el.innerHTML=ic+' '+label+'<br><strong>'+(item||'Empty')+'</strong>'+(item?'<br><button class="pdUnequip" type="button">Unequip</button>':'');
      const b=el.querySelector('.pdUnequip');if(b)b.onclick=e=>{e.stopPropagation();invSet(item,(inventory[item]?.count||0)+1);if(kind==='weapon')state.weapon='';if(kind==='armor')state.armor=null;if(kind==='tool')state.tool=null;refreshDoll();safeRenderBag()};
    });
  }
  function equipItem(name){
    if(typeof inventory!=='object'||!inventory[name]||inventory[name].count<1)return;
    if(/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3)$/.test(name)){if(state.weapon)invSet(state.weapon,(inventory[state.weapon]?.count||0)+1);state.weapon=name}
    else if(name==='Iron Armor'){if(state.armor)invSet(state.armor,(inventory[state.armor]?.count||0)+1);state.armor=name}
    else if(/^(Woodcutting Axe|Fishing Rod)$/.test(name)){if(state.tool)invSet(state.tool,(inventory[state.tool]?.count||0)+1);state.tool=name}
    else return;
    invSet(name,(inventory[name]?.count||1)-1);refreshDoll();safeRenderBag();if(typeof showMessage==='function')showMessage('✅ '+name+' equipped!');
  }
  function wireEquipment(){
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      if(card.dataset.pandaniaEquipWired==='1')return;
      const el=card.querySelector('.itemName');if(!el)return;const name=el.textContent.trim();
      if(!/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3|Iron Armor|Woodcutting Axe|Fishing Rod)$/.test(name))return;
      card.dataset.pandaniaEquipWired='1';card.addEventListener('dblclick',e=>{e.preventDefault();equipItem(name)});
      card.addEventListener('touchend',e=>{if(e.detail>=2){e.preventDefault();equipItem(name)}},{passive:false});
    });
  }
  let rendering=false;
  function safeRenderBag(){if(rendering||typeof window.renderBag!=='function')return;rendering=true;try{window.renderBag()}catch(e){console.error('Pandania bag render error:',e)}finally{rendering=false}setTimeout(()=>{ensureDoll();refreshDoll();wireEquipment();forcePdaCard()},0)}

  /* Do NOT replace/wrap renderBag. The previous patch caused recursive
     renderBag -> refreshDoll -> renderBag calls and crashed the bag. */
  const bagObserver=new MutationObserver(()=>{if(!rendering){ensureDoll();wireEquipment();forcePdaCard()}});
  bagObserver.observe(document.body,{childList:true,subtree:true});
  setTimeout(()=>{ensureDoll();wireEquipment();forcePdaCard()},300);

  /* ---------- PDA COIN ---------- */
  const PDA_SRC='images/pda.png',PDA_NAME='PDA Coin';
  function forcePdaCard(){
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const name=card.querySelector('.itemName');if(!name||name.textContent.trim()!==PDA_NAME)return;
      let img=card.querySelector('img[data-pandania-pda]');
      if(!img){img=document.createElement('img');img.dataset.pandaniaPda='1';img.alt=PDA_NAME;img.src=PDA_SRC;img.style.cssText='width:42px;height:42px;object-fit:contain;display:block;margin:0 auto';const existing=card.querySelector('.itemIcon');if(existing){existing.innerHTML='';existing.appendChild(img)}else card.insertBefore(img,name)}
      else if(img.src.indexOf('/images/pda.png')<0)img.src=PDA_SRC;
    });
  }
  const pdaPreload=new Image();pdaPreload.onload=forcePdaCard;pdaPreload.src=PDA_SRC;

  /* ---------- SUBTLE AMBIENCE ---------- */
  let audioStarted=false,audioCtx,master;
  function startMusic(){if(audioStarted)return;audioStarted=true;try{audioCtx=new(window.AudioContext||window.webkitAudioContext)();master=audioCtx.createGain();master.gain.value=.025;master.connect(audioCtx.destination);const notes=[196,220,261.63,293.66,261.63,220,174.61,196];let q=0;function tone(){const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='sine';o.frequency.value=notes[q++%notes.length];g.gain.setValueAtTime(.0001,audioCtx.currentTime);g.gain.exponentialRampToValueAtTime(.08,audioCtx.currentTime+.3);g.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+2);o.connect(g);g.connect(master);o.start();o.stop(audioCtx.currentTime+2.1)}tone();setInterval(tone,2100)}catch(e){}}
  window.startMusic=startMusic;['keydown','pointerdown','touchstart'].forEach(e=>window.addEventListener(e,startMusic,{once:true,passive:true}));
  window.__pandaniaGameplayV10=true;
})();
/* ===== END PANDANIA FINAL STABLE PATCH v10 ===== */'''

text=text.replace('</script>','\n'+patch+'\n</script>',1)
path.write_text(text,encoding='utf-8')
