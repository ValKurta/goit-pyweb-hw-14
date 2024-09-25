import unittest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from sqlalchemy.future import select
from database.models import User
from database.schemas import UserModel

from repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    get_user_by_id,
    update_totp_secret,
    confirmed_email,
    get_user_from_data
)

class TestUserService(unittest.IsolatedAsyncioTestCase):

    @patch('repository.users.Session', autospec=True)
    async def test_get_user_by_email(self, mock_session):
        email = "test@example.com"

        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_scalars = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.first.return_value = User(email=email)

        user = await get_user_by_email(email, mock_session)

        mock_session.execute.assert_called_once_with(ANY)
        self.assertEqual(user.email, email)

    @patch('repository.users.Session', autospec=True)
    async def test_create_user(self, mock_session):
        user_data = UserModel(
            username="test_user",
            email="test@example.com",
            password="pass123"
        )
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        new_user = await create_user(user_data, mock_session)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        self.assertEqual(new_user.email, user_data.email)

    @patch('repository.users.Session', autospec=True)
    async def test_update_token(self, mock_session):
        user = User(email="test@example.com", refresh_token=None)
        token = "new_refresh_token"
        mock_session.commit = AsyncMock()

        await update_token(user, token, mock_session)

        self.assertEqual(user.refresh_token, token)
        mock_session.commit.assert_awaited_once()

    @patch('repository.users.Session', autospec=True)
    async def test_get_user_by_id(self, mock_session):
        user_id = 1
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_scalars = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.first.return_value = User(id=user_id)

        user = await get_user_by_id(user_id, mock_session)

        mock_session.execute.assert_called_once_with(ANY)
        self.assertEqual(user.id, user_id)

    @patch('repository.users.Session', autospec=True)
    async def test_update_totp_secret(self, mock_session):
        user = User(email="test@example.com", totp_secret=None)
        totp_secret = "new_totp_secret"
        mock_session.commit = AsyncMock()

        await update_totp_secret(user, totp_secret, mock_session)

        self.assertEqual(user.totp_secret, totp_secret)
        mock_session.commit.assert_awaited_once()

    @patch('repository.users.Session', autospec=True)
    async def test_confirmed_email(self, mock_session):
        email = "test@example.com"
        mock_user = User(email=email, confirmed=False)
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_scalars = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_scalars.first.return_value = mock_user
        mock_session.commit = AsyncMock()

        await confirmed_email(email, mock_session)

        mock_session.execute.assert_called_once_with(ANY)
        self.assertTrue(mock_user.confirmed)
        mock_session.commit.assert_awaited_once()

    async def test_get_user_from_data(self):
        data = {
            "id": 1,
            "username": "test_user",
            "email": "test@example.com",
            "password": "password123",
            "avatar": None,
            "refresh_token": "some_token",
            "totp_secret": None,
            "confirmed": False
        }

        user = await get_user_from_data(data)

        self.assertEqual(user.id, data["id"])
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.username, data["username"])

if __name__ == '__main__':
    unittest.main()
