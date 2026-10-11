
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be configured."
    )


# Extract the Bearer token from the request.
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    email: str | None
    access_token: str
    db: Client


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> AuthenticatedUser:

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    token = credentials.credentials

    try:
        # Client 1: validate the token.
        auth_client = create_client(
            SUPABASE_URL,
            SUPABASE_KEY,
        )

        response = auth_client.auth.get_user(jwt=token)
        user = response.user

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired access token.",
            )

        # Client 2: use the validated user's JWT for database access.
        user_db = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        user_db.postgrest.auth(token)

        return AuthenticatedUser(
            user_id=str(user.id),
            email=user.email,
            access_token=token,
            db=user_db,
        )

    except HTTPException:
        raise

    except Exception as exc:
        print("AUTH ERROR TYPE:", type(exc).__name__)
        print("AUTH ERROR:", str(exc))

        raise HTTPException(
            status_code=500,
            detail="Authentication service failed.",
        )