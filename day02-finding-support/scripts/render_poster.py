"""Render the shareable map from local geometry and checked address points."""
import json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'dist/data/locations.json').read_text())
boroughs=json.loads((ROOT/'dist/data/boroughs.geojson').read_text())
context=json.loads((ROOT/'source-data/context-states.geojson').read_text())
fonts=ROOT/'dist/fonts'
serif=FontProperties(fname=str(fonts/'font-5.ttf'));italic=FontProperties(fname=str(fonts/'font-4.ttf'));sans=FontProperties(fname=str(fonts/'font-0.ttf'));bold=FontProperties(fname=str(fonts/'font-2.ttf'))
paper,ink,muted,water='#fbfaf7','#25282d','#879296','#e7eef1'
colors={'adult':'#c65b3d','intake':'#5664be','youth':'#168579'};markers={'adult':'o','intake':'D','youth':'s'}
C=math.cos(math.radians(40.7))
fig=plt.figure(figsize=(10,11.5),facecolor=paper)
def txt(x,y,s,size=10,color=ink,font=sans,**kwargs):return fig.text(x,y,s,fontsize=size,color=color,fontproperties=font,**kwargs)
txt(.055,.955,'FINDING SUPPORT  /  AN NYC SERVICE ATLAS',8,font=bold)
txt(.945,.955,'02  /  LINES',8,color=muted,ha='right')
fig.add_artist(plt.Line2D([.055,.945],[.935,.935],transform=fig.transFigure,color='#d9dfdf',lw=.7))
txt(.055,.86,'Finding Support',34,font=bold)
txt(.058,.82,'NYC’s homelessness services and nearby rail',15,font=sans)
txt(.945,.865,'21',33,font=sans,ha='right')
txt(.945,.837,'SERVICE–STATION CONNECTIONS',7,color=muted,ha='right')
ax=fig.add_axes([.045,.225,.91,.56],facecolor=water)
def polygons(g):return g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
def draw(ax,extent):
 ax.set_facecolor(water)
 for f in context['features']:
  for poly in polygons(f['geometry']):
   ax.add_patch(Polygon([(x*C,y) for x,y,*_ in poly[0]],facecolor='#f0f0e9',edgecolor='#d7dfdf',lw=.4,zorder=1))
 for f in boroughs['features']:
  for poly in polygons(f['geometry']):
   ax.add_patch(Polygon([(x*C,y) for x,y,*_ in poly[0]],facecolor='#fffefa',edgecolor='#bbc8cc',lw=.5,zorder=2))
 ax.set(xlim=(extent[0]*C,extent[1]*C),ylim=extent[2:],aspect='equal')
 ax.set_xticks([]);ax.set_yticks([])
 for spine in ax.spines.values():spine.set_visible(False)
 for r in rows:
  st=r['nearest_station'];color=colors[r['type']]
  ax.plot([st['lon']*C,r['lon']*C],[st['lat'],r['lat']],color=color,lw=1.3,zorder=6,solid_capstyle='round')
  ax.scatter([st['lon']*C],[st['lat']],s=12,facecolors=paper,edgecolors='#697a7c',linewidths=.6,zorder=7)
  ax.scatter([r['lon']*C],[r['lat']],s=12,c=color,edgecolors='white',linewidths=.5,zorder=8)
draw(ax,[-74.265,-73.69,40.49,40.90])
for name,x,y in [('BRONX',-73.871,40.868),('QUEENS',-73.803,40.755),('BROOKLYN',-73.954,40.63),('STATEN ISLAND',-74.151,40.56)]:
 ax.text(x*C,y,name,fontproperties=bold,fontsize=8,color='#87969d',ha='center',zorder=5)
ax.text(-73.982*C,40.779,'MANHATTAN',fontproperties=bold,fontsize=7,color='#87969d',rotation=59,ha='center',zorder=5)
ax.text(-74.055*C,40.65,'Upper Bay',fontproperties=italic,fontsize=10,color='#9caeb7',ha='center',zorder=4)
ax.text(-73.844*C,40.59,'Jamaica Bay',fontproperties=italic,fontsize=10,color='#9caeb7',ha='center',zorder=4)
ax.text(-74.21*C,40.76,'NEW JERSEY',fontproperties=sans,fontsize=7,color='#afb6b5',ha='center')
ax.annotate('N',xy=(-73.718*C,40.882),xytext=(-73.718*C,40.853),ha='center',fontsize=8,color=ink,fontproperties=sans,arrowprops={'arrowstyle':'->','color':ink,'lw':.7})
# Five-kilometre scale based on the local equirectangular projection.
x0,y0=-74.21*C,40.515;length=5/111.32
ax.plot([x0,x0+length],[y0,y0],color='#82949d',lw=1.1,zorder=9)
ax.text(x0,y0-.008,'0',fontsize=6,fontproperties=sans,color=muted)
ax.text(x0+length,y0-.008,'5 km',ha='right',fontsize=6,fontproperties=sans,color=muted)
# Inset retains geographic positions; labels are displaced for legibility.
inset=fig.add_axes([.068,.565,.226,.19],facecolor=water)
draw(inset,[-74.014,-73.976,40.717,40.772])
for sp in inset.spines.values():sp.set_visible(True);sp.set_edgecolor('#aab9c0');sp.set_linewidth(.7)
inset.set_title('MANHATTAN / NEAREST RAIL',fontsize=6,color=muted,fontproperties=bold,pad=6)
for r in rows:
 if r['borough']=='Manhattan' and r['lat']<40.78:
  n=r['number'];offset={'09':(10,8),'12':(-18,-9),'15':(-20,0),'04':(-17,6),'03':(-18,2),'14':(9,-4),'01':(9,1)}.get(n,(8,0))
  inset.annotate(n,xy=(r['lon']*C,r['lat']),xytext=offset,textcoords='offset points',fontproperties=bold,fontsize=6,color=colors[r['type']],arrowprops={'arrowstyle':'-','lw':.5,'color':colors[r['type']]},zorder=10)
ax.annotate('Project Hospitality — Youth\n≈4.8 km to Tompkinsville (SIR)',xy=(-74.104*C,40.638),xytext=(-74.218*C,40.678),fontsize=6.5,fontproperties=sans,color='#5c7475',linespacing=1.6,arrowprops={'arrowstyle':'-','color':'#8fa4a7','lw':.6},zorder=11)
fig.add_artist(plt.Line2D([.055,.945],[.206,.206],transform=fig.transFigure,color='#d9dfdf',lw=.7))
for x,kind,title,count,desc in [(.06,'adult','Adult drop-in','08','Basic services and housing referrals'),(.365,'intake','Shelter intake','05','Shelter applications by household type'),(.67,'youth','Youth drop-in','08','Support and referrals for ages 14–24')]:
 txt(x,.168,count,23,font=sans,color=colors[kind]);txt(x+.049,.177,title,11,font=bold)
 txt(x,.142,desc,7.2,color=muted)
txt(.058,.108,'Each line joins a service address to its nearest subway or Staten Island Railway station.',8,color='#69777b')
txt(.058,.073,'Straight-line proximity, not a walking route. Bus service, entrances and step-free access are not modeled.',6.8,color=muted)
txt(.058,.058,'Sources: NYC311, ACCESS NYC, NYC DYCD, MTA stations. Snapshot: 02 Nov 2026. Address points: U.S. Census (approximate).',6,color=muted)
txt(.058,.043,'Filled endpoint: service. Open endpoint: station centroid. Boroughs: NYC DCP. Land: Natural Earth. Local equirectangular projection.',6,color=muted)
txt(.945,.023,'THOMAS HAGOS  /  #30DAYMAPCHALLENGE',6.5,color=ink,ha='right')
out=ROOT/'dist/finding-support-poster.png';fig.savefig(out,dpi=240,facecolor=paper);plt.close(fig)
print(out)
