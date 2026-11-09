"""Two States. One Agency. — the NY–NJ state line down the Hudson, and the five agency crossings stitched across it."""
from pathlib import Path
import json,os
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib import patheffects as pe
from PIL import Image
import numpy as np
from pyproj import Transformer
import geopandas as gpd
OUT=R/'outputs';OUT.mkdir(exist_ok=True);T=Transformer.from_crs(4326,26918,always_xy=True)
PA=json.loads((R/'data/port-authority.json').read_text())
serif=FontProperties(fname=str(R/'fonts/serif.ttf'));sans=FontProperties(fname=str(R/'fonts/sans.ttf'))
def ft(fig,x,y,s,size=10,col='#2b2520',font=sans,**kw):return fig.text(x,y,s,color=col,fontproperties=font,fontsize=size,**kw)

def text_on_curve(ax,text,curve,fontsize=12,color='#2b2520',font=serif,tracking=1.2):
 """Place glyphs at true display-space arc lengths; rotate each to the local tangent.

 `curve` is an Nx2 sequence in the map's projected units. Tracking is in points.
 No geometry, font size or aspect ratio is changed by this helper.
 """
 ax.figure.canvas.draw();xy=ax.transData.transform(np.asarray(curve));seg=np.linalg.norm(np.diff(xy,axis=0),axis=1);arc=np.r_[0,np.cumsum(seg)];pt=ax.figure.dpi/72
 widths=[]
 for ch in text:
  w=TextPath((0,0),ch if ch!=' ' else 'n',size=fontsize,prop=font).get_extents().width
  widths.append((w if ch!=' ' else w*.6)*pt+tracking*pt)
 assert sum(widths)<arc[-1], 'Water label does not fit its saved curve.'
 cursor=(arc[-1]-sum(widths))/2;artists=[]
 for ch,w in zip(text,widths):
  d=cursor+w/2;k=min(max(np.searchsorted(arc,d)-1,0),len(seg)-1);f=(d-arc[k])/max(seg[k],1e-9);pos=xy[k]*(1-f)+xy[k+1]*f;rot=np.degrees(np.arctan2(*(xy[k+1]-xy[k])[::-1]));data=ax.transData.inverted().transform(pos)
  if ch!=' ':artists.append(ax.text(*data,ch,rotation=rot,rotation_mode='anchor',ha='center',va='center',fontproperties=font,fontsize=fontsize,color=color,zorder=6))
  cursor+=w
 return artists

# Ink on paper: one warm sheet, sepia linework, vermilion stitches, IM FELL lettering.
PAPER='#f4eddd';WATER='#e6dfcd';INK='#2b2520';SEPIA='#7d6d5a';VERM='#b23a24'
script=FontProperties(fname=str(R/'fonts/serif-italic.ttf'))
FOCUS=PA['design']['focus_wgs84']
SHEETS={'landscape':{'year':27,'name':11.5,'lw':2.6,'off':380,'river':19,'side':11.5,'d':215},
        'phone':{'year':23,'name':12.5,'lw':3.0,'off':470,'river':19,'side':12,'d':280}}
# id, year in the hand, small name, the bank the label sits on
STITCHES=[('gwb','1931','George Washington Bridge','nj'),('lincoln','1937','Lincoln Tunnel','ny'),('holland','1927','Holland Tunnel · agency 1930','ny'),
 ('path-uptown','1908','PATH tubes · agency 1962','nj'),('path-downtown','1909','PATH tubes · agency 1962','nj')]
def mapped_crossings():return gpd.read_file(R/'data/processed/port-authority-crossings-mapped.geojson').to_crs(26918).set_index('id')
def along_line(line,lat0,lat1,shift=0,n=40):
 """Points on the state line between two latitudes, south to north, shifted sideways (+ west/NJ, - east/NY) in metres."""
 from shapely.geometry import box as _box
 ya,yb=T.transform(-74,lat0)[1],T.transform(-74,lat1)[1];part=line.intersection(_box(line.bounds[0]-1e4,ya,line.bounds[2]+1e4,yb))
 if part.geom_type!='LineString':from shapely.ops import linemerge;part=linemerge(part)
 c=np.asarray(part.coords)
 if c[0,1]>c[-1,1]:part=type(part)(c[::-1])
 p=np.array([part.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,n)]);g=np.gradient(p,axis=0);g/=np.linalg.norm(g,axis=1)[:,None]
 return p+shift*np.c_[-g[:,1],g[:,0]]
def draw_pa_map(ax,sheet='landscape'):
 """The Hudson as a seam: the state line down mid-river in a fine pen line, five vermilion stitches across it."""
 k=SHEETS[sheet];x0,y0=T.transform(FOCUS[0],FOCUS[1]);x1,y1=T.transform(FOCUS[2],FOCUS[3])
 if sheet=='phone':c=(x0+x1)/2;x0,x1=c-11000,c+11000  # phone frame is near-square: widen, never crop the river
 ax.set_facecolor(WATER);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
 for sp in ax.spines.values():sp.set_color(INK);sp.set_linewidth(.8)
 from shapely.geometry import box as _box
 land=gpd.read_file(R/'data/processed/port-authority-land.geojson').to_crs(26918);frame=_box(x0-3000,y0-3000,x1+3000,y1+3000)
 L=land.geometry.union_all().intersection(frame)
 # Engraver's waterlines: the shore repeated outward, fading, as on old harbour charts.
 for d,a in [(110,.30),(240,.18),(400,.09)]:
  ring=gpd.GeoSeries([L.buffer(d,resolution=8).boundary]);ring.plot(ax=ax,color=INK,linewidth=.35,alpha=a,zorder=1)
 gpd.GeoSeries([L]).plot(ax=ax,color=PAPER,edgecolor=INK,linewidth=.55,zorder=2)
 sl=gpd.read_file(R/'data/processed/port-authority-state-line.geojson').to_crs(26918);line=sl.geometry.iloc[0]
 if line.geom_type=='MultiLineString':from shapely.ops import linemerge;line=linemerge(line)
 sl.plot(ax=ax,color=INK,linewidth=.8,linestyle=(0,(.5,2.4)),capstyle='round',alpha=.85,zorder=4)
 cx=mapped_crossings();mode={'bridge':'-','tunnel':(0,(2.4,1.3)),'rail':(0,(.6,1.3))};labels=[]
 halo=[pe.withStroke(linewidth=3.2,foreground=PAPER)]
 for ident,year,name,side in STITCHES:
  row=cx.loc[ident];xs,ys=row.geometry.xy
  ax.plot(xs,ys,color=WATER,lw=k['lw']+2.4,solid_capstyle='round',zorder=7);ax.plot(xs,ys,color=VERM,lw=k['lw'],ls=mode[row['mode']],solid_capstyle='butt',dash_capstyle='round',zorder=8);ax.scatter(xs,ys,s=k['lw']*6,color=VERM,ec=PAPER,lw=.5,zorder=9)
  i=-1 if side=='ny' else 0;px,py=row.geometry.coords[i];d=k['off'] if side=='ny' else -k['off'];ha='left' if side=='ny' else 'right'
  labels.append(ax.text(px+d,py+40,year,ha=ha,va='bottom',fontproperties=script,fontsize=k['year'],color=VERM,zorder=11,path_effects=halo))
  labels.append(ax.text(px+d,py-80,name,ha=ha,va='top',fontproperties=serif,fontsize=k['name'],color=INK,zorder=11,path_effects=halo))
 ax.figure.canvas.draw()
 # The river carries its own lettering; the two states are written on either side of the line.
 water=text_on_curve(ax,'Hudson River',along_line(line,40.800,40.846),fontsize=k['river'],color=INK,font=script,tracking=.9)
 for q in water:q.set_path_effects([pe.withStroke(linewidth=4,foreground=WATER)]);q.set_alpha(.85)
 for txt,s in [('New Jersey',k['d']),('New York',-k['d'])]:
  water+=text_on_curve(ax,txt,along_line(line,40.766,40.796,s),fontsize=k['side'],color=INK,font=script,tracking=.5)
 sx,sy=T.transform(FOCUS[0]+.012,40.697) if sheet=='landscape' else (x0+900,T.transform(-74,40.697)[1]);length=1609.344
 ax.plot([sx,sx+length],[sy,sy],color=INK,lw=.8,zorder=6);[ax.plot([xx,xx],[sy-90,sy+90],color=INK,lw=.8,zorder=6) for xx in (sx,sx+length)]
 ax.text(sx+length/2,sy+220,'one mile',ha='center',fontproperties=script,fontsize=k['side'],color=INK,zorder=6,path_effects=halo)
 ax.annotate('',xy=(.955,.975),xytext=(.955,.925),xycoords='axes fraction',arrowprops=dict(arrowstyle='-|>,head_width=.25,head_length=.6',color=INK,lw=.7))
 ax.text(.955,.915,'N',transform=ax.transAxes,ha='center',va='top',fontproperties=serif,fontsize=k['name'],color=INK)
 ax.add_patch(Rectangle((-.012,-.009),1.024,1.018,transform=ax.transAxes,fill=False,ec=INK,lw=.4,clip_on=False))
 return labels,water


def record_layout(fig,labels,edition):
 """Record named-label and figure-text bounds for reproducible collision checks."""
 fig.canvas.draw();renderer=fig.canvas.get_renderer();inv=fig.transFigure.inverted();records=[]
 for q in list(fig.texts)+labels:
  if not q.get_text().strip():continue
  b=q.get_window_extent(renderer).transformed(inv);records.append({'text':q.get_text(),'bounds':[b.x0,b.y0,b.x1,b.y1]})
 overlaps=[]
 for i,a in enumerate(records):
  x0,y0,x1,y1=a['bounds']
  for b in records[i+1:]:
   u0,v0,u1,v1=b['bounds']
   if min(x1,u1)>max(x0,u0)+.0001 and min(y1,v1)>max(y0,v0)+.0001:overlaps.append([a['text'],b['text']])
 return {'edition':edition,'labels':records,'overlapping_text':overlaps,'all_text_inside_canvas':all(0<=v['bounds'][0]<v['bounds'][2]<=1 and 0<=v['bounds'][1]<v['bounds'][3]<=1 for v in records)}

# Landscape sheet: ink on paper. The argument on the left, the seam on the right. Nothing else.
fig=plt.figure(figsize=(14,12),facecolor=PAPER)
ft(fig,.055,.955,'THOMAS HAGOS  ·  30-DAY MAP CHALLENGE 2026',7.5,SEPIA,sans);ft(fig,.945,.955,'DAY 12  ·  POWER',7.5,SEPIA,sans,ha='right')
ft(fig,.053,.885,'Seeing the Hudson',38,INK,serif);ft(fig,.056,.853,'the power to join two shores',15,SEPIA,script)
fig.add_artist(plt.Line2D([.056,.11],[.828,.828],transform=fig.transFigure,color=INK,lw=.6))
ft(fig,.050,.680,'1921',96,VERM,script)
ft(fig,.056,.565,'Two states.\nOne agency.',34,INK,script,linespacing=1.1)
ft(fig,.056,.400,'The line between New York and\nNew Jersey runs down the middle\nof the Hudson. In 1921 the two states\nmade one agency to share the port.\nIt built or took over every\ncrossing stitched here.',13.5,INK,serif,linespacing=1.5)
y=.300
for lab,ls in [('a bridge, over the river','-'),('a road tunnel, under it',(0,(2.4,1.3))),('the PATH train tubes',(0,(.6,1.3)))]:
 fig.add_artist(plt.Line2D([.056,.09],[y,y],transform=fig.transFigure,color=VERM,lw=2.2,ls=ls,dash_capstyle='round'));ft(fig,.102,y-.005,lab,12,INK,script);y-=.028
fig.add_artist(plt.Line2D([.056,.09],[y,y],transform=fig.transFigure,color=INK,lw=.9,ls=(0,(.5,2.4)),dash_capstyle='round'));ft(fig,.102,y-.005,'the state line',12,INK,script)
a=fig.add_axes([.375,.075,.55,.775]);labels,water=draw_pa_map(a,'landscape')
ft(fig,.055,.030,'Five agency crossings of the Hudson, drawn schematically bank to bank; anchors approximate; years are opening dates.  Land: U.S. Census 2024 counties (1:500k) minus TIGER/Line water · State line: TIGER/Line 2024 · EPSG:26918.',6.8,SEPIA,sans)
ft(fig,.055,.016,'Lettering: IM FELL English, Igino Marini (SIL OFL).',6.8,SEPIA,sans);ft(fig,.945,.016,'#30DayMapChallenge  ·  #teamMUSA',7,SEPIA,sans,ha='right')
layout=[record_layout(fig,labels,'landscape')];fig.savefig(OUT/'two-states-one-agency.png',dpi=250,facecolor=PAPER);plt.close(fig)
# Phone edition: the same seam, larger.
f=plt.figure(figsize=(8,10),facecolor=PAPER);ft(f,.06,.955,'Seeing the Hudson',28,INK,serif);ft(f,.062,.928,'the power to join two shores  ·  Day 12, Power',12,SEPIA,script)
ft(f,.055,.835,'1921',58,VERM,script);ft(f,.42,.872,'Two states.',25,INK,script);ft(f,.42,.836,'One agency.',25,INK,script)
m=f.add_axes([.035,.095,.93,.715]);mobile_labels,_=draw_pa_map(m,'phone')
ft(f,.06,.058,'Vermilion: Hudson crossings built or run by the Port Authority. Dotted: the state line.',11,INK,script)
ft(f,.06,.030,'Census 2024 land and water · EPSG:26918 · IM FELL English (OFL) · Thomas Hagos',6.8,SEPIA,sans)
layout.append(record_layout(f,mobile_labels,'phone'));f.savefig(OUT/'two-states-one-agency-phone.png',dpi=200,facecolor=PAPER);plt.close(f);(R/'docs/layout.json').write_text(json.dumps(layout,indent=2))
print('Rendered Two States. One Agency.')

# 600 × 600 gallery thumbnail: the stitched lower Hudson, cut from the landscape sheet.
Image.open(OUT/'two-states-one-agency.png').convert('RGB').crop((1400,1100,2950,2650)).resize((600,600),Image.LANCZOS).save(OUT/'12-thomas-hagos.png',optimize=True)
