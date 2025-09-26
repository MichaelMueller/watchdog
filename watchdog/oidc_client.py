from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
from jose import jwt, JWTError
import httpx, asyncio, secrets, urllib.parse

from watchdog.data.oidc_config import OidcConfig


# --- OIDC client wrapper ---
class OidcClient:
    FIXED_SCOPES = ["openid", "profile", "email"]

    def __init__(self, config: OidcConfig, post_login_redirect: str):
        self.config = config
        self._post_login_redirect = post_login_redirect
        self._metadata_cache: dict = {}
        self._jwks_cache: dict = {}
        self._lock = asyncio.Lock()

    async def _get_metadata(self) -> dict:
        if self._metadata_cache:
            return self._metadata_cache
        async with self._lock:
            if not self._metadata_cache:
                url = self.config.issuer.rstrip("/") + "/.well-known/openid-configuration"
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=5.0)
                    resp.raise_for_status()
                    self._metadata_cache = resp.json()
        return self._metadata_cache

    async def _get_jwks(self) -> dict:
        if self._jwks_cache:
            return self._jwks_cache
        metadata = await self._get_metadata()
        async with httpx.AsyncClient() as client:
            jwks_url = metadata.get("jwks_uri")
            resp = await client.get(jwks_url, timeout=5.0)
            resp.raise_for_status()
            self._jwks_cache = resp.json()
        return self._jwks_cache

    async def verify_id_token(self, id_token: str) -> dict:
        jwks = await self._get_jwks()
        try:
            claims = jwt.decode(
                id_token,
                jwks,
                algorithms=["RS256"],
                audience=self.config.client_id,
                issuer=self.config.issuer,
            )
            return claims
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid ID token: {e}")

    async def _exchange_code_for_tokens(self, code: str, redirect_uri: str) -> dict:
        metadata = await self._get_metadata()
        token_endpoint:str = metadata.get("token_endpoint")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_s,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            return resp.json()

    async def _login(self, request: Request):
        metadata = await self._get_metadata()
        auth_endpoint:str = metadata.get("authorization_endpoint")

        redirect_uri = str(request.url_for("callback"))

        state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.FIXED_SCOPES),
            "state": state,
        }
            
        url = f"{auth_endpoint}?{urllib.parse.urlencode(params)}"
        return RedirectResponse(url)

    async def _callback(self, request: Request):
        code = request.query_params.get("code")
        if not code:
            return JSONResponse({"error": "Missing authorization code"}, status_code=400)

        redirect_uri = str(request.url_for("callback"))
        tokens = await self._exchange_code_for_tokens(code, redirect_uri)

        id_token = tokens.get("id_token")
        if not id_token:
            return JSONResponse({"error": "No ID token"}, status_code=400)

        _ = await self.verify_id_token(id_token)
        
        # You typically need to set a session cookie or return a bearer token for authentication.
        # Example: Set a session cookie with the ID token (not recommended for production, use a session manager).
        response = RedirectResponse(request.url_for(self._post_login_redirect))
        response.set_cookie("id_token", id_token, httponly=True, secure=True)
        return response
        
        # ✅ Redirect to configured target
        return RedirectResponse(request.url_for(self._post_login_redirect) )

    # --- Public dependency for other routes ---
    async def get_current_user(self, request: Request) -> dict:
        """FastAPI dependency: extracts and verifies ID token from Authorization header."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            id_token = auth_header.split(" ", 1)[1]
        else:
            id_token = request.cookies.get("id_token")
            if not id_token:
                raise HTTPException(status_code=401, detail="Missing Bearer token or session cookie")
        return await self.verify_id_token(id_token)

    def get_router(self) -> APIRouter:
        router = APIRouter()
        router.add_api_route("/login", self._login, methods=["GET"])
        router.add_api_route("/callback", self._callback, methods=["GET"], name="callback")
        return router
