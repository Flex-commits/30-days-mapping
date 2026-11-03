"""Create a dedicated 600 × 600 gallery composition from the rendered map."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import os,io,json
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import geopandas as gpd
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'data/processed'
crs=json.loads((D/'validation.json').read_text())['projection'];r=gpd.read_file(D/'rivers.gpkg').to_crs(crs);b=gpd.read_file(D/'basin.gpkg').to_crs(crs);l=gpd.read_file(D/'lakes.gpkg').to_crs(crs)
fig,ax=plt.subplots(figsize=(3.15,5.35),dpi=150);fig.patch.set_facecolor('#101e2b');ax.set_facecolor('#101e2b');b.plot(ax=ax,color='#293e4b',edgecolor='#405562',linewidth=.3)
colors={'White Nile system':'#ffe7a3','Blue Nile system':'#ffb052','Atbara system':'#f65d40','Main Nile / other connected tributaries':'#c2d4df'}
for system,color in colors.items():
 rr=r[r.system==system];segments=[np.asarray(g.coords) for g in rr.geometry];widths=[.03+.025*o**1.5 for o in rr.ORD_STRA];ax.add_collection(LineCollection(segments,colors=color,linewidths=widths,alpha=.8))
l.plot(ax=ax,color='#101e2b',edgecolor='none',zorder=5);ax.set_aspect('equal');ax.axis('off');fig.subplots_adjust(left=.01,right=.99,bottom=.01,top=.99)
buf=io.BytesIO();fig.savefig(buf,format='png',facecolor='#101e2b',dpi=150);plt.close(fig);buf.seek(0);panel=Image.open(buf).convert('RGB');panel=panel.resize((315,535),Image.Resampling.LANCZOS)
out=Image.new('RGB',(600,600),'#101e2b');out.paste(panel,(282+(315-panel.width)//2,42));d=ImageDraw.Draw(out)
def text(x,y,s,size=14,color='#f2eee2',font='sans.ttf'):
 d.text((x,y),s,font=ImageFont.truetype(str(R/'docs/fonts'/font),size),fill=color)
text(30,34,'02 / LINES',12,color='#ffbf69',font='bold.ttf');d.line((30,66,245,66),fill='#304451')
text(30,108,'THE NILE,',29,font='bold.ttf');text(30,150,'CONNECTED',29,font='bold.ttf')
text(30,226,'One basin,',16);text(30,250,'many tributaries.',16)
for y,color,s in [(326,'#ffe7a3','White Nile system'),(360,'#ffb052','Blue Nile system'),(394,'#f65d40','Atbara system')]:
 d.line((30,y+7,53,y+7),fill=color,width=2);text(63,y,s,12)
# Tiny continental locator supports geographic recognition in the square gallery.
africa=gpd.read_file(R/'data/raw/countries.zip');africa=africa[africa.CONTINENT=='Africa'].to_crs('+proj=laea +lat_0=0 +lon_0=20 +datum=WGS84 +units=m +no_defs')
f,aa=plt.subplots(figsize=(1.1,1.15),dpi=150);f.patch.set_facecolor('#101e2b');aa.set_facecolor('#101e2b');africa.plot(ax=aa,color='#293e4b',edgecolor='#405562',linewidth=.15);b.to_crs(africa.crs).plot(ax=aa,color='#ffbf69',edgecolor='none');aa.axis('off');f.subplots_adjust(left=0,right=1,bottom=0,top=1);bb=io.BytesIO();f.savefig(bb,format='png',facecolor='#101e2b');plt.close(f);bb.seek(0);mini=Image.open(bb).convert('RGB').resize((110,115),Image.Resampling.LANCZOS);out.paste(mini,(24,431))
text(145,463,'133,797',18,color='#ffbf69',font='bold.ttf');text(145,493,'river reaches',11)
text(30,557,'THOMAS HAGOS',11,font='bold.ttf');out.save(R/'outputs/02-thomas-hagos.png')
