# msal_handler.py
import msal
from pydantic import BaseModel
from typing import Optional, List

class UserInfo(BaseModel):
    email: Optional[str]
    name: Optional[str]

class AuthResult(BaseModel):
    token: dict
    user: UserInfo

# Funziona con public client
class MicrosoftAuth:
    def __init__(
        self,
        client_id: str,
        authority: str,
        redirect_uri: str,
        client_secret: Optional[str] = None,
        scopes: Optional[List[str]] = None
    ) -> None:
        self.client_id = client_id
        self.authority = authority
        self.redirect_uri = redirect_uri
        self.client_secret = client_secret
        self.scopes = scopes or ["User.Read"]

        self.app = msal.ConfidentialClientApplication(
            client_id=client_id,
            authority=authority,
            client_credential=client_secret if client_secret else None
        )

    def get_auth_url(self, random_code: Optional[str] = None) -> str:
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
            state=random_code
        )
        return auth_url

    def process_callback(self, code: str, state: Optional[str] = None) -> Optional[AuthResult]:
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        if "error" in result:
            return None
        user_claims = result.get("id_token_claims", {})
        user_info = UserInfo(
            email=user_claims.get("preferred_username"),
            name=user_claims.get("name")
        )
        return AuthResult(token=result, user=user_info)