# Aksum, Reimagined — 3D city study

A navigable, projected-metre 3D prototype. This is an imaginative contemporary city proposal informed by Aksumite architectural motifs, not an archaeological reconstruction or development plan.

## What is real
- Copernicus modern DSM: tracked terrain.npz in the parent project's data folder; 8,720 terrain vertices.
- Approximate OSM landmark anchors, unchanged from the source snapshot.
- 384 present-day OSM highway ways in the saved November 10, 2026 API map extract. These are a separate optional layer, not ancient streets.
- UNESCO approximate returned-obelisk height (24m) and fallen Great Stele length (33m), represented schematically. Widths, carving and fallen orientation are not surveyed replicas.

## What is imagined
150 generated houses, courtyard blocks, a marketplace, colonnades, a speculative Dungur palace, streets, residents and clothing. The city grid does not claim historical or present-day parcel geometry. There is no structural feasibility claim. Foundations are illustrative; the terrain is not ancient ground. The Dungur tower is a massing study, not a reconstruction. Yeha is shown separately in a regional schematic; no real or proposed transport route is asserted. This scene has no vertical exaggeration.

## Controls
Drag to orbit; scroll/pinch to approach; right-drag to pan. Camera presets: whole city, market square, street level and Dungur. Street level is a camera preset, not a collision-aware walking game. Pause life respects reduced-motion preferences initially. The layer selector separates the proposal, schematic monuments and today's street references. Red landmark spheres open historical notes and licensed photographs.

## Reproduce
With Python dependencies from the parent project installed, run `python prepare.py` inside this folder. The saved OSM extract and parent terrain/landmark snapshots regenerate scene-data.json. Then run `npm ci` and `npm run build` here (Three.js 0.180.0, esbuild 0.25.11). Serve this folder under the parent project, or copy index.html, scene.js and THREE-LICENSE.txt to docs/aksum-built/three-d. Fonts and photographic references resolve through the parent page's folders. No runtime CDN or API key is needed.

## Attribution
© OpenStreetMap contributors, ODbL. Original architecture and composition: Thomas Hagos, CC BY 4.0. Three.js: MIT, license bundled. Photos: parent data/photos/manifest.json. Sources: UNESCO Aksum https://whc.unesco.org/en/list/15/ ; returned obelisk https://whc.unesco.org/en/news/458/ ; The Met, Monumental Architecture of the Aksumite Empire. Rome precedent: https://www.baroquerome.org/about/ . No Rome project models or images were reused.

Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.
The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.


## Recognizable landmarks update
The old Mary of Zion church and the new domed cathedral are distinct models. OSM ways 188465648 and 262791601 define their footprint meshes. Roofline, arch, window and dome geometry is drawn from visual references, with explicit assumed elevations in landmark-models.json. The old church is associated with seventeenth-century rebuilding; the new cathedral was inaugurated in 1965 (UNESCO 2013 reactive monitoring mission). OSM's unverified start_date=1950 tag is not used for chronology. Simplified crosses are symbolic, not exact reproductions. No interior is modeled. The buildings are not laser scans or photogrammetric meshes.

The returned Stele 2 is approximately 24m (UNESCO). Stele 3 is 20.57m above earth in the DAI Stelae of Aksum chapter, printed p99. The Great Stele is approximately 33m fallen length (UNESCO); its fragmentation and orientation remain schematic. Carved facade patterns are representative, not exact tracing.

Zamani Project / University of Cape Town laser scans were found for Stele 1, Stele 3 and the stelae field. Public Sketchfab API records on November 10, 2026 all list isDownloadable=false and no redistribution license. No meshes were extracted. The official viewers are linked from the stelae evidence panel: https://zamaniproject.org/site-ethiopia-aksum-stelae-field.html . Integration of those scan files would require a lawful download or permission.

Reference photographs: old church by A.Savin, Wikipedia (Free Art License); new church by Sailko (CC BY 3.0), both 2018. Resized but not cropped or otherwise edited. See parent data/photos/manifest.json. These images are shown as references, not projected as textures.


## Movement, landscape and export update
Walking speed 1.3 m/s; horse walking speed 2.2 m/s. Arms, feet and quadruped legs use procedural gait cycles; heading changes ease with quaternion interpolation. Residents sometimes pause at intersections. These are illustrative behaviors, not measured Aksum movement data. Proposed shade trees and planters are not historical vegetation observations.

The Zamani scans button loads the official Sketchfab iframe only on demand, with attribution. It does not copy research meshes into this scene. Three public model records were rechecked November 10, 2026: isDownloadable=false, no redistribution license listed.

Save image exports the current WebGL camera at 3840×2160. Record tour captures a clean 1920×1080, 20-second WebM through whole-city, church, stelae and market views; labels remain outside the captured canvas. Published downloadable MP4s can be transcoded from that capture. Source credits accompany exports separately.


## Delivered media
The actual WebGL scene was exported to a 3840×2160 PNG and recorded as a canvas-only tour, then encoded to H.264 MP4 at 1920×1080, 30fps (approximately 20 seconds). The media contain no text overlays. Credits and distinctions accompany the files in source-credits.txt. The official Zamani scans are not present in these original-scene exports. The MP4 uses an actual transfer-function/range conversion from the browser recording to Rec.709; it is not a relabeled render.
