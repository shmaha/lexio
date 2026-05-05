# ============================================================
# auth.py -- API key authentication
# ============================================================
# Protects your API from unauthorized access.
# Every request must include a valid API key in the header:
#   X-API-Key: your-secret-key
#
# v3 will extend this to support Bearer tokens and OAuth 2.0.
# ============================================================

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import API_SECRET_KEY

# Tells FastAPI to look for this header on every protected request
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency function -- FastAPI injects this into any endpoint
    that requires authentication. If the key is missing or wrong,
    the request is rejected before your endpoint code runs.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header."
        )

    if api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key."
        )

    return api_key