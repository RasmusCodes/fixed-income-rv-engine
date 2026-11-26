"""Copy the terminal (web/) into the personal site's apps folder.

    python scripts/sync_website.py PATH/TO/website [VERSION]

Writes apps/fixed-income/{firv.js, terminal.js, terminal.css, index.html, data/*.json} and
prints the embed snippet for content/projects/fixed-income.md. VERSION is appended to the
script and stylesheet URLs (?v=) so browsers do not keep an old copy.
"""
from __future__ import annotations

import datetime as dt
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def main(site: str, version: str | None = None):
    version = version or dt.date.today().strftime("%Y%m%d") + "a"
    dest = Path(site) / "apps" / "fixed-income"
    (dest / "data").mkdir(parents=True, exist_ok=True)
    for name in ("firv.js", "terminal.js", "terminal.css"):
        shutil.copy2(WEB / name, dest / name)
    for f in sorted((WEB / "data").glob("*.json")):
        shutil.copy2(f, dest / "data" / f.name)
    html = (WEB / "index.html").read_text(encoding="utf-8")
    html = html.replace('href="https://rasmuscodes.github.io/projects/fixed-income/"', 'href="/projects/fixed-income/"')
    for name in ("firv.js", "terminal.js", "terminal.css"):
        html = html.replace(f'"{name}"', f'"{name}?v={version}"')
    (dest / "index.html").write_text(html, encoding="utf-8")
    print(f"copied terminal to {dest}")
    print(f"""
<link rel="stylesheet" href="/apps/fixed-income/terminal.css?v={version}">

<div id="fi-terminal" class="fi-terminal" data-base="/apps/fixed-income/"><p class="fi-loading">Loading the terminal...</p></div>

<script src="/apps/fixed-income/firv.js?v={version}"></script>
<script src="/apps/fixed-income/terminal.js?v={version}"></script>
""")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
