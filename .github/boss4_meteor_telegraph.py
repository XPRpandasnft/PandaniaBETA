from pathlib import Path
p=Path("Adventures Of Pandania The Lost Realms/index.html")
s=p.read_text(encoding="utf-8")
patch=r'''<!-- ===== BOSS4 METEOR TELEGRAPH FINAL AUTHORITATIVE LAYER ===== -->
<script>
(function(){'use strict';
window.__finalBoss4Meteors=window.__finalBoss4Meteors||[];
window.__boss4MeteorNext=window.__boss4MeteorNext||0;
window.__boss4MeteorImage=window.__boss4MeteorImage||null;
function boss4HasBoss(){return inDungeon&&typeof dungeonLevel!=="undefined"&&dungeonLevel===4&&Array.isArray(monsters)&&monsters.some(function(m){return m.type==="boss4"&&m.hp>0;});}
function boss4Image(){if(window.__boss4MeteorImage)return window.__boss4MeteorImage;var img=new Image();img.onload=function(){window.__boss4MeteorImage=img;};img.src="./images/metalmonsterspecialattack.png";return img;}
window.__finalBoss4Tick=function(){
  if(!boss4HasBoss()){window.__finalBoss4Meteors.length=0;window.__boss4MeteorNext=0;return;}
  var now=performance.now();
  if(!window.__boss4MeteorNext)window.__boss4MeteorNext=now+2500;
  if(now>=window.__boss4MeteorNext){
    for(var i=0;i<3;i++){
      var x=140+Math.random()*Math.max(1,dungeon.width-280);
      var targetY=150+Math.random()*Math.max(1,dungeon.height-300);
      window.__finalBoss4Meteors.push({x:x,targetY:targetY,y:-150-Math.random()*80,vy:12.5,warningUntil:now+1000,active:false,impacted:false,impactUntil:0,damage:48,radius:24});
    }
    window.__boss4MeteorNext=now+2500;
    if(typeof bossSound==="function")bossSound();
  }
  for(var j=window.__finalBoss4Meteors.length-1;j>=0;j--){
    var q=window.__finalBoss4Meteors[j];
    if(!q.active&&!q.impacted&&now>=q.warningUntil)q.active=true;
    if(q.active){
      q.y+=q.vy;
      if(q.y>=q.targetY){
        q.y=q.targetY;q.active=false;q.impacted=true;q.impactUntil=now+220;
        if(Math.hypot(player.x-q.x,player.y-q.targetY)<=q.radius&&player.invincible<=0){
          player.hp-=q.damage;addDamageNumber(player.x,player.y-48,q.damage,'#fff');player.invincible=30;if(typeof hitSound==="function")hitSound();if(player.hp<=0)respawnPlayer();
        }
      }
    }else if(q.impacted&&now>q.impactUntil)window.__finalBoss4Meteors.splice(j,1);
  }
};
window.__finalBoss4DrawWorld=function(){
  if(!boss4HasBoss())return;
  window.__finalBoss4Tick();
  var now=performance.now(),img=boss4Image();
  for(var i=0;i<window.__finalBoss4Meteors.length;i++){
    var q=window.__finalBoss4Meteors[i];ctx.save();
    if(!q.impacted&&now<q.warningUntil){
      ctx.globalAlpha=.68+Math.sin(now/90)*.12;ctx.fillStyle="rgba(0,0,0,.65)";ctx.shadowColor="rgba(0,0,0,.95)";ctx.shadowBlur=9;ctx.beginPath();ctx.arc(q.x,q.targetY,24,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;ctx.strokeStyle="rgba(255,255,255,.5)";ctx.lineWidth=2;ctx.beginPath();ctx.arc(q.x,q.targetY,23,0,Math.PI*2);ctx.stroke();
    }
    if(q.active){
      ctx.globalAlpha=.95;ctx.shadowColor="#b13cff";ctx.shadowBlur=32;
      if(img&&img.complete&&img.naturalWidth>0){ctx.imageSmoothingEnabled=false;ctx.drawImage(img,q.x-42,q.y-84,84,84);}
    }else if(q.impacted&&now<q.impactUntil){
      ctx.globalAlpha=.95;ctx.shadowColor="#b13cff";ctx.shadowBlur=36;
      if(img&&img.complete&&img.naturalWidth>0){var w=84*(1+(1-(q.impactUntil-now)/220)*.35);ctx.drawImage(img,q.x-w/2,q.y-w/2,w,w);}
    }
    ctx.restore();
  }
};
})();
</script>
<!-- ===== END BOSS4 METEOR TELEGRAPH FINAL AUTHORITATIVE LAYER ===== -->
'''
s=s.replace("</body>",patch+"\n</body>",1)
p.write_text(s,encoding="utf-8")
