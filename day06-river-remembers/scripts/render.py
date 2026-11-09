"""Original reference cartography paired with attributed, unwarped archival details."""
from pathlib import Path
import json,os
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import geopandas as gpd
from pyproj import Transformer
from PIL import Image
C=json.loads((R/'config.json').read_text());P=C['colors'];T=Transformer.from_crs(4326,C['projection'],always_xy=True)
F={k:FontProperties(fname=str(R/'fonts'/v)) for k,v in {'script':'calligraphy.ttf','serif':'serif.ttf','sans':'sans.ttf','bold':'bold.ttf'}.items()}
fig=plt.figure(figsize=C['figure_inches'],facecolor=P['paper'])
def text(x,y,s,size=12,font='sans',color=None,**kw):
 return fig.text(x,y,s,fontproperties=F[font],fontsize=size,color=color or P['ink'],**kw)
def rule(y,x0=.055,x1=.945):fig.add_artist(Line2D([x0,x1],[y,y],transform=fig.transFigure,color=P['line'],lw=.7))
text(.055,.961,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',9,'bold',P['muted']);text(.945,.961,'06  ·  VINTAGE',9,'bold',P['muted'],ha='right');rule(.946)
text(.5,.875,C['title'],78,'script',ha='center')
text(.5,.838,C['subtitle'],20,'serif',P['muted'],ha='center')
text(.5,.811,'A river moves. The bends it leaves behind still have a shape.',12,'serif',ha='center');rule(.789)
text(.055,.768,'01  /  READING THE LANDSCAPE',10,'bold')
text(.055,.747,'Helena area · Arkansas / Mississippi',11,'serif',P['muted'])
# Reference map is independently projected, never registered to the historical scan.
ax=fig.add_axes([.055,.225,.565,.5],facecolor=P['paper']);ax.set_aspect('equal');ax.axis('off')
r=gpd.read_file(R/'data/processed/reference.gpkg',layer='river-areas');l=gpd.read_file(R/'data/processed/reference.gpkg',layer='lakes')
r.plot(ax=ax,color=P['river'],edgecolor='none',zorder=2);l.plot(ax=ax,color=P['lake'],edgecolor='none',zorder=3)
x0,y0=T.transform(C['bounds_wgs84'][0],C['bounds_wgs84'][1]);x1,y1=T.transform(C['bounds_wgs84'][2],C['bounds_wgs84'][3]);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1)
# Light geographic grid, labeled in degrees; map coordinates and scale remain metric internally.
for lon in [-90.8,-90.6,-90.4]:
 pts=[T.transform(lon,v) for v in [34.24,34.60]];ax.plot(*zip(*pts),color=P['line'],lw=.35,alpha=.6,zorder=0)
for lat in [34.3,34.4,34.5,34.6]:
 pts=[T.transform(v,lat) for v in [-90.86,-90.40]];ax.plot(*zip(*pts),color=P['line'],lw=.35,alpha=.6,zorder=0)
for v in C['labels']:
 xy=T.transform(v['lon'],v['lat']);tx,ty=T.transform(v['text_lon'],v['text_lat'])
 ax.annotate(v['name'],xy=xy,xytext=(tx,ty),ha=v['align'],fontproperties=F['serif'],fontsize=16,color=P['ink'],arrowprops={'arrowstyle':'-','color':P['muted'],'lw':.6,'connectionstyle':'angle3'},zorder=8,path_effects=[pe.withStroke(linewidth=3,foreground=P['paper'])])
 if v['note']:ax.text(tx,ty-1300,v['note'],fontproperties=F['sans'],fontsize=8,color=P['muted'],zorder=8)
# River name stays in open space, with a leader to the mapped channel.
xy=T.transform(-90.595,34.49);tx,ty=T.transform(-90.815,34.535)
ax.annotate('Mississippi River',xy=xy,xytext=(tx,ty),fontsize=25,fontproperties=F['script'],color=P['river'],arrowprops={'arrowstyle':'-','lw':.6,'color':P['river']},zorder=8)
for s,lon,lat in [('A R K A N S A S',-90.77,34.484),('M I S S I S S I P P I',-90.52,34.36)]:
 ax.text(*T.transform(lon,lat),s,fontproperties=F['sans'],fontsize=8,color=P['muted'],ha='center')

# UTM grid-north pointer and measured miles (5 mi = 8046.72 m).
ax.annotate('',xy=(.94,.965),xytext=(.94,.89),xycoords='axes fraction',arrowprops={'arrowstyle':'-|>','lw':.8,'color':P['ink']});ax.text(.94,.975,'N',transform=ax.transAxes,ha='center',fontsize=18,fontproperties=F['serif'],color=P['ink'])
sx=x0+.65*(x1-x0);sy=y0+.065*(y1-y0);mile=1609.344
for i in range(5):ax.add_patch(Rectangle((sx+i*mile,sy),mile,220,facecolor=P['ink'] if i%2==0 else P['paper'],edgecolor=P['ink'],lw=.5))
ax.text(sx,sy+650,'0',fontsize=8,fontproperties=F['sans'],color=P['muted']);ax.text(sx+5*mile,sy+650,'5 miles',fontsize=8,ha='right',fontproperties=F['sans'],color=P['muted'])
# Side-by-side evidence, not a spatial overlay; source colors are unchanged.
text(.665,.768,'02  /  READING THE ARCHIVE',10,'bold');text(.665,.747,'Mississippi River Commission · 1938',11,'serif',P['muted'])
for name,bottom,label,caption in [('montezuma',.552,'Montezuma Bend / Moon Lake','Earlier banks wrap around the bend.'),('horseshoe',.327,'Horse-Shoe Cut-Off','The old loop is still visible in the survey.')]:
 a=fig.add_axes([.665,bottom,.28,.17]);a.imshow(Image.open(R/f'data/processed/archive-{name}.png'));a.axis('off')
 for spine in a.spines.values():spine.set_visible(True);spine.set_edgecolor(P['line'])
 text(.665,bottom-.012,label,13,'serif');text(.665,bottom-.031,caption,8,'sans',P['muted'])
# Source legend must retain its specific periods, not four invented single-year snapshots.
text(.665,.265,'SURVEY PERIODS IN THE ARCHIVE',8,'bold',P['muted'])
for i,(s,c) in enumerate([('1765  ·  Ross survey','#07a5c6'),('1820–1830  ·  Land Office surveys','#e77ca4'),('1881–1893  ·  River Commission','#a5bc5c'),('1930–1932  ·  River Commission','#e4c75a')]):
 y=.245-i*.019;fig.add_artist(Line2D([.665,.69],[y+.002,y+.002],transform=fig.transFigure,lw=5,color=c));text(.703,y,s,8.2)
text(.055,.205,'REFERENCE MAP',8,'bold',P['muted'])
for x,c,label in [(.055,P['river'],'River / stream areas'),(.29,P['lake'],'Lake / pond areas*')]:
 fig.add_artist(Rectangle((x,.180),.012,.009,transform=fig.transFigure,facecolor=c));text(x+.02,.179,label,9)
text(.055,.158,'USGS NHD · downloaded Nov. 8, 2026 · mixed source dates',8,'sans',P['muted'])
text(.055,.146,'*Lakes smaller than 7.4 acres are omitted.',7,'sans',P['muted'])
text(.665,.166,'Dashed pink: indeterminate 1820–1830 bankline.',7,'sans',P['muted'])
rule(.139)
text(.055,.121,'The loop outlasts the channel.',23,'serif')
text(.055,.103,'Moon Lake is an oxbow of the Mississippi. The lake keeps the curve\nof a former river bend; the river now follows a different path.',11,'serif',linespacing=1.5,va='top')
text(.665,.121,'HOW TO READ THIS',8,'bold',P['muted'])
text(.665,.108,'The left map uses USGS water geometry.\nThe right details come from one historical sheet.\nThey have different scales and orientations;\nno precise before-and-after alignment is claimed.',8.5,linespacing=1.5,va='top')
rule(.057)
text(.055,.041,'Reference: USGS National Hydrography Dataset · NAD83 / UTM 15N · grid north · locator: Natural Earth 1:50m',7,'sans',P['muted'])
text(.055,.026,'Archive: MRC, Early Stream Channels, Sheet 5 (Aug. 1938), scan: Michigan State University Libraries. Original colors retained.',7,'sans',P['muted'])
# Small geographic locator in a quiet corner of the reference map.
loc=fig.add_axes([.064,.661,.14,.083],facecolor=P['paper']);states=gpd.read_file(R/'data/processed/us-states.geojson').to_crs(5070);states.plot(ax=loc,facecolor='#e9dfc8',edgecolor=P['line'],lw=.25)
loc.set_xlim(-2200000,2500000);loc.set_ylim(200000,3100000);loc.axis('off');ll=Transformer.from_crs(4326,5070,always_xy=True);loc.plot(*ll.transform(-90.63,34.43),'o',ms=4,color=P['lake']);loc.text(.02,-.05,'LOWER MISSISSIPPI, USA',transform=loc.transAxes,fontsize=6,fontproperties=F['sans'],color=P['muted'])
(R/'outputs').mkdir(exist_ok=True);fig.savefig(R/'outputs/the-river-remembers.png',dpi=C['dpi'],facecolor=P['paper']);plt.close(fig)
# Dedicated square gallery composition; no unreadable full-poster reduction.
f,a=plt.subplots(figsize=(6,6));f.patch.set_facecolor(P['paper']);a.set_facecolor(P['paper']);r.plot(ax=a,color=P['river'],edgecolor='none');l.plot(ax=a,color=P['lake'],edgecolor='none');a.set_xlim(x0,x1);a.set_ylim(y0,y1);a.axis('off');a.set_position([.08,.10,.84,.65]);f.text(.5,.88,C['title'],ha='center',fontsize=35,fontproperties=F['script'],color=P['ink']);f.text(.5,.80,'DAY 06 · VINTAGE  /  THOMAS HAGOS',ha='center',fontsize=8,fontproperties=F['sans'],color=P['muted']);f.text(.5,.06,'Old bends along the Lower Mississippi',ha='center',fontsize=11,fontproperties=F['serif'],color=P['ink']);f.savefig(R/'outputs/06-thomas-hagos.png',dpi=100,facecolor=P['paper']);plt.close(f)
print('Rendered 4500 × 5400 poster and 600 × 600 thumbnail.')
