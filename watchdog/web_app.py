import os
from fastapi import FastAPI
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from watchdog.web_app_config import WebAppConfig

class WebApp:
    def __init__(self):
        self._started = False
        self._base_dir = None
        
    def run(self):
        if not self._started:
            self._started = True
            config = WebAppConfig()
            
            script_name = os.path.basename(__file__)
            factory_string = f"{self.__class__.__module__}:{self.__class__.__name__}.{self.create_app.__name__}"
        
            uvicorn.run(
                factory_string,
                host=config.host,
                port=config.port,
                reload=config.reload,
                log_level=config.log_level,
                workers=config.workers,
                factory=True
            )
            
    @classmethod
    def create_app(cls) -> FastAPI:
        app = FastAPI()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, "html_templates")
        static_dir = os.path.join(base_dir, "public_html")

        # Mount static files (CSS, JS, images)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # Tell FastAPI where Jinja2 templates live
        templates = Jinja2Templates(directory=template_dir)
        
        @app.get("/")
        async def home(request: Request):
            return templates.TemplateResponse("base.html", {"request": request, "current_year": 2025})

        @app.get("/login")
        async def login_get(request: Request):
            return templates.TemplateResponse("login.html", {"request": request, "current_year": 2025})
            
        return app
