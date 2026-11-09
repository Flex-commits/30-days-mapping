# Ten Minutes of Sunlight

**Day 07 · 10 minute map · 30-Day Map Challenge 2026**
Thomas Hagos

Light leaving the Sun reaches Earth in about eight minutes. Ten minutes on, it has passed us and is still short of Mars.

[Public page](https://flex-commits.github.io/30-days-mapping/ten-minutes-of-sunlight/) · [Full PNG](outputs/ten-minutes-of-sunlight.png) · [600px thumbnail](outputs/07-thomas-hagos.png)

## Method

- Planet positions for **7 November 2026, 00:00 UTC** come from JPL's approximate Keplerian elements (E. M. Standish, valid 1800–2050), solved with Kepler's equation. Orbits are drawn flat in the ecliptic plane; inclination is ignored.
- Light time is Sun-to-planet distance ÷ c (299,792.458 km/s; 1 AU = 149,597,870.7 km). One light-minute is 17,987,547 km; ten minutes is 1.2024 AU.
- On that date: Mercury 2 min 35 s, Venus 6 min 00 s, Earth 8 min 15 s, Mars 13 min 19 s.

## Reproduce

```sh
pip install -r requirements.txt
python scripts/render.py
```

No downloads, no API keys. Fonts: IM FELL English (SIL OFL 1.1), DejaVu Sans (bundled license).
