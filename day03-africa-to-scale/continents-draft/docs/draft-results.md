# Geographic draft results

These are the best saved results of a finite search, not proofs of impossibility. Areas use the definitions in config.json.

| Comparison | Guest area (million km²) | Guest area inside host | Outside host (km²) | Status |
|---|---:|---:|---:|---|
| South America | 17.69 | 98.6% | 252,131 | partial overlay; full containment not found |
| Australia | 7.69 | 100.0% | 0 | verified fit |
| Antarctica | 13.92 | 99.3% | 92,416 | partial overlay; full containment not found |
| Europe | 10.01 | 98.9% | 109,927 | partial overlay; full containment not found |
| North America | 24.24 | 82.3% | 4,295,864 | partial overlay; full containment not found |
| Africa over Asia | 29.90 | 93.8% | 1,853,634 | partial overlay; full containment not found |

The paired South America + Australia and Antarctica + Europe searches also failed to find a complete fit. See outputs/validation.csv for guest overlap, outside area and unique host coverage.

Australia is the only verified complete fit in this draft. South America, Antarctica and Europe are close partial overlays; North America and the reverse Africa-over-Asia comparison have more substantial protrusions. No claim is made that another placement cannot improve these results.

Recommendation for review: use the individual-panel set as honest same-scale overlays, with each comparison continent appearing once, rather than claiming that all continents literally fit. Final layout, country labels, colors and export composition remain for review.

The Asia overlay intersects 35 source country/territory units. The largest covered portions are in China, the Asian part of Russia, India, Kazakhstan, Iran and Mongolia. Exact portions and source-piece coverage classes are in outputs/asia-country-coverage.csv. These are not a collection of whole-country equivalents.

Validation: 242 unique raw country identifiers; all raw geometries valid; no measured area overlap between assembled geographic continents; zero display simplification; rigid placement area drift below 1e-12. Preparation repairs are saved separately. The 11 selected geometry, table and PNG files reproduced byte-for-byte in a fresh directory (docs/clean-rebuild.json).

Pending: review of continent boundaries/islands, historical Antarctic shelf extent, literal fits versus overlays, and the preferred panel structure. Further independent published-area checks and final typography, gallery thumbnail, local page/portfolio and shared-repository proposals follow that review.
