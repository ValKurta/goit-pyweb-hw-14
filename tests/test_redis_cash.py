import unittest
from unittest.mock import patch, AsyncMock
import os
from services.redis_cache import get_redis, redis_client

class TestGetRedis(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        global redis_client
        redis_client = None

    def tearDown(self):
        global redis_client
        redis_client = None

    @patch('services.redis_cache.aioredis.from_url', new_callable=AsyncMock)
    @patch.dict(os.environ, {'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379'})
    async def test_get_redis_first_call(self, mock_from_url):
        mock_redis_instance = AsyncMock()
        mock_from_url.return_value = mock_redis_instance

        client = await get_redis()

        mock_from_url.assert_called_once_with("redis://localhost:6379")
        self.assertEqual(client, mock_redis_instance)

    @patch('services.redis_cache.aioredis.from_url', new_callable=AsyncMock)
    @patch.dict(os.environ, {'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379'})
    async def test_get_redis_subsequent_call(self, mock_from_url):
        mock_redis_instance = AsyncMock()
        mock_from_url.return_value = mock_redis_instance

        client_first = await get_redis()
        client_second = await get_redis()

        mock_from_url.assert_called_once()
        self.assertEqual(client_first, client_second)

    @patch('services.redis_cache.aioredis.from_url', new_callable=AsyncMock)
    @patch.dict(os.environ, {'REDIS_HOST': 'custom_host', 'REDIS_PORT': '1234'})
    async def test_get_redis_custom_env(self, mock_from_url):
        mock_redis_instance = AsyncMock()
        mock_from_url.return_value = mock_redis_instance

        client = await get_redis()

        mock_from_url.assert_called_once_with("redis://custom_host:1234")
        self.assertEqual(client, mock_redis_instance)

    @patch('services.redis_cache.aioredis.from_url', new_callable=AsyncMock)
    @patch.dict(os.environ, {'REDIS_HOST': 'localhost', 'REDIS_PORT': '6379'})
    async def test_get_redis_exception(self, mock_from_url):
        mock_from_url.side_effect = Exception("Failed to connect to Redis")

        with self.assertRaises(Exception) as context:
            await get_redis()

        self.assertEqual(str(context.exception), "Failed to connect to Redis")
        mock_from_url.assert_called_once_with("redis://localhost:6379")

if __name__ == '__main__':
    unittest.main()
