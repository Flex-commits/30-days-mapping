"""Create the square gallery image required by the MUSA repository."""
from pathlib import Path
import runpy
s=runpy.run_path(str(Path(__file__).with_name('render_poster.py')))
plt=s['plt'];fig=plt.figure(figsize=(6,6),facecolor=s['paper'])
fig.text(.06,.925,'FINDING SUPPORT',fontsize=24,fontproperties=s['bold'],color=s['ink'])
fig.text(.063,.875,'NYC services and nearby rail',fontsize=11,fontproperties=s['sans'],color=s['muted'])
ax=fig.add_axes([.045,.155,.91,.66]);s['draw'](ax,[-74.265,-73.69,40.49,40.90])
for name,x,y in [('BRONX',-73.871,40.868),('QUEENS',-73.803,40.755),('BROOKLYN',-73.954,40.63),('STATEN ISLAND',-74.151,40.56)]:
 ax.text(x*s['C'],y,name,fontproperties=s['sans'],fontsize=5,color=s['muted'],ha='center')
fig.text(.06,.095,'DAY 02 / LINES',fontsize=9,fontproperties=s['bold'],color=s['ink'])
fig.text(.06,.055,'Thomas Hagos · 21 service–station connections',fontsize=7,fontproperties=s['sans'],color=s['muted'])
fig.savefig(s['ROOT']/'dist/02-thomas-hagos.png',dpi=100,facecolor=s['paper']);plt.close(fig)
