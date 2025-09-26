#3rd party
import uvicorn
#internal
from watchdog.data.web_app_config import WebAppConfig

if __name__ == "__main__":
    config = WebAppConfig()
    uvicorn_args = config.model_dump(exclude={"oidc"})
    uvicorn.run("watchdog.app:app", **uvicorn_args)
