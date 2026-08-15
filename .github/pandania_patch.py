from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')
for version in ('v2','v3','v4','v5','v6','v7'):
    text = re.sub(rf'/\* ===== PANDANIA GAMEPLAY PATCH {version} ===== \*/.*?/\* ===== END PANDANIA GAMEPLAY PATCH {version} ===== \*/', '', text, flags=re.S)

new_patch = r'''/* ===== PANDANIA GAMEPLAY PATCH v7 ===== */
(function(){
  /* PDA Coin uses the SAME native inventory image system as the weapons.
     The base game already renders item.image through images[] and imageFiles[]. */
  imageFiles.pda = IMAGE_FOLDER + 'pda.png';
  const pdaImg = new Image();
  pdaImg.onload = function(){
    images.pda = pdaImg;
    if(inventory['PDA Coin']) inventory['PDA Coin'].image = 'pda';
    if(typeof renderBag==='function') renderBag();
  };
  pdaImg.onerror = function(){
    console.warn('Pandania: images/pda.png could not be loaded');
  };
  pdaImg.src = imageFiles.pda;

  /* Also set the item definition immediately so every future PDA drop has the
     correct image key before the asynchronous image finishes loading. */
  if(inventory['PDA Coin']) inventory['PDA Coin'].image = 'pda';

  const state=window.__pandaniaEquipment||(window.__pandaniaEquipment={weapon:'Wooden Sword',armor:null,tool:null,dir:'down',dirX:0,dirY:1});
  const keyDir=k=>({a:'left',arrowleft:'left',d:'right',arrowright:'right',w:'up',arrowup:'up',s:'down',arrowdown:'down'})[k]||null;
  function face(d){state.dir=d;if(d==='left'){state.dirX=-1;state.dirY=0}if(d==='right'){state.dirX=1;state.dirY=0}if(d==='up'){state.dirX=0;state.dirY=-1}if(d==='down'){state.dirX=0;state.dirY=1}player.attackDX=state.dirX;player.attackDY=state.dirY}
  window.addEventListener('keydown',e=>{const d=keyDir(e.key.toLowerCase());if(d)face(d)},true);

  function mobileUI(){
    if(document.getElementById('pandaniaMobileControls'))return;
    const box=document.createElement('div');box.id='pandaniaMobileControls';box.innerHTML=`
      <div id="pmDpad"><button data-k="w">▲</button><div><button data-k="a">◀</button><button data-k="s">▼</button><button data-k="d">▶</button></div></div>
      <div id="pmActions"><button id="pmAttack">⚔️</button><button id="pmInteract">💬</button><button id="pmBag">🎒</button></div>`;
    document.body.appendChild(box);
    const style=document.createElement('style');style.textContent=`
      #pandaniaMobileControls{display:none;position:fixed;z-index:99999;left:0;right:0;bottom:12px;pointer-events:none;justify-content:space-between;align-items:flex-end;padding:0 14px;font-family:Arial}
      #pandaniaMobileControls button{width:54px;height:54px;margin:3px;border:2px solid rgba(255,216,106,.75);border-radius:50%;background:rgba(20,14,10,.78);color:#fff;font-size:22px;touch-action:none;user-select:none;-webkit-user-select:none}
      #pmDpad{pointer-events:auto;text-align:center}#pmDpad>div{display:flex;justify-content:center}#pmActions{pointer-events:auto;display:flex;gap:3px}#pmActions button{width:58px;height:58px}
      @media(max-width:700px),(pointer:coarse){#pandaniaMobileControls{display:flex}#gameWrap{width:100vw;height:100vh}canvas{touch-action:none}}
    `;document.head.appendChild(style);
    function hold(btn,key){const start=e=>{e.preventDefault();btn.setPointerCapture?.(e.pointerId);keys[key]=true;face(keyDir(key));if(typeof startMusic==='function')startMusic()};const stop=e=>{e.preventDefault();keys[key]=false};btn.addEventListener('pointerdown',start);btn.addEventListener('pointerup',stop);btn.addEventListener('pointercancel',stop);btn.addEventListener('pointerleave',e=>{if(e.buttons===0)stop(e)})}
    box.querySelectorAll('[data-k]').forEach(b=>hold(b,b.dataset.k));
    document.getElementById('pmAttack').addEventListener('pointerdown',e=>{e.preventDefault();swordAttack()});
    document.getElementById('pmInteract').addEventListener('pointerdown',e=>{e.preventDefault();interact()});
    document.getElementById('pmBag').addEventListener('pointerdown',e=>{e.preventDefault();openBag()});
  }
  mobileUI();

  const oldUpdate=updatePlayer;
  updatePlayer=function(){const ox=player.x,oy=player.y;oldUpdate();let dx=0,dy=0;if(keys.a||keys.arrowleft)dx--;if(keys.d||keys.arrowright)dx++;if(keys.w||keys.arrowup)dy--;if(keys.s||keys.arrowdown)dy++;if(dx||dy)face(Math.abs(dx)>=Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down'));for(const m of monsters){if(m.dead)continue;const r=(m.collisionRadius||28)+18;if(Math.hypot(player.x-m.x,player.y-m.y)<r){player.x=ox;player.y=oy;break}}};

  /* Preserve/recreate the approved paper doll without changing its layout. */
  function ensureDoll(){const bag=document.getElementById('bagWindow'),items=document.getElementById('bagItems');if(!bag||!items)return;if(document.getElementById('pandaniaEquipment'))return;const p=document.createElement('div');p.id='pandaniaEquipment';p.style.cssText='margin:0 0 16px;padding:14px;border:2px solid #8b683e;border-radius:12px;background:#15100c;color:#fff';p.innerHTML='<div style="text-align:center;color:#ffd86a;font-size:19px;font-weight:bold;margin-bottom:10px">🧍 Pandee — Equipment</div><div style="display:grid;grid-template-columns:1fr 130px 1fr;gap:10px;align-items:center"><div id="equipWeapon" style="padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center">⚔️ Weapon<br><span>Empty</span></div><div style="height:145px;border:2px solid #6f5333;border-radius:10px;background:#090909;display:flex;align-items:center;justify-content:center;font-size:70px">🐼</div><div id="equipArmor" style="padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center">🛡️ Armor<br><span>Empty</span></div></div><div id="equipTool" style="margin:8px auto 0;max-width:220px;padding:10px;border:1px solid #705333;border-radius:8px;background:#21170f;text-align:center">🛠️ Tool<br><span>Empty</span></div>';items.parentNode.insertBefore(p,items)}
  function setInv(n,c){if(!inventory[n]&&c>0)inventory[n]={icon:'⚔️',count:0};if(inventory[n])inventory[n].count=Math.max(0,c);if(inventory[n]?.count===0)delete inventory[n]}
  function refreshDoll(){ensureDoll();const vals=[['equipWeapon','⚔️','Weapon',state.weapon,'weapon'],['equipArmor','🛡️','Armor',state.armor,'armor'],['equipTool','🛠️','Tool',state.tool,'tool']];vals.forEach(([id,ic,label,item,kind])=>{const el=document.getElementById(id);if(!el)return;el.innerHTML=ic+' '+label+'<br><strong>'+(item||'Empty')+'</strong>'+(item?'<br><button class="pdUnequip" type="button">Unequip</button>':'');const b=el.querySelector('.pdUnequip');if(b)b.onclick=e=>{e.stopPropagation();setInv(item,(inventory[item]?.count||0)+1);if(kind==='weapon')state.weapon='';if(kind==='armor')state.armor=null;if(kind==='tool')state.tool=null;refreshDoll();renderBag()}});document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{const el=card.querySelector('.itemName');if(!el)return;const n=el.textContent.trim();if(!/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3|Iron Armor|Woodcutting Axe|Fishing Rod)$/.test(n))return;card.ondblclick=e=>{e.preventDefault();e.stopPropagation();if(!inventory[n]||inventory[n].count<1)return;if(/^(Wooden Sword|Weapon 1|Weapon 2|Weapon 3)$/.test(n)){if(state.weapon)setInv(state.weapon,(inventory[state.weapon]?.count||0)+1);state.weapon=n}else if(n==='Iron Armor'){if(state.armor)setInv(state.armor,(inventory[state.armor]?.count||0)+1);state.armor=n}else{if(state.tool)setInv(state.tool,(inventory[state.tool]?.count||0)+1);state.tool=n}setInv(n,(inventory[n]?.count||1)-1);refreshDoll();renderBag();showMessage('✅ '+n+' equipped!')}})}
  const oldBag=renderBag;renderBag=function(){oldBag();ensureDoll();refreshDoll()};setTimeout(()=>{ensureDoll();refreshDoll()},200);

  /* Subtle original ambience. */
  let audioStarted=false,audioCtx,master;function startMusic(){if(audioStarted)return;audioStarted=true;try{audioCtx=new(window.AudioContext||window.webkitAudioContext)();master=audioCtx.createGain();master.gain.value=.025;master.connect(audioCtx.destination);const notes=[196,220,261.63,293.66,261.63,220,174.61,196];let q=0;function tone(){const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='sine';o.frequency.value=notes[q++%notes.length];g.gain.setValueAtTime(.0001,audioCtx.currentTime);g.gain.exponentialRampToValueAtTime(.08,audioCtx.currentTime+.3);g.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+2);o.connect(g);g.connect(master);o.start();o.stop(audioCtx.currentTime+2.1)}tone();setInterval(tone,2100)}catch(e){}}
  ['keydown','pointerdown','touchstart'].forEach(e=>window.addEventListener(e,startMusic,{once:true,passive:true}));
  window.__pandaniaGameplayV7=true;
})();
/* ===== END PANDANIA GAMEPLAY PATCH v7 ===== */'''

text=text.replace('</script>','\n'+new_patch+'\n</script>',1)
path.write_text(text,encoding='utf-8')
