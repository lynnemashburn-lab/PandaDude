"""Halloween signs for the color printer, all on US Letter.

- Business sign for the 8.5 x 11 sign holder.
- Fold-over tent cards for the bowls: the page folds across the middle, and the
  top half is printed upside down so both faces read right way up once it stands.

Artwork comes from assets/art/<name>.png (made in OpenArt, no words in it). All
words and QR codes are laid on top here so the spelling, the count and the
stats tags stay exact.
"""
import json
import pathlib
import subprocess

from PIL import Image

from labels import PANDA, qr_svg

HERE = pathlib.Path(__file__).parent
OUT = HERE / "build"
PRINT = HERE / "print"
PREVIEW = HERE / "previews"
ART = HERE / "assets" / "art"

DRAGONS = 40
QR = "https://pandadudeproducts.com/glow/?s={}"
URL_SHOWN = "pandadudeproducts.com/glow"


def qr(tag):
    m = 10
    n, body = qr_svg(QR.format(tag), 0, 0, m, 11)
    q = 2 * m
    return (
        f'<svg class="qr" viewBox="{-q} {-q} {n * m + 2 * q} {n * m + 2 * q}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="{-q}" y="{-q}" width="{n * m + 2 * q}" height="{n * m + 2 * q}" fill="#fff"/>{body}</svg>'
    )


def panda(cls="panda"):
    return f'<svg class="{cls}" viewBox="0 0 200 176" xmlns="http://www.w3.org/2000/svg">{PANDA}</svg>'


def art(name, cls="art"):
    path = ART / f"{name}.png"
    if path.exists():
        clean = OUT / f"art-{name}.png"
        img = Image.open(path).convert("RGB")
        img.point(lambda v: min(255, round(v * 255 / 236))).save(clean)
        return f'<img class="{cls}" src="{clean.resolve().as_uri()}">'
    return f'<div class="{cls} missing">art: {name}</div>'


CSS = """
@font-face { font-family: Anton; src: url(../fonts/Anton-Regular.ttf); }
@font-face { font-family: 'Space Mono'; font-weight: 400; src: url(../fonts/SpaceMono-Regular.ttf); }
@font-face { font-family: 'Space Mono'; font-weight: 700; src: url(../fonts/SpaceMono-Bold.ttf); }
@font-face { font-family: Archivo; font-weight: 100 900; font-stretch: 62% 125%; src: url(../fonts/Archivo-var.ttf); }
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; }
body { width: 8.5in; height: 11in; overflow: hidden; color: #111; font-family: Archivo, sans-serif; }
:root { --ink: #111; --glow: #b6ff5c; --glow-dim: #6fb12a; }
.band {
  display: flex; align-items: center; justify-content: center; gap: 0.14in;
  background: var(--glow); border: 3px solid var(--ink); border-radius: 0.14in;
  font-family: 'Space Mono'; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
}
.band .panda { height: 0.34in; }
.head { font-family: Anton; text-transform: uppercase; line-height: 0.95; letter-spacing: 0.01em; margin: 0; }
.qr { display: block; width: 100%; height: auto; }
.missing { display: flex; align-items: center; justify-content: center; border: 2px dashed #aaa; color: #999; font-family: 'Space Mono'; }
.art { object-fit: contain; display: block; }
.mono { font-family: 'Space Mono'; font-weight: 700; }
.fine { font-size: 8.5pt; color: #333; line-height: 1.3; }

/* Tent cards: two 8.5 x 5.5 faces, the top one upside down. */
.face { position: absolute; left: 0; width: 8.5in; height: 5.5in; padding: 0.42in 0.45in 0.4in; display: flex; flex-direction: column; }
.face.top { top: 0; transform: rotate(180deg); }
.face.bottom { top: 5.5in; }
.fold { position: absolute; top: 5.5in; left: 0.3in; right: 0.3in; border-top: 1.5px dashed #9a9a9a; }
.fold span { position: absolute; right: 0; top: -0.17in; font: 700 7pt 'Space Mono'; color: #9a9a9a; letter-spacing: 0.1em; }
.face .band { height: 0.46in; font-size: 11pt; flex: none; }
.face .body { flex: 1; display: grid; grid-template-columns: 1fr 2.45in; column-gap: 0.3in; padding-top: 0.18in; min-height: 0; }
.face .left { display: flex; flex-direction: column; min-width: 0; }
.face .right { display: flex; flex-direction: column; align-items: center; justify-content: space-between; min-height: 0; }
.face .lede { font-weight: 800; font-size: 18pt; line-height: 1.15; margin: 0.12in 0 0.06in; }
.face .line { font-weight: 600; font-size: 13.5pt; line-height: 1.25; margin: 0.04in 0 0; }
.face .foot { margin-top: auto; }
.face .allgone { font-weight: 700; font-size: 11pt; line-height: 1.25; margin: 0 0 0.05in; }
.scan { width: 1.78in; text-align: center; }
.scan .cap { font-family: Anton; font-size: 11.5pt; letter-spacing: 0.03em; line-height: 1.05; margin-top: 0.04in; text-transform: uppercase; }
.scan .url { font: 700 7.2pt 'Space Mono'; margin-top: 0.02in; }
"""


def page(body, extra_css=""):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}{extra_css}</style></head><body>{body}</body></html>"


def tent(face_html, cls):
    faces = "".join(f'<div class="face {pos} {cls}">{face_html}</div>' for pos in ("top", "bottom"))
    return page(faces + '<div class="fold"><span>FOLD HERE</span></div>')


def band(text):
    return f'<div class="band">{panda()}<span>{text}</span></div>'


def scan_block(tag, caption):
    return f'<div class="scan">{qr(tag)}<div class="cap">{caption}</div><div class="url">{URL_SHOWN}</div></div>'


def dragon_tent():
    face = f"""
{band("PandaDude &nbsp;★&nbsp; Happy Halloween")}
<div class="body">
  <div class="left">
    <h1 class="head" style="font-size:78pt">Free glow<br>dragon</h1>
    <p class="lede">One per person, please. There are {DRAGONS}.</p>
    <p class="line">Carter, age 8, printed them in this house.</p>
    <p class="line">Charge it in light, then turn the lights off.</p>
    <div class="foot">
      <p class="allgone">All gone? Sorry, {DRAGONS} was the limit. Scan anyway: bigger dragons, porch pickup, no shipping.</p>
      <p class="fine">Small parts: not for kids under 3. Dragon designs by Cinderwing3D, printed under license.</p>
    </div>
  </div>
  <div class="right">
    {art("dragon", "art tentart")}
    {scan_block("sign", "Scan: story + 10% off")}
  </div>
</div>"""
    return tent(face, "dragon")


def fidget_home_tent():
    face = f"""
{band("PandaDude &nbsp;★&nbsp; Happy Halloween")}
<div class="body">
  <div class="left">
    <h1 class="head" style="font-size:78pt">Free<br>fidgets</h1>
    <p class="lede">Take one! Carter printed every one.</p>
    <p class="line">Glow ones: charge it in light, then turn the lights off.</p>
    <div class="foot">
      <p class="fine">PandaDude Products, a kid-run 3D print shop. Small parts: not for kids under 3.</p>
    </div>
  </div>
  <div class="right">
    {art("fidget", "art tentart")}
    {scan_block("sign", "Scan: story + 10% off")}
  </div>
</div>"""
    return tent(face, "fidget")


def fidget_party_tent():
    face = f"""
{band("PandaDude &nbsp;★&nbsp; Kid-run 3D print shop")}
<div class="body">
  <div class="left">
    <h1 class="head" style="font-size:58pt">Carter, age 8,<br>printed these!</h1>
    <p class="lede">Take one!</p>
    <p class="line">PandaDude Products is his kid-run 3D print shop in Forsyth County.</p>
    <p class="line">Glow ones: charge it in light, then turn the lights off.</p>
    <div class="foot">
      <p class="fine">Small parts: not for kids under 3.</p>
    </div>
  </div>
  <div class="right">
    {art("fidget", "art tentart")}
    {scan_block("party", "Scan: story + 10% off")}
  </div>
</div>"""
    return tent(face, "party")


def candy_tent():
    face = f"""
{band("PandaDude &nbsp;★&nbsp; Happy Halloween")}
<div class="candy">
  {art("candy", "art candyart")}
  <div>
    <h1 class="head" style="font-size:104pt">Candy<br>bars</h1>
    <p class="lede" style="font-size:30pt;margin-top:0.14in">Take one too.</p>
  </div>
</div>
<div class="foot"><p class="fine">Happy Halloween from Carter and the panda.</p></div>"""
    extra = """
.face .candy { flex: 1; display: grid; grid-template-columns: 3.2in 1fr; column-gap: 0.35in; align-items: center; padding-top: 0.15in; min-height: 0; }
.candyart { width: 3.2in; height: 3.2in; }
"""
    return tent(face, "candy").replace("</style>", extra + "</style>", 1)


TENT_EXTRA = ".tentart { width: 2.45in; height: 1.72in; }"


def business_sign():
    body = f"""
<div class="biz">
  <div class="band bigband">{panda()}<span>Take 1 from each bowl!</span>{panda()}</div>
  {art("panda", "art bizart")}
  <h1 class="head" style="font-size:80pt;text-align:center;margin-top:0.08in">Meet PandaDude</h1>
  <p class="who">Carter, age 8, printed these right here in this house.</p>
  <p class="what">PandaDude Products is his kid-run 3D print shop in Forsyth County: articulated dragons that wiggle, curl and click, printed one thin layer at a time.</p>
  <div class="scanrow">
    <div class="bigqr">{qr("sign")}</div>
    <div class="head" style="font-size:40pt">Scan for<br>the story<br>+ 10% off</div>
  </div>
  <p class="fine" style="text-align:center;margin-top:auto">Dragon designs by Cinderwing3D, printed under license. Small parts: not for kids under 3.</p>
</div>"""
    extra = """
.biz { width: 8.5in; height: 11in; padding: 0.5in 0.55in 0.45in; display: flex; flex-direction: column; align-items: stretch; }
.biz .bigband { height: 0.85in; flex: none; font-family: Anton; font-weight: 400; font-size: 36pt; letter-spacing: 0.02em; gap: 0.22in; }
.biz .bigband .panda { height: 0.52in; }
.bizart { width: 100%; height: 3.7in; margin-top: 0.15in; }
.biz .who { font-weight: 800; font-size: 20pt; text-align: center; margin: 0.12in 0 0; }
.biz .what { font-weight: 500; font-size: 13pt; text-align: center; margin: 0.1in 0.25in 0; line-height: 1.35; }
.scanrow { display: flex; justify-content: center; align-items: center; gap: 0.4in; margin-top: 0.3in; }
.bigqr { width: 2.2in; }
"""
    return page(body, extra)


SIGNS = {
    "Sign-holder-MEET-PANDADUDE": business_sign,
    "Tent-DRAGONS": dragon_tent,
    "Tent-CANDY": candy_tent,
    "Tent-FIDGETS-home": fidget_home_tent,
    "Tent-FIDGETS-party": fidget_party_tent,
}


def main():
    for d in (OUT, PRINT, PREVIEW):
        d.mkdir(exist_ok=True)
    jobs = []
    for name, make in SIGNS.items():
        html = make().replace("</style>", TENT_EXTRA + "</style>", 1)
        src = OUT / f"{name}.html"
        src.write_text(html)
        jobs.append({"html": str(src), "pdf": str(PRINT / f"{name}.pdf"), "width": "8.5in", "height": "11in"})
        jobs.append({"html": str(src), "png": str(PREVIEW / f"{name}.png"), "vw": 816, "vh": 1056, "scale": 1})
    (OUT / "sign-jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(HERE / "render.js"), str(OUT / "sign-jobs.json")], check=True)


if __name__ == "__main__":
    main()
