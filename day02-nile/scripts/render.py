"""Render a static Nile atlas from saved native river geometry."""
from pathlib import Path
import json,sys,math
import geopandas as gpd
import numpy as np
import os
os.environ.setdefault('MPLCONFIGDIR',str(ROOT_CACHE:=Path(__file__).resolve().parents[1]/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.font_manager import FontProperties
from matplotlib import patheffects as pe
from pyproj import Transformer,Geod
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/processed';O=ROOT/'outputs';O.mkdir(exist_ok=True)
CRS=json.loads((D/'validation.json').read_text())['projection'];T=Transformer.from_crs(4326,CRS,always_xy=True)
FONT=ROOT/'docs/fonts';sans=FontProperties(fname=str(FONT/'sans.ttf'));bold=FontProperties(fname=str(FONT/'bold.ttf'))
CONFIG=json.loads((ROOT/'config.json').read_text())
PAPER='#101e2b';INK='#f2eee2';MUTED='#a8b7c2';COLORS=CONFIG['colors']
WIDTH={int(k):v for k,v in CONFIG['width_points_by_strahler'].items()}
r=gpd.read_file(D/'rivers.gpkg').to_crs(CRS);basin=gpd.read_file(D/'basin.gpkg').to_crs(CRS);countries=gpd.read_file(D/'countries.gpkg').to_crs(CRS);lakes=gpd.read_file(D/'lakes.gpkg').to_crs(CRS)
fig=plt.figure(figsize=(12,16),facecolor=PAPER)
def txt(x,y,s,size=10,color=INK,font=sans,**kw):return fig.text(x,y,s,fontproperties=font,fontsize=size,color=color,**kw)
ax=fig.add_axes([.055,.155,.89,.67]);ax.set_facecolor(PAPER)
countries.plot(ax=ax,facecolor='#182b38',edgecolor='#304451',linewidth=.45,zorder=1)
basin.plot(ax=ax,facecolor='#293e4b',edgecolor='#405562',linewidth=.7,zorder=2)
lakes.plot(ax=ax,facecolor='#101e2b',edgecolor='#577582',linewidth=.4,zorder=5)
# Native line vertices are projected only; no smoothing, invented connectors or clipping.
for order in sorted(WIDTH):
 for system,color in COLORS.items():
  subset=r[(r.ORD_STRA==order)&(r.system==system)]
  segments=[np.asarray(line.coords)[:,:2] for geom in subset.geometry for line in (geom.geoms if geom.geom_type=='MultiLineString' else [geom])]
  if segments:ax.add_collection(LineCollection(segments,colors=color,linewidths=WIDTH[order],alpha=.72 if order<4 else .95,zorder=3+order*.05,capstyle='round'))
# Large channels cross generalized lake outlines: lake polygons sit above routing centerlines.
x0,y0=T.transform(20.7,-4.8);x1,y1=T.transform(41.5,32.7);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal');ax.axis('off')
HALO=[pe.withStroke(linewidth=3,foreground=PAPER,alpha=.92)]
def label(s,x,y,size=9,color=INK,rotation=0,ha='center',weight=False):
 xx,yy=T.transform(x,y);return ax.text(xx,yy,s,fontproperties=bold if weight else sans,fontsize=size,color=color,rotation=rotation,ha=ha,zorder=10,path_effects=HALO)
for s,x,y,size in [('EGYPT',27.2,27,11),('SUDAN',27.1,18.1,12),('SOUTH SUDAN',27.6,7.5,10),('ETHIOPIA',39.1,8,10),('ERITREA',39,16.4,7),('UGANDA',30.5,1.3,8),('KENYA',37.2,.8,8),('TANZANIA',34.5,-3.5,8),('DR CONGO',25.8,1,8),('RWANDA',28.1,-1.9,6),('BURUNDI',28.1,-3,6)]:label(s,x,y,size,color='#a8b7c2')
for s,x,y,rotation,color in [('Nile',31.1,25.3,80,COLORS['Main Nile / other connected tributaries']),('White Nile',31.1,12.4,85,COLORS['White Nile system']),('Blue Nile',35.8,12.7,-44,COLORS['Blue Nile system']),('Atbara',36.9,16.6,-38,COLORS['Atbara system']),('Bahr el Ghazal',26.6,8.7,10,COLORS['White Nile system']),('Sobat',33.9,9,15,COLORS['White Nile system'])]:label(s,x,y,9,color,rotation)
for s,x,y,dx,dy in [('Khartoum',32.53,15.60,12,-4),('Cairo',31.24,30.04,12,0),('Juba',31.6,4.85,-12,-8)]:
 xx,yy=T.transform(x,y);ax.scatter([xx],[yy],s=12,c=INK,edgecolors=PAPER,linewidths=.7,zorder=12);ax.annotate(s,(xx,yy),xytext=(dx,dy),textcoords='offset points',ha='left' if dx>0 else 'right',fontsize=9,fontproperties=bold,color=INK,zorder=12,path_effects=HALO)
# Leader lines keep displaced lake names tied to the correct waterbody.
for s,tx,ty,lx,ly in [('Lake Victoria',33,-1.4,35.8,-1.7),('Lake Albert',30.75,1.7,27.8,2.1),('Lake Tana',37.3,12.0,39.2,12.2),('Lake Nasser',32.6,22.7,28.8,23.4)]:
 ax.annotate(s,xy=T.transform(tx,ty),xytext=T.transform(lx,ly),ha='center',fontproperties=sans,fontsize=7,color='#a8b7c2',zorder=10,path_effects=HALO,arrowprops={'arrowstyle':'-','color':'#708c9c','lw':.45,'shrinkA':4,'shrinkB':2})
label('MEDITERRANEAN SEA',31,32.0,8,color='#a8b7c2');label('RED SEA',38.9,23,8,color='#a8b7c2',rotation=-65)
# Geodesic 300-mile scale at 6°N, projected into the map CRS.
geod=Geod(ellps='WGS84');sx,sy=22.6,3.6;ex,ey,_=geod.fwd(sx,sy,90,300*1609.344);xx,yy=T.transform([sx,ex],[sy,ey]);ax.plot(xx,yy,color=INK,lw=1,zorder=12);ax.text(xx[0],yy[0]+45000,'0',fontsize=7,fontproperties=sans,color=MUTED);ax.text(xx[1],yy[1]+45000,'300 miles',ha='right',fontsize=7,fontproperties=sans,color=MUTED)
# Page typography and explanatory text outside the geographic field.
txt(.065,.951,'02  /  LINES',11,font=bold,color='#ffbf69')
txt(.935,.951,'THOMAS HAGOS',9,ha='right')
fig.add_artist(plt.Line2D([.065,.935],[.935,.935],transform=fig.transFigure,color='#304451',lw=.7))
txt(.065,.89,'THE NILE, CONNECTED',36,font=bold)
txt(.068,.858,'One basin, many tributaries.',17,color=MUTED)
txt(.068,.835,'133,797 connected river reaches  /  Nile drainage basin',11,color='#ffbf69')
# Use quiet space west of the river above the dense southern network.
txt(.08,.728,'READING THE NETWORK',8,font=bold,color=MUTED)
for i,(key,name) in enumerate([('White Nile system','White Nile system'),('Blue Nile system','Blue Nile system'),('Atbara system','Atbara system'),('Main Nile / other connected tributaries','Main Nile & other tributaries')]):
 yy=.702-i*.021;fig.add_artist(plt.Line2D([.08,.111],[yy+.003,yy+.003],transform=fig.transFigure,color=COLORS[key],lw=1.6));txt(.121,yy,name,8)
txt(.08,.592,'Colors follow upstream connections,',8,color=MUTED);txt(.08,.578,'not national borders.',8,color=MUTED)
for order,x in [(1,.08),(4,.13),(8,.18)]:
 fig.add_artist(plt.Line2D([x,x+.027],[.55,.55],transform=fig.transFigure,color=INK,lw=WIDTH[order]));txt(x,.535,str(order),7,color=MUTED)
txt(.08,.516,'Line width: Strahler stream order',8,color=MUTED)
txt(.08,.502,'Higher order → thicker line',8,color=MUTED)
txt(.08,.477,'Modeled drainage lines; not all',8,color=MUTED)
txt(.08,.463,'channels carry water year-round.',8,color=MUTED)
# Continental locator uses the complete Africa features from the same source archive.
locator_crs='+proj=laea +lat_0=0 +lon_0=20 +datum=WGS84 +units=m +no_defs'
africa=gpd.read_file(ROOT/'data/raw/countries.zip')
africa=africa[africa.CONTINENT=='Africa'].to_crs(locator_crs)
locator=fig.add_axes([.065,.205,.195,.205],facecolor=PAPER)
africa.plot(ax=locator,facecolor='#293e4b',edgecolor='#405562',linewidth=.3,zorder=1)
basin.to_crs(locator_crs).plot(ax=locator,facecolor='#ffbf69',edgecolor='#ffe7a3',linewidth=.35,zorder=2)
locator.set_aspect('equal');locator.axis('off')
txt(.08,.433,'AFRICA',9,font=bold,color=INK)
txt(.08,.192,'Highlighted: Nile drainage basin',7.5,color=MUTED)
# Geographic narrative is explicit about multiple headwater regions, not one invented source.
txt(.735,.785,'TO THE MEDITERRANEAN',7,font=bold,color='#ffbf69')
txt(.735,.770,'The Nile flows north through',7.5,color=MUTED)
txt(.735,.757,'Egypt to its delta and the sea.',7.5,color=MUTED)
txt(.735,.738,'Source data retains one outlet;',7,color=MUTED)
txt(.735,.725,'not every delta branch is mapped.',7,color=MUTED)
# Leader ties the outlet note to the source network’s actual downstream endpoint.
outlet=r[r.NEXT_DOWN==0].geometry.iloc[0];outlet_xy=tuple(outlet.coords[-1][:2])
ax.annotate('',xy=outlet_xy,xycoords='data',xytext=(.735,.79),textcoords=fig.transFigure,arrowprops={'arrowstyle':'-','color':'#708c9c','lw':.65,'shrinkB':3},zorder=12)
# Headwater labels retain the existing lake leaders and add explanatory regions.
txt(.745,.345,'ETHIOPIAN HIGHLANDS',7,font=bold,color=COLORS['Blue Nile system'])
txt(.745,.331,'Blue Nile from Lake Tana',7.5,color=MUTED)
ax.annotate('',xy=T.transform(37.3,12.0),xytext=(.745,.35),textcoords=fig.transFigure,arrowprops={'arrowstyle':'-','color':COLORS['Blue Nile system'],'lw':.65,'shrinkB':3},zorder=12)
txt(.745,.235,'EQUATORIAL HEADWATERS',7,font=bold,color=COLORS['White Nile system'])
txt(.745,.221,'Rivers feeding Lake Victoria,',7.5,color=MUTED)
txt(.745,.208,'including Rwanda and Burundi',7.5,color=MUTED)
ax.annotate('',xy=T.transform(29.9,-2.4),xytext=(.745,.24),textcoords=fig.transFigure,arrowprops={'arrowstyle':'-','color':COLORS['White Nile system'],'lw':.65,'shrinkB':3},zorder=12)
fig.add_artist(plt.Line2D([.065,.935],[.138,.138],transform=fig.transFigure,color='#304451',lw=.7))
report=json.loads((D/'validation.json').read_text());n=report['connected_reaches']
txt(.068,.115,f'{n:,} connected river reaches',14,font=bold,color='#ffbf69')
txt(.068,.096,'Selected by downstream connectivity within HydroBASINS’ Nile basin (level 2, code 17).',8,color=MUTED)
txt(.068,.080,'Smaller streams below source thresholds and disconnected inland networks are excluded. Lake crossings are modeled routing.',7,color=MUTED)
txt(.068,.064,'HydroRIVERS v1.0 & HydroBASINS v1.c © WWF; accessed via UNESCO IHP-WINS. Context: Natural Earth.',7,color=MUTED)
txt(.068,.049,'Sources: Lehner & Grill (2013), hydrosheds.org. Projection: Lambert azimuthal equal-area, 32°E / 14°N.',7,color=MUTED)
txt(.068,.034,'Not a current-flow, navigation or water-allocation map. Boundaries are contextual. Data downloaded 03 Nov 2026.',7,color=MUTED)
draft='--draft' in sys.argv;out=O/('nile-geographic-draft.png' if draft else 'nile-connected.png');fig.savefig(out,dpi=120 if draft else 300,facecolor=PAPER);plt.close(fig);print(out)
