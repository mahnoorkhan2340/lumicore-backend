from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utils import (
    normalize_record,
    is_valid,
    remove_duplicates,
)

@api_view(["POST"])
def normalize_data(request):
    """
    POST api/normalize/
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