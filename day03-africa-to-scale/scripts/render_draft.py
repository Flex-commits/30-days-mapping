from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.path import Path as MPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import shape
from PIL import Image
BG='#101e2b';FG='#f2eee2';MUTED='#a8b7c2';COL={'CHN':'#ffe7a3','USA48':'#ffe7a3','IND':'#ffbf69','DEU':'#f08063','JPN':'#75acb9'}
def draw(ax,g,fc,ec,lw,z):
 for p in g.geoms if hasattr(g,'geoms') else [g]:
  vertices=[];codes=[]
  for ring in [p.exterior,*p.interiors]:
   c=list(ring.coords);vertices.extend(c);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(c)-2)+[MPath.CLOSEPOLY])
  ax.add_patch(PathPatch(MPath(vertices,codes),facecolor=fc,edgecolor=ec,lw=lw,zorder=z))
def main():
 D=R/'data/processed';v=json.loads((D/'draft-validation.json').read_text());f=json.loads((D/'layout.geojson').read_text())['features'];geos={p['properties']['id']:shape(p['geometry']) for p in f};areas={x['id']:x for x in json.loads((D/'area-preparation.json').read_text())};font=R/'docs/fonts';sans=FontProperties(fname=str(font/'sans.ttf'));bold=FontProperties(fname=str(font/'bold.ttf'))
 fig=plt.figure(figsize=(12,14),facecolor=BG)
 def tx(x,y,s,size=10,c=FG,b=False,**kw):fig.text(x,y,s,fontproperties=bold if b else sans,fontsize=size,color=c,**kw)
 tx(.06,.957,'03 / POLYGONS  ·  GEOGRAPHIC DRAFT',10,'#ffbf69',True);tx(.94,.957,'THOMAS HAGOS',9,ha='right');tx(.06,.905,'AFRICA, TO SCALE',36,b=True);tx(.06,.874,'Real country outlines. One consistent area scale.',14,MUTED)
 tx(.06,.844,f"{v['share_percent']:.1f}% represented by this selection · not a perfect fill",10,'#ffbf69')
 ax=fig.add_axes([.05,.19,.90,.63]);ax.set_facecolor(BG);af=geos['AFR'];draw(ax,af,'#293e4b',FG,.85,1)
 for k in v['selected']:
  g=geos[k];draw(ax,g,COL[k],BG,.65,3);main=max(g.geoms,key=lambda p:p.area) if hasattr(g,'geoms') else g;p=main.representative_point();label=areas[k]['label']
  if k in ['CHN','USA48','IND']:
   label=label.replace('Contiguous United States','CONTIGUOUS\nUNITED STATES').upper();ax.text(p.x,p.y,label,fontproperties=bold,fontsize=12 if k=='IND' else 14,ha='center',va='center',color=BG,zorder=8)
  else:ax.annotate(label,(p.x,p.y),xytext=(-40,20) if k=='DEU' else (25,10),textcoords='offset points',fontproperties=bold,fontsize=9,color=FG,zorder=9,arrowprops={'arrowstyle':'-','color':FG,'lw':.6})
 x0,y0,x1,y1=af.bounds;ax.set(xlim=(x0-250000,x1+250000),ylim=(y0-200000,y1+200000),aspect='equal');ax.axis('off')
 # Draft key uses calculated geometry areas, not published figures.
 n=len(v['selected']);positions=[.06+i*.88/n for i in range(n)]
 for x,k in zip(positions,v['selected']):
  fig.add_artist(Rectangle((x,.157),.013,.012,transform=fig.transFigure,facecolor=COL[k],edgecolor=FG,lw=.35));tx(x+.021,.159,areas[k]['label'],8,b=True);tx(x+.021,.140,f"{areas[k]['geodesic_area_km2']/1e6:.2f} million km²",8,MUTED)
 tx(.06,.112,f"Africa: {v['africa_km2']/1e6:.2f} million km²  /  Remaining comparison area: {v['remaining_comparison_area_km2']/1e6:.2f} million km²",9,'#ffbf69')
 tx(.06,.086,'Country shapes repositioned and rotated; geodesic polygon areas preserved.',8.5)
 tx(.06,.065,'Locally centered WGS84 equal-area shapes; rigid placements. Natural Earth 1:50m, v5.1.1. No overlap or clipping.',7.5,MUTED)
 tx(.06,.045,'Africa uses source African-region units + Mayotte/Réunion, including Madagascar and listed remote islands. Surface polygons, not a dry-land mask.',6.8,MUTED)
 tx(.06,.026,'Unoccupied comparison area is not “empty” African land. First feasibility draft; country selection and geographic definitions remain for review.',7,MUTED)
 fig.savefig(R/'outputs/africa-geographic-draft.png',dpi=220,facecolor=BG);plt.close(fig)
 im=Image.open(R/'outputs/africa-geographic-draft.png');im.thumbnail((1500,1700));im.save(R/'outputs/africa-geographic-draft-preview.png')
 print('Rendered real-outline geographic draft.')
if __name__=='__main__':main()
