# tools/generate_icon.py
# Genere l'icone (icon.png) et l'ecran de lancement (presplash.png) de XAU ORACLE.
# Utilise Pillow. Lance automatiquement dans GitHub Actions avant le build.
#   python tools/generate_icon.py

from PIL import Image, ImageDraw, ImageFont

GOLD = (212, 175, 55, 255)
GOLD_LIGHT = (255, 215, 90, 255)
BG_TOP = (15, 16, 22)
BG_BOTTOM = (28, 24, 12)


def _vertical_gradient(size, top, bottom):
    img = Image.new("RGB", (size, size), top)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        t = y / max(size - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    return img.convert("RGBA")


def _font(size):
    for name in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial_Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _centered(draw, text, font, cx, cy, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, font=font, fill=fill)


def make_icon(path, size=512):
    img = _vertical_gradient(size, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)

    # Anneau doré (l'"oracle")
    m = int(size * 0.10)
    for i, col in enumerate((GOLD, GOLD_LIGHT)):
        off = m + i * int(size * 0.012)
        draw.ellipse([off, off, size - off, size - off],
                     outline=col, width=max(4, int(size * 0.02)))

    # Texte central
    _centered(draw, "XAU", _font(int(size * 0.26)), size / 2, size * 0.42, GOLD_LIGHT)
    _centered(draw, "ORACLE", _font(int(size * 0.13)), size / 2, size * 0.64, GOLD)

    img.save(path)
    print("ecrit:", path)


def make_presplash(path, size=512):
    img = _vertical_gradient(size, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    _centered(draw, "XAU ORACLE", _font(int(size * 0.11)), size / 2, size * 0.46, GOLD_LIGHT)
    _centered(draw, "Haute Probabilite", _font(int(size * 0.05)), size / 2, size * 0.58, GOLD)
    img.save(path)
    print("ecrit:", path)


if __name__ == "__main__":
    make_icon("icon.png")
    make_presplash("presplash.png")
