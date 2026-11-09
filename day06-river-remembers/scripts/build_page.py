"""Assemble the self-contained public page and exactly two MUSA submission files."""
from pathlib import Path
import shutil
from PIL import Image
R=Path(__file__).resolve().parents[1];S=R/'site';A=S/'assets';A.mkdir(parents=True,exist_ok=True)
for n in ['the-river-remembers.png','06-thomas-hagos.png']:shutil.copy2(R/'outputs'/n,A/n)
im=Image.open(R/'outputs/the-river-remembers.png').convert('RGB');im.resize((1800,2160),Image.Resampling.LANCZOS).save(A/'the-river-remembers-preview.jpg',quality=92,optimize=True)
shutil.copytree(R/'fonts',S/'fonts',dirs_exist_ok=True)
source='https://github.com/Flex-commits/30-days-mapping/tree/main/day06-river-remembers';raw='https://raw.githubusercontent.com/Flex-commits/30-days-mapping/main/day06-river-remembers/'
html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The River Remembers — Thomas Hagos</title>
<meta name="description" content="Old bends along the Lower Mississippi: a new USGS water-reference map beside archival details from a 1938 survey. Day 6: Vintage, by Thomas Hagos.">
<meta property="og:title" content="The River Remembers"><meta property="og:description" content="Old bends along the Lower Mississippi. Day 06 · Vintage."><meta property="og:image" content="https://flex-commits.github.io/30-days-mapping/the-river-remembers/assets/the-river-remembers-preview.jpg">
<style>
@font-face{font-family:Vibes;src:url(fonts/calligraphy.ttf) format('truetype');font-display:swap}@font-face{font-family:Fell;src:url(fonts/serif.ttf) format('truetype');font-display:swap}
:root{--paper:#f5eedf;--ink:#263d3c;--muted:#756c5b;--rule:#c7bba1;--rust:#b46b49}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 system-ui,sans-serif}main{max-width:1250px;margin:auto;padding:32px clamp(20px,4vw,64px) 50px}a{color:inherit;text-underline-offset:4px}a:hover{color:var(--rust)}nav{display:flex;justify-content:space-between;gap:20px;font-size:12px;border-bottom:1px solid var(--rule);padding-bottom:20px}.eyebrow{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}header{text-align:center;margin:50px auto 35px;max-width:850px}h1{font:clamp(52px,8vw,105px)/1.15 Vibes,cursive;margin:25px 0 8px;font-weight:400}header .subtitle{font:clamp(21px,3vw,29px)/1.4 Fell,serif;margin:12px 0}.intro{max-width:640px;margin:25px auto}.links{display:flex;gap:15px 25px;flex-wrap:wrap;justify-content:center;font-size:14px}.map{margin:40px 0 15px}.map img{display:block;width:100%;height:auto;border:1px solid var(--rule)}figcaption{font-size:12px;color:var(--muted);margin-top:12px}.reading{display:grid;grid-template-columns:1fr 1fr;gap:50px;border-top:1px solid var(--rule);margin-top:48px;padding-top:25px}h2{font:28px/1.25 Fell,serif;font-weight:400;margin:15px 0}p{margin:15px 0}.reading p{font-size:15px}.sources{border-top:1px solid var(--rule);margin-top:40px;padding-top:20px;font-size:13px}.sources h2{font-size:23px}.sources li{margin:10px 0}footer{border-top:1px solid var(--rule);margin-top:35px;padding-top:20px;font-size:12px;color:var(--muted)}:focus-visible{outline:2px solid var(--rust);outline-offset:4px}@media(max-width:650px){.reading{grid-template-columns:1fr;gap:10px}main{padding-top:20px}nav{font-size:11px}header{margin-top:35px}.map{margin-left:-10px;margin-right:-10px}.links{gap:10px 20px}}
</style></head><body><main>
<nav aria-label="Project navigation"><a href="../">← All maps</a><span>THOMAS HAGOS · MUSA 2026</span></nav>
<header><p class="eyebrow">30-Day Map Challenge / Day 06 / Vintage</p><h1>The River Remembers</h1><p class="subtitle">Old bends along the Lower Mississippi</p>
<p class="intro">A river moves. But it doesn’t erase every trace. Near Helena, Arkansas, lakes still hold the curves of old Mississippi River bends.</p>
<div class="links"><a href="assets/the-river-remembers.png" download>Download the full map</a><a href="SOURCE">Code, data &amp; methods</a><a href="RAWdocs/linkedin.md">Post draft</a></div></header>
<figure class="map"><a href="assets/the-river-remembers.png" aria-label="Open the full-resolution map"><img src="assets/the-river-remembers-preview.jpg" width="1800" height="2160" alt="Cream-colored atlas composition: a teal Mississippi River and rust-colored lakes near Helena, Arkansas, alongside two credited 1938 survey details showing earlier channel positions. Calligraphic title: The River Remembers."></a><figcaption>Original reference cartography and layout by Thomas Hagos. Archival details: Mississippi River Commission, 1938, Sheet 5; scan courtesy of Michigan State University Libraries.</figcaption></figure>
<section class="reading"><div><p class="eyebrow">The landscape</p><h2>The loop outlasts the channel.</h2><p>Moon Lake is an oxbow of the Mississippi. The shape of the old bend remains beside a river that now follows a different path.</p><p>On the reference map, teal marks river and stream areas. Rust marks lakes and ponds—not a classification of every lake as an oxbow. The lake layer omits features smaller than about 7.4 acres.</p></div>
<div><p class="eyebrow">The archive</p><h2>A different way to read a river.</h2><p>The two details come from the River Commission’s 1938 <em>Early Stream Channels</em> map. Its legend records surveys from 1765, 1820–1830, 1881–1893 and 1930–1932. Original channel colors are retained, including dashed pink for an indeterminate 1820–1830 bankline.</p><p>The reference map and archive have different scales and orientations. The scan has not been aligned to USGS geometry, so this is a visual comparison—not a measurement of channel movement.</p></div></section>
<section class="sources"><h2>Sources and the small print</h2><ul>
<li><a href="https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer">USGS National Hydrography Dataset</a>, saved November 8, 2026. Features have mixed source dates; this is not a survey of today’s water level. NAD83 / UTM zone 15N; five-mile reference scale; grid north.</li>
<li><a href="RAWdata/raw/mrc-1938-sheet05.pdf">Complete 1938 archival sheet</a>, including its original legend and scale. Federal government map, public domain in the U.S. <a href="https://blogs.loc.gov/maps/2016/06/the-meandering-mississippi/">Library of Congress account of the series</a>.</li>
<li><a href="https://www.mdwfp.com/fishing-boating/lakes/moon-lake">Mississippi Department of Wildlife, Fisheries, and Parks</a> confirms Moon Lake’s oxbow origin. No exact cutoff year is inferred here.</li>
<li><a href="https://www.naturalearthdata.com/">Natural Earth</a> supplies the small U.S. locator. Source records, geometry selections, licenses and checksums are in the <a href="RAWdata/source-manifest.json">source manifest</a>.</li>
</ul><p>No migration rates, exact historical alignments or complete reconstructed channels are claimed. NHD water areas do not include every small stream, pond or dry former channel. The map is for geographic interpretation, not navigation.</p></section>
<footer>Thomas Hagos · University of Pennsylvania, MUSA · 2026<br>Original cartography, layout and text: CC BY 4.0. Source credits retained. Great Vibes and IM FELL English: SIL OFL 1.1; DejaVu Sans: bundled open font license.</footer>
</main></body></html>'''.replace('SOURCE',source).replace('RAW',raw)
(S/'index.html').write_text(html)
md='''---
day: 6
creator: Thomas Hagos
title: The River Remembers
thumbnail: /assets/thumbnails/2026/06-thomas-hagos.png
source: https://github.com/Flex-commits/30-days-mapping/tree/main/day06-river-remembers/scripts
---

**Old bends along the Lower Mississippi.**

A river moves, but it doesn’t erase every trace. I mapped river and lake areas near Helena, Arkansas, and paired the new reference map with two credited details from the Mississippi River Commission’s 1938 *Early Stream Channels* sheet.

[Explore the map](https://flex-commits.github.io/30-days-mapping/the-river-remembers/) · [Code, source snapshots and methods](https://github.com/Flex-commits/30-days-mapping/tree/main/day06-river-remembers)

![The River Remembers: a new water-reference map beside two credited 1938 Mississippi River Commission details](https://flex-commits.github.io/30-days-mapping/the-river-remembers/assets/the-river-remembers-preview.jpg)

The reference map uses mixed-date USGS NHD geometry, downloaded November 8, 2026; the archival colors retain the original survey periods. The views have different scales and orientations and are not precisely registered. No migration rates, current-water-level survey or complete reconstructed historical channels are claimed.

Original reference cartography, design and text: Thomas Hagos, CC BY 4.0. Archival details: Mississippi River Commission, August 1938, Sheet 5; scan: Michigan State University Libraries. USGS data, federal source map and Natural Earth locator: public domain in the U.S. Font licenses and full source records are included in the project.
'''
(R/'submission/_maps_2026/06-thomas-hagos.md').write_text(md);shutil.copy2(R/'outputs/06-thomas-hagos.png',R/'submission/assets/thumbnails/2026/06-thomas-hagos.png')
print('Built static page and two submission files.')
