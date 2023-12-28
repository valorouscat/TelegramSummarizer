from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.endpoints import summarizer, db
from app.api.security import auth
import logging
from app.api.endpoints.db import lifespan

# logging
logging.getLogger().name = __name__
logging.basicConfig(filename='logs.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(name)-14s - %(levelname)-8s - %(message)s')

# start FastAPI app with routers
app = FastAPI(lifespan=lifespan)
app.include_router(summarizer.router, prefix='/summarizer')
app.include_router(db.router, prefix='/db')
app.include_router(auth.router, prefix='/auth')

# global exc handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    logging.exception("Unhandled server extencion")

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )





