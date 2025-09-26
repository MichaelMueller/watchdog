# Standard library imports
import os, json, secrets, asyncio, urllib.parse, logging
from typing import Callable, Optional
# FastAPI imports
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
# Async HTTP client
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx
# local imports
from watchdog.data.web_app_config import WebAppConfig
from watchdog.oidc_client import OidcClient

###### FUNCTIONS ######
_oidc_metadata_cache: dict[str, dict] = {}
_oidc_lock = asyncio.Lock()

async def get_server_metadata(issuer: str) -> dict:
    if issuer in _oidc_metadata_cache:
        return _oidc_metadata_cache[issuer]

    async with _oidc_lock:
        if issuer not in _oidc_metadata_cache:  # double-check inside lock
            url = issuer.rstrip("/") + "/.well-known/openid-configuration"
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=5.0)
                resp.raise_for_status()
                _oidc_metadata_cache[issuer] = resp.json()

    return _oidc_metadata_cache[issuer]

###### APP SETUP ######
# Load configuration
config = WebAppConfig()

logging.basicConfig(
    level=config.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logging.info("Starting application with configuration:")
logging.info(json.dumps(config.model_dump(), indent=4))
# create app
app = FastAPI()

# setup dirs
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "html_templates")
static_dir = os.path.join(base_dir, "public_html")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=template_dir)

oidc = OidcClient(config.oidc, post_login_redirect="welcome")
app.include_router(oidc.get_router())

# Example protected route
@app.get("/")
async def start():
    return RedirectResponse(url="/login")

# Example protected route
@app.get("/welcome")
async def welcome(user: dict = Depends(oidc.get_current_user)):
    return {"message": f"Hello {user.get('email') or user.get('sub')}!"}

# routes

# @app.get("/")
# @app.get("/login")
# async def login(request: Request):
#     metadata = await get_server_metadata(config.oidc.issuer)
#     auth_endpoint = metadata["authorization_endpoint"]
#     scopes = ["openid", "profile", "email"]
#     redirect_uri = request.url_for("/auth/callback")
#     state = secrets.token_urlsafe(16)
#     params = {
#         "client_id": config.oidc.client_id,
#         "response_type": "code",
#         "redirect_uri": redirect_uri,
#         "scope": " ".join(scopes),
#         "state": state,
#     }
#     url = f"{auth_endpoint}?{urllib.parse.urlencode(params)}"
#     return RedirectResponse(url)

# @app.get("/auth/callback")
# async def callback(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         return JSONResponse({"error": "Missing authorization code"}, status_code=400)

#     metadata = await get_server_metadata(config.oidc.issuer)
#     token_endpoint = metadata["token_endpoint"]

#     redirect_uri = request.url_for("/auth/callback")
#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(
#             token_endpoint,
#             data={
#                 "grant_type": "authorization_code",
#                 "code": code,
#                 "redirect_uri": REDIRECT_URI,
#                 "client_id": config.oidc.client_id,
#                 "client_secret": CLIENT_SECRET,
#             },
#             headers={"Content-Type": "application/x-www-form-urlencoded"},
#         )
#         token_resp.raise_for_status()
#         tokens = token_resp.json()

#     # Decode ID token without validation (demo only!)
#     id_token = tokens.get("id_token")
#     claims = jwt.get_unverified_claims(id_token) if id_token else {}

#     return JSONResponse({"tokens": tokens, "id_token_claims": claims})

# @app.get("/")
# async def home(request: Request):
#     return templates.TemplateResponse("base.html", {"request": request, "current_year": 2025})



# OIDC setup
# oidc_config = config.oidc.model_dump()
# _authenticate_user: Callable = get_auth(**oidc_config)

# async def fetch_user_groups(access_token: str):
#     url = "https://graph.microsoft.com/v1.0/me/memberOf"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     async with httpx.AsyncClient() as client:
#         r = await client.get(url, headers=headers)
#         if r.status_code != 200:
#             raise HTTPException(403, detail="Cannot read user groups")
#         data = r.json()
#         return [g["displayName"] for g in data.get("value", [])]
    
# @app.get("/auth/callback")
# async def callback(tokens=Depends(oidc.callback)):
#     # tokens contains id_token, access_token, etc.
#     if config.oidc.allowed_o365_groups:
#         groups = await fetch_user_groups(tokens["access_token"])
#         if not any(g in config.oidc.allowed_o365_groups for g in groups):
#             raise HTTPException(status_code=403, detail="User not in allowed groups")
#     elif config.oidc.allowed_users:
#         userinfo = await oidc.userinfo(tokens["access_token"])
#         email = userinfo.get("email") or userinfo.get("sub")
#         if email not in config.oidc.allowed_users:
#             raise HTTPException(status_code=403, detail="User not allowed")
#     # store groups in session or check immediately
#     return RedirectResponse(url="/dashboard")

# def allowed_user(userinfo=Depends(oidc.userinfo)):
#     email = userinfo.get("email") or userinfo.get("sub")
#     if config.oidc.allowed_users and email not in config.oidc.allowed_users:
#         raise HTTPException(status_code=403, detail="User not allowed")
#     return userinfo

# # protected dashboard
# @app.get("/dashboard")
# async def dashboard(user=Depends(allowed_user)):
#     return {"msg": "Welcome!", "user": user}
        
