# Copyright (c) 2025-2026 K.N.Narin. Non-commercial use only. See LICENSE.
import os
import jwt
from jwt import PyJWKClient, PyJWTError

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

SUPABASE_CONFIGURED = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

supabase = None
jwks_client = None

if SUPABASE_CONFIGURED:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        jwks_client = PyJWKClient(
            f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", cache_keys=True
        )
    except Exception as e:
        print(f"Supabase init failed: {e}")
        SUPABASE_CONFIGURED = False


def get_user_id(request):
    """Return user_id from Bearer token, or None if unauthenticated/unconfigured."""
    if not SUPABASE_CONFIGURED or not jwks_client:
        return None
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token, signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated"
        )
        return payload.get('sub')
    except PyJWTError:
        return None
