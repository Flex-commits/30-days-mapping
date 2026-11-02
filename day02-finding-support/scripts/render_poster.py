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
txt(.058,.82,'How far are NYC’s homelessness service access points from rail?',12.5,font=sans)
txt(.945,.865,'21',33,font=sans,ha='right')
txt(.945,.837,'SERVICE–STATION CONNECTIONS',7,color=muted,ha='right')
ax=fig.add_axes([.055,.55,.38,.23],facecolor=water)
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
ax.set_title('CITYWIDE CONTEXT',fontsize=7,color=muted,fontproperties=bold,pad=8)
# Each panel retains geography; extents follow all service–station pairs in that borough.
for i,borough in enumerate(['Manhattan','Bronx','Brooklyn']):
 local=fig.add_axes([.055+i*.303,.245,.283,.265],facecolor=water)
 rr=[r for r in rows if r['borough']==borough]
 xs=[x for r in rr for x in [r['lon'],r['nearest_station']['lon']]]
 ys=[y for r in rr for y in [r['lat'],r['nearest_station']['lat']]]
 draw(local,[min(xs)-.006,max(xs)+.006,min(ys)-.006,max(ys)+.006])
 local.set_anchor('N')
 local.set_title(borough.upper(),fontproperties=bold,fontsize=9,color=ink,pad=10)
 # Half-mile scale shared in units, with each view fitted independently.
 x0=local.get_xlim()[0]+.003;y0=local.get_ylim()[0]+.003;length=.5*1.609344/111.32
 local.plot([x0,x0+length],[y0,y0],color='#697d83',lw=1)
 local.text(x0,y0+.002,'0.5 mi',fontproperties=sans,fontsize=6,color=muted)
txt(.49,.755,'THE LONGEST RAIL CONNECTION',7,color=muted,font=bold)
txt(.49,.72,'Port Richmond → Tompkinsville',14,font=bold)
txt(.49,.68,'2.99 miles',25,color=colors['youth'])
txt(.49,.643,'Project Hospitality’s youth drop-in center to the nearest',8,color='#69777b')
txt(.49,.626,'rail station, measured in a straight line.',8,color='#69777b')
txt(.49,.594,'Bus and ferry options are outside this analysis.',8,color='#69777b')
txt(.49,.577,'Rail distance alone does not describe overall transit access.',8,color='#69777b')
fig.add_artist(plt.Line2D([.055,.945],[.206,.206],transform=fig.transFigure,color='#d9dfdf',lw=.7))
for x,kind,title,count,desc in [(.06,'adult','Adult drop-in','08','Basic services and housing referrals'),(.365,'intake','Shelter intake','05','Shelter applications by household type'),(.67,'youth','Youth drop-in','08','Support and referrals for ages 14–24')]:
 txt(x,.168,count,23,font=sans,color=colors[kind]);txt(x+.049,.177,title,11,font=bold)
 txt(x,.142,desc,7.2,color=muted)
txt(.058,.108,'Each line joins a service address to its nearest subway or Staten Island Railway station.',8,color='#69777b')
txt(.058,.073,'Straight-line proximity, not a walking route. Bus and ferry service, entrances and step-free access are not modeled.',6.8,color=muted)
txt(.058,.058,'Sources: NYC311, ACCESS NYC, NYC DYCD, MTA stations. Snapshot: 02 Nov 2026. Address points: U.S. Census (approximate).',6,color=muted)
txt(.058,.043,'Filled endpoint: service. Open endpoint: station centroid. Boroughs: NYC DCP. Land: Natural Earth. Local equirectangular projection.',6,color=muted)
txt(.945,.023,'THOMAS HAGOS  /  #30DAYMAPCHALLENGE',6.5,color=ink,ha='right')
out=ROOT/'dist/finding-support-poster.png';fig.savefig(out,dpi=240,facecolor=paper);plt.close(fig)
print(out)
