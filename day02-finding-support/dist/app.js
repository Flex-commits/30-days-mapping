'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kind={adult:{label:'Adult drop-in',color:'#c65b3d',description:'Day-to-day support, basic services and connections to housing assistance. Drop-in service is not a guarantee of an overnight bed.'},intake:{label:'Shelter intake',color:'#5664be',description:'A place to apply for shelter. The correct intake location depends on your age and household. Check the official eligibility guidance before travel.'},youth:{label:'Youth drop-in',color:'#168579',description:'Support and referrals for young people ages 14–24. Services and hours vary by location; check with the provider before travel.'}};
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
let map,rows=[],visible=[],type='all',selected=null,points=L.layerGroup(),markers=new Map(),grouping=false,mode='lines';
const symbol=t=>`<i class="symbol ${t}" aria-hidden="true"></i>`;
const distanceText=m=>`≈${(m/1609.344).toFixed(2)} mi`;
function rowHTML(r){const d=r.rail_distance_m,st=r.nearest_station;return `<button class="location-row${selected===r.id?' selected':''}" data-id="${r.id}" aria-pressed="${selected===r.id}"><span class="row-number">${r.number}</span><span class="row-text"><strong>${esc(r.name)}</strong><small>${esc(r.borough)} · ${esc(kind[r.type].label)}</small><span class="distance-row"><span class="distance-track"><i style="width:${Math.max(1,d/5000*100)}%;background:${kind[r.type].color}"></i></span><span>${distanceText(d)} to ${esc(st.name)}</span></span></span></button>`;}
function updateList(){
 $('list').innerHTML=visible.length?visible.map(rowHTML).join(''):'<p class="empty">No services match these filters.<br>Try a different term or reset the filters.</p>';
 $('result-count').textContent=`${visible.length} OF ${rows.length} LOCATIONS`;
 $('list').querySelectorAll('.location-row').forEach(el=>el.onclick=()=>select(el.dataset.id));
}
function filter(fitMap=false){
 const q=$('search').value.toLowerCase().trim(),borough=$('borough').value,fullTime=$('hours').checked;
 visible=rows.filter(r=>(type==='all'||r.type===type)&&(borough==='all'||r.borough===borough)&&(!fullTime||r.listed24h)&&`${r.name} ${r.address} ${r.borough} ${r.audience} ${r.category}`.toLowerCase().includes(q));
 if(!visible.some(r=>r.id===selected)){selected=null;$('detail').hidden=true;}
 const order=$('sort').value;visible.sort(order==='far'?(a,b)=>b.rail_distance_m-a.rail_distance_m:order==='near'?(a,b)=>a.rail_distance_m-b.rail_distance_m:(a,b)=>a.name.localeCompare(b.name));
 updateList();drawPoints();if(fitMap)fit();
}
function fit(){
 selected=null;$('detail').hidden=true;updateList();
 if(visible.length){map.fitBounds(L.latLngBounds(visible.map(r=>[r.lat,r.lon])),{paddingTopLeft:[55,155],paddingBottomRight:[55,155],maxZoom:14,animate:!reduce});}
 drawPoints();
}
function individual(r){
 const icon=L.divIcon({className:'point-icon'+(r.id===selected?' chosen':''),html:`<span class="point ${r.type}"></span>`,iconSize:[22,22],iconAnchor:[11,11]});
 const marker=L.marker([r.lat,r.lon],{icon,title:`${r.name} — ${kind[r.type].label}`,alt:r.name,keyboard:true,zIndexOffset:r.id===selected?2000:0}).addTo(points);
 marker.bindTooltip(`${esc(r.name)}<br><span style="color:#8c9492;font-size:8px">${esc(kind[r.type].label)} · ${esc(r.borough)}</span>`,{direction:'top',offset:[0,-10]});
 marker.on('click',()=>select(r.id));markers.set(r.id,marker);
}
function drawPoints(){
 if(!map||grouping)return;if(mode==='lines'){drawLines();return;}grouping=true;points.clearLayers();markers.clear();
 const unselected=visible.filter(r=>r.id!==selected),parent=unselected.map((_,i)=>i),px=unselected.map(r=>map.project([r.lat,r.lon]));
 const root=i=>{while(parent[i]!==i)i=parent[i];return i;};
 for(let i=0;i<unselected.length;i++)for(let j=i+1;j<unselected.length;j++)if(px[i].distanceTo(px[j])<26)parent[root(i)]=root(j);
 const groups=new Map();unselected.forEach((r,i)=>{let k=root(i);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(r);});
 groups.forEach(group=>{
  if(group.length===1){individual(group[0]);return;}
  let lat=group.reduce((s,r)=>s+r.lat,0)/group.length,lon=group.reduce((s,r)=>s+r.lon,0)/group.length;
  const icon=L.divIcon({className:'group-icon',html:`<span class="group-disc">${group.length}</span>`,iconSize:[30,30],iconAnchor:[15,15]});
  const marker=L.marker([lat,lon],{icon,title:`${group.length} nearby locations — zoom to separate`,keyboard:true}).addTo(points).bindTooltip(`${group.length} nearby locations · click to expand`,{direction:'top',offset:[0,-14]});
  marker.on('click',()=>map.fitBounds(group.map(r=>[r.lat,r.lon]),{padding:[80,120],maxZoom:18,animate:!reduce}));
 });
 if(selected){const r=visible.find(r=>r.id===selected);if(r)individual(r);}
 grouping=false;
}
function drawLines(){
 points.clearLayers();markers.clear();
 visible.forEach(r=>{
  const st=r.nearest_station,on=r.id===selected,opacity=selected && !on ? .2 : .9;
  const line=L.polyline([[st.lat,st.lon],[r.lat,r.lon]],{color:kind[r.type].color,weight:on?4:2.6,opacity,lineCap:'round'}).addTo(points);
  line.bindTooltip(`${esc(r.name)} → ${esc(st.name)}<br>${distanceText(r.rail_distance_m)} straight-line distance`,{sticky:true});line.on('click',()=>select(r.id));
  const station=L.circleMarker([st.lat,st.lon],{radius:on?4:3,color:'#506165',weight:1.3,fillColor:'#fbfaf7',fillOpacity:1,opacity}).addTo(points).bindTooltip(`${esc(st.name)} · ${esc(st.routes)}`,{direction:'top'});
  station.on('click',()=>select(r.id));
  const service=L.circleMarker([r.lat,r.lon],{radius:on?5:4,color:'#fffefa',weight:1.3,fillColor:kind[r.type].color,fillOpacity:opacity,opacity}).addTo(points).bindTooltip(esc(r.name),{direction:'top'});
  service.on('click',()=>select(r.id));markers.set(r.id,service);
 });
}
function select(id){
 const r=rows.find(r=>r.id===id);if(!r)return;
 selected=id;updateList();drawPoints();
 const info=kind[r.type],dest=encodeURIComponent(r.address+', '+r.borough+', New York');
 $('detail').innerHTML=`<div class="detail-head">${symbol(r.type)} <span>${esc(info.label.toUpperCase())}</span><button id="close-detail" aria-label="Close location details">×</button></div><div class="detail-body"><span class="location-index">LOCATION ${r.number} / ${rows.length}</span><h2>${esc(r.name)}</h2><p class="address">${esc(r.address)}<br>${esc(r.borough)}, New York</p><div class="rail-fact"><span>NEAREST RAIL STATION</span><strong>${esc(r.nearest_station.name)} · ${esc(r.nearest_station.routes)}</strong><small><b>${distanceText(r.rail_distance_m)}</b>straight-line distance</small><p>Station centroid to service address. Not a walking route.</p></div><p class="service-intro">${esc(info.description)}</p><dl><dt>WHO IT SERVES</dt><dd>${esc(r.audience)}</dd><dt>LISTED HOURS</dt><dd>${r.listed24h?'<span class="hours-badge">Listed 24 hours / 7 days</span>':esc(r.hours)}<span class="hours-detail">Confirm hours and intake before travel.</span></dd>${r.phone?`<dt>CONTACT</dt><dd><a href="tel:+1${r.phone.replace(/\D/g,'')}">${esc(r.phone)}</a>${r.phone_ext?' · ext. '+esc(r.phone_ext):''}</dd>`:''}</dl><div class="detail-actions"><a class="primary" href="${esc(r.source)}" target="_blank" rel="noopener">Official information ↗</a><a href="https://www.google.com/maps/dir/?api=1&destination=${dest}&travelmode=transit" target="_blank" rel="noopener">Transit directions ↗</a></div></div><div class="detail-source">Public listing checked 02 Nov 2026 · Independent map<details><summary>Location method & sources</summary><p>Approximate address point from the U.S. Census geocoder; not a surveyed entrance. <a href="${esc(r.coordinate_source)}" target="_blank" rel="noopener">Coordinate source ↗</a>${r.additional_source?` · <a href="${esc(r.additional_source)}" target="_blank" rel="noopener">Supporting city listing ↗</a>`:''}</p></details></div>`;
 $('detail').hidden=false;
 $('close-detail').onclick=()=>{selected=null;$('detail').hidden=true;updateList();drawPoints();};
 const mobile=innerWidth<=760;
 if(mode==='lines'){
  const st=r.nearest_station;
  map.fitBounds([[r.lat,r.lon],[st.lat,st.lon]],{paddingTopLeft:mobile?[30,65]:[65,145],paddingBottomRight:mobile?[30,480]:[Math.min(385,map.getSize().x*.42),140],maxZoom:16,animate:!reduce});
 }else{
  let center=L.latLng(r.lat,r.lon),zoom=mobile?14:15;
  if(mobile){let p=map.project(center,zoom);center=map.unproject([p.x,p.y+map.getSize().y/2-115],zoom);}
  map.flyTo(center,zoom,{duration:reduce?0:1.1});
 }
 if(mobile)$('map').scrollIntoView({behavior:reduce?'instant':'smooth',block:'start'});
}
function reset(){type='all';$('search').value='';$('borough').value='all';$('hours').checked=false;document.querySelectorAll('.type').forEach(b=>{let on=b.dataset.type==='all';b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});filter(true);}
function openDirectory(){
 $('directory-list').innerHTML=rows.map(r=>rowHTML(r)).join('');
 $('directory-list').querySelectorAll('.location-row').forEach(b=>b.onclick=()=>{$('directory').close();reset();select(b.dataset.id);});
 $('directory').showModal();
}
async function init(){
 const [data,boroughs,context]=await Promise.all([fetch('data/locations.json').then(r=>r.json()),fetch('data/boroughs.geojson').then(r=>r.json()),fetch('data/context-states.geojson').then(r=>r.json())]);rows=data;
 map=L.map('map',{zoomControl:false,minZoom:10,maxZoom:18,scrollWheelZoom:true,zoomSnap:.25}).setView([40.715,-73.96],11);
 L.control.zoom({position:'topright'}).addTo(map);const MilesScale=L.Control.extend({options:{position:'bottomleft'},onAdd(m){const box=L.DomUtil.create('div','leaflet-control-scale'),line=L.DomUtil.create('div','leaflet-control-scale-line',box);const update=()=>{const y=m.getSize().y/2,max=m.distance(m.containerPointToLatLng([0,y]),m.containerPointToLatLng([80,y]))/1609.344;const ticks=[.001,.002,.005,.01,.02,.05,.1,.2,.5,1,2,3,5,10,20];const miles=ticks.filter(v=>v<=max).pop()||.001;line.style.width=(80*miles/max)+'px';line.textContent=miles+' mi';};m.on('moveend zoomend resize',update);m.whenReady(update);return box;}});new MilesScale().addTo(map);
 const tiles=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,opacity:.23,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · Boroughs: <a href="https://data.cityofnewyork.us/d/gthc-hcne">NYC DCP</a>'});
 map.createPane('boroughs');map.getPane('boroughs').style.zIndex=300;
 const contextLayer=L.geoJSON(context,{pane:'boroughs',interactive:false,style:{fillColor:'#eeefea',fillOpacity:1,color:'#cdd6d9',weight:.65},attribution:'Regional land: <a href="https://www.naturalearthdata.com/">Natural Earth</a>'}).addTo(map);
 const boroughLayer=L.geoJSON(boroughs,{pane:'boroughs',interactive:false,style:{fillColor:'#fffefa',fillOpacity:1,color:'#bac8ce',weight:1},attribution:'Boroughs: <a href="https://data.cityofnewyork.us/d/gthc-hcne">NYC DCP</a>'}).addTo(map);
 $('streets').onclick=()=>{const on=$('streets').getAttribute('aria-pressed')!=='true';$('streets').setAttribute('aria-pressed',String(on));if(on)tiles.addTo(map);else map.removeLayer(tiles);contextLayer.setStyle({fillOpacity:on?.2:1});boroughLayer.setStyle({fillOpacity:on?.45:1});};
 map.createPane('labels');map.getPane('labels').style.zIndex=450;map.getPane('labels').style.pointerEvents='none';
 const labels=[['BRONX',40.855,-73.867,''],['QUEENS',40.745,-73.807,''],['BROOKLYN',40.635,-73.948,''],['STATEN ISLAND',40.597,-74.119,''],['MANHATTAN',40.776,-73.98,'manhattan']];
 labels.forEach(([label,lat,lon,cls])=>L.marker([lat,lon],{pane:'labels',interactive:false,icon:L.divIcon({className:'borough-label',html:`<span class="${cls}">${label}</span>`,iconSize:[150,20],iconAnchor:[75,10]})}).addTo(map));
 [['Upper Bay',40.655,-74.048],['Jamaica Bay',40.60,-73.85],['Hudson River',40.775,-74.024]].forEach(([label,lat,lon])=>L.marker([lat,lon],{pane:'labels',interactive:false,icon:L.divIcon({className:'water-label',html:label,iconSize:[100,20],iconAnchor:[50,10]})}).addTo(map));
 points.addTo(map);map.on('zoomend',drawPoints);
 document.querySelectorAll('.type').forEach(b=>b.onclick=()=>{type=b.dataset.type;document.querySelectorAll('.type').forEach(t=>{let on=t===b;t.classList.toggle('active',on);t.setAttribute('aria-pressed',String(on));});filter(true);});
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{mode=b.dataset.view;document.querySelector('.map-area').dataset.mode=mode;document.querySelectorAll('[data-view]').forEach(t=>{let on=t===b;t.classList.toggle('active',on);t.setAttribute('aria-pressed',String(on));});$('map').setAttribute('aria-label',mode==='lines'?'Straight-line connections to nearest rail stations':'Service locations');document.querySelector('.line-reading').innerHTML=mode==='lines'?'<b>● ───── ○</b> Service to nearest station':'Equal-size points; numbers group nearby locations';document.querySelector('.map-caption p').textContent=mode==='lines'?'Nearest rail connections':'Service locations';drawPoints();if(selected)select(selected);});
 $('sort').onchange=()=>filter();$('search').oninput=()=>filter();$('borough').onchange=()=>filter(true);$('hours').onchange=()=>filter(true);$('reset').onclick=reset;$('fit').onclick=fit;
 $('explore-nav').onclick=()=>{if($('directory').open)$('directory').close();fit();};$('directory-nav').onclick=openDirectory;
 $('about-nav').onclick=()=>$('about').showModal();
 document.querySelectorAll('dialog').forEach(d=>{d.querySelector('.close-modal').onclick=()=>d.close();d.onclick=e=>{if(e.target===d){let r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}};});
 window.addEventListener('resize',()=>map.invalidateSize());
 let loaded=false,errors=0;tiles.on('tileload',()=>{loaded=true;document.querySelector('.offline-note')?.remove();});tiles.on('tileerror',()=>{if(++errors>8&&!loaded&&!document.querySelector('.offline-note'))$('map').insertAdjacentHTML('afterend','<div class="offline-note">Street context is unavailable. Local borough outlines and service points remain visible.</div>');});
 filter(true);
}
init().catch(e=>{$('list').innerHTML='<p class="empty">The service data could not load. Please refresh, or use the NYC311 link below.</p>';console.error(e);});
