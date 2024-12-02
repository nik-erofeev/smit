from fastapi import APIRouter, HTTPException
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.utils.db import Db


class DefaultRouter:
    def __init__(self, db: Db):
        self._db = db

    @property
    def api_router(self) -> APIRouter:
        router = APIRouter()
        self._register(router)
        return router

    def _register(self, router: APIRouter) -> None:
        @router.get("/ping", include_in_schema=False)
        async def _ping() -> str:
            logger.debug("ping")
            return "pong"

        @router.get("/ready", include_in_schema=False)
        async def _ready() -> bool:
            logger.debug("ready")
            try:
                logger.debug("testing db")
                async with self._db.get_session() as session:
                    await session.execute(text("SELECT 1"))
            except SQLAlchemyError:
                raise HTTPException(500, "Database not ready")
            logger.debug("pg ready")

            return True
