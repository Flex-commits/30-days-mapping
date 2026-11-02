"""Render Day 1 from frozen USGS and Natural Earth GeoJSON snapshots."""
import json
from pathlib import Path
from datetime import datetime, timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize, LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'data/earthquakes.geojson').read_text())
land = json.loads((ROOT/'data/land.geojson').read_text())
events = sorted([f for f in data['features'] if f['geometry'] and f['properties']['mag'] is not None], key=lambda f:f['properties']['mag'])
BG, FG, MUTED = '#101e2b', '#f2eee2', '#a8b7c2'
CMAP = LinearSegmentedColormap.from_list('seismic', ['#ffe7a3','#ffb052','#f65d40','#d72e43'])
NORM = Normalize(4.5, 6.5)
size = lambda m: 16*2**(m-4.5)
date = lambda t: datetime.fromtimestamp(t/1000,timezone.utc).strftime('%d %b %Y')
times = [f['properties']['time'] for f in events]
period = f'{date(min(times))} – {date(max(times))} UTC'
x=[f['geometry']['coordinates'][0] for f in events]
y=[f['geometry']['coordinates'][1] for f in events]
m=[f['properties']['mag'] for f in events]
assert len(events)==data['metadata']['count']
assert all(-70 <= lat <= 85 for lat in y), 'Expand the map to include every event'

def draw_map(ax, thumbnail=False):
    ax.set_facecolor(BG)
    for f in land['features']:
        g=f['geometry']; polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for poly in polygons:
            ax.add_patch(Polygon(poly[0],facecolor='#293e4b',edgecolor='#405562',linewidth=.35))
    for lon in range(-180,181,60): ax.axvline(lon,color='#304451',lw=.4,zorder=0)
    for lat in range(-60,81,30): ax.axhline(lat,color='#304451',lw=.4,zorder=0)
    ax.scatter(x,y,s=[size(v)*(1.7 if thumbnail else 1) for v in m],c=m,cmap=CMAP,norm=NORM,alpha=.95,edgecolors='#ffe5b6',linewidths=.4,zorder=3)
    ax.set(xlim=(-180,180),ylim=(-70,85),aspect='equal')
    ax.set_xticks([-120,-60,0,60,120]); ax.set_yticks([-60,-30,0,30,60])
    ax.set_xticklabels(['120°W','60°W','0°','60°E','120°E'])
    ax.set_yticklabels(['60°S','30°S','0°','30°N','60°N'])
    ax.tick_params(colors=MUTED,labelsize=8,length=0,pad=8)
    for spine in ax.spines.values(): spine.set_visible(False)
    if thumbnail: ax.set_xticks([]); ax.set_yticks([])

out=ROOT/'outputs'; out.mkdir(exist_ok=True)
fig=plt.figure(figsize=(14,10),facecolor=BG)
fig.text(.055,.935,'01  /  POINTS',color='#ffbf69',fontsize=11,weight='bold')
fig.text(.055,.875,'THE RESTLESS EARTH',color=FG,fontsize=36,weight='bold')
fig.text(.057,.835,'One week of magnitude 4.5+ earthquakes',color=MUTED,fontsize=17)
fig.text(.057,.794,f'{period}   •   {len(events)} recorded epicenters',color='#ffbf69',fontsize=11)
ax=fig.add_axes([.055,.285,.89,.475]); draw_map(ax)
fig.text(.057,.225,'Magnitude',color=FG,fontsize=11,weight='bold')
key=fig.add_axes([.055,.167,.32,.045],facecolor=BG)
for i,v in enumerate([4.5,5.5,6.5]):
    key.scatter(i,.5,s=size(v),color=CMAP(NORM(v)),edgecolors='#ffe5b6',linewidths=.4)
    key.text(i+.14,.5,f'{v:.1f}',va='center',color=FG,fontsize=11)
key.set(xlim=(-.15,2.65),ylim=(0,1)); key.axis('off')
fig.text(.45,.223,'Earthquakes trace the edges of a restless planet.',color=FG,fontsize=12)
fig.text(.45,.188,'Larger, warmer points indicate higher magnitude.\nCircle area doubles per magnitude unit; it does not represent energy.',color=MUTED,fontsize=10,linespacing=1.7)
fig.text(.057,.115,'#30DayMapChallenge 2026   /   Thomas Hagos',color=FG,fontsize=10)
fig.text(.057,.061,f'USGS Earthquake Hazards Program • 7-day feed saved {date(data["metadata"]["generated"])} UTC\nLand: Natural Earth, 1:110m • Plate carrée projection • All {len(events)} snapshot events shown\nCreated with Python / Matplotlib; AI-assisted code and design.',color=MUTED,fontsize=8,linespacing=1.6)
fig.savefig(out/'01-points-earthquakes.png',dpi=200,facecolor=BG)
plt.close(fig)

# A separate gallery composition keeps text legible at 300px display size.
fig=plt.figure(figsize=(6,6),facecolor=BG)
fig.text(.065,.915,'01 / POINTS',color='#ffbf69',fontsize=11,weight='bold')
fig.text(.065,.76,'THE RESTLESS\nEARTH',color=FG,fontsize=26,weight='bold',linespacing=1.05)
ax=fig.add_axes([.035,.28,.93,.43]); draw_map(ax,True)
fig.text(.065,.215,f'{len(events)} EARTHQUAKES  /  M 4.5+',color='#ffbf69',fontsize=11,weight='bold')
fig.text(.065,.155,period,color=MUTED,fontsize=8)
fig.text(.065,.085,'Thomas Hagos • Data: USGS / Natural Earth',color=MUTED,fontsize=8)
fig.savefig(out/'01-points-thumbnail.png',dpi=100,facecolor=BG)
plt.close(fig)
print(f'Rendered full map and 600px thumbnail; all {len(events)} events shown.')
