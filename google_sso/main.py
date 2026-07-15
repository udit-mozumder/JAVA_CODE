"""Application entrypoint for the Google SSO service (SCRUM-5)."""
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

logging.basicConfig(level=logging.INFO, format='%(message)s')

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event('startup')
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get('/health', tags=['health'])
async def health() -> JSONResponse:
    return JSONResponse({'status': 'ok'})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
