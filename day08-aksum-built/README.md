# Aksum, Built

**Day 08 · Utopia · MUSA 30-Day Map Challenge 2026**  
Thomas Hagos

An imagined skyline for Ethiopia’s ancient capital. I placed speculative towers and homes on a sourced surface model of Aksum, using documented landmarks as anchors. Vermilion marks the imagined landmark towers; the smaller pale houses are imagined too.

[Public project](https://flex-commits.github.io/30-days-mapping/aksum-built/) · [Full map](outputs/aksum-built.png) · [Skyline detail](outputs/aksum-skyline-detail.png) · [Gallery thumbnail](outputs/08-thomas-hagos.png)

## The idea and its limits

Aksum’s carved stelae suggest architecture in miniature. This map imagines a skyline around those forms. It is **a design scenario, not an archaeological reconstruction, development proposal or structural safety assessment**. The model does not establish what could safely be built at any Aksum site.

The height module comes from Drieschner et al.’s **2023 reconstruction of Grat Be’al Gibri at Yeha**: a 6 m podium, 3.36 m clear storey and 0.96 m ceiling, giving 4.32 m per storey. Their eight-storey model is 40.56 m high. Yeha is a different site and an earlier period; the dimensions are used here as an illustrative design module, not as measured Aksum building dimensions.

BTU’s **September 2026 research report** describes numerical studies of two Yeha wall sections and reports a capacity corresponding to at least 19 storeys under the modeled assumptions. The 2026 study is cited through BTU’s institutional account; the full journal article was not consulted. That report does not prove the ancient palace reached that height, establish a universal 19-storey limit, or certify entire hypothetical towers at Aksum. This scenario chooses 19 as its tallest storey count; `6 + 19 × 4.32 = 88.08 m` is arithmetic for the drawing, not an engineering result for Dungur.

| Landmark anchor | Chosen storeys | Scenario height |
|---|---:|---:|
| Dungur palace | 19 | 88.08 m |
| Three great stelae | 13 / 10 / 9 | 62.16 / 49.20 / 44.88 m |
| Church of Mary of Zion | 12 | 57.84 m |
| Tombs of Kaleb and Gebre Meskel | 11 each | 53.52 m |
| Enda Nebura’ed | 8 | 40.56 m |
| Ezana inscription | 7 | 36.24 m |
| Tomb of King Bazen | 6 | 31.92 m |

All listed storey counts are **scenario choices**. The stelae-inspired counts are not claimed as newly verified counts of carved floors. Footprints, setbacks, doors/windows, twin-tower offsets, reservoir symbol and housing locations are schematic. Houses use three chosen storeys; the map makes no claim that every historical house had that height.

## Geography and drawing

- **Surface:** Copernicus GLO-30 tile N14 E038, nominal 30 m / one arc second. The tracked 80 × 109 sample crop was independently checked against its source GeoTIFF: all elevation values agree. Pixel centers come from the GeoTIFF georeferencing, not an assumed corner grid. This is a modern DSM including surface objects, not reconstructed ancient bare earth. Local pixel acquisition dates are not established.
- **Sites:** OpenStreetMap landmark nodes and approximate area centers, saved November 9, 2026. Source node XML and the two source way geometries are tracked, with object IDs and versions. Area-center anchors are arithmetic means of geometry vertices, not surveyed archaeological centroids. Place names do not validate traditional historical attributions.
- **Plan coordinates:** WGS84 positions transformed to WGS84 / UTM zone 37N (EPSG:32637). Northing is foreshortened by 0.36 for the north-facing oblique view. Ground relief and all buildings receive the same 3× vertical exaggeration. The 500 m scale refers to the east–west plan direction; it does not measure sloping screen distances or vertical heights.
- **Linework:** successive terrain profiles are drawn back to front. They are sampled elevation profiles, **not contour lines**. Houses use a fixed random seed and spacing/slope filters for a reproducible illustration. Neither these filters nor the skyline are a land-capacity or hazard model.
- **Locator:** Natural Earth 1:110m countries, Ethiopia highlighted within Africa. It provides context only.

## Reproduce

Python 3.9 was used. All small frozen inputs are tracked; no API keys are needed.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download.py
python scripts/prepare.py
python scripts/render.py
python scripts/build_page.py
python scripts/validate.py
```

`download.py` verifies the frozen inputs. To independently regenerate the terrain crop, download the original ~40 MB tile with `python scripts/download.py --terrain`, then run `python scripts/prepare.py --terrain data/raw/dem.tif`. The large tile is ignored by Git; its URL, hash, pixel-center transform and extraction window are recorded in `data/terrain-provenance.json` and `config.json`. Tracked `data/terrain.npz` supports normal offline rendering. Mutable sources must not silently replace the frozen snapshot.

The renderer saves every imagined building, its height and position to `data/scenario-buildings.json`. `config.json` fixes the height module, random seed and view parameters. Validation checks source hashes, site anchors against OSM source records, terrain bounds, height arithmetic, scene extents, output sizes, local page links and repeat-render image hashes.

`site/` is generated. Publish its contents to `docs/aksum-built/`. The earlier **A City of Towers** comparison remains available as a separate earlier study; this is the Day 8 Utopia project.

## Sources

- Drieschner, M., Wilhelm, S., Petryna, Y., Schnelle, M., Gerlach, I. (2023), *Preliminary Structural Analysis for the Archaeological Reconstruction of the Ancient Palace Grat Be’al Gibri in Yeha, Ethiopia*, §2.2 geometric model. https://www.omicsonline.org/open-access/preliminary-structural-analysis-for-the-archaeological-reconstruction-of-the-ancient-palace-grat-beal-gibri-in-yeha-ethiopia-124381.html
- BTU Cottbus-Senftenberg (September 25, 2026), research report on Drieschner & Schnelle (2026), *Heritage* 9(7):270, DOI 10.3390/heritage9070270. https://www.b-tu.de/news/artikel/32371-btu-statiker-liefert-neue-erkenntnisse-zu-antikem-palast-in-aethiopien
- Ethiopia Ministry of Culture and Tourism / UNESCO, *The Cultural Heritage of Yeha*, tentative-list submission (2020), supports the temple’s 14 m surviving height and earlier Yeha context. https://whc.unesco.org/en/tentativelists/6477 . Its displayed location text contains inconsistencies; this project uses OSM coordinates, not that coordinate string.
- UNESCO, *Aksum*, Outstanding Universal Value, supports the roughly 33 m length of the fallen Great Stele and the city’s heritage context. https://whc.unesco.org/en/list/15/
- Copernicus DEM source and licensing: https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
- OpenStreetMap contributors, ODbL: https://www.openstreetmap.org/copyright
- Natural Earth: https://www.naturalearthdata.com/about/terms-of-use/

Full records, URLs, dates and checksums: `data/source-manifest.json`. Claim decisions and limitations: `docs/research-notes.md`.

## Credits and licensing

Original scenario illustration, composition and text: Thomas Hagos, CC BY 4.0. Source data retain their own rights: OSM-derived geographic database ODbL; Natural Earth public domain; Copernicus DEM license. Font software is separately licensed: IM FELL English by Igino Marini, SIL OFL 1.1; DejaVu Sans, bundled DejaVu license. Neither study illustrations nor third-party photographs are reproduced.

Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.
