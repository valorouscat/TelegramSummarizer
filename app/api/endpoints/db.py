from databases import Database
from fastapi import APIRouter, HTTPException, FastAPI, Depends
import logging
from contextlib import asynccontextmanager
from config import Config
import app.api.models.models as models
import asyncpg
from app.api.security.auth import auth_check


# logging
logger = logging.getLogger(__name__)

# lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

# router
router = APIRouter()

# database
database = Database(Config.DATABASE_URL)
tabe_name = Config.TABLE_NAME

# creating new user
@router.post("/create_users/", response_model=models.User)
async def create_user(user: models.User):
    query = f"INSERT INTO {tabe_name} (username) VALUES (:username)"
    values = {"username": user.username} 
    try:
        await database.execute(query=query, values=values)
        logger.info(f'Added new user: {user.username}')
        return {**user.model_dump()}
    except asyncpg.exceptions.UniqueViolationError:
        logger.info('Duplicated user')
        raise HTTPException(status_code=500, detail="User already in database")
    except Exception as e:
        logger.exception(f'Failed to add new user: {user.username}')
        raise HTTPException(status_code=500, detail="Failed to create user")
    

# geting user    
@router.get("/get_user/", response_model=models.User)
async def get_user(username: str):
    query = f"SELECT * FROM {tabe_name} WHERE username = (:username)"
    values = {"username": username}
    try: 
        user = await database.fetch_one(query=query, values=values)
        if user:
            logger.info(f'Got user: {username}')
            return user
        logger.warning(f'Failed to find user with username: {username}')
        return None
    except Exception as e:
        logger.exception(f'Failed to get user: {username}')
        raise HTTPException(status_code=500, detail="Failed to get user")


# changing number of promts_left
@router.put("/promts")
async def promts(delta: int, current_user: dict = Depends(auth_check)):
    query = f"UPDATE {tabe_name} SET promts_left=promts_left+(:delta) WHERE username=(:username) RETURNING promts_left"
    values = {"delta": delta, "username": current_user.username}
    try: 
        response = await database.fetch_one(query=query, values=values)
        logger.info(f'Promts_left for user was updated: {current_user.username}, {delta}')
        return models.User(username=current_user.username, promts_left=response[0])
    except Exception as e:
        logger.exception('Failed to update number of promts left')
        raise HTTPException(status_code=500, detail="Failed to update number of promts left")

