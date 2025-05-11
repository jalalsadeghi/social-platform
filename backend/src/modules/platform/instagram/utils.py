# utils.py
import httpx
from core.config import settings

async def instagram_api_call(endpoint, method="GET", token=None, data=None):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.instagram.com/{endpoint}"
    async with httpx.AsyncClient() as client:
        if method == "POST":
            response = await client.post(url, headers=headers, json=data)
        else:
            response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()