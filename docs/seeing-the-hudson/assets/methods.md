# Seeing the Hudson

**Two shores. One river. Different views.**  
Thomas Hagos · Day 05: Senses: Sight · MUSA 30-Day Map Challenge 2026

Same river. Different picture. I paired six public places on the New York and New Jersey shores to look at the Hudson from both sides: two skylines, a sunset, and two views of the George Washington Bridge. The photographs were taken on different days, so the light, weather and surroundings change too.

[Public project](https://flex-commits.github.io/30-days-mapping/seeing-the-hudson/) · [Full map](outputs/seeing-the-hudson.png) · [Viewpoint records](data/processed/viewpoints.csv) · [Photo credits](data/photo-credits.json)

## Read the map

The overview locates all six places; numbered rectangles identify the three close-up areas supplied as separate paired-site sheets. West-shore markers use the pair's accent color; east-shore markers are cream. All geographic frames are north-up. The coordinate reference system is **EPSG:26918, NAD83 / UTM zone 18N**, in meters; displayed scale bars use miles.

**Dashed lines pair places for comparison. They are not viewing rays, walking routes, camera headings or proof of mutual visibility.** Aerial imagery shows the shoreline and urban context; it is not a simulated ground-level view. There is no terrain/building/vegetation viewshed model.

The title refers to the NY–NJ Lower Hudson corridor, not the entire Hudson watershed. The three pairs are intentionally selected examples, not a representative sample, access ranking or comprehensive inventory.

| Pair | New Jersey | New York |
|---|---|---|
| 01 · Skyline to skyline | Liberty State Park | Rockefeller Park riverfront |
| 02 · A skyline. A sunset. | Hamilton Park, Weehawken | Pier 84, Hudson River Park |
| 03 · One bridge. Two frames. | Fort Lee Historic Park | Fort Washington Park |

Public-site status and descriptions are documented by [NJ State Parks](https://dep.nj.gov/parksandforests/liberty-state-park), [Battery Park City Authority](https://bpca.ny.gov/place/rockefeller-park/), [Weehawken Township](https://www.weehawken-nj.us/Home/Components/FacilityDirectory/FacilityDirectory/29/211), [Hudson River Park](https://hudsonriverpark.org/locations/pier-84/), [Palisades Interstate Park](https://njpalisades.org/fortlee/), and [NYC Parks](https://nycgovparks.org/parks/fort-washington-park/highlights/11044). These sources document the sites, not a current closure or accessibility survey.

## Dates and geographic accuracy

- **Aerial imagery:** USGS Imagery Only / The National Map cached orthoimagery. Its metadata reports continental-U.S. NAIP sources from **2017–2021**; exact local pixel acquisition dates are not exposed by the MapServer. Its **June 2024 service refresh** is not a capture date. Frozen exports were downloaded November 8, 2026. The frames are not synchronized or current to that date. Water/coverage seams remain source limitations. Near-black pixels display transparently over navy for legibility; this is a graphic mask, not a water or building classification.
- **Photographs:** captured in 2008, 2010, 2015, 2017, 2021 and 2022, as attributed beside the images. Dates come from photographer-supplied Commons metadata. They differ in season, weather, time, camera field of view and position. The skyline/sunset pairing does not isolate a causal effect of shore orientation; these are examples, not a controlled comparison.
- **Coordinates:** five site anchors use approximate photographer-supplied coordinates. The Fort Lee anchor uses the operator's published park GPS/entrance, **not** an inferred camera position. Coordinates and their basis are in `viewpoints.csv`; decimal precision does not imply survey accuracy. Marker placement does not certify an exact viewing platform or that a site can see its paired point.
- **Distances:** the machine-readable pair table reports WGS84 geodesic distances between anchors, using 1,609.344 meters per mile. These are neither river-width measurements nor travel distances and are not the map's headline.

## Sources and rights

### Aerial imagery

USGS / USDA, **The National Map — USGS Imagery Only**. Rolling cached MapServer; byte-frozen exports downloaded November 8, 2026. Service attribution: USDA, USGS The National Map: Orthoimagery. Data refreshed June, 2024.v1.2. That refresh date is not the acquisition date. The service describes CONUS NAIP imagery from 2017–2021, with partner sources where NAIP is unavailable; no exact per-pixel local date is claimed.

- [Service metadata](https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer)
- [National Map licensing/terms](https://www.usgs.gov/faqs/what-are-terms-uselicensing-map-services-and-data-national-map)
- Frozen service metadata: `data/raw/usgs-imagery-metadata.json`.
- Exact export requests, returned extents, pixel dimensions and hashes: `data/imagery-frames.json`.

US federal CONUS orthoimagery is public-domain source material; no endorsement is implied. The service's separate Alaska SPOT restrictions are outside this study's coverage. Source geography is not generated. Darkening and a near-black transparency mask are display treatments, not inferred shoreline geometry.

### Photographs

Five selected photographs are **CC BY-SA 4.0**; the Jmccabe371 photograph is **CC BY-SA 3.0**. Each source-page URL, original and downloaded image URL, author, date, license URL and modification record is retained in `data/photo-credits.json`. Images are resized/cropped for the composition; no objects are added or removed. Author names and dates appear beside the photos; full linked credits are on the project page.

- Liberty State Park → Manhattan: **Dtabb73**, 2015-10-19.
- Rockefeller Park riverfront → Jersey City: **Kidfly182**, 2022-12-10.
- Hamilton Park → Manhattan: **Famartin**, 2021-05-14.
- Pier 84 sunset: **G. Scott Segler**, 2017-06-08.
- Fort Lee Historic Park: **Jllm06**, 2008-06-28.
- Little Red Lighthouse, Fort Washington Park: **Jmccabe371**, 2010-05-29, CC BY-SA 3.0.

[Creative Commons Attribution–ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The Jmccabe371 source remains CC BY-SA 3.0; adaptations may use a later BY-SA version under [section 4(b)](https://creativecommons.org/licenses/by-sa/3.0/legalcode.en). The poster and photographic paired-site sheets are shared under CC BY-SA 4.0 with the required source-photo attributions. The project is an original cartographic composition of attributed source photography, not a claim that Thomas took the photographs. DejaVu font licensing is bundled under `docs/fonts/`. Python source code is provided under MIT; source data and photographs retain their respective terms.

## Reproduce

Use Python 3.9+ with the pinned package versions in `requirements.txt`. The checked runtime uses Python 3.9.6. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/prepare.py
python scripts/render.py
python scripts/build_page.py
python scripts/validate.py
```

The saved, reasonably sized photo and aerial snapshots allow offline regeneration of the outputs. `scripts/download.py` can restore missing frozen inputs using recorded URLs and hashes; raw service export links may expire. `scripts/fetch_basemap.py` documents the acquisition process and can obtain a **new** imagery snapshot, but a refreshed source must be reviewed rather than silently assigned the old date. Original photo API metadata and aerial-source metadata are saved. `config.json` records selection and placement; geometry is generated in `prepare.py` rather than hand-drawn for the poster.

Directories follow the professors' workflow: `scripts/`, `data/raw/`, `data/processed/`, `outputs/`, `docs/`. Validation covers source integrity, six unique sites/three pairs, geographic bounds, source/coordinate provenance, photo licenses, unit conversion, imagery georeferencing, image dimensions, and deterministic re-rendering. Browser QA, where available, is reported separately from numeric checks.

## Submission

The shared Weitzman-MUSA repository receives only `_maps_2026/05-thomas-hagos.md` and `assets/thumbnails/2026/05-thomas-hagos.png`. All scripts, data, photographs, full exports and the public page stay in **Flex-commits/30-days-mapping**. The entry follows the current upstream template and links to this project. Submitted as [MUSA pull request #122](https://github.com/weitzman-musa/30DayMapChallenge/pull/122); gallery publication awaits maintainer review/merge.

The aerial-only gallery thumbnail is separately licensed CC BY 4.0 for the shared gallery; it contains no source photograph.
