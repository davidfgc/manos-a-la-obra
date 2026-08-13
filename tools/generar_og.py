"""Genera las imagenes Open Graph (1200x630) por seccion, sin navegador.

Uso:
    uv run python tools/generar_og.py

Requiere Pillow (dependencia de desarrollo) y la fuente en
tools/assets/Inter.ttf. Los PNG resultantes viven en static/og/ y se commitean;
el runtime solo los sirve como estaticos.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = Path(__file__).resolve().parent / "assets" / "Inter.ttf"
SALIDA = RAIZ / "static" / "og"

W, H = 1200, 630
MARGEN = 84

# Paleta del sistema de diseno.
INK = (14, 27, 42)
MUTED = (76, 90, 103)
WHITE = (255, 255, 255)
AZUL = (15, 76, 129)
FLAG = [(255, 205, 0), (0, 56, 168), (206, 17, 38)]  # bandera de Colombia

# label / titulo (CTA) / subtitulo / acento (triage), por seccion.
SECCIONES = {
    "home": {
        "label": "TERREMOTO EN COLOMBIA",
        "titulo": "Encontrá cómo ayudar",
        "sub": "Archivos 3D para imprimir y puntos de acopio, curados y actualizados.",
        "acento": (15, 76, 129),
    },
    "impresion": {
        "label": "IMPRESIÓN 3D",
        "titulo": "Imprimí una férula en 3D",
        "sub": "Modelos validados, ordenados por prioridad. Tu impresora puede ayudar hoy.",
        "acento": (193, 18, 31),
    },
    "puntos": {
        "label": "PUNTOS DE ACOPIO",
        "titulo": "Encontrá un punto de acopio",
        "sub": "Direcciones, horarios y qué reciben. Colombia y el exterior.",
        "acento": (43, 147, 72),
    },
}


def fuente(size, weight="Regular"):
    f = ImageFont.truetype(str(FUENTE), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def envolver(draw, texto, font, max_w):
    lineas, linea = [], ""
    for palabra in texto.split():
        prueba = (linea + " " + palabra).strip()
        if draw.textlength(prueba, font=font) <= max_w or not linea:
            linea = prueba
        else:
            lineas.append(linea)
            linea = palabra
    if linea:
        lineas.append(linea)
    return lineas


def corazon(draw, x, y, s, color):
    """Corazon simple con dos circulos y un triangulo."""
    draw.ellipse([x, y, x + s * 0.55, y + s * 0.55], fill=color)
    draw.ellipse([x + s * 0.45, y, x + s, y + s * 0.55], fill=color)
    draw.polygon(
        [(x + s * 0.04, y + s * 0.34), (x + s * 0.96, y + s * 0.34), (x + s / 2, y + s)],
        fill=color,
    )


def tarjeta(cfg):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # Barra de acento superior (color de triage de la seccion).
    d.rectangle([0, 0, W, 12], fill=cfg["acento"])

    # Lockup de marca: chip azul con corazon + wordmark.
    chip = 68
    cx, cy = MARGEN, 78
    d.rounded_rectangle([cx, cy, cx + chip, cy + chip], radius=16, fill=AZUL)
    corazon(d, cx + 18, cy + 22, 32, WHITE)
    d.text((cx + chip + 22, cy + 4), "Manos a la Obra", font=fuente(36, "Bold"), fill=INK)
    d.text(
        (cx + chip + 22, cy + 44),
        "Ayuda para el terremoto en Colombia",
        font=fuente(21, "Regular"),
        fill=MUTED,
    )

    # Franja de bandera.
    fy, bw = 186, 116
    for i, c in enumerate(FLAG):
        d.rectangle([MARGEN + i * bw, fy, MARGEN + (i + 1) * bw, fy + 14], fill=c)

    # Etiqueta de seccion.
    d.text((MARGEN, 244), cfg["label"], font=fuente(26, "SemiBold"), fill=cfg["acento"])

    # Titulo = llamado a la accion.
    ft = fuente(82, "ExtraBold")
    y = 288
    for ln in envolver(d, cfg["titulo"], ft, W - 2 * MARGEN):
        d.text((MARGEN, y), ln, font=ft, fill=INK, stroke_width=1, stroke_fill=INK)
        y += 96

    # Subtitulo.
    fs = fuente(31, "Regular")
    y += 6
    for ln in envolver(d, cfg["sub"], fs, W - 2 * MARGEN - 40):
        d.text((MARGEN, y), ln, font=fs, fill=MUTED)
        y += 44

    # Pie: dominio, en el color de acento.
    d.text(
        (MARGEN, H - 74),
        "manos-a-la-obra-production.up.railway.app",
        font=fuente(23, "Medium"),
        fill=cfg["acento"],
    )
    return img


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, cfg in SECCIONES.items():
        destino = SALIDA / f"{nombre}.png"
        tarjeta(cfg).save(destino, optimize=True)
        print(f"escrito {destino.relative_to(RAIZ)} ({destino.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
