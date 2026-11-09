# The Garden City

**Day 08 · Utopia · 30-Day Map Challenge 2026**
Thomas Hagos

Ebenezer Howard's town of tomorrow, drawn to scale from his 1898 text: 30,000 people on 1,000 acres, held inside 5,000 acres of countryside.

[Public page](https://flex-commits.github.io/30-days-mapping/the-garden-city/) · [Full PNG](outputs/the-garden-city.png) · [600px thumbnail](outputs/08-thomas-hagos.png)

## Dimensions used

From Ebenezer Howard, *To-morrow: A Peaceful Path to Real Reform* (1898), reissued as *Garden Cities of To-morrow* (1902):

- Estate: 6,000 acres; town: 1,000 acres at the centre; agricultural belt: 5,000 acres.
- Town radius: 1,240 yards from centre to circumference.
- Central garden: 5½ acres. Central Park: 145 acres, ringed by the Crystal Palace glass arcade.
- Grand Avenue: 420 ft wide. Six boulevards, 120 ft wide, divide the town into six wards.
- Factories, warehouses and markets at the outer ring, on a circular railway.
- Population: 30,000 in the town, 2,000 on the agricultural estate.

Circles are computed from those areas (radius = √(area/π)). Widths the text does not give (the civic ring, the factory belt, Grand Avenue's distance from the centre) are estimates. Howard called his drawings diagrams, not plans for a real site, and this map follows them.

## Reproduce

```sh
pip install -r requirements.txt
python scripts/render.py
```

No downloads, no API keys. Fonts: IM FELL English (SIL OFL 1.1), DejaVu Sans (bundled license).
