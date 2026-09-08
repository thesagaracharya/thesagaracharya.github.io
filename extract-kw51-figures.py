#!/usr/bin/env python3
"""
Pull the seven KW51 figures out of your previous index.html and save them as
real image files, so the new page can load them normally.

    python3 extract-kw51-figures.py old-index.html

Writes:  figures/kw51-01.webp ... figures/kw51-07.webp

Why: the figures were embedded as base64 data URIs, which added roughly 5 MB to
every page load, could never be cached by the browser, and had to be re-parsed
each visit. As separate files they are cached, lazy-loaded, and the HTML drops
from ~5 MB to ~200 KB.
"""

import base64
import os
import re
import sys

EXT = {
    "image/webp": "webp",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/svg+xml": "svg",
}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    source = sys.argv[1]
    if not os.path.isfile(source):
        print(f"Cannot find {source}. Pass the path to your old index.html.")
        return 1

    with open(source, encoding="utf-8", errors="replace") as fh:
        html = fh.read()

    pattern = re.compile(r'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=\s]+?)["\')]')
    matches = pattern.findall(html)

    if not matches:
        print("No embedded images found. Is this the file with the base64 figures?")
        return 1

    os.makedirs("figures", exist_ok=True)
    written = 0

    for index, (mime, payload) in enumerate(matches, start=1):
        ext = EXT.get(mime, "bin")
        name = f"figures/kw51-{index:02d}.{ext}"
        try:
            data = base64.b64decode(re.sub(r"\s+", "", payload))
        except Exception as err:  # noqa: BLE001
            print(f"  skipped image {index}: {err}")
            continue
        with open(name, "wb") as out:
            out.write(data)
        print(f"  wrote {name}  ({len(data) / 1024:,.0f} KB)")
        written += 1

    print(f"\nDone. {written} image(s) written to ./figures/")
    if written != 7:
        print(
            "Expected 7 figures. Open the new index.html and check which figure "
            "reports 'Figure not found', then rename the files to match "
            "kw51-01.webp through kw51-07.webp in slide order."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
