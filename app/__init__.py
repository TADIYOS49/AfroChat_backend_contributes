from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


from app.routers import api_v1_router
from app.utils.logger import FastApiLogger
from config import Config


async def logger_middleware(request: Request, call_next):
    request.state.logger = FastApiLogger
    response = await call_next(request)
    return response


def create_app(config: Config) -> FastAPI:
    FastApiLogger.info(f"App started as {config.CONFIG_TYPE}")
    app = FastAPI(
        # disable docs in production
        # docs_url=None
        # if config.CONFIG_TYPE == "production"
        # else "/docs",
    )
    app.include_router(api_v1_router)
    app.middleware("http")(logger_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
