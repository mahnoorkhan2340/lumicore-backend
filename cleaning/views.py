from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .utils import (
    fetch_with_retry,
    post_with_retry,
    normalize_record,
    is_valid,
    remove_duplicates,
)

@api_view(["GET"])
def fetch_raw_data(request):
    """
    api/data?batch=1 endpoint.
    Fetch messy data from LumiCore API (batch query param allowed).
    """
    batch = request.query_params.get("batch", "1")
    try:
        resp = fetch_with_retry("/api/data", params={"batch": batch})
        data = resp.json()
        return Response({"raw": data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

@api_view(["POST"])
def normalize_data(request):
    """
    POST /api/normalize/
    Body: { "items": [ ...raw records from LumiCore... ] }
    Returns normalized items + validation and duplicate removal.
    """
    items = request.data.get("items", [])
    normalized_items = []

    for raw in items:
        n = normalize_record(raw)
        n["is_valid"] = is_valid(n)
        normalized_items.append(n)

    deduped = remove_duplicates(normalized_items)

    return Response(
        {
            "count_raw": len(items),
            "count_after_dedup": len(deduped),
            "items": deduped,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
def submit_cleaned_data(request):
    """
    api/submit endpoint.
    Submit cleaned items to LumiCore and return API response (including score).
    """
    cleaned_items = request.data.get("cleaned_items", [])
    batch_id = request.data.get("batch_id", "1")
    candidate_name = request.data.get("candidate_name", "Mahnoor Pervaiz")

    body = {
        "candidate_name": candidate_name,
        "batch_id": batch_id,
        "cleaned_items": cleaned_items,
    }
    try:
        resp = post_with_retry("/api/submit", json_body=body)
        return Response(resp.json(), status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )
