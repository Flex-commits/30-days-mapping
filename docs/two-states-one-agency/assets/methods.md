# Day 12 — Power: Two States. One Agency.

**Live page:** https://flex-commits.github.io/30-days-mapping/two-states-one-agency/

The line between New York and New Jersey runs down the middle of the Hudson. In 1921 the two states put their shared port under a single agency, the Port Authority of New York and New Jersey. This map shows only that idea: the state line drawn down the river, and the five Hudson crossings the agency built or took over, stitched across it in vermilion.

| Year | Crossing | Agency role |
| --- | --- | --- |
| 1908 / 1909 | Hudson & Manhattan tubes (PATH) | taken over in 1962 |
| 1927 | Holland Tunnel | under agency control from 1930 |
| 1931 | George Washington Bridge | built by the agency |
| 1937 | Lincoln Tunnel | built by the agency |

A companion to Day 5, [Seeing the Hudson](../day05-seeing-hudson/), where this map began as section 04.

## Outputs

- `outputs/two-states-one-agency.png`: landscape sheet, 3500 × 3000
- `outputs/two-states-one-agency-phone.png`: 4:5 phone and LinkedIn edition, 1600 × 2000
- `outputs/12-thomas-hagos.png`: 600 × 600 gallery thumbnail

## Data and method

- **Land:** U.S. Census Bureau 2024 cartographic boundary counties (1:500k), minus TIGER/Line 2024 area-water polygons of at least 5 ha for the 13 counties in frame, dissolved by state.
- **State line:** the shared boundary of the TIGER/Line 2024 New York and New Jersey state polygons.
- **Crossings:** approximate portal or terminal anchors from public maps, each snapped to its own state's shoreline (all snaps under 600 m). These are schematic bank-to-bank links, not surveyed alignments.
- **Facts:** every date and claim is sourced in `data/port-authority.json`; checks and rejected claims are in [docs/research-notes.md](docs/research-notes.md).
- **Projection:** NAD83 / UTM zone 18N (EPSG:26918), north up.
- **Lettering:** IM FELL English roman and italic by Igino Marini (SIL OFL 1.1); DejaVu Sans for small print. Font hashes are in `data/sources.json`.

## Reproduce

Python 3.9. From this folder:

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/prepare.py      # downloads Census inputs if absent, checks hashes
python scripts/render.py
python scripts/build_page.py
python scripts/validate.py
```

The built page in `site/` is copied to `docs/two-states-one-agency/` for GitHub Pages.

Map and text: Thomas Hagos.
