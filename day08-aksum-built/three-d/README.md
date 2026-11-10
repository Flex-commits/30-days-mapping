# Aksum, Reimagined — 3D city study

A navigable, projected-metre 3D prototype. This is an imaginative contemporary city proposal informed by Aksumite architectural motifs, not an archaeological reconstruction or development plan.

## What is real
- Copernicus modern DSM: tracked terrain.npz in the parent project's data folder; 8,720 terrain vertices.
- Approximate OSM landmark anchors, unchanged from the source snapshot.
- 384 present-day OSM highway ways in the saved November 10, 2026 API map extract. These are a separate optional layer, not ancient streets.
- UNESCO approximate returned-obelisk height (24m) and fallen Great Stele length (33m), represented schematically. Widths, carving and fallen orientation are not surveyed replicas.

## What is imagined
164 generated houses, courtyard blocks, a marketplace, colonnades, a speculative Dungur palace, streets, residents and clothing. The city grid does not claim historical or present-day parcel geometry. There is no structural feasibility claim. Foundations are illustrative; the terrain is not ancient ground. The Dungur tower is a massing study, not a reconstruction. Yeha is shown separately in a regional schematic; no real or proposed transport route is asserted. This scene has no vertical exaggeration.

## Controls
Drag to orbit; scroll/pinch to approach; right-drag to pan. Camera presets: whole city, market square, street level and Dungur. Street level is a camera preset, not a collision-aware walking game. Pause life respects reduced-motion preferences initially. The layer selector separates the proposal, schematic monuments and today's street references. Red landmark spheres open historical notes and licensed photographs.

## Reproduce
With Python dependencies from the parent project installed, run `python prepare.py` inside this folder. The saved OSM extract and parent terrain/landmark snapshots regenerate scene-data.json. Then run `npm ci` and `npm run build` here (Three.js 0.180.0, esbuild 0.25.11). Serve this folder under the parent project, or copy index.html, scene.js and THREE-LICENSE.txt to docs/aksum-built/three-d. Fonts and photographic references resolve through the parent page's folders. No runtime CDN or API key is needed.

## Attribution
© OpenStreetMap contributors, ODbL. Original architecture and composition: Thomas Hagos, CC BY 4.0. Three.js: MIT, license bundled. Photos: parent data/photos/manifest.json. Sources: UNESCO Aksum https://whc.unesco.org/en/list/15/ ; returned obelisk https://whc.unesco.org/en/news/458/ ; The Met, Monumental Architecture of the Aksumite Empire. Rome precedent: https://www.baroquerome.org/about/ . No Rome project models or images were reused.

Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.
The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.
