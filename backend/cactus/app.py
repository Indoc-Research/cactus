from cactus.components.repo import repo_router
from cactus.components.vm import vm_router
from cactus.config import Settings
from cactus.config import get_settings
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles


def create_app(settings: Settings | None = None) -> FastAPI:
    """Initialize and configure the application."""

    if settings is None:
        settings = get_settings()

    middlewares = setup_middlewares()

    app = FastAPI(
        openapi_url=f'{settings.path_hash}/openapi.json',
        docs_url=f'{settings.path_hash}/docs',
        redoc_url=None,
        middleware=middlewares,
    )

    setup_routers(app, settings)

    app.mount(f'{settings.path_hash}', StaticFiles(directory='../frontend', html=True), name='frontend')

    return app


def setup_routers(app: FastAPI, settings: Settings) -> None:
    """Configure the application routers."""

    app.include_router(vm_router, prefix=settings.path_hash)
    app.include_router(repo_router, prefix=settings.path_hash)


def setup_middlewares() -> list[Middleware]:
    """Configure the application middlewares."""

    return [
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    ]
