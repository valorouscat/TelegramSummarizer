from fastapi import FastAPI, Depends, Request, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
import logging
import app.api.models.models as models
import asyncio
from datetime import datetime, timezone, timedelta
from config import Config
import httpx


# logging
logger = logging.getLogger(__name__)

# router
router = APIRouter()
# oauth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# encode jwt token
def create_jwt_token(data: dict):
    return jwt.encode(data, Config.SECRET_KEY, algorithm=Config.ALGORITHM)


async def get_user(username: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{Config.API_HOST}/db/get_user/?username={username}')
        return models.User(**response.json())


# generating token for user from db
@router.post("/login")
async def login(username: str): 
    if await get_user(username):
            logger.info(f'JWT token was encoded for user: {username}')
            return {"access_token": create_jwt_token({"sub": username, "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=600)}), "token_type": "bearer"}
    logger.warning(f'Login request from unknown user: {username}')
    return {"error": "Invalid credentials"}




# get username from token
async def auth_check(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM]) 
        logger.info('JWT token was decoded')
        username: str = payload.get("sub")
        user: models.User | None = await get_user(username)
        if user is None:
            logger.warning('Got JWT token for unknown user')
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        logger.error('Got expired JWT token')
        raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"})
    except jwt.InvalidTokenError:
        logger.error('Got invalid token')
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    logger.info(f'User authorized: {user.username}')
    return user
