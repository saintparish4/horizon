"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from horizon.api.routes import agents, memories, organizations
from horizon.config.database import engine
from horizon.config.settings import get_settings

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.is_production and settings.api_key_pepper == "dev-only-insecure-pepper":
        raise RuntimeError("API_KEY_PEPPER must be set in production")
    # Warn at startup rather than 500 on the first write. Every memory and agent
    # write embeds its text, so a missing key breaks those paths only — the app
    # still boots, and tests/benchmarks inject an offline provider instead.
    if not settings.openai_api_key:
        log.warning(
            "openai_api_key.missing",
            detail="Writes that embed text will fail. Set OPENAI_API_KEY in .env.",
        )
    log.info("startup", environment=settings.environment)
    yield
    await engine.dispose()
    log.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Horizon",
        description="Memory infrastructure and memory-aware routing for AI agent systems.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if not settings.is_production else [],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(organizations.router)
    app.include_router(memories.router)
    app.include_router(agents.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
