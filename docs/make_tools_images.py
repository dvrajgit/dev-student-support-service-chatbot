"""Generate simple icon/illustration images for each tool & library.

Produces one PNG per tool under docs/tools_images/ with a branded colour
tile, a hand-drawn vector glyph and the tool name. These images are
embedded in the Tools & Libraries presentation.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).parent / "tools_images"
OUT_DIR.mkdir(exist_ok=True)

W, H = 900, 700
CX = W // 2
ICON_CY = 290  # centre of icon area


def font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    p = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(p), size)


def centered(draw, cx, y, text, fnt, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (r - l) / 2 - l, y), text, font=fnt, fill=fill)


def base_card(bg, accent):
    img = Image.new("RGB", (W, H), (250, 251, 253))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 60, W - 60, H - 60), radius=48, fill=bg)
    d.ellipse((CX - 150, ICON_CY - 150, CX + 150, ICON_CY + 150), fill=accent)
    return img, d


def finish(img, d, name, accent):
    centered(d, CX, 500, name, font(60), accent)


# ---- individual icon painters (drawn inside the accent circle) ----

def ic_python(d, fg):
    # two interlocking rounded rectangles (snake bodies)
    d.rounded_rectangle((CX - 70, ICON_CY - 90, CX + 10, ICON_CY + 10), 30, fill=(53, 114, 165))
    d.rounded_rectangle((CX - 10, ICON_CY - 10, CX + 70, ICON_CY + 90), 30, fill=(255, 212, 59))
    d.ellipse((CX - 55, ICON_CY - 78, CX - 39, ICON_CY - 62), fill=(255, 255, 255))
    d.ellipse((CX + 39, ICON_CY + 62, CX + 55, ICON_CY + 78), fill=(53, 114, 165))


def ic_flask(d, fg):
    d.line([(CX - 30, ICON_CY - 80), (CX - 30, ICON_CY - 20), (CX - 70, ICON_CY + 70),
            (CX + 70, ICON_CY + 70), (CX + 30, ICON_CY - 20), (CX + 30, ICON_CY - 80)],
           fill=fg, width=10, joint="curve")
    d.line([(CX - 45, ICON_CY - 80), (CX + 45, ICON_CY - 80)], fill=fg, width=10)
    d.line([(CX - 48, ICON_CY + 30), (CX + 48, ICON_CY + 30)], fill=(90, 200, 250), width=14)


def ic_brain(d, fg):
    # scikit-learn: three connected nodes (mini neural net)
    pts = [(CX - 70, ICON_CY), (CX + 10, ICON_CY - 70), (CX + 10, ICON_CY + 70), (CX + 70, ICON_CY)]
    for a in range(len(pts)):
        for b in range(a + 1, len(pts)):
            d.line([pts[a], pts[b]], fill=fg, width=6)
    for p in pts:
        d.ellipse((p[0] - 20, p[1] - 20, p[0] + 20, p[1] + 20), fill=fg)


def ic_disk(d, fg):
    # joblib: floppy disk (save)
    d.rounded_rectangle((CX - 75, ICON_CY - 75, CX + 75, ICON_CY + 75), 14, fill=fg)
    d.rectangle((CX - 45, ICON_CY - 75, CX + 45, ICON_CY - 25), fill=(55, 71, 79))
    d.rectangle((CX + 15, ICON_CY - 70, CX + 38, ICON_CY - 30), fill=fg)
    d.rounded_rectangle((CX - 45, ICON_CY + 5, CX + 45, ICON_CY + 60), 6, fill=(55, 71, 79))


def ic_globe(d, fg):
    b = (CX - 78, ICON_CY - 78, CX + 78, ICON_CY + 78)
    d.ellipse(b, outline=fg, width=8)
    d.line([(CX, ICON_CY - 78), (CX, ICON_CY + 78)], fill=fg, width=6)
    d.ellipse((CX - 78, ICON_CY - 40, CX + 78, ICON_CY + 40), outline=fg, width=6)
    d.ellipse((CX - 40, ICON_CY - 78, CX + 40, ICON_CY + 78), outline=fg, width=6)
    d.line([(CX - 78, ICON_CY), (CX + 78, ICON_CY)], fill=fg, width=6)


def ic_robot(d, fg):
    d.rounded_rectangle((CX - 70, ICON_CY - 50, CX + 70, ICON_CY + 70), 20, fill=fg)
    d.line([(CX, ICON_CY - 80), (CX, ICON_CY - 50)], fill=fg, width=8)
    d.ellipse((CX - 8, ICON_CY - 95, CX + 8, ICON_CY - 79), fill=fg)
    d.ellipse((CX - 45, ICON_CY - 20, CX - 15, ICON_CY + 10), fill=(244, 91, 66))
    d.ellipse((CX + 15, ICON_CY - 20, CX + 45, ICON_CY + 10), fill=(244, 91, 66))
    d.line([(CX - 35, ICON_CY + 40), (CX + 35, ICON_CY + 40)], fill=(244, 91, 66), width=8)


def _tag(d, fg, bg):
    centered(d, CX, ICON_CY - 55, "</>", font(90), bg)


def ic_html(d, fg):
    _tag(d, fg, (227, 79, 38))


def ic_css(d, fg):
    _tag(d, fg, (38, 77, 228))


def ic_js(d, fg):
    d.rectangle((CX - 70, ICON_CY - 70, CX + 70, ICON_CY + 70), fill=(30, 30, 30))
    centered(d, CX, ICON_CY - 48, "JS", font(90), (247, 223, 30))


def ic_json(d, fg):
    centered(d, CX, ICON_CY - 55, "{ }", font(96), (67, 160, 71))


def ic_check(d, fg):
    d.line([(CX - 55, ICON_CY), (CX - 15, ICON_CY + 45), (CX + 60, ICON_CY - 55)],
           fill=fg, width=18, joint="curve")


TOOLS = [
    ("python", ic_python, "Python", (38, 50, 71), (255, 255, 255)),
    ("flask", ic_flask, "Flask", (25, 25, 25), (245, 245, 245)),
    ("scikit_learn", ic_brain, "scikit-learn", (247, 148, 29), (41, 100, 140)),
    ("joblib", ic_disk, "joblib", (55, 71, 79), (129, 212, 250)),
    ("requests", ic_globe, "requests", (33, 33, 90), (120, 180, 255)),
    ("groq", ic_robot, "Groq LLM API", (244, 91, 66), (255, 255, 255)),
    ("html5", ic_html, "HTML5", (227, 79, 38), (255, 255, 255)),
    ("css3", ic_css, "CSS3", (38, 77, 228), (255, 255, 255)),
    ("javascript", ic_js, "JavaScript", (30, 30, 30), (247, 223, 30)),
    ("json", ic_json, "JSON Data", (30, 90, 45), (255, 255, 255)),
    ("unittest", ic_check, "unittest", (94, 53, 177), (76, 217, 100)),
]


for fname, painter, name, bg, accent in TOOLS:
    img, d = base_card(bg, accent)
    painter(d, bg)
    finish(img, d, name, accent)
    img.save(OUT_DIR / f"{fname}.png")

print(f"Generated {len(TOOLS)} images in {OUT_DIR}")
