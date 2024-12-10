import uvicorn
from cactus.config import get_settings

if __name__ == '__main__':
    settings = get_settings()
    uvicorn.run(
        'cactus.app:create_app',
        factory=True,
        host=settings.host,
        port=settings.port,
        log_level=settings.logging_level,
        workers=settings.workers,
        reload=settings.reload,
    )
