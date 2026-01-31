"""Share card 1080x1080 image."""
from __future__ import annotations

import io
import logging

from app.core.config import get_settings
from app.services.storage import save_file

logger = logging.getLogger(__name__)


def generate_share_card(session_id: str, share_token: str) -> str:
    """Generate 1080x1080 share image, save, return relative path."""
    settings = get_settings()
    base_url = settings.BASE_URL.rstrip("/")
    link = f"{base_url}/result/{session_id}?t={share_token}"

    try:
        from PIL import Image, ImageDraw, ImageFont

        w = h = 1080
        img = Image.new("RGB", (w, h), color=(250, 248, 240))
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except OSError:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()

        draw.rectangle([80, 80, w - 80, h - 80], outline=(200, 180, 120), width=4)
        draw.text((w // 2, 220), "Cittadino Energetico Consapevole", fill=(60, 50, 40), font=font_title, anchor="mm")
        draw.text((w // 2, 380), "Ho verificato la mia posizione nel quartiere", fill=(80, 70, 60), font=font_body, anchor="mm")
        draw.text((w // 2, 520), "Scopri anche tu dove sei", fill=(100, 90, 70), font=font_body, anchor="mm")
        draw.text((w // 2, 680), link[:40] + "...", fill=(120, 110, 100), font=font_body, anchor="mm")

        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(link)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200))
            img.paste(qr_img, (w // 2 - 100, 750))
        except Exception as e:
            logger.warning("QR on share card: %s", e)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        path = f"share_cards/{session_id}.png"
        save_file(path, buf.read(), mime="image/png")
        return path
    except Exception as e:
        logger.exception("Share card generation failed")
        raise RuntimeError(f"Generazione share card non riuscita: {e}") from e
