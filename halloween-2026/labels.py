"""Bag labels for the MUNBYN thermal printer: 2 in clear round labels, black only.

Builds one SVG per label in printer dots (203 dpi, so 2 in = 406 dots) with the
QR modules on whole dots, then render.js turns each into a 1-bit PNG and a
2 x 2 in PDF.
"""
import json
import pathlib
import subprocess

import segno
from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).parent
OUT = HERE / "build"

DPI = 203
SIZE = 2 * DPI            # 406 dots across the label
C = SIZE / 2              # label center
MODULE = 5                # dots per QR module
QR_SHIFT = -10            # nudge the QR up to leave room for the text below it
LOGO_MODULES = 11         # white knockout in the QR center for the panda

LABELS = {
    "dragon": "https://pandadudeproducts.com/glow/?s=dragon",
    "fidget": "https://pandadudeproducts.com/glow/?s=card",
}

PANDA = (
    '<circle cx="42" cy="34" r="30" fill="#000"/>'
    '<circle cx="158" cy="34" r="30" fill="#000"/>'
    '<ellipse cx="100" cy="96" rx="86" ry="76" fill="#fff" stroke="#000" stroke-width="10"/>'
    '<rect x="26" y="72" width="148" height="34" rx="17" fill="#000"/>'
    '<ellipse cx="100" cy="126" rx="12" ry="9" fill="#000"/>'
    '<path d="M100 135 q10 12 24 6" stroke="#000" stroke-width="8" fill="none" stroke-linecap="round"/>'
)


def qr_svg(url, x0, y0, module, logo_modules):
    """QR as whole-module rects, with a white center square holding the panda."""
    qr = segno.make(url, error="h", micro=False, boost_error=False)
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    lo = (n - logo_modules) // 2
    hi = lo + logo_modules
    rects = []
    for r, row in enumerate(matrix):
        for c, on in enumerate(row):
            if on and not (lo <= r < hi and lo <= c < hi):
                rects.append(f'<rect x="{x0 + c * module}" y="{y0 + r * module}" width="{module}" height="{module}"/>')
    box = logo_modules * module
    pad = module * 0.8
    scale = (box - 2 * pad) / 200
    logo = (
        f'<g transform="translate({x0 + lo * module + pad},{y0 + lo * module + pad + (200 - 176) / 2 * scale}) scale({scale})">'
        f"{PANDA}</g>"
    )
    return n, f'<g fill="#000" shape-rendering="crispEdges">{"".join(rects)}</g>{logo}'


def label_svg(url):
    n, qr = qr_svg(url, 0, 0, MODULE, LOGO_MODULES)
    side = n * MODULE
    x0 = round(C - side / 2)
    y0 = round(C - side / 2 + QR_SHIFT)
    _, qr = qr_svg(url, x0, y0, MODULE, LOGO_MODULES)

    r_top = 145           # baseline radius of the name arc (letters stand outward)
    r_bot = 172           # baseline radius of the website arc (letters hang inward)
    small_y = y0 + side + 24
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
<defs>
  <path id="top" d="M {C - r_top},{C} A {r_top},{r_top} 0 0 1 {C + r_top},{C}"/>
  <path id="bot" d="M {C - r_bot},{C} A {r_bot},{r_bot} 0 0 0 {C + r_bot},{C}"/>
</defs>
<rect width="{SIZE}" height="{SIZE}" fill="#fff"/>
{qr}
<text font-family="Anton" font-size="48" letter-spacing="3" fill="#000" text-anchor="middle">
  <textPath href="#top" startOffset="50%">PANDADUDE</textPath>
</text>
<text font-family="Space Mono" font-weight="700" font-size="21" fill="#000" text-anchor="middle">
  <textPath href="#bot" startOffset="50%">pandadudeproducts.com</textPath>
</text>
<text x="{C}" y="{small_y}" font-family="Archivo" font-weight="800" font-stretch="75%" font-size="15" letter-spacing="0.5" fill="#000" text-anchor="middle">SMALL PARTS · NOT FOR UNDER 3</text>
</svg>"""


FONTS = """<style>
@font-face { font-family: Anton; src: url(../fonts/Anton-Regular.ttf); }
@font-face { font-family: 'Space Mono'; font-weight: 700; src: url(../fonts/SpaceMono-Bold.ttf); }
@font-face { font-family: Archivo; font-weight: 100 900; font-stretch: 62% 125%; src: url(../fonts/Archivo-var.ttf); }
html, body { margin: 0; padding: 0; background: #fff; }
svg { display: block; }
</style>"""


def main():
    OUT.mkdir(exist_ok=True)
    PRINT = HERE / "print"
    PREVIEW = HERE / "previews"
    PRINT.mkdir(exist_ok=True)
    PREVIEW.mkdir(exist_ok=True)
    jobs = []
    for name, url in LABELS.items():
        svg = label_svg(url)
        # PNG: one CSS px per printer dot. PDF: the same drawing at exactly 2 x 2 in.
        (OUT / f"label-{name}-dots.html").write_text(FONTS + svg)
        (OUT / f"label-{name}-2in.html").write_text(
            FONTS + svg.replace(f'width="{SIZE}" height="{SIZE}"', 'width="192" height="192"', 1)
        )
        jobs.append({"html": str(OUT / f"label-{name}-dots.html"), "png": str(OUT / f"label-{name}-raw.png"), "vw": SIZE, "vh": SIZE})
        jobs.append({"html": str(OUT / f"label-{name}-2in.html"), "pdf": str(PRINT / f"Bag-label-{name.upper()}-2in.pdf"), "width": "2in", "height": "2in"})
    (OUT / "label-jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(HERE / "render.js"), str(OUT / "label-jobs.json")], check=True)

    for name in LABELS:
        # Thermal heads print dots on or off, so hand the app a clean 1-bit image.
        img = Image.open(OUT / f"label-{name}-raw.png").convert("L").point(lambda v: 255 if v > 140 else 0).convert("1")
        img.save(PRINT / f"Bag-label-{name.upper()}-203dpi.png", dpi=(DPI, DPI))
        # Preview only: the round die-cut drawn in, so you can see how it sits on the label.
        prev = img.convert("RGB")
        ImageDraw.Draw(prev).ellipse([1, 1, SIZE - 2, SIZE - 2], outline=(200, 0, 0), width=2)
        prev.save(PREVIEW / f"label-{name}.png")
        print("wrote", PRINT / f"Bag-label-{name.upper()}-203dpi.png")


if __name__ == "__main__":
    main()
