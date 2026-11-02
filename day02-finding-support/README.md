# Finding Support

NYC’s homelessness service access points. An independent map by Thomas Hagos for Day 02 / Lines, #30DayMapChallenge 2026. AI assisted research, code and design.

## Lines revision

The map now defaults to Lines. Each of the 21 service addresses is linked to the nearest MTA subway or Staten Island Railway station centroid using haversine distance across all 496 station records in the saved MTA snapshot. These are straight-line proximity links, not street paths or transit routes. Buses, ferries, entrances, crossings, step-free access, schedules and bed availability are not modeled. The final edition shows lines only. The copy uses a short first-person question; decorative slogans and the oversized italic headline were removed. Design references: https://work.co/clients/mta/ and https://morphocode.com/announcing-urban-layers/ .

MTA source: https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f . Raw data and metadata are saved in source-data. Retrieved November 2, 2026. No claim of live service status.

Rebuild with `python3 scripts/build_data.py` followed by `python3 scripts/build_rail_links.py`. `build_data.py` alone recreates the service layer without rail fields.

Public map: https://flex-commits.github.io/30-days-mapping/finding-support/

Source: https://github.com/Flex-commits/30-days-mapping/tree/main/day02-finding-support

`outputs/` contains the full map image and 600px gallery thumbnail.

## Deliverables

- `dist/index.html`: interactive city atlas with equal-size service symbols, spatial grouping, search, borough/type/hour filters, directory, audience and source details, and destination-only transit links.
- `dist/finding-support-poster.png`: 2400 × 2760 shareable map image with Manhattan inset.
- `dist/data/locations.json` and `locations.geojson`: all 21 source-linked address points. `rail-links.geojson` contains the 21 nearest-rail connections, with distance and method attributes.
- `source-data/`: source directory, cached Census queries, NYC borough geometry and regional context geometry.

## Run

No web build step or package installation is needed:

```sh
python3 scripts/build_data.py
python3 scripts/build_rail_links.py
python3 -m http.server 8766 --directory dist
```

Open http://127.0.0.1:8766/ . The default basemap, boundaries, fonts and service points are local. Optional street context requests OpenStreetMap tiles. Directions open Google Maps with only the public destination address; this site does not request or record the visitor’s location.

## Reproduce the poster

Python 3.9+ with Matplotlib 3.9.4:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
MPLCONFIGDIR=.mplconfig python scripts/render_poster.py
```

The poster uses a local equirectangular projection centered at 40.7°N. The interactive map uses Leaflet/Web Mercator. Static point labels 01, 03, 04, 09, 12, 14 and 15 in the Manhattan inset correspond to `number` in the JSON and the interactive directory.

## Service data and source hierarchy

Public listings checked November 2, 2026:

1. Adult drop-in (8): https://portal.311.nyc.gov/article/?kanumber=KA-02528
2. Shelter intake (5): https://portal.311.nyc.gov/article/?kanumber=KA-02501 and https://access.nyc.gov/programs/homeless-intake-shelters-and-drop-in-centers-dics/
3. Youth drop-in (8): https://www.nyc.gov/site/dycd/services/runaway-homeless-youth/borough-based-drop-in-centers.page and https://access.nyc.gov/programs/runaway-and-homeless-youth-drop-in-centers/

The eight adult Open Data coordinate pairs were cross-checked with Census address matching. NYC311 current hours take precedence over outdated Open Data comments. The men's intake at 8 East 3rd Street and AFIC at 333 Bowery reflect August 1, 2026 relocations. An older DYCD `/families/borough-based-drop-in-centers.page` directory with different addresses was not used. The Brooklyn youth site’s ZIP was omitted because the directory ZIP differs from address matching.

Open Data background: https://data.cityofnewyork.us/Social-Services/Directory-Of-Homeless-Drop-In-Centers/bmxf-3rd4 . Source row metadata reported an October 8, 2026 update when retrieved in this chat; this does not mean every field was up to date.

## Coordinates and geography

- U.S. Census public address geocoder: https://geocoding.geo.census.gov/geocoder/ . Cached responses and query URLs are saved. **Points are interpolated street locations, not surveyed entrances.** Existing adult points differed by no more than 80 m from the Census matches. Every point falls within its listed borough in the unsimplified official geometry.
- NYC borough boundaries: https://data.cityofnewyork.us/d/gthc-hcne . Cached GeoJSON contains the five boroughs; `build_data.py` simplifies display geometry to approximately 5 m. The original is retained.
- Regional land context: Natural Earth 1:10m administrative states, New York / New Jersey / Connecticut subset, public domain. Source: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_1_states_provinces.geojson . https://www.naturalearthdata.com/about/terms-of-use/ . Subset snapshot retained, so reproduction does not require a new download.
- Optional street context: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright . No bulk tile download is bundled.

`geocode.py` fetches missing cached Census matches. `check_queens.py` records the four Queens queries with their postal localities, because “Queens” alone did not match them. The final builder uses saved successful results and can run offline.

## Interpretation

This map covers publicly listed access points in the three source directories, not every NYC shelter, confidential facility or the location of individual people. A dot does not establish capacity, live vacancy, safety or guaranteed admission. Adult drop-in services, shelter application intake, and youth support are distinct. Listed 24/7 is an official-directory attribute, not an “open now” result. Eligibility, hours and intake should be confirmed through the official source or provider before travel. Counts describe this directory, not neighborhood demand or service adequacy. Built-in spatial groups expand on click; equal-size underlying symbols represent one location each.

## Verification

- 21 distinct IDs; category totals 8 / 5 / 8; all coordinates in the listed borough.
- JavaScript syntax checked.
- Browser checks: Adult filter 8, Queens filter 4, Listed 24/7 filter 18, search “families” 2, full directory 21, intake and youth detail cards, street-context toggle, resets and source modal.
- Responsive checks: 1512 × 982 desktop; 390 × 844 phone with no horizontal overflow. Selected phone marker is positioned above the detail card.
- Poster visually inspected at full output; optional street tiles visibly loaded in local preview. Private deployment verified through Sites publication status; live app access requires the owner's ChatGPT sign-in.

## Libraries and typography

Leaflet 1.9.4 (BSD-2-Clause; `dist/LEAFLET-LICENSE.txt`). DM Sans and Instrument Serif (SIL Open Font License; font licenses in `dist/fonts/`). Third-party data and libraries retain their respective terms; attribution is not a claim of endorsement. This map is not an official City of New York product.


Revision QA: line/point mode switching, distance sorting (Paul’s Place / 6 Av ~0.04 miles first), Queens filtering, nearest-rail detail fields, and longest connection on phone (Project Hospitality—Youth / Tompkinsville SIR ~2.99 miles); 390px viewport with no overflow. Source credits retain one factual AI-assistance note in methods; no claim of entirely unaided authorship.

Final display units: miles throughout, using exactly 1 mile = 1609.344 metres. Original metre fields are retained for reproducible calculations. The interactive scale uses miles at every zoom.
