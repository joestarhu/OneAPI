from fastapi import APIRouter
from fastapi import Depends,  HTTPException, Security, status
from datetime import datetime, timedelta, timezone

from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes,
)

# from jwt.exceptions import InvalidTokenError
# from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError


api = APIRouter(prefix="/role")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    nick_name: str | None = None
    scopes: list[str] = []


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/role/token",
    scopes={"me": "Read information about the current user.",
            "items": "Read items."},
)


# @api.post("/token")
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
# ) -> Token:
#     return Token(access_token="access_token", token_type="bearer")
