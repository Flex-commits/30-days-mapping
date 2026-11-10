"""Self-contained animated SVG atlas. Geographic anchors stay fixed; motion is illustrative."""
from pathlib import Path
import json,math,base64,html,random,os
import numpy as np
from PIL import Image,ImageDraw
from io import BytesIO
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];O=Path(os.environ.get('AKSUM_OUTPUT_DIR',str(R/'outputs/living-city')));O.mkdir(parents=True,exist_ok=True)
T=np.load(R/'data/terrain.npz');Z=T['z'];latop=float(T['lat_top']);lonleft=float(T['lon_left']);step=float(T['step']);tx=Transformer.from_crs(4326,32637,always_xy=True);origin=tx.transform(lonleft,latop-(len(Z)-1)*step)
def project(lat,lon):
 row=(latop-lat)/step;col=(lon-lonleft)/step;r=max(0,min(len(Z)-2,int(row)));c=max(0,min(Z.shape[1]-2,int(col)));fr=max(0,min(1,row-r));fc=max(0,min(1,col-c));z=Z[r,c]*(1-fr)*(1-fc)+Z[r+1,c]*fr*(1-fc)+Z[r,c+1]*(1-fr)*fc+Z[r+1,c+1]*fr*fc
 x,y=tx.transform(lon,lat);return (x-origin[0])*.58+30,940-((y-origin[1])*.36+(float(z)-2090)*3)*.58
B=json.loads((R/'data/scenario-buildings.json').read_text())['buildings'];sites=json.loads((R/'data/sites.json').read_text())['sites'];S={s['name']:s for s in sites};parts=[]
def path(d,**attrs):return '<path d="'+d+'" '+ ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())+'/>'
def poly(points,fill,stroke='#a77957',sw=.65):return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def building(b):
 x,y=project(b['lat'],b['lon']);w=b['width_metres']*.58;d=b['depth_metres']*.58;h=b['height_metres']*3*.58;red=b['kind']!='imagined home';stroke='#a8442e' if red else '#827361';front='#e3ae8d' if red else '#e8ddc5';out=[]
 out.append(f'<ellipse cx="{x+w*.6:.2f}" cy="{y+3:.2f}" rx="{w*.9:.2f}" ry="{max(2,d*.13):.2f}" fill="#443d2b" opacity=".13"/>');n=b['storeys'];tiers=[(.12,1.16),(.55,1),(.23,.78),(.10,.58)] if red else [(1,1)]
 yy=y
 for frac,fac in tiers:
  hh=h*frac;ww=w*fac;dx=d*.38*fac;dy=d*.36*fac
  out.append(poly([(x-ww/2,yy),(x+ww/2,yy),(x+ww/2,yy-hh),(x-ww/2,yy-hh)],front,stroke))
  out.append(poly([(x+ww/2,yy),(x+ww/2+dx,yy-dy),(x+ww/2+dx,yy-dy-hh),(x+ww/2,yy-hh)],'#c39271' if red else '#c8b998',stroke))
  out.append(poly([(x-ww/2,yy-hh),(x+ww/2,yy-hh),(x+ww/2+dx,yy-dy-hh),(x-ww/2+dx,yy-dy-hh)],'#f5dfbd',stroke))
  rows=max(1,int(hh/7.5))
  for j in range(rows):
   wy=yy-(j+.6)*hh/rows
   out.append(path(f'M{x-ww/2-1:.2f},{wy+2:.2f}h{ww+2:.2f}',stroke=stroke,stroke_width='.5',fill='none'))
   for f in [-.27,0,.27]:out.append(f'<rect x="{x+ww*f-1:.2f}" y="{wy-2:.2f}" width="2" height="3" fill="{stroke}"/>')
  yy-=hh
 return '<g class="scenario-building">'+''.join(out)+'</g>'
# Height-derived shaded surface. Materials are an artistic palette, not mapped land cover.
terrain_image=Image.new('RGBA',(3900,2100),(0,0,0,0));terrain_draw=ImageDraw.Draw(terrain_image)
light=np.array([-.55,-.45,.7]);light=light/np.linalg.norm(light)
for r in range(0,len(Z)-2,2):
 for c in range(0,Z.shape[1]-2,2):
  ids=[(r,c),(r,c+2),(r+2,c+2),(r+2,c)]
  for tri in [(0,1,2),(0,2,3)]:
   grid=[ids[i] for i in tri];points=[project(latop-rr*step,lonleft+cc*step) for rr,cc in grid]
   zz=np.array([float(Z[rr,cc]) for rr,cc in grid]);gy=(float(Z[min(r+2,len(Z)-1),c])-float(Z[r,c]))/60;gx=(float(Z[r,min(c+2,Z.shape[1]-1)])-float(Z[r,c]))/60
   normal=np.array([-gx,-gy,1]);normal/=np.linalg.norm(normal);shade=float(np.clip(np.dot(normal,light),0,1))
   blend=float(np.clip((zz.mean()-2140)/180,0,1));base=np.array([201,185,147])*(1-blend)+np.array([155,162,127])*blend;rgb=np.clip(base*(.77+.28*shade),0,255).astype(int);color='#%02x%02x%02x'%tuple(rgb)
   terrain_draw.polygon([(round(x*2),round(y*2)) for x,y in points],fill=color)
buf=BytesIO();terrain_image.save(buf,format='PNG');terrain_uri=base64.b64encode(buf.getvalue()).decode();parts.append(f'<image x="0" y="0" width="1950" height="1050" href="data:image/png;base64,{terrain_uri}"/>')
for row in range(0,len(Z),2):
 la=latop-row*step;pts=[project(la,lonleft+c*step) for c in range(0,Z.shape[1],2)]
 d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in pts)
 parts.append(path(d,stroke='#5f6651',stroke_width='.45',fill='none',opacity='.08'))
# A light paved court beneath each town cluster. All imagined.
for la,lo in [(14.1305,38.7195),(14.1265,38.709),(14.127,38.724)]:
 x,y=project(la,lo);parts.append(f'<ellipse cx="{x}" cy="{y+7}" rx="85" ry="23" fill="#e9ddbf" opacity=".5"/>')
for b in sorted(B,key=lambda b:-b['lat']):parts.append(building(b))
# Imagined colonnaded courts: a little civic life between the tower clusters.
for la,lo in [(14.1265,38.709),(14.127,38.724)]:
 x,y=project(la,lo);arc=[]
 arc.append(poly([(x-40,y+12),(x+40,y+12),(x+49,y+7),(x-31,y+7)],'#d2bd91','#8d795b',.35))
 for k in range(9):
  xx=x-35+k*9
  arc.append(f'<path d="M{xx},{y+10}v-13" stroke="#856f51" stroke-width="1.4"/>')
 arc.append(poly([(x-40,y-5),(x+40,y-5),(x+49,y-10),(x-31,y-10)],'#b99970','#8d795b',.4))
 parts.append('<g class="scenario-building">'+''.join(arc)+'</g>')
# Every moving figure is independent of surveyed landmark points.
random.seed(8);agents=[]
for k in range(96):
 center=[(14.1305,38.7195),(14.1265,38.709),(14.127,38.724)][k%3]
 # Choose compact circulation clear of projected building volumes.
 for attempt in range(250):
  la=center[0]+random.uniform(-.0018,.0018);lo=center[1]+random.uniform(-.003,.003);x,y=project(la,lo)
  blocked=False
  for bb in B:
   bx,by=project(bb['lat'],bb['lon']);bw=bb['width_metres']*.58;bh=bb['height_metres']*3*.58
   if x+28>bx-bw/2-3 and x-28<bx+bw*.9+3 and y+10>by-bh-3 and y-18<by+6:blocked=True;break
  if not blocked:break
 # Screen-space circulation around the imaginary courts, not modeled travel routes.
 rx=random.uniform(12,24);ry=random.uniform(3,6);dur=random.uniform(24,55);horse=k%16==0
 d=f'M {x-rx:.2f},{y:.2f} Q {x:.2f},{y-ry:.2f} {x+rx:.2f},{y:.2f} Q {x:.2f},{y+ry:.2f} {x-rx:.2f},{y:.2f}'
 color=['#ad4831','#4d5b52','#c4a16e','#ddd0ad'][k%4]
 if horse:
  body='<ellipse cx="0" cy="-4.6" rx="4" ry="1.7" fill="#795840"/><path d="M2,-5 L3,-9 L5,-9 L5.8,-7 L4,-6 L3,-3 M-3,-4 Q-6,-6 -5,-2" fill="#795840" stroke="#49392e" stroke-width=".65"/><g class="legs"><path d="M-2.6,-4 L-3.5,0 M-1.2,-4 L-.5,0 M1.2,-4 L.5,0 M2.6,-4 L3.5,0" stroke="#49392e" fill="none" stroke-width=".8"/></g><circle cy="-12" r=".85" fill="#49392e"/><path d="M-.6,-11 L.8,-11 L1.3,-6 L-1,-6 Z" fill="'+color+'" stroke="#49392e" stroke-width=".4"/>'
 else:
  body='<ellipse cy=".8" rx="1.8" ry=".45" fill="#483d2c" opacity=".12"/><g class="legs"><path d="M-.55,-1 L-1.1,1 M.55,-1 L1.1,1" fill="none" stroke="#49392e" stroke-width=".6"/></g><path d="M-.55,-5.1 L.55,-5.1 L1.4,-.8 L-1.4,-.8 Z" fill="'+color+'" stroke="#65513e" stroke-width=".35"/><path d="M-.45,-4.8 L.8,-1.5" stroke="#f4eddd" stroke-width=".4"/><circle cy="-6.2" r=".75" fill="#49392e"/>'
 agents.append(f'<g class="resident" aria-hidden="true"><animateMotion dur="{dur:.2f}s" begin="-{random.uniform(0,dur):.2f}s" repeatCount="indefinite" path="{d}"/><g class="body" style="animation-delay:-{k*.17}s"><g transform="scale(1.3)">{body}</g></g></g>')
landmarks=[('Dungur / Palace of Queen of Sheba','Dungur','Palace ruins; built before the seventh century CE. The 19-storey tower here is imagined.'),('Northern Stelae Field','Northern stelae field','Decorated stelae broadly third–fourth centuries CE. The three tower heights are design choices.'),('Ezana Inscription','Ezana inscription','Fourth-century inscriptions. This imagined tower is not the monument’s actual form.'),('Church of Our Lady Mary of Zion','Mary of Zion','The standing church reflects seventeenth-century rebuilding. Its twelve-storey form here is imagined.'),('Tombs of Kings Kaleb and Gebremeskel','Royal tombs','Traditional names, not confirmed identities of occupants. Twin towers are imagined.')]
labels=[]
for key,name,note in landmarks:
 site=S[key];x,y=project(site['lat'],site['lon']);labels.append(f'<g class="landmark" tabindex="0" role="button" aria-label="{html.escape(name+": "+note)}" data-name="{html.escape(name)}" data-note="{html.escape(note)}"><circle cx="{x}" cy="{y+10}" r="9" fill="#eee8d8" stroke="#a8442e"/><text x="{x}" y="{y+13}" text-anchor="middle" font-size="9" fill="#a8442e">{len(labels)+1}</text></g>')
# Two evidence-based monument sketches. Orientations and small details remain schematic.
monuments=[]
x,y=project(S['Stele 2']['lat'],S['Stele 2']['lon']);hh=24*3*.58;w=2.32*.58
monuments.append('<g class="monument-shape"><title>Returned obelisk: approximately 24 m, UNESCO; schematic elevation, 3× vertical exaggeration.</title>'+poly([(x-w/2,y),(x+w/2,y),(x+w/2,y-hh+2),(x+.2,y-hh),(x-.2,y-hh),(x-w/2,y-hh+2)],'#b3b6ac','#4f554d',.6))
for j in range(9):
 yy=y-4-j*hh/11
 monuments.append(f'<path d="M{x-w*.4},{yy}h{w*.8}" stroke="#555c54" stroke-width=".5"/>')
monuments.append('</g>')
x,y=project(S['Stele 1']['lat'],S['Stele 1']['lon']);length=33*.58
for j in range(3):
 xx=x+j*(length/3+1);monuments.append(poly([(xx,y),(xx+length/3,y),(xx+length/3+1.5,y-2),(xx+1.5,y-2)],'#a7aca2','#4f554d',.5))
monument_layer='<g id="monuments" style="display:none">'+''.join(monuments)+'</g>'
svg='<svg id="city" viewBox="0 320 1950 710" role="img" aria-labelledby="maptitle mapdesc" xmlns="http://www.w3.org/2000/svg"><title id="maptitle">Aksum, Built: a living imagined city</title><desc id="mapdesc">Modern terrain and fixed landmark locations with speculative towers, ninety walking figures and six riders. Movement and clothing are illustrative.</desc>'+'<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#d5e0df"/><stop offset="1" stop-color="#e2dfca"/></linearGradient></defs><rect x="0" y="180" width="1950" height="900" fill="url(#sky)"/>'+''.join(parts)+''.join(agents)+monument_layer+''.join(labels)+'</svg>'

photos={
 'Dungur':{'file':'dungur-2018.jpg','caption':'Dungur: surviving stepped masonry, photographed in 2018. A.Savin, Wikipedia. Free Art License. Resized; otherwise unchanged.','source':'https://commons.wikimedia.org/wiki/File:ET_Axum_asv2018-01_img48_Dungur.jpg','license':'https://artlibre.org/licence/lal/en/','alt':'Surviving stepped masonry and wall foundations at Dungur, Aksum.'},
 'Northern stelae field':{'file':'obelisk-2008.jpg','caption':'Obelisk reinstallation, 2008. © UNESCO / Michel Ravassard. CC BY-SA 3.0 IGO. Resized; otherwise unchanged. Commons date field and embedded camera date differ; year is consistent.','source':'https://commons.wikimedia.org/wiki/File:Aksum-107549.jpg','license':'https://creativecommons.org/licenses/by-sa/3.0/igo/','alt':'Archaeological conservation work during the Aksum obelisk reinstallation in 2008.'}}
for info in photos.values():
 info['image']='data:image/jpeg;base64,'+base64.b64encode((R/'data/photos'/info['file']).read_bytes()).decode()

# Photographic evidence is visible on the map, linked to site anchors (not camera positions).
photo_callouts=[]
for key,name,x,title,credit in [
 ('Dungur','Dungur / Palace of Queen of Sheba',100,'Dungur · surviving masonry · 2018','A.Savin, Wikipedia · Free Art License'),
 ('Northern stelae field','Stele 2',1250,'Returned obelisk · conservation · 2008','© UNESCO / Michel Ravassard · CC BY-SA 3.0 IGO')]:
 info=photos[key];px,py=project(S[name]['lat'],S[name]['lon']);cx=x+280
 photo_callouts.append(f'<g class="photo-connection"><path d="M{px:.2f},{py+14:.2f} L{px:.2f},1035 L{cx},1035 L{cx},1060" fill="none" stroke="#934c34" stroke-width="1.2"/><circle cx="{px:.2f}" cy="{py+14:.2f}" r="3" fill="#934c34"/><rect x="{x}" y="1060" width="560" height="345" rx="5" fill="#eeeade" stroke="#b9b59f"/><a href="{info["source"]}" target="_blank" rel="noopener"><image x="{x+12}" y="1072" width="536" height="242" preserveAspectRatio="xMidYMid meet" href="{info["image"]}"><title>{html.escape(info["alt"])}</title></image><text x="{x+16}" y="1340" fill="#403c30" font-family="serif" font-size="23">{title}</text></a><text x="{x+16}" y="1366" fill="#746b57" font-family="sans-serif" font-size="14">{credit}</text><a href="{info["license"]}" target="_blank" rel="noopener"><text x="{x+16}" y="1388" fill="#746b57" font-family="sans-serif" font-size="13">Resized, otherwise unchanged · source and license ↗</text></a></g>')
svg=svg.replace('</desc>','</desc><rect x="0" y="0" width="1950" height="1600" fill="#e7e5d9"/>').replace('</svg>','<g id="photo-connections">'+''.join(photo_callouts)+'</g></svg>').replace('viewBox="0 320 1950 710"','viewBox="0 260 1950 1180"')
font=base64.b64encode((R/'fonts/serif.ttf').read_bytes()).decode()
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aksum, Built · A living city</title><style>
@font-face{font-family:Fell;src:url(data:font/ttf;base64,FONT)}*{box-sizing:border-box}body{margin:0;background:#e7e5d9;color:#30291f;font:14px/1.6 system-ui}main{max-width:1600px;margin:auto;padding:30px 4vw}nav{border-bottom:1px solid #bcbca8;padding-bottom:16px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:.12em;color:#796b54}h1{letter-spacing:-.035em;font:clamp(48px,7vw,88px)/1.1 Fell,serif;font-weight:400;margin:35px 0 8px}header p{color:#a8442e;font:22px Fell,serif;margin:0}header{position:relative}header .history{max-width:780px;font:14px/1.7 system-ui;color:#5f604e;margin:18px 0 6px}header .question{font:21px Fell,serif;color:#a8442e;margin:8px 0}.photo-card{max-width:850px;display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:16px 0}.photo-card[hidden]{display:none}.photo-card img{width:100%;height:auto;display:block}.photo-card p,.photo-card a{font-size:12px}.photo-card h2{font:26px Fell,serif;font-weight:400}.photo-card svg{max-width:300px}.photo-card figcaption{font-size:11px;color:#76664f}.photo-card figure{margin:0}@media(max-width:650px){.photo-card{grid-template-columns:1fr}}button{background:#ede9dc;color:inherit;border:1px solid #b5a387;padding:9px 16px;cursor:pointer;border-radius:22px;font:inherit}button:hover,button[aria-pressed=true]{background:#e4d7b9}button:focus-visible,.landmark:focus-visible{outline:2px solid #a8442e;outline-offset:4px}.controls{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0 0}.map{margin:8px -3vw 0;background:linear-gradient(#d5e0df 0%,#e2e4d9 32%,#d9d5bc 100%);border:1px solid #c5c4b4;border-radius:5px;overflow:hidden;box-shadow:0 14px 45px #313d2d12}svg{width:100%;height:auto;display:block;overflow:hidden}.landmark{cursor:pointer}.landmark:hover circle,.landmark:focus circle{fill:#e8c5a4}.body{animation:bob 1.1s ease-in-out infinite}.legs{transform-origin:center;animation:stride .65s ease-in-out infinite alternate}@keyframes bob{50%{transform:translateY(-.35px)}}@keyframes stride{to{transform:skewX(15deg)}}.paused *{animation-play-state:paused!important}#detail{min-height:65px;border-top:1px solid #d4c4a5;padding:14px 0;max-width:850px}#detail strong{font:23px Fell,serif;margin-right:16px}#detail span{color:#76664f;font-size:13px}details{max-width:900px;border-top:1px solid #d4c4a5;padding:15px 0}summary{cursor:pointer}details p{font-size:12px;color:#76664f}footer{font-size:10px;color:#84735b;margin:20px 0}a{color:inherit} .key{display:flex;gap:24px;flex-wrap:wrap;color:#84735b;font-size:11px;margin:5px 0 12px} @media(prefers-reduced-motion:reduce){.body,.legs{animation:none}}@media(max-width:650px){main{padding:22px 20px}.map{margin:18px -18px}header p{font-size:18px}#detail strong{display:block}.key{gap:8px 18px}}
</style><main><nav><span>THOMAS HAGOS / MUSA 2026</span><span>DAY 08 · UTOPIA</span></nav><header><h1>Aksum, Built</h1><p>An imagined city, lived in.</p><p class="history">Aksum, in northern Ethiopia, was the capital of a kingdom linking Africa, Arabia and the Mediterranean world. Its stone monuments still carry the language of its architecture: doors, windows and projecting beam ends.</p><p class="question">What if that architectural language grew into a living city?</p></header><div class="controls"><button id="pause" aria-pressed="false">Pause movement</button><button id="zoom" aria-pressed="false">Closer view</button><button id="marks" aria-pressed="true">Landmarks</button><button id="photo-toggle" aria-pressed="true">Photo connections</button><button id="evidence" aria-pressed="false">Monument evidence</button></div><div class="map">SVG</div><div class="key"><span>Terracotta · imagined landmark towers</span><span>Stone · imagined homes</span><span>Numbered circles · real landmark anchors</span><span>Looking north · heights exaggerated 3×</span><span>Relief from elevation; surface colors are illustrative</span></div><section id="detail" aria-live="polite"><strong>A city in motion.</strong><span>Select a landmark. Pins 1 and 2 include archaeological photographs.</span></section><section id="photo-card" class="photo-card" hidden aria-label="Landmark photographic evidence"></section><details><summary>The evidence beneath the city.</summary><p>Terrain: modern Copernicus GLO-30 surface model. Approximate landmark positions: © OpenStreetMap contributors, ODbL. Projection: UTM zone 37N, north foreshortened to 0.36. Towers, homes, colonnaded courts, people, riders and circulation are speculative. Garments and horses are interpretive entourage, not verified historical reconstructions. Animated paths do not represent excavated roads or measured journeys. Shaded relief is computed from the saved elevation grid; colors do not reconstruct ancient vegetation or stone types. Two monument sketches use UNESCO dimensions; the fallen stele’s orientation and carved details are schematic. <a href="https://whc.unesco.org/en/news/458/">Returned obelisk: UNESCO, 2008</a>; <a href="https://whc.unesco.org/en/list/15/">Great Stele: UNESCO</a>. Ninety pedestrians and six riders; figure size is increased for legibility.</p><p>Tower module: a chosen 6 m podium plus 4.32 m per storey, informed by Yeha reconstruction research. Nineteen chosen storeys gives 88.08 m; this is not evidence of ancient Aksum building heights or structural capacity. Historical periods follow <a href="https://whc.unesco.org/en/list/15/">UNESCO</a> and <a href="https://www.metmuseum.org/essays/monumental-architecture-and-stelae-of-the-aksumite-empire">The Met</a>. No shared historical moment is implied.</p><p>Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.</p></details><footer><p><a href="https://github.com/Flex-commits/30-days-mapping/tree/main/day08-aksum-built">Code, data and sources</a> · <a href="assets/aksum-built.png">Static map</a> · <a href="../">All maps</a></p>Thomas Hagos · Original drawing and composition, CC BY 4.0. IM FELL English by Igino Marini, SIL OFL 1.1. Geographic sources retain their own licenses.</footer></main><script>
const photoToggle=document.querySelector('#photo-toggle');photoToggle.onclick=()=>{const on=photoToggle.getAttribute('aria-pressed')!=='true';photoToggle.setAttribute('aria-pressed',String(on));document.querySelector('#photo-connections').style.display=on?'':'none';document.querySelector('#city').setAttribute('viewBox',on?'0 260 1950 1180':'0 320 1950 710')};
const PHOTOS=PHOTOJSON;
function showPhoto(name){const card=document.querySelector('#photo-card'),p=PHOTOS[name];card.replaceChildren();card.hidden=!p;if(!p)return;const figure=document.createElement('figure'),image=Object.assign(document.createElement('img'),{src:p.image,alt:p.alt}),cap=Object.assign(document.createElement('figcaption'),{textContent:p.caption});figure.append(image,cap);const body=document.createElement('div'),heading=Object.assign(document.createElement('h2'),{textContent:name==='Dungur'?'The surviving foundation':'The monument, conserved'}),note=Object.assign(document.createElement('p'),{textContent:name==='Dungur'?'The photograph shows the remains. The profile below explains a stepped base only; it is not a surveyed elevation. No measured podium height is asserted for Dungur.':'This is documentation of conservation in 2008, not a photograph of ancient construction.'});body.append(heading,note);if(name==='Dungur'){const diagram=document.createElementNS('http://www.w3.org/2000/svg','svg');diagram.setAttribute('viewBox','0 0 300 100');diagram.setAttribute('role','img');diagram.setAttribute('aria-label','Schematic stepped base, not measured.');diagram.innerHTML='<path d="M10 85H290 M30 85V70H50V55H70V40H230V55H250V70H270V85Z" fill="#b8aa89" stroke="#625d4b"/><text x="150" y="98" text-anchor="middle" font-size="10">Schematic only · no measured dimensions</text>';body.append(diagram)}const source=Object.assign(document.createElement('a'),{href:p.source,textContent:'Photograph and source record'}),license=Object.assign(document.createElement('a'),{href:p.license,textContent:'Photo license'});body.append(source,document.createTextNode(' · '),license);card.append(figure,body)}
const evidence=document.querySelector('#evidence');let evidenceMode=false;
evidence.onclick=()=>{evidenceMode=!evidenceMode;evidence.setAttribute('aria-pressed',String(evidenceMode));document.querySelectorAll('.scenario-building').forEach(e=>e.style.opacity=evidenceMode?'.12':'1');document.querySelectorAll('.resident').forEach(e=>e.style.display=evidenceMode?'none':'');document.querySelector('#monuments').style.display=evidenceMode?'':'none';document.querySelector('#detail').textContent=evidenceMode?'Stone evidence: returned obelisk ≈24 m; fallen Great Stele ≈33 m long. Simplified drawings at approximate OSM anchors; fallen orientation is schematic. Other monuments are not modeled.':'Select a landmark. Pins 1 and 2 include archaeological photographs.'};
const city=document.querySelector('#city'),pause=document.querySelector('#pause'),zoom=document.querySelector('#zoom'),marks=document.querySelector('#marks');let stopped=false;
function setPaused(value){stopped=value;city.classList.toggle('paused',value);value?city.pauseAnimations():city.unpauseAnimations();pause.textContent=value?'Play movement':'Pause movement';pause.setAttribute('aria-pressed',String(value))}
pause.onclick=()=>setPaused(!stopped);const reduced=matchMedia('(prefers-reduced-motion: reduce)');setPaused(reduced.matches);reduced.addEventListener('change',e=>setPaused(e.matches));
zoom.onclick=()=>{const active=zoom.getAttribute('aria-pressed')!=='true';zoom.setAttribute('aria-pressed',String(active));city.setAttribute('viewBox',active?'450 460 1050 500':(photoToggle.getAttribute('aria-pressed')==='true'?'0 260 1950 1180':'0 320 1950 710'));zoom.textContent=active?'Whole city':'Closer view'};
marks.onclick=()=>{const active=marks.getAttribute('aria-pressed')!=='true';marks.setAttribute('aria-pressed',String(active));document.querySelectorAll('.landmark').forEach(el=>el.style.display=active?'':'none')};
document.querySelectorAll('.landmark').forEach(el=>{function show(){showPhoto(el.dataset.name);document.querySelector('#detail').replaceChildren(Object.assign(document.createElement('strong'),{textContent:el.dataset.name}),Object.assign(document.createElement('span'),{textContent:el.dataset.note}))}el.onclick=show;el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();show()}}});
document.addEventListener('visibilitychange',()=>{if(document.hidden){city.pauseAnimations();city.classList.add('paused')}else if(!stopped){city.unpauseAnimations();city.classList.remove('paused')}});
</script></html>'''.replace('FONT',font).replace('SVG',svg).replace('PHOTOJSON',json.dumps(photos))
(O/'aksum-living-city.html').write_text(page);(O/'city.svg').write_text(svg)
(O/'README.md').write_text('Open aksum-living-city.html in a browser. Self-contained; no network required. Pause, zoom and keyboard-accessible landmark details included. Movement is illustrative, not historical routing.\n')
print('Built',len(B),'buildings;',len(agents),'animated residents;',len(labels),'landmarks')
