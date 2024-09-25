from sqlalchemy.orm import Session
from sqlalchemy.future import select
from database.models import User
from database.schemas import UserModel
import logging


async def get_user_by_email(email: str, db: Session):
    result = await db.execute(select(User).filter(User.email == email))
    scalar_result = result.scalars()
    return scalar_result.first()

async def create_user(user: UserModel, db: Session):
    new_user = User(**user.model_dump(), totp_secret=None)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    await db.commit()

async def get_user_by_id(user_id: int, db: Session):
    result = await db.execute(select(User).filter(User.id == user_id))
    scalar_result = result.scalars()
    return scalar_result.first()

async def update_totp_secret(user: User, totp_secret: str, db: Session):
    user.totp_secret = totp_secret
    await db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.add(user)
    logging.info(f"Confirming email for user: {user.email}")
    await db.commit()

async def get_user_from_data(data: dict) -> User:
    return User(
        id=data["id"],
        username=data["username"],
        email=data["email"],
        password=data["password"],
        created_at=data.get("created_at"),
        avatar=data.get("avatar"),
        refresh_token=data.get("refresh_token"),
        totp_secret=data.get("totp_secret"),
        confirmed=data.get("confirmed"),
    )
