# The Nile, Connected

**One basin, many tributaries.** Day 2: Lines · MUSA 30-Day Map Challenge · Thomas Hagos

[View the project](https://flex-commits.github.io/30-days-mapping/nile/) · [High-resolution map](outputs/nile-connected.png)

I followed the Nile upstream through the river network: across Sudan, into the Ethiopian highlands and the equatorial lake catchments. Color makes the White Nile, Blue Nile and Atbara systems visible. Line thickness follows stream order.

## Reproduce

Python 3.9.6 was used. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/download.py
python scripts/build.py
python scripts/check_geometry.py
python scripts/render.py
python scripts/thumbnail.py
python scripts/package_site.py
# Optional full rebuild and byte-for-byte image check:
python scripts/verify_reproduction.py
```

The pinned direct dependencies are in `requirements.txt`; the full environment is in `requirements-lock.txt`. Source downloads are cached under `data/raw/`. If the catalog download is unavailable, obtain the named archive from the linked catalog, place it under the expected filename, and rerun. `data/downloads.json` preserves the original snapshot URLs and checksums; a rerun writes `downloads-current.json` instead and fails if archive bytes differ from the original snapshot. Raw source files and generated GeoPackages stay local because the HydroSHEDS license restricts stand-alone redistribution. The scripts, derived reach-classification table, checks, rendered images, fonts and web page are tracked.

## Scope and selection

The boundary is HydroBASINS level 2 **PFAF_ID 17**, **HYBAS_ID 1020034170**, in the Africa customized-with-lakes v1.c file. UNESCO's documented Nile river subset was selected with that basin; this project then uses **MAIN_RIV 10047863** to retain its largest connected river network. A rectangular crop is not used to decide river membership.

There are **133,797 retained reaches**, out of 141,522 in the source subset. Of the 7,725 excluded reaches, 6,635 are flagged endorheic; the other 1,090 belong to other source outlet networks. The broad basin outline remains visible, including areas not surface-connected to the retained network. These are modeled topological connections, not evidence that each drainage carries perennial flow.

## Tributary colors and line width

The downstream table (`NEXT_DOWN`) defines connectivity. The White and Blue Nile branch candidates are located immediately upstream of their Khartoum confluence, checked against Nile Basin Initiative reference geography. Their paths identify the final pre-confluence reaches, **10441408** and **10441642**. The Atbara final pre-confluence reach is **10382814**. Reverse traversal assigns every upstream reach to one of these systems; remaining connected reaches are classified as Main Nile / other connected tributaries. This is a project-specific four-group classification, not NBI's ten-subbasin classification.

`ORD_STRA` determines width in points: 1→0.10, 2→0.15, 3→0.23, 4→0.35, 5→0.55, 6→0.85, 7→1.20, 8→1.65. In Strahler ordering, two streams of the same order create the next order at their confluence; a smaller tributary does not increase the larger stream's order. Width represents network hierarchy, not measured discharge, navigability or present-day water volume.

River vertices are preserved in local WGS84 caches. Projection for rendering: Lambert azimuthal equal-area, centered on 32°E, 14°N. The 300-mile scale is computed geodesically at 3.6°N; a projection has varying local scale. No smoothing or artificial connectors are added. Lake polygons are drawn over modeled routing centerlines inside open water.

## Validation and limits

See `data/processed/validation.json`. All downstream IDs are retained (except the zero outlet), every path terminates without a cycle, and every downstream endpoint matches the next reach's upstream endpoint with a maximum gap of **0 m**. Every retained reach intersects the selected basin. These are source-consistency checks, not field verification.

HydroRIVERS is based on 15-arc-second hydrography, approximately 500 m at the equator. It includes reaches meeting a catchment threshold of 10 km² or estimated mean discharge of 0.1 m³/s, or both. It does not include every stream. Arid drainage lines can be intermittent or dry. Lake outlines are generalized independently of the river network. Wetlands and lake crossings are routing abstractions.

The single-flow-direction network reaches the Mediterranean through **one modeled outlet**; it is not a complete Nile delta distributary or irrigation-channel inventory. No missing branches were invented. The map does not show current river flow, reservoir operations, water allocations or navigation routes. Country boundaries are context only.

Names and major geographic relationships were corroborated with the [NBI major-subbasin reference](https://nilebasin.org/en/media-center/maps/major-subbasins) and [hydromet directory](https://nilebasin.org/hydromet/map). Lake names/targets come from Natural Earth. Text is manually placed for readability; lake labels use leader lines. The source river records do not provide names.

## Sources and licensing

Full source/version/license details: [`data/sources.json`](data/sources.json). Archive URLs, byte counts and SHA-256: [`data/downloads.json`](data/downloads.json).

HydroRIVERS v1.0 and HydroBASINS v1.c: WWF / McGill, accessed through UNESCO IHP-WINS. Citation: Lehner, B. & Grill, G. (2013), *Global river hydrography and network routing*, Hydrological Processes 27:2171–2186, [doi:10.1002/hyp.9740](https://doi.org/10.1002/hyp.9740).

This derived map incorporates HydroSHEDS v1 data, © World Wildlife Fund, Inc. (2006–2022), used under the [HydroSHEDS license](https://data.hydrosheds.org/file/technical-documentation/HydroSHEDS_TechDoc_v1_4.pdf). WWF has not evaluated this map and gives no warranty of its accuracy, completeness, currency or suitability. Underlying contributions include USGS, NASA, ESRI, CIAT, UNEP-WCMC, WWF, the Commonwealth of Australia, and the British Crown as detailed in that license. HydroSHEDS geometry is not relicensed by this repository.

Natural Earth country and lake geometry is public domain. Typography matches Day 1: DejaVu Sans, with its license bundled in `docs/fonts/`. The navy background, cream headings, warm accents and numbered day marker follow The Restless Earth. Cartography and narrative: Thomas Hagos. Research, implementation and editing were assisted by AI; river geometry is sourced data, not generated imagery.

## Outputs and publication

- `outputs/nile-connected.png`: 3600 × 4800 PNG, 300 dpi.
- `outputs/02-thomas-hagos.png`: dedicated 600 × 600 gallery thumbnail.
- `docs/`: project page source, fonts and notices; `scripts/package_site.py` copies to the repository's `docs/nile/` Pages directory.
- `data/processed/reach-classification.csv`: derived membership and styling table, without geometry.
- `data/processed/validation.json`: reproducible checks and counts.

Finding Support remains a separate portfolio project. This Nile map is the proposed Day 2 submission; only its thumbnail and Markdown description belong in the shared MUSA repository. No pull request should be opened until Thomas reviews the prepared submission.
