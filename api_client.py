import aiohttp
from config import API_BASE_URL, API_USER, API_PASS
import logging

logger = logging.getLogger(__name__)

async def create_hosting_user(username: str, password: str, server_type: str = "python") -> dict:
    url = f"{API_BASE_URL}/admin/api/users"
    auth = aiohttp.BasicAuth(API_USER, API_PASS)
    payload = {
        "username": username,
        "password": password,
        "server_type": server_type,
        "ram_mb": 512,
        "disk_gb": 1
    }
    
    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.error(f"API Error: Status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"API Connection Exception: {e}")
            return None

async def delete_hosting_user(server_id: str) -> bool:
    url = f"{API_BASE_URL}/admin/api/users/{server_id}"
    auth = aiohttp.BasicAuth(API_USER, API_PASS)
    
    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            async with session.delete(url) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"API Deletion Exception: {e}")
            return False
