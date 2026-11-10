from pathlib import Path
import xml.etree.ElementTree as ET,re,math,io,json,subprocess
from PIL import Image,ImageDraw,ImageFont
import resvg_py,imageio_ffmpeg
R=Path(__file__).resolve().parents[1];ROOT=R;O=R/'outputs/video';O.mkdir(parents=True,exist_ok=True)
ns='{http://www.w3.org/2000/svg}';ET.register_namespace('',ns[1:-1]);tree=ET.parse(R/'outputs/living-city/city.svg');svg=tree.getroot();
for element in list(svg):
 if element.get('class')=='landmark':svg.remove(element)
for parent in svg.iter():
 for child in list(parent):
  if child.tag==ns+'text':parent.remove(child)
for element in svg:
 if element.tag==ns+'rect' and element.get('fill')=='url(#sky)':element.set('y','0');element.set('height','1400')
svg.set('viewBox','0 260 1950 1180')
residents=[e for e in svg if e.get('class')=='resident'];actors=[]
for e in residents:
 motion=e.find(ns+'animateMotion');body=e.find(ns+'g');dur=float(motion.get('dur')[:-1]);begin=float(motion.get('begin')[:-1]);nums=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',motion.get('path'))));points=[tuple(nums[i:i+2]) for i in range(0,len(nums),2)]
 sprites=[]
 for phase in range(4):
  bodycopy=ET.fromstring(ET.tostring(body));legs=next((g for g in bodycopy.iter() if g.get('class')=='legs'),None)
  if legs is not None:legs.set('transform',f'skewX({math.sin(phase*math.pi/2)*16:.2f})')
  source='<svg xmlns="http://www.w3.org/2000/svg" width="160" height="208" viewBox="-10 -22 20 26">'+ET.tostring(bodycopy,encoding='unicode')+'</svg>'
  sprites.append(Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=source))).convert('RGBA').resize((40,52),Image.Resampling.LANCZOS))
 actors.append((points,dur,begin,sprites));svg.remove(e)
svg.set('width','3900');svg.set('height','2360');base=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=ET.tostring(svg,encoding='unicode')))).convert('RGBA')
W,H,FPS,SECONDS=3840,2324,30,4
serif=ImageFont.truetype(str(R/'fonts/serif.ttf'),76);italic=ImageFont.truetype(str(R/'fonts/serif-italic.ttf'),29);small=ImageFont.truetype(str(R/'fonts/sans.ttf'),19);tiny=ImageFont.truetype(str(R/'fonts/sans.ttf'),16)
encoder=imageio_ffmpeg.get_ffmpeg_exe();cmd=[encoder,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(O/'aksum-utopia-4-seconds-4k.mp4')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(O/'encode.log','w'))
def bez(a,b,c,t):return ((1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0],(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1])
def ease(v):return v*v*(3-2*v)
for f in range(FPS*SECONDS):
 t=f/FPS;scene=base.copy()
 for k,(pts,dur,begin,sprites) in enumerate(actors):
  u=((t-begin)%dur)/dur
  x,y=bez(*pts[:3],u*2) if u<.5 else bez(*pts[2:],(u-.5)*2)
  sprite=sprites[int((t+k*.17)*6)%4];bob=math.sin((t+k*.17)*2*math.pi/1.1)*.35
  scene.alpha_composite(sprite,(round((x-10)*2),round((y-260-22+bob)*2)))
 # Full composition: all photo cards, connectors and city remain visible.
 scene=scene.resize((W,H),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(W,H),'#e7e5d9');canvas.paste(scene,(0,0),scene)
 p.stdin.write(canvas.tobytes())
 if f in [0,60,119]:canvas.save(O/f'frame-{f:04}.jpg',quality=92)
 if f%120==0:print(f'Encoded {f}/{FPS*SECONDS}',flush=True)
p.stdin.close();assert p.wait()==0
(O/'render-settings.json').write_text(json.dumps({'duration_seconds':SECONDS,'fps':FPS,'width':W,'height':H,'audio':'none','source':'c937e7d photo-linked animated city','renderer':'Original SVG static scene; same quadratic motion paths with deterministic sprite walk cycles','zoom':'none: full composition, photo callouts and motion, no text or numbered markers','codec':'H.264, yuv420p, faststart'},indent=2));(O/'source-credits.txt').write_text('Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.\nLandmark anchors: © OpenStreetMap contributors, ODbL. Original scenario: Thomas Hagos, CC BY 4.0. Buildings, clothing and movement are interpretations.\nPhotographs: A.Savin, Wikipedia, Free Art License (https://artlibre.org/licence/lal/en/); © UNESCO / Michel Ravassard, CC BY-SA 3.0 IGO (https://creativecommons.org/licenses/by-sa/3.0/igo/). Resized; otherwise unchanged. Source records: https://github.com/Flex-commits/30-days-mapping/tree/main/day08-aksum-built/data/photos .\nSources and methods: https://flex-commits.github.io/30-days-mapping/aksum-built/\n');print('DONE',flush=True)
