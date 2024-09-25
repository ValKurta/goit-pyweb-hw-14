import unittest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db, SessionLocal


class TestGetDb(unittest.IsolatedAsyncioTestCase):
    @patch('database.db.SessionLocal', autospec=True)
    async def test_get_db(self, mock_session_local):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session_local.return_value.__aexit__.return_value = AsyncMock()

        db_gen = get_db()
        session = await anext(db_gen)

        self.assertEqual(session, mock_session)

        with self.assertRaises(StopAsyncIteration):
            await anext(db_gen)

        mock_session.close.assert_awaited()


if __name__ == '__main__':
    unittest.main()
