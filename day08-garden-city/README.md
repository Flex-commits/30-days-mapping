# The Social City

**Day 08 · Utopia · 30-Day Map Challenge 2026**
Thomas Hagos

Ebenezer Howard's group of "slumless, smokeless cities" (1898), redrawn to scale: 250,000 people in seven towns, joined by rail and canal, with farms and forests between them. One of the towns is named Philadelphia.

[Public page](https://flex-commits.github.io/30-days-mapping/the-garden-city/) · [Full PNG](outputs/the-social-city.png) · [600px thumbnail](outputs/08-thomas-hagos.png)

## Source

Ebenezer Howard, *To-morrow: A Peaceful Path to Real Reform* (London: Swan Sonnenschein, 1898), Diagram No. 7, "Group of Slumless Smokeless Cities". The diagram was dropped from the 1902 edition, *Garden Cities of To-morrow*. Scan: [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Garden_Cities_of_To-Morrow_(book)) (public domain).

## Figures used

Printed on the diagram:

| | Area | Population |
|---|---|---|
| Whole group | 66,000 acres | 250,000 |
| Central City | 12,000 acres | 58,000 |
| Each of six garden cities (Garden City, Gladstone, Justitia, Rurisville, Philadelphia, Concord) | 9,000 acres | 32,000 |

The printed figures check out: 6 × 9,000 + 12,000 = 66,000 acres, and 6 × 32,000 + 58,000 = 250,000 people.

Derived and measured:

- Circles come from the printed areas (radius = √(area/π)): whole group 5.73 mi, Central City boundary 2.44 mi, each town of 1,000 acres 0.71 mi (Howard, ch. 1). The six 9,000-acre sectors fill the ring between 2.44 mi and 5.73 mi exactly.
- The garden-city ring and inter-municipal canal (4.20 mi), the inter-municipal railway (3.18 mi) and the Central City's built area (1.14 mi) are measured against the diagram's own two-mile scale bar. The measured outer radius matches the 66,000-acre figure.
- Each town is drawn with the ring plan of Howard's Diagram No. 2: park, Grand Avenue and six boulevards.
- The countryside labels are Howard's own words, placed roughly where he put them, including the period's asylums and "homes for inebriates".

## Reproduce

```sh
pip install -r requirements.txt
python scripts/render.py
```

No downloads, no API keys. Fonts: IM FELL English (SIL OFL 1.1), DejaVu Sans (bundled license).
