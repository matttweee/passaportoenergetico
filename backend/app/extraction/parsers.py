from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


def _norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_decimal_eur(s: str) -> Decimal | None:
    """Accetta formati tipici IT (1.234,56) o (1234.56)."""
    if not s:
        return None
    s = s.strip()
    s = s.replace("€", "").replace("EUR", "").replace("euro", "").strip()
    s = s.replace(" ", "")
    # trova prima occorrenza numero
    m = re.search(r"(-?\d{1,3}(?:[.\s]\d{3})*(?:,\d{1,2})|-?\d+(?:[.,]\d{1,2})?)", s)
    if not m:
        return None
    num = m.group(1)
    num = num.replace(" ", "")
    # migliaia con punto, decimali con virgola -> standard
    if "," in num and "." in num:
        num = num.replace(".", "").replace(",", ".")
    elif "," in num:
        num = num.replace(",", ".")
    try:
        return Decimal(num)
    except InvalidOperation:
        return None


def parse_float_eur(s: str) -> float | None:
    d = parse_decimal_eur(s)
    return float(d) if d is not None else None


def parse_kwh(text: str) -> float | None:
    # kWh può apparire come "kWh 123,45" o "123,45 kWh"
    # Evita match con "kW/h" (falso positivo)
    m = re.search(r"(\d{1,6}(?:[.,]\d{1,3})?)\s*(kwh)\b(?!\s*/)", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(kwh)\b(?!\s*/)\s*[:\-]?\s*(\d{1,6}(?:[.,]\d{1,3})?)", text, re.IGNORECASE)
        if not m:
            return None
        val = m.group(2)
    else:
        val = m.group(1)
    return float(str(parse_decimal_eur(val) or "").replace(",", ".")) if parse_decimal_eur(val) else None


def parse_smc(text: str) -> float | None:
    # Smc / mc / m3
    m = re.search(r"(\d{1,6}(?:[.,]\d{1,3})?)\s*(smc|mc|m3|m³)\b", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(smc|mc|m3|m³)\s*[:\-]?\s*(\d{1,6}(?:[.,]\d{1,3})?)", text, re.IGNORECASE)
        if not m:
            return None
        val = m.group(2)
    else:
        val = m.group(1)
    d = parse_decimal_eur(val)
    return float(d) if d is not None else None


def parse_pod(text: str) -> str | None:
    m = re.search(r"\bPOD\b[^A-Z0-9]*(IT[0-9A-Z]{14})\b", text, re.IGNORECASE)
    return m.group(1).upper() if m else None


def parse_pdr(text: str) -> str | None:
    m = re.search(r"\bPDR\b[^0-9]*(\d{14})\b", text, re.IGNORECASE)
    return m.group(1) if m else None


def parse_period(text: str) -> dict[str, Any]:
    # prova pattern "dal 01/01/2025 al 31/01/2025"
    m = re.search(
        r"\bdal\s+(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})\s+al\s+(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})\b",
        text,
        re.IGNORECASE,
    )
    if not m:
        return {}
    try:
        start = date_parser.parse(m.group(1), dayfirst=True).date()
        end = date_parser.parse(m.group(2), dayfirst=True).date()
        days = (end - start).days + 1 if end >= start else None
        return {"period_start": start.isoformat(), "period_end": end.isoformat(), "period_days": days}
    except Exception:
        return {}


def parse_supplier(text: str) -> str | None:
    # euristica: cerca "Fornitore" o usa prima riga "significativa"
    m = re.search(r"\bfornitore\b\s*[:\-]?\s*([^\n]{3,80})", text, re.IGNORECASE)
    if m:
        return _norm_space(m.group(1))[:80]
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    # prima riga “probabile brand” (evita intestazioni tipo "BOLLETTA" o "FATTURA")
    for l in lines[:10]:
        if any(w in l.upper() for w in ["BOLLETTA", "FATTURA", "PAGAMENTO", "CLIENTE"]):
            continue
        if len(l) >= 3:
            return _norm_space(l)[:80]
    return _norm_space(lines[0])[:80]


def extract_amount_by_label(text: str, labels: list[str]) -> float | None:
    # prende la cifra che segue un’etichetta su stessa riga
    for lab in labels:
        m = re.search(rf"{lab}[^\n\r]{{0,40}}?(-?\d{{1,3}}(?:[.\s]\d{{3}})*(?:,\d{{1,2}})|-?\d+(?:[.,]\d{{1,2}})?)\s*€?",
                      text, re.IGNORECASE)
        if m:
            return parse_float_eur(m.group(1))
    return None


def parse_fields_from_text(text: str) -> dict[str, Any]:
    t = text or ""
    fields: dict[str, Any] = {}

    supplier = parse_supplier(t)
    if supplier:
        fields["supplier"] = supplier

    fields.update(parse_period(t))

    pod = parse_pod(t)
    if pod:
        fields["pod"] = pod
    pdr = parse_pdr(t)
    if pdr:
        fields["pdr"] = pdr

    kwh = parse_kwh(t)
    if kwh is not None:
        fields["kwh"] = kwh
    smc = parse_smc(t)
    if smc is not None:
        fields["mc"] = smc

    total = extract_amount_by_label(t, ["totale", "importo totale", "totale bolletta", "da pagare"])
    if total is not None:
        fields["total_eur"] = total

    fixed = extract_amount_by_label(t, ["quota fissa", "spesa fissa", "fissi"])
    if fixed is not None:
        fields["fixed_fees"] = fixed

    variable = extract_amount_by_label(t, ["quota variabile", "spesa variabile", "spesa per la materia", "materia energia", "materia gas"])
    if variable is not None:
        fields["variable_eur"] = variable

    vat = extract_amount_by_label(t, ["iva"])
    if vat is not None:
        fields["vat_eur"] = vat

    excise = extract_amount_by_label(t, ["accisa", "imposta di consumo"])
    if excise is not None:
        fields["excise_eur"] = excise

    return fields

