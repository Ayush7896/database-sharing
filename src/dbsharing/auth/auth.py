
from datetime import timedelta, timezone
import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from schemas.pydantic_models import CreateUserRequest, Token
from db.models import Users
from passlib.context import CryptContext
from db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
SECRET_KEY = "a2c4557a1531731c84059d83f4b552862dff447eec697e62ae40a1a5b0c6ef83"
ALGORITHM = "HS256"

# secret key and algorithm will work together to add a signature to the JWT token to make sure that JWT is secured and authoirized.

# JWT is a great way for information exchange between the client and the server.Once a user logs in, the server generates a JWT token that contains the user's information and signs it with a secret key. The client can then use this token to access protected resources without needing to log in again.



#OAuth2PasswordBearer used to decode the JWT token.
def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# form_data.username based on this username, go ahead and fetch the user from the database.

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id : int, user_role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'user_role': user_role}
    expires = datetime.datetime.now() + expires_delta
    encode.update({"exp": expires})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("user_role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            #     headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "user_id": user_id, 'user_role': user_role}
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            # headers={"WWW-Authenticate": "Bearer"},
        )
        

@router.post("/", status_code=status.HTTP_201_CREATED)

async def create_user(db:db_dependency,create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password =bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        phone_number=create_user_request.phone_number,
        is_active=True
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {"message": "User created successfully", "user_id": create_user_model.id}


# we need to allow users to authenicate themselves so they can sign in.
@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            # headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        user_role=user.role,
        expires_delta=timedelta(minutes=30)  # Token valid for 30 minutes
    )
    # return token
    return Token(access_token=token, token_type="bearer")
