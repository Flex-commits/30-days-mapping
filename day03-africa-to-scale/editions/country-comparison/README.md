# Africa, to Scale
Thomas Hagos · 2026 MUSA Day 03 / Polygons

**Current direction: continent comparisons.** See the [continent draft](continents-draft/README.md), [six-panel map](continents-draft/outputs/continents-individual-draft.png), and [validated findings](continents-draft/docs/draft-results.md). These are review drafts; only Australia currently has verified complete containment.

The country comparison below is preserved as an earlier exploratory edition.

**Geographic feasibility draft, awaiting review.** This is a truthful partial packing, not an exact fill or a final submission. No existing NYC projects or submission proposals were replaced.

The contiguous United States, India, Germany and Japan occupy 11.82 million km²: 39.5% of the selected Africa geometry (29.90 million km²). Remaining comparison area is 18.09 million km². These are polygon surface areas, not dry-land statistics. Residual space is not “empty” African land.

## Geographic definitions
Natural Earth 1:50m Admin 0 Countries, version 5.1.1, supplies every outline. Africa is the union of source REGION_UN=Africa units plus complete Mayotte and Réunion components from France. It includes Madagascar, island states, source-listed remote dependencies and whole Egypt, including Sinai. This source-country regional grouping needs review: it is not a strict continental or mainland-only mask. Exact membership is saved in data/processed/africa-membership.json.

The contiguous United States retains all represented coastal components selected by the saved geographic component rule; Alaska and Hawaii are excluded. India, Germany and Japan retain every component of their source feature, including represented islands. The USA component audit is saved separately. Natural Earth uses generalized de facto boundaries, which do not certify sovereignty. Country polygons preserve their source holes; water enclosed by polygons is included, so this is not a uniform land-only mask.

## Area and placement method
WGS84 ellipsoidal source-polygon areas are calculated with pyproj.Geod. Edges are geodesically densified to at most 10 km. Each comparison country is projected to its own locally centered Lambert azimuthal equal-area coordinate system in metres. Africa uses LAEA centered at 20°E, 5°N. Minute numerical area normalization (about 0.1 parts per million linearly) matches projected representations to source geodesic areas. Factors are saved in area-preparation.json; they are unrelated to fitting.

Thereafter only rigid rotation and translation are allowed. Local projections alter shape and direction: relocated outlines are planar area comparisons, not exact spherical relocations. Display simplification is zero. A simplified search proxy accelerates tests but never supplies the delivered geometry. The bounded deterministic search uses 125 km grid spacing, 15° rotation steps and 15 km clearance. Failed larger combinations are search outcomes, not impossibility proofs. Saved placements reproduce the successful arrangement without searching again.

All delivered polygons are valid; no repairs were required. Actual display polygons have exactly zero measured outside area and pairwise overlap. Relative area drift through placement is below 7e-16. See draft-validation.json. More comprehensive independent area reasonableness checks, clean-directory reproduction, final visual refinement and submission preparation remain for the next stage.

## Reproduce
Python 3.11 was used. Install requirements in a virtual environment. Raw downloads are excluded from Git; their exact URLs, retrieval timestamp and SHA-256 are retained in data/downloads.json.

```sh
python scripts/download.py
python scripts/prepare.py
python scripts/replay.py
python scripts/render_draft.py
```

Compare the downloaded archive checksum with the saved snapshot before treating it as the frozen input. To repeat the bounded search instead of saved placement, run scripts/place.py. Original geographic, projected comparison, display-preplacement and final layout GeoJSON are separate files. Projected GeoJSON coordinates are metres in the documented per-feature frames, not longitude/latitude interchange files.

## Sources and review
Made with Natural Earth. Natural Earth data are public domain: https://www.naturalearthdata.com/about/terms-of-use/ . Exact source download and source-page URLs are recorded in source-manifest.json and data/downloads.json. Generalized coastlines omit small features; the 2022 release is not a current legal boundary record. Independent published country areas use different border and water conventions and must not be used to resize the silhouettes.

The current course repository identifies 2026 Day 3 as Polygons. Its current template has day, creator, title, thumbnail and source fields. Eventual shared files are assets/thumbnails/2026/03-thomas-hagos.png and _maps_2026/03-thomas-hagos.md. No proposal replacement, commit, push, deployment or pull request has been performed. Submission safeguards and current remote conflicts will be checked again before preparing those files.

This original arrangement belongs to the broader tradition of country-area comparison maps; no existing composition or branding was copied.

Review requested: the four-country selection, partial packing and the explicit island-inclusive Africa definition. Final styling and remaining deliverables follow review.
