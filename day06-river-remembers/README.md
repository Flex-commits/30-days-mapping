# The River Remembers

**Day 06 · Vintage · MUSA 30-Day Map Challenge 2026**  
Thomas Hagos

Old bends along the Lower Mississippi, near Helena, Arkansas. A new water-reference map sits beside two credited details from the Mississippi River Commission’s 1938 *Early Stream Channels* sheet. Moon Lake is an oxbow of the Mississippi: the curve remains even though the river follows a different path.

[Public project](https://flex-commits.github.io/30-days-mapping/the-river-remembers/) · [High-resolution PNG](outputs/the-river-remembers.png) · [600px gallery thumbnail](outputs/06-thomas-hagos.png)

## What this map does

The reference map uses USGS NHD river/stream areas and lake/pond polygons. Teal means river/stream areas. Rust marks the three named lakes that sit in old river bends; every other lake/pond is a pale tan. Dashed gold boxes **A** (Moon Lake) and **B** (Horseshoe Lake) match the two archive details on the right. The three named lakes are labeled using their NHD GNIS names. Leader anchors are interior representative points of their corresponding polygons.

The archival details show Montezuma Bend / Moon Lake and Horse-Shoe Cut-Off on Sheet 5. Their colors and geometry are retained. The original legend records 1765, 1820–1830, 1881–1893 and 1930–1932 surveys, including an indeterminate 1820–1830 bankline shown with dashed pink. Those are survey periods, not four complete reconstructed time slices.

The new reference map and archival details have different scales and orientations. The scan has **not** been georeferenced to NHD. This is a visual reading of related geographic evidence, not a measured migration analysis or a precisely registered historical overlay. No synthetic historical channel geometry is drawn.

## Reproduce

Python 3.9.6 was used. From this folder:

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

All required source snapshots and font licenses are tracked. `download.py` verifies their hashes and can restore missing inputs if the remote bytes still agree. Mutable services can change; use this Git snapshot for exact reproduction. No API keys are required.

- `config.json`: study extent, projection, archival crop rectangles, label positions, palette and export size.
- `data/raw/`: original PDF, complete queried GeoJSON and service metadata; never altered by processing.
- `data/processed/`: geographically clipped, unsimplified display layers, projected GeoPackage, U.S. locator and unwarped archival crops.
- `data/source-manifest.json`: publishers, URLs, versions/snapshots, download date, rights, limitations and SHA-256 hashes.
- `scripts/`: download/verification, preparation, rendering, page assembly and validation.
- `outputs/`: 4500 × 5400 PNG and dedicated 600 × 600 thumbnail.
- `docs/`: processing and validation reports, methods and LinkedIn draft.
- `submission/`: only the two files intended for MUSA.

To publish the generated static page, copy the contents of `site/` to the repository’s `docs/the-river-remembers/`. `site/` is generated and ignored. The repository already hosts GitHub Pages from `main:/docs`.

## Data and selection

**USGS National Hydrography Dataset / The National Map.** Saved November 8, 2026. Layer 9 selects `FTYPE=460` (river/stream areas). Layer 12 selects `FTYPE=390` (lake/pond), `AREASQKM >= 0.03` (approximately 7.4 acres). Queries intersect the WGS84 envelope `[-90.86, 34.24, -90.40, 34.60]`; a subsequent clip matches the display extent. Both queries returned complete results without a transfer-limit flag. Raw identifiers, feature dates, names and classifications are preserved. Geometry is not simplified. Source metadata states an October 2026 refresh; feature dates vary and are not a common observation year.

**Mississippi River Commission.** *Lower Mississippi River: Early Stream Channels at Approximate Half-Century Intervals*, Sheet 5, Mile 258–331, prepared August 1938; reproduction imprint 1939. Scan: Michigan State University Libraries. The scan URL includes “1927”; the title block establishes the actual map date. The full original PDF is saved so its legend, orientation and scale can be inspected. The matching USACE download returned HTTP 403, so the accessible library-hosted scan was used. [Library of Congress context](https://blogs.loc.gov/maps/2016/06/the-meandering-mississippi/) independently describes this 1938 series.

**Natural Earth, 1:50m states/provinces.** U.S. locator only; saved master snapshot identified by hash. Public domain.

**Mississippi Department of Wildlife, Fisheries, and Parks.** [Moon Lake](https://www.mdwfp.com/fishing-boating/lakes/moon-lake) confirms its Mississippi River oxbow origin. No exact cutoff date is inferred.

The project began with Fisk’s 1944 atlas as an inspiration. The final archival evidence is the earlier 1938 MRC sheet, whose dated survey legend suits this focused comparison. Fisk geometry is not used.

## Cartography and limits

The reference map uses NAD83 / UTM zone 15N (EPSG:26915), equal map-axis units and a five-mile scale bar. The arrow indicates grid north. The small U.S. locator uses EPSG:5070. Neither of these reference projections is attributed to the historical scan; that scan’s original orientation is retained without inferring its projection.

NHD water outlines are mixed-date reference geometry, not today’s water level or a survey suitable for navigation. Small ponds, reservoirs, swamps and line-only streams are not a complete surface-water inventory. Dry paleochannels are not mapped. Archival survey uncertainty, generalization and overprinting remain; crops are not measurements. No claim is made about whether each change was natural or engineered.

## Design and rights

Original reference cartography, layout and text: Thomas Hagos, **CC BY 4.0**. U.S. federal source maps/data and Natural Earth are public domain in the United States, with credits retained. Fonts: Great Vibes by Robert E. Leuschke and IM FELL English by Igino Marini (SIL OFL 1.1), plus DejaVu Sans (bundled license). Calligraphy is reserved for the title and river name; map labels and methods use readable serif/sans faces. No invented paper texture or geography is used.

## MUSA submission

The shared repository receives only `assets/thumbnails/2026/06-thomas-hagos.png` and `_maps_2026/06-thomas-hagos.md`. Code, data, full exports and this page remain in `Flex-commits/30-days-mapping`. The submission branch is checked against existing Day 6 entries and pull requests before creation.
