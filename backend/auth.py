
import os
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions
from database import supabase


from dataclasses import dataclass

SUPABASE_URL=os.environ.get("SUPABASE_URL"),
SUPABASE_KEY=os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be configured."
    )

bearer_scheme=HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    id:str
    email:str | None
    access_token: str

def get_current_user(
credentials: HTTPAuthorizationCredentials | None=Depends(bearer_scheme), 
)-> AuthenticatedUser:

    """Validate the supabase access token
    and create a database client scoped to that user's JWT"""

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower()!="bearer":
        raise HTTPException(
            status_code=401,
            detail="Bearer authentication required.",
        )

    token=credentials.credentials

    try:

        """create a fresh client for this request"""

        db=create_client(
            SUPABASE_URL,
            SUPABASE_KEY,
            options=ClientOptions(
                headers={
                    "Authorization":f"Bearer {token}"
                },auto_refresh_token=False,
                persist_session=False,
            ),)
        response= db.auth.get_user(jwt=token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired access token.",
            )
        return AuthenticatedUser(
            user_id=str(response.user.id),
            access_token=token,
            db=db
        )
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
        )


        
        
    