# Africa, to Scale — continent feasibility draft
Thomas Hagos · 2026 MUSA Day 03 / Polygons

This folder continues the project with continents. It preserves the earlier country comparison and every NYC project. **This is a geographic draft for review, not a final map or submission.**

See [draft results and review decisions](docs/draft-results.md), the [six-panel preview](outputs/continents-individual-preview.png), and the [four-panel trial](outputs/continents-feasibility-preview.png).

## What is being tested
Four proposed panels: South America + Australia over Africa; Antarctica + Europe over Africa; North America over Africa; and Africa over country-colored Asia. The files also test individual-continent fallback panels, without repeating a comparison continent within that set. Repeated Africa outlines are the common reference; the Asian panel reverses the reference.

The title does not assert universal containment. A larger area does not guarantee that one complete shape can fit inside another. Partial overlays visibly hatch every portion outside the host; crosshatching identifies overlap between guests. Failed bounded searches are not proofs that a fit is impossible. A verified fit requires exactly zero computed outside area and zero overlap on the actual display geometry. No broad tolerance hides protrusions.

## Definitions
- All coastlines start from Natural Earth 1:50m Admin 0 Countries v5.1.1, using its generalized de facto boundaries and represented components. Original country polygons preserve source holes in a separate file. For comparison, interior rings are uniformly filled after assembling each continent. These are coastline-enclosed surface areas including enclosed inland water, not dry-land areas or sovereignty certification. Water open to the coastline or the continental divider remains outside. This avoids treating an African lake as a failed coast-outline fit. The convention applies to every continent before computing its target area; no hole is removed selectively to obtain a fit.
- Africa includes Madagascar, the source's African-region island units, Mayotte and Réunion, and whole Egypt including Sinai. The complete source-region grouping includes remote islands; the membership file records every component.
- South America includes French Guiana and source South American country/island components. North America includes Greenland, Arctic islands, Central America and Caribbean components; Hawaii is excluded.
- Australia is the mainland, Tasmania and represented nearby Australian components within the saved geographic rule. It does not mean all Oceania, New Zealand or New Guinea. Other Oceania and remote overseas components outside these definitions are explicitly listed as excluded, not silently removed for fitting.
- Europe and Asia divide Russia, Kazakhstan, Türkiye, Georgia and Azerbaijan. The saved mask traces Natural Earth's Europe physical-region eastern boundary, extending the dividing route through water and north to the Arctic. Russian Far East components west of the antimeridian remain Asian. Other source-country island allocations are retained, including Cyprus in Asia and Greek islands in Europe. This is a documented cartographic convention, not a unique universal continent boundary. Inspect the divider and membership before final approval.
- Antarctica combines the source country polygon with Natural Earth's perennial ice-shelf polygons, embedded archive v4.1.0. It excludes seasonal sea ice. Ice-shelf data derive from a 2003–04 mosaic lineage and are not a current ice-front survey. The web page still labels the download v4.0.0; the manifest records this discrepancy rather than silently substituting the page version.

The initial country-only Antarctic polygon was about 12.36 million km²; adding the documented perennial shelf extent gives about 13.92 million km² before the uniform interior-ring convention. This explicit definition replaces the provisional country-only Antarctic calculation. Published roughly 14.2 million km² figures should not be used to resize the outline.

## Geometry and area
Geodesic target areas use the consistently filled WGS84 ellipsoidal continent polygons with pyproj.Geod. Edges are densified geodesically to no more than 10 km. Each continent receives its own locally centered WGS84 Lambert azimuthal equal-area frame in metres; centers are saved in config.json. Projected representations are normalized minutely to their calculated geodesic polygon areas. This is numerical representation correction, not scaling to obtain a fit.

Original geographic data, continent assemblies, projected comparisons, display-preplacement geometry and placed layouts are separate. No display simplification is applied. A 0.01 m preparation precision grid removes numerical seam slivers; geometry repairs and their measured area effects are logged. Normalization follows preparation so target areas remain consistent. The prepared display shapes undergo only rotation and translation thereafter. Search-only proxies use 18 km simplification without topology retention, followed by proxy-only repair; every delivered metric and visible polygon uses full geometry.

Equal-area representations preserve the intended area comparison, but distort shape and direction. Moving a projected outline does not create an exact geographic relocation on the ellipsoid. Every panel uses the same physical area scale. Residual comparison space is not politically or physically “empty” land.

## Asia panel
Asian country portions share Asia's single projection and numerical frame. Countries are not separately projected in this panel. The moved Africa outline is intersected with those country pieces; the CSV reports covered area and percentage of each Asian country piece. Russia and other split countries refer only to their Asian portions. A covered portion is never counted as the entire country. Source country polygons retain their water holes; enclosed waters added to the continent surface are an unattributed-water/geometry remainder, not assigned to a country by invention. Countries and territories follow the source units, without a sovereignty endorsement. Major countries are named in this first draft; the full coverage table supplies names for all intersected units. Full labeling and adjacent color separation remain design work after review.

## Reproduce from frozen inputs
Tested dependency versions and Python runtime are saved in requirements.txt and docs/environment.txt. Create a virtual environment and install the requirements.

```sh
python scripts/download_frozen.py
python scripts/prepare_continents.py
python scripts/replay_and_validate.py
python scripts/country_coverage.py
python scripts/audit_geography.py
python scripts/proxy_audit.py
python scripts/render_continents.py
python scripts/render_continents.py --individual
```

The downloader checks exact SHA-256 values and stops if upstream bytes have changed. Existing frozen raw files can be copied instead; large/raw downloads are excluded from Git. To regenerate bounded searches instead of replaying the saved placements, run scripts/test_layouts.py and then scripts/test_individuals.py. Searches are deterministic with saved seeds and finite trial limits, not optimal packing solvers.

Projected GeoJSON uses metre coordinates in documented local frames; it is not RFC 7946 longitude/latitude interchange data. Consult projection-frames.json before loading it into GIS.

## Sources, course and remaining review
Made with Natural Earth. Data are public domain; exact URLs, embedded versions, retrieval timestamps, checksums, terms, attribution, coverage and limitations are in source-manifest.json. Its physical-region polygons are approximate label-region boundaries, used only to inform the Eurasian division, not as an unquestioned universal continental standard.

The current course category file confirms 2026 Day 03 / Polygons. https://github.com/weitzman-musa/30DayMapChallenge . The previously inspected template uses day, creator, title, thumbnail and source fields. Proposed shared paths remain assets/thumbnails/2026/03-thomas-hagos.png and _maps_2026/03-thomas-hagos.md. No submission replacement is prepared at this draft milestone. Existing fork/PR conflicts and the template will be checked again before any final proposal.

Review decisions: literal containment versus honest same-scale overlays; paired versus separate panels; the island-inclusive definitions and Eurasian divider; the historic perennial-ice-shelf Antarctic definition. Independent published-area reasonableness checks, final cartography, thumbnail, full page/portfolio drafts and submission files remain for the post-review stage. No publication, push, commit or PR is authorized or performed.

This original series belongs to the broader area-comparison map tradition. It does not copy a prior “True Size of Africa” composition or artwork.

Initial published-area check: [Geoscience Australia](https://www.ga.gov.au/scientific-topics/national-location-information/geography/areas-of-australia) reports 7,688,287 km²; the initial source-hole-preserving Natural Earth Australia geometry was about 0.038% larger. The updated, uniformly filled comparison area is recorded separately in the check table. Different coastline resolution and inclusion conventions explain why these are a reasonableness check, not an exact matching target. Details are saved in docs/published-area-checks.json.
