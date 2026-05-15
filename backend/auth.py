"""Supabase JWT verification.

Verifies tokens against the project's JWKS endpoint (asymmetric signing).
No shared secret required — only the project URL.
"""
import os

from fastapi import Depends, Header, HTTPException
import jwt
from jwt import PyJWKClient

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
ISSUER = f"{SUPABASE_URL}/auth/v1"

# PyJWKClient caches keys internally and refreshes on cache miss
_jwks_client = PyJWKClient(JWKS_URL)


def get_current_user(authorization: str = Header(default="")) -> dict:
    """FastAPI dependency: verifies the Bearer JWT and returns the user claims.

    Returns dict with at least: 'sub' (supabase user id) and 'email'.
    Raises 401 on any failure.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=ISSUER,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")

    if not claims.get("email"):
        raise HTTPException(status_code=401, detail="Token missing email claim")

    return claims
