# modules/auth/oauth.py 
import httpx
from core.config import settings
from fastapi import HTTPException

async def get_instagram_user(code: str):
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        'client_id': settings.INSTAGRAM_CLIENT_ID,
        'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
        'redirect_uri': settings.INSTAGRAM_REDIRECT_URI,
        'code': code
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.get(token_url, params=params)
        token_response.raise_for_status()
        access_token = token_response.json()['access_token']

        fb_user_url = "https://graph.facebook.com/v19.0/me/accounts"
        user_response = await client.get(fb_user_url, params={'access_token': access_token})
        user_response.raise_for_status()
        user_data = user_response.json()

        if not user_data.get('data'):
            raise HTTPException(status_code=400, detail="No Facebook pages found for this user. Please create and connect a Facebook page first.")

        page_id = user_data['data'][0]['id']
        page_access_token = user_data['data'][0]['access_token']

        insta_account_url = f"https://graph.facebook.com/v19.0/{page_id}"
        insta_response = await client.get(insta_account_url, params={
            'fields': 'instagram_business_account',
            'access_token': page_access_token
        })
        insta_response.raise_for_status()
        insta_data = insta_response.json()

        if 'instagram_business_account' not in insta_data:
            raise HTTPException(status_code=400, detail="Instagram Business account not connected to your Facebook page. Please connect your Instagram account.")

        insta_user_id = insta_data['instagram_business_account']['id']

        insta_user_info_url = f"https://graph.facebook.com/v19.0/{insta_user_id}"
        insta_user_info_response = await client.get(insta_user_info_url, params={
            'fields': 'id,username',
            'access_token': page_access_token
        })
        insta_user_info_response.raise_for_status()
        insta_user_info = insta_user_info_response.json()

        return {
            'access_token': page_access_token,
            'instagram_user_id': insta_user_info['id'],
            'username': insta_user_info['username']
        }
