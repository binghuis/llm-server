from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.apis import routers
from server.core.config import settings

app = FastAPI()

app.include_router(routers)

if len(settings.cors_origins) > 0:
    app.add_middleware(
        CORSMiddleware,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_credentials=False,
        allow_origins=settings.cors_origins,
        allow_origin_regex="",
        max_age=600,
        expose_headers=[],
    )


@app.get("/")
async def health() -> JSONResponse:
    return JSONResponse("hello, world")
