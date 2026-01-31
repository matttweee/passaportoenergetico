"""OpenAI-based bill extraction with strict JSON schema."""
from __future__ import annotations

import base64
import json
import logging
from typing import Any

from app.core.config import get_settings
from app.services.extract_schema import ExtractionOutput, validate_extraction_payload, second_pass_validate

logger = logging.getLogger(__name__)

SCHEMA_JSON = {
    "type": "object",
    "properties": {
        "period_start": {"type": ["string", "null"], "format": "date"},
        "period_end": {"type": ["string", "null"], "format": "date"},
        "issue_date": {"type": ["string", "null"], "format": "date"},
        "total_due": {"type": ["number", "null"]},
        "kwh": {"type": ["number", "null"]},
        "smc": {"type": ["number", "null"]},
        "energy_cost": {"type": ["number", "null"]},
        "transport_cost": {"type": ["number", "null"]},
        "taxes": {"type": ["number", "null"]},
        "supplier": {"type": ["string", "null"]},
        "tariff_name": {"type": ["string", "null"]},
        "cap_or_zone_hint": {"type": ["string", "null"]},
        "confidence": {
            "type": "object",
            "properties": {k: {"type": "number", "minimum": 0, "maximum": 1} for k in [
                "period_start", "period_end", "issue_date", "total_due", "kwh", "smc",
                "energy_cost", "transport_cost", "taxes", "supplier", "tariff_name", "cap_or_zone_hint"
            ]},
            "additionalProperties": False,
        },
        "notes": {"type": ["string", "null"]},
    },
    "additionalProperties": False,
}


def extract_from_text(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Call OpenAI to extract structured data from bill text. Returns (raw_dict, error)."""
    api_key = get_settings().OPENAI_API_KEY
    if not api_key:
        return None, "OPENAI_API_KEY non configurata"

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=get_settings().OPENAI_MODEL,
            messages=[
                {"role": "system", "content": """Sei un estrattore di dati da bollette luce/gas.
Restituisci SOLO un JSON valido con i campi richiesti. Se un valore non è leggibile, usa null.
Non inventare mai valori. confidence per ogni campo deve essere tra 0 e 1."""},
                {"role": "user", "content": f"Estrai i dati dalla seguente bolletta:\n\n{text[:12000]}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)
    except Exception as e:
        logger.exception("OpenAI extraction failed")
        return None, f"Estrazione non riuscita: {str(e)[:200]}"

    out, err = validate_extraction_payload(data)
    if err:
        return None, f"Schema non valido: {err}"
    warnings = second_pass_validate(out)
    if warnings:
        logger.warning("Second-pass warnings: %s", warnings)
    return data, None


def extract_from_image_base64(b64: str) -> tuple[dict[str, Any] | None, str | None]:
    """Extract from image (base64). Uses vision model if available."""
    api_key = get_settings().OPENAI_API_KEY
    if not api_key:
        return None, "OPENAI_API_KEY non configurata"

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Estrai dalla bolletta energia i campi: period_start, period_end, issue_date, total_due, kwh, smc, energy_cost, transport_cost, taxes, supplier, tariff_name, cap_or_zone_hint. Restituisci JSON con confidence 0-1 per campo. Se non leggibile: null."},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ]},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)
    except Exception as e:
        logger.exception("OpenAI vision extraction failed")
        return None, f"Estrazione immagine non riuscita: {str(e)[:200]}"

    out, err = validate_extraction_payload(data)
    if err:
        return None, f"Schema non valido: {err}"
    return data, None
