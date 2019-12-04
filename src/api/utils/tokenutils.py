from datetime import datetime

from django.conf import settings
from jose import jwt


def timestamp():
    return (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()


def create_token(auth_user_id, expire_in=7200):
    token_header = {"typ": "JWT", "alg": "HS256"}
    issued_at = timestamp()
    expiration_time = timestamp() + expire_in
    token_payload = {
        "iss": settings.ADMIN_API_AUDIENCE,
        "sub": auth_user_id,
        "aud": settings.API_AUDIENCE,
        "iat": issued_at,
        "exp": expiration_time,
    }
    return jwt.encode(
        token_payload,
        key=settings.API_SIGNING_SECRET,
        algorithm="HS256",
        headers=token_header,
    )
