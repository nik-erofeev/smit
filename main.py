import asyncio

import uvicorn
from fastapi.responses import JSONResponse

from app.applications import Application, logger
from app.bootstrap import bootstrap
from app.settings import APP_CONFIG


container = bootstrap(APP_CONFIG)
container.register(Application)

application: Application = container.resolve(Application)
app = application.app


@app.exception_handler(Exception)
async def http_exception_handler(request, exc):
    logger.exception("Unexpected error occurred")
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


config = uvicorn.Config(app, host="0.0.0.0", port=8000, reload=True)
server = uvicorn.Server(config)
try:
    logger.warning("Starting server...Hello")
    asyncio.run(server.serve())
except KeyboardInterrupt:
    logger.warning("Server stop by user, shutting down! Bye-Bye!!!")
