# PandaDude Halloween 2026: signs and bag labels

Everything to print is in `print/`. Pictures of each one are in `previews/`.

## What to print

| File | Printer | Paper | How many |
|---|---|---|---|
| `Sign-holder-MEET-PANDADUDE.pdf` | Color | Letter cardstock | 1, goes in the 8.5 x 11 holder |
| `Tent-DRAGONS.pdf` | Color | Letter cardstock | 1 |
| `Tent-CANDY.pdf` | Color | Letter cardstock | 1 |
| `Tent-FIDGETS-home.pdf` | Color | Letter cardstock | 1 if the fidgets stay home |
| `Tent-FIDGETS-party.pdf` | Color | Letter cardstock | 1 if the fidgets go to the party |
| `Bag-label-DRAGON-203dpi.png` | MUNBYN | 2 in clear round | 28, one per dragon bag |
| `Bag-label-FIDGET-203dpi.png` | MUNBYN | 2 in clear round | one per fidget bag |

Print the signs at **100% / Actual size**, never "Fit to page".

**Tent cards:** fold along the dashed line so the words face out on both sides.
The top half is printed upside down on purpose.

**Bag labels (MUNBYN app):** open the PNG, set the label to 50 x 50 mm, scale
100%. Print one, stick it on the white back of a bag and scan it with a phone
before printing the rest. The `-2in.pdf` versions are the same labels if the
app prefers PDF.

## QR codes

All of them open `pandadudeproducts.com/glow/` with a tag the stats page counts:

| Tag | Where |
|---|---|
| `?s=dragon` | dragon bag labels |
| `?s=card` | fidget bag labels |
| `?s=sign` | sign-holder sign, dragon and fidget tent cards at home |
| `?s=party` | party fidget tent card |

Stats: `pandadudeproducts.com/stats?key=...` (key is in the plan).

## Changing something

Words, the dragon count and the tags live in `signs.py` and `labels.py`. Art
is in `assets/art/` (made in OpenArt; the other options are in
`assets/art/options/`). Rebuild with:

```
python3 labels.py
python3 signs.py
```

Needs Python with `segno` and `pillow`, plus Node with Playwright.
