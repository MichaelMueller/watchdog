# bultin
import os, json, secrets, asyncio, urllib.parse, logging
from typing import Callable, Optional
from contextlib import asynccontextmanager
# 3rd party
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
# local imports
from watchdog.data.web_app_config import WebAppConfig
from watchdog.oidc import Oidc

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

# FastAPI app lifecycle events using lifespan context

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("FastAPI app startup: initializing resources")
    yield
    logging.info("FastAPI app shutdown: cleaning up resources")
    # Example: cleanup tasks if needed

# create app
app = FastAPI(lifespan=lifespan)

# create app
app = FastAPI()

# setup dirs
base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(base_dir)
var_dir = os.path.join(project_dir, "var")
data_file = os.path.join(var_dir, "data.json")
os.makedirs(var_dir, exist_ok=True)

template_dir = os.path.join(base_dir, "html_templates")
static_dir = os.path.join(base_dir, "public_html")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=template_dir)

oidc_config_data = config.oidc.model_dump()
oidc_config_data.update({"post_login_redirect": "watchdogs", "post_logout_redirect": "logged_out"})
oidc = Oidc(Oidc.Config(**oidc_config_data))
app.include_router(oidc.get_router())

@app.get("/")
async def start():
    return RedirectResponse(url="/login")

@app.get("/watchdogs")
async def watchdogs(request: Request, user: dict = Depends(oidc.get_current_user)):
    if not os.path.exists(data_file):
        watchdogs = []
    else:
        with open(data_file, "r", encoding="utf-8") as f:
            watchdogs = json.load(f)
    data = {
        "request": request,
        "watchdogs": watchdogs,
        "user": user
    }
    return templates.TemplateResponse( "watchdogs.html", data )

@app.post("/watchdogs")
async def create_watchdog(request: Request, user: dict = Depends(oidc.get_current_user)):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
    data = await request.json()
    if not os.path.exists(data_file):
        watchdogs = []
    else:
        with open(data_file, "r", encoding="utf-8") as f:
            watchdogs = json.load(f)
    watchdogs.append(data)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(watchdogs, f, indent=2)

    return JSONResponse({"status": "success", "message": "Watchdog created"})
    

@app.post("/oidc_config")
async def oidc_config(request: Request, user: dict = Depends(oidc.get_current_user)):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")

    config_data = await request.json()
    await oidc.set_config(Oidc.Config(**config_data))
    return JSONResponse({"status": "success"})

@app.get("/oidc_config")
async def oidc_config(request: Request, user: dict = Depends(oidc.get_current_user)):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")

    config:Oidc.Config = oidc.config()
    data = {
        "request": request,
        "message": "OIDC Configuration",
        "detail": config.model_dump_json(indent=4),
        "pre_content": True,
        "link_url": "/watchdogs",
        "link_text": "Show watchdogs"
    }
    return templates.TemplateResponse("message.html", data, status_code=200)

@app.get("/forbidden")
async def forbidden(request: Request):
    data = {
        "request": request, 
        "message": "Forbidden", 
        "detail": "You do not have permission to access this resource."
    }
    return templates.TemplateResponse("message.html", data, status_code=403)

@app.get("/logged_out")
async def logged_out(request: Request):
    data = {
        "request": request,
        "message": "Logged Out",
        "detail": "You have been logged out successfully.",
        "link_url": "/",
        "link_text": "Return to Home"
    }
    return templates.TemplateResponse("message.html", data, status_code=200)

@app.get("/error")
async def error(request: Request):
    data = {
        "request": request,
        "message": "Error",
        "detail": "An unexpected error occurred."
    }
    return templates.TemplateResponse("message.html", data, status_code=500)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        return RedirectResponse(url="/forbidden")
    return RedirectResponse(url="/error")  # fallback for other HTTP errors

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
        
