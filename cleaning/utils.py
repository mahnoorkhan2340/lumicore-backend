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

RETRIABLE_STATUS = {429, 500, 503}
MAX_RETRIES = 5
BASE_DELAY = 0.3  # seconds


def fetch_with_retry(path: str, params: Dict[str, Any] | None = None) -> requests.Response:
    url = f"{BASE_URL}{path}"
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt+1}/{MAX_RETRIES}: {url}")  # ✅ Debug log
            resp = requests.get(url, headers=HEADERS, params=params, timeout=5)
            print(f"Status: {resp.status_code}") 
            
            if resp.status_code not in RETRIABLE_STATUS:
                resp.raise_for_status()
                return resp
            
            print(f"Retriable {resp.status_code}, will retry...")
            
        except Exception as e:
            print(f" Request failed: {e}")
        
        if attempt < MAX_RETRIES - 1:
            delay = BASE_DELAY * (2 ** attempt)
            print(f"Waiting {delay:.1f}s before retry...")
            time.sleep(delay)
    
    raise Exception(f"All {MAX_RETRIES} attempts failed to {url}")



def post_with_retry(path: str, json_body: Dict[str, Any]) -> requests.Response:
    url = f"{BASE_URL}{path}"
    headers = {**HEADERS, "Content-Type": "application/json"}
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(url, headers=headers, json=json_body, timeout=5)
            if resp.status_code in RETRIABLE_STATUS:
                raise requests.HTTPError(f"Retriable status {resp.status_code}")
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == MAX_RETRIES - 1:
                raise
            delay = BASE_DELAY * (2 ** attempt)
            time.sleep(delay)


# ===== Normalization rules from challenge =====

DOC_ID_KEYS = ["doc_id", "id", "documentId", "ref", "document_ref", "doc_number"]
TYPE_KEYS = ["type", "docType", "category", "document_type", "doc_category"]
COUNTERPARTY_KEYS = ["counterparty", "vendorName", "supplier", "partyA", "vendor", "party_name"]
PROJECT_KEYS = ["project", "projectName", "project_name", "proj"]
EXPIRY_KEYS = ["expiry_date", "expiry", "expiryDate", "end_date", "valid_till", "expires_on", "expiration"]
AMOUNT_KEYS = ["amount", "value", "contractValue", "amount_aed", "total", "contract_amount"]


def get_first(data: Dict[str, Any], keys: List[str]) -> Any:
    for k in keys:
        if k in data and data[k] not in (None, ""):
            return data[k]
    return None


def parse_date_to_iso(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)

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