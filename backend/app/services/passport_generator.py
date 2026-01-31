"""PDF Passport generator with QR."""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.services.storage import save_file

logger = logging.getLogger(__name__)

POSITION_LABELS = {"green": "In linea", "yellow": "In scostamento", "red": "Fuori trend"}


def generate_passport_pdf(
    session_id: str,
    zone_label: str,
    position: str,
    qr_token: str,
) -> str:
    """Generate PDF, save to storage, return relative path."""
    settings = get_settings()
    base_url = settings.BASE_URL.rstrip("/")
    result_url = f"{base_url}/result/{session_id}?t={qr_token}"
    title = f"PASSAPORTO ENERGETICO — {zone_label}"
    status_label = POSITION_LABELS.get(position, position)
    date_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, h - 50, title)
        c.setFont("Helvetica", 12)
        c.drawString(40, h - 80, f"Stato: {status_label}")
        c.drawString(40, h - 100, f"Data: {date_str}")
        c.drawString(40, h - 130, "Scansiona il QR per aprire il risultato:")
        c.drawString(40, h - 160, result_url[:60] + "..." if len(result_url) > 60 else result_url)

        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=4, border=2)
            qr.add_data(result_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            from reportlab.lib.utils import ImageReader
            c.drawImage(ImageReader(img_bytes), 40, h - 320, width=120, height=120)
        except Exception as e:
            logger.warning("QR not drawn: %s", e)

        c.save()
        buf.seek(0)
        path = f"passports/{session_id}.pdf"
        save_file(path, buf.read(), mime="application/pdf")
        return path
    except Exception as e:
        logger.exception("PDF generation failed")
        raise RuntimeError(f"Generazione PDF non riuscita: {e}") from e
