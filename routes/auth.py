from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database.db import get_db
from database.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from repository import users as repository_users
from services.auth import auth_service
from services.email import send_email
import logging
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.templating import Jinja2Templates
from pathlib import Path
from services.redis_cache import get_redis, redis_client
import json
from database.models import User

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="services/templates")



async def get_user_from_cache(user_id: int, db: Session):
    cached_user = redis_client.get(f"user:{user_id}")

    if cached_user:
        print("User is not in cash!")
        return json.loads(cached_user)

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        redis_client.setex(f"user:{user.id}", 3600, json.dumps(user.__dict__))
        return user
    return None

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {"message": "User created", "user": new_user}

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request, "form": {}})


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), redis=Depends(get_redis)):
    cached_user = await redis.get(body.username)

    if cached_user:
        print("User found in cache")
        user_data = json.loads(cached_user)
        user = User(**user_data)
    else:
        user = await repository_users.get_user_by_email(body.username, db)
        if user:
            await redis.set(body.username, json.dumps(user.as_dict()), ex=3600)
            print("User added to cache")

    #user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not confirmed")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return RedirectResponse(url="/auth/dashboard", status_code=status.HTTP_302_FOUND)


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = await auth_service.create_access_token(data={"sub": email})
    new_refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, new_refresh_token, db)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/enable_2fa")
async def enable_2fa(user_id: int, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    totp_secret = auth_service.generate_totp_secret()
    await repository_users.update_totp_secret(user, totp_secret, db)

    return {"totp_secret": totp_secret}


@router.post("/login_2fa")
async def login_2fa(email: str, password: str, token: str, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(email, db)
    if not user or not auth_service.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not auth_service.verify_totp_token(user.totp_secret, token):
        raise HTTPException(status_code=401, detail="Invalid 2FA token")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get('/auth/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}

@router.get("/dashboard")
async def dashboard():
    return {"message": "Welcome to your dashboard!"}

@router.get("/password_reset")
async def password_reset(request: Request):
    return templates.TemplateResponse("users/password_reset.html", {"request": request})

@router.post("/password_reset")
async def handle_password_reset(background_tasks: BackgroundTasks, request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(email, db)
    if user:
        token = auth_service.create_email_token({"sub": user.email})
        background_tasks.add_task(send_reset_email, user.email, token, str(request.base_url))
    return RedirectResponse(url="/password_reset_done", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/password_reset_done")
async def password_reset_done(request: Request):
    return templates.TemplateResponse("users/password_reset_done.html", {"request": request})

@router.get("/password_reset_confirm/{token}")
async def password_reset_confirm(request: Request, token: str, db: Session = Depends(get_db)):
    try:
        email = await auth_service.get_email_from_token(token)
        user = await repository_users.get_user_by_email(email, db)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token or user does not exist")

        return templates.TemplateResponse("users/password_reset_confirm.html", {"request": request, "token": token})

    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

@router.post("/password_reset_confirm/{token}")
async def password_reset_confirm_post(request: Request, token: str, password: str = Form(...),
                                      confirm_password: str = Form(...), db: Session = Depends(get_db)):
    try:
        if password != confirm_password:
            return templates.TemplateResponse("users/password_reset_confirm.html", {
                "request": request,
                "token": token,
                "error": "Passwords do not match"
            })

        email = await auth_service.get_email_from_token(token)
        user = await repository_users.get_user_by_email(email, db)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token or user does not exist")

        hashed_password = auth_service.get_password_hash(password)

        user.password = hashed_password
        db.commit()

        return RedirectResponse(url="/password_reset_complete", status_code=status.HTTP_303_SEE_OTHER)

    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

@router.get("/password_reset_complete")
async def password_reset_complete(request: Request):
    return templates.TemplateResponse("users/password_reset_complete.html", {"request": request})
