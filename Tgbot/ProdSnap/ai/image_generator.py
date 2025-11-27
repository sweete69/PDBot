# ProdSnap/ai/image_generator.py
import os
import uuid
from PIL import Image, ImageDraw, ImageFont

# Параметры по умолчанию
WIDTH = 1024
HEIGHT = 576
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (20, 20, 20)

def _ensure_temp():
    os.makedirs("temp", exist_ok=True)

def generate_image(prompt: str) -> str:
    """
    Генерирует простое изображение с текстом prompt и возвращает путь к файлу.
    Оффлайн-имплементация для тестирования.
    """
    if prompt is None:
        prompt = ""
    _ensure_temp()
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()

    max_width = WIDTH - 40
    words = str(prompt).split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        try:
            bbox = draw.textbbox((0, 0), test, font=font)
            text_width = bbox[2] - bbox[0]
        except Exception:
            # fallback
            text_width = font.getsize(test)[0]
        if text_width > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    y = 20
    line_height = font.getsize("A")[1] + 8
    for line in lines:
        draw.text((20, y), line, fill=TEXT_COLOR, font=font)
        y += line_height

    filename = os.path.join("temp", f"generated_{uuid.uuid4().hex}.jpg")
    img.save(filename, quality=85)
    return filename

def generate_image_from_photo(photo_path: str, prompt: str) -> str:
    """
    Берёт фото (photo_path), добавляет подпись prompt и возвращает путь к новому файлу.
    """
    _ensure_temp()
    if not os.path.exists(photo_path):
        raise FileNotFoundError(f"Photo not found: {photo_path}")

    try:
        base = Image.open(photo_path).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Не удалось открыть фото: {e}")

    base.thumbnail((WIDTH, HEIGHT))
    draw = ImageDraw.Draw(base)

    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()

    text = (prompt or "")[:400]
    try:
        w, h = draw.textsize(text, font=font)
    except Exception:
        w, h = font.getsize(text)

    padding = 10
    rect_h = h + padding * 2
    # Рисуем полупрозрачную подложку (если режим RGBA не поддерживается, используем сплошную)
    try:
        overlay = Image.new("RGBA", (base.width, rect_h), (255, 255, 255, 200))
        base.paste(overlay, (0, base.height - rect_h), overlay)
        draw = ImageDraw.Draw(base)
    except Exception:
        draw.rectangle([0, base.height - rect_h, base.width, base.height], fill=(255,255,255))

    x = padding
    y = base.height - rect_h + padding
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    filename = os.path.join("temp", f"generated_from_photo_{uuid.uuid4().hex}.jpg")
    base.save(filename, quality=85)
    return filename
