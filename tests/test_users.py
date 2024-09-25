import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.orm import Session
from database.models import User
from repository import users as repository_users
from fastapi import HTTPException, BackgroundTasks, Request, Depends
from database.schemas import UserModel
from services.auth import auth_service
from services.email import send_email
from fastapi.security import OAuth2PasswordRequestForm
from services.redis_cache import get_redis


class TestUserRepository(unittest.IsolatedAsyncioTestCase):

    @patch('repository.users.Session', new_callable=AsyncMock)
    async def test_get_user_by_email_existing_user(self, mock_session):
        mock_user = User(
            id=16,
            username="ValKurta",
            email="valentyn.kurta@gmail.com",
            password="$argon2id$v=19$m=102400,t=6,p=8$gLC2lpJyzpkzJiTk3Jvzvg$...",
            avatar=None,
            refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            totp_secret=None,
            confirmed=True
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_session.execute.return_value = mock_result

        user = await repository_users.get_user_by_email("valentyn.kurta@gmail.com", mock_session)

        self.assertEqual(user, mock_user)
        self.assertEqual(user.email, "valentyn.kurta@gmail.com")

    @patch('repository.users.Session', new_callable=AsyncMock)
    async def test_get_user_by_email_no_user(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        user = await repository_users.get_user_by_email("nonexistentuser@gmail.com", mock_session)

        self.assertIsNone(user)


@patch('repository.users.get_user_by_email', new_callable=AsyncMock)
@patch('repository.users.create_user', new_callable=AsyncMock)
@patch('services.email.send_email', new_callable=AsyncMock)
@patch('services.auth.auth_service.get_password_hash', new_callable=MagicMock)
async def test_signup_success(mock_get_password_hash, mock_send_email, mock_create_user, mock_get_user_by_email):

    mock_get_user_by_email.return_value = None

    mock_user = MagicMock()
    mock_user.email = "newuser@example.com"
    mock_user.username = "newuser"
    mock_create_user.return_value = mock_user

    mock_get_password_hash.return_value = "hashedpassword"


    body = UserModel(
        email="newuser@example.com",
        username="newuser",
        password="password"
    )


    background_tasks = BackgroundTasks()
    request = MagicMock(Request)

    from routes.auth import signup

    response = await signup(body, background_tasks, request)

    for task in background_tasks.tasks:
        await task()

    mock_create_user.assert_called_once()

    mock_send_email.assert_called_once_with("newuser@example.com", "newuser", ANY)  # Используем ANY для base_url

    assert response["message"] == "User created"

    @patch('repository.users.get_user_by_email', new_callable=AsyncMock)
    async def test_signup_user_already_exists(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = MagicMock()

        body = UserModel(
            email="existinguser@example.com",
            username="existinguser",
            password="password"
        )

        background_tasks = BackgroundTasks()
        request = MagicMock(Request)

        from routes.auth import signup

        with self.assertRaises(HTTPException) as context:
            await signup(body, background_tasks, request)

        self.assertEqual(context.exception.status_code, 409)


if __name__ == '__main__':
    unittest.main()
