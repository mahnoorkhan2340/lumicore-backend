import time
from typing import Any, Dict, List

import requests
from django.conf import settings
from datetime import datetime
from dateutil import parser as date_parser

BASE_URL = settings.LUMICORE_BASE_URL
CANDIDATE_ID = settings.CANDIDATE_ID

HEADERS = {
    "X-Candidate-Id": CANDIDATE_ID,
}


# ===== Normalization rules from challenge =====

DOC_ID_KEYS = ["doc_id", "id", "documentId", "ref", "document_ref", "doc_number"]
TYPE_KEYS = ["type", "docType", "category", "document_type", "doc_category"]
COUNTERPARTY_KEYS = ["counterparty", "vendorName", "supplier", "partyA", "vendor", "party_name"]
PROJECT_KEYS = ["project", "projectName", "project_name", "proj"]
EXPIRY_KEYS = ["expiry_date", "expiry", "expiryDate", "end_date", "valid_till", "expires_on", "expiration"]
AMOUNT_KEYS = ["amount", "value", "contractValue", "amount_aed", "total", "contract_amount"]
# All mappings and date formats are defined in the PDF. [file:1]


def get_first(data: Dict[str, Any], keys: List[str]) -> Any:
    for k in keys:
        if k in data and data[k] not in (None, ""):
            return data[k]
    return None


def parse_date_to_iso(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)

    # per challenge: ambiguous formats treated as DD/MM/YYYY
    try:
        dt = date_parser.parse(text, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    if len(text) == 8 and text.isdigit():
        try:
            dt = datetime.strptime(text, "%Y%m%d")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None

    return None


def clean_amount(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value)
    for token in ["AED", "aed", " ", ","]:
        text = text.replace(token, "")
    if text == "":
        return None
    try:
        return float(text)
    except Exception:
        return None


def extract_project(raw: Dict[str, Any]) -> Any:
    meta = raw.get("meta")
    if isinstance(meta, dict) and "project" in meta and meta["project"]:
        return meta["project"]
    return get_first(raw, PROJECT_KEYS)


def normalize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    doc_id = get_first(raw, DOC_ID_KEYS)
    type_ = get_first(raw, TYPE_KEYS)
    counterparty = get_first(raw, COUNTERPARTY_KEYS)
    project = extract_project(raw)
    expiry_raw = get_first(raw, EXPIRY_KEYS)
    expiry_date = parse_date_to_iso(expiry_raw)
    amount_raw = get_first(raw, AMOUNT_KEYS)
    amount = clean_amount(amount_raw)

    normalized = {
        "doc_id": doc_id,
        "type": type_,
        "counterparty": counterparty,
        "project": project,
        "expiry_date": expiry_date,
        "amount": amount,
    }
    return normalized


def is_valid(normalized: Dict[str, Any]) -> bool:
    required = ["doc_id", "type", "counterparty", "project", "expiry_date", "amount"]
    for field in required:
        if normalized.get(field) in (None, ""):
            return False
    return True


def remove_duplicates(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_ids = set()
    unique: List[Dict[str, Any]] = []
    for r in records:
        key = r.get("doc_id")
        if key and key not in seen_ids:
            seen_ids.add(key)
            unique.append(r)
    return unique
