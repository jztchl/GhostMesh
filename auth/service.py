from datetime import timedelta, datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4
from fastapi import Depends
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from entities.users import User
from . import models
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from exceptions import AuthenticationError
import logging
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from exceptions import UserAlreadyExistsError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logging.warning(f"Failed authentication attempt for email: {email}")
        return False
    return user


def create_access_token(email: str, user_id: UUID, expires_delta: timedelta) -> str:
    encode = {
        "sub": email,
        "id": str(user_id),
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> models.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        return models.TokenData(user_id=user_id)
    except PyJWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise AuthenticationError()


def register_user(
    db: Session, register_user_request: models.RegisterUserRequest
) -> None:
    try:
        create_user_model = User(
            id=uuid4(),
            email=register_user_request.email,
            first_name=register_user_request.first_name,
            last_name=register_user_request.last_name,
            password_hash=get_password_hash(register_user_request.password),
        )
        db.add(create_user_model)
        db.commit()
    except IntegrityError:
        logging.error(
            f"Failed to register user: {register_user_request.email} user already exists"
        )
        raise UserAlreadyExistsError(email=register_user_request.email)
    except Exception as e:
        logging.error(
            f"Failed to register user: {register_user_request.email}. Error: {str(e)}"
        )
        raise


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> models.TokenData:
    return verify_token(token)


CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]


def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session
) -> models.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError()
    token = create_access_token(
        user.email, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return models.Token(access_token=token, token_type="bearer")
