from cactus.components.vm import vm_router
from cactus.config import Settings
from cactus.config import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    """Initialize and configure the application."""

    if settings is None:
        settings = get_settings()

    app = FastAPI()

    setup_routers(app, settings)
    setup_middlewares(app)

    return app


def setup_routers(app: FastAPI, settings: Settings) -> None:
    """Configure the application routers."""

    app.include_router(vm_router, prefix=settings.vm_router_prefix)


def setup_middlewares(app: FastAPI) -> None:
    """Configure the application middlewares."""

    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=['*'],
    )
