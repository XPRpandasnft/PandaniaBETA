from pathlib import Path
import re

path = Path('Adventures Of Pandania The Lost Realms/index.html')
text = path.read_text(encoding='utf-8')
# Keep the already-working v8 gameplay layer. Only replace a previous v9 PDA layer.
text = re.sub(r'/\* ===== PANDANIA PDA FIX v9 ===== \*/.*?/\* ===== END PANDANIA PDA FIX v9 ===== \*/', '', text, flags=re.S)

patch = r'''/* ===== PANDANIA PDA FIX v9 ===== */
(function(){
  const PDA_SRC='images/pda.png';
  const PDA_NAME='PDA Coin';

  function forcePdaImage(){
    /* Make the actual item definition point at the image used by the working
       item renderer, when those structures exist. */
    try{
      if(typeof imageFiles==='object') imageFiles.pda=PDA_SRC;
      if(typeof inventory==='object' && inventory[PDA_NAME]) inventory[PDA_NAME].image='pda';
    }catch(e){}

    /* More importantly, directly repair the rendered PDA Coin card. This does
       not depend on CSS classes, icon names, or the inventory data structure. */
    document.querySelectorAll('#bagWindow .itemCard').forEach(card=>{
      const name=card.querySelector('.itemName');
      if(!name || name.textContent.trim()!==PDA_NAME)return;
      let holder=card.querySelector('.itemIcon');
      if(!holder){holder=document.createElement('div');holder.className='itemIcon';card.insertBefore(holder,name)}
      holder.innerHTML='';
      const img=document.createElement('img');
      img.src=PDA_SRC;
      img.alt='PDA Coin';
      img.className='itemImage';
      img.style.cssText='width:42px;height:42px;object-fit:contain;display:block;margin:0 auto;image-rendering:auto';
      holder.appendChild(img);
    });
  }

  /* Run after the bag renders, after image loading, and whenever the inventory
     DOM changes. This catches a PDA Coin that is added after a monster drop. */
  const originalRenderBag=typeof renderBag==='function'?renderBag:null;
  if(originalRenderBag){
    renderBag=function(){originalRenderBag();setTimeout(forcePdaImage,0);setTimeout(forcePdaImage,100)};
  }
  const observer=new MutationObserver(()=>forcePdaImage());
  observer.observe(document.body,{childList:true,subtree:true});

  const preload=new Image();
  preload.onload=forcePdaImage;
  preload.src=PDA_SRC;
  setTimeout(forcePdaImage,250);
  setTimeout(forcePdaImage,1000);

  /* If the game's PDA Coin is represented by a dropped DOM element before
     pickup, give that element the same actual image wherever it exposes the
     item name. */
  document.querySelectorAll('*').forEach(el=>{
    if(el.childElementCount===0 && el.textContent.trim()===PDA_NAME){
      el.style.backgroundImage='url("'+PDA_SRC+'")';
      el.style.backgroundSize='contain';
      el.style.backgroundRepeat='no-repeat';
      el.style.backgroundPosition='center';
    }
  });

  window.__pandaniaPdaFixV9=true;
})();
/* ===== END PANDANIA PDA FIX v9 ===== */'''

text=text.replace('</script>','\n'+patch+'\n</script>',1)
path.write_text(text,encoding='utf-8')
