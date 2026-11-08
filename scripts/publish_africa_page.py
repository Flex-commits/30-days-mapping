"""Publish the existing Africa page to the repository's GitHub Pages docs root.
Reuse tracked full-resolution assets through their public raw GitHub URLs.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'day03-africa-to-scale/site/index.html';target=ROOT/'docs/africa-to-scale/index.html';page=source.read_text();repo='https://github.com/Flex-commits/30-days-mapping/blob/main/';raw='https://raw.githubusercontent.com/Flex-commits/30-days-mapping/main/'
def replace(m):
 attr,relative=m.groups();p=(source.parent/relative).resolve();assert p.is_file(),relative;path=p.relative_to(ROOT.resolve()).as_posix();return attr+'="'+(repo if p.suffix=='.md' else raw)+path+'"'
page=re.sub(r'(href|src)="(\.\./[^"#]+)"',replace,page);page=page.replace('<main>','<main><nav><a href="../">← All maps</a></nav>',1);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(page);print(target)
