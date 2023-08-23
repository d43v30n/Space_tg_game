import json
import os
import logging
import asyncio
from dotenv import load_dotenv
import aiohttp


load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = "nanofract.glowing.space"

url = {
    "url": "https://" + DOMAIN + "/api/telegram"
}

API_URL = 'https://api.telegram.org/bot%s/setWebhook' % API_TOKEN


async def register_webhook():
    headers = {
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL,
                                data=json.dumps(url),
                                headers=headers) as resp:
            try:
                assert resp.status == 200
            except Exception as e:
                return {'success': False, 'message': 'Возникла ошибка'}
            result = await resp.json()
            return {'success': result['result'], 'message': result['description']}


if __name__ == '__main__':
    response = asyncio.run(register_webhook())
    print(response['message'])
    if response['success']:
        exit(0)
    else:
        exit(1)
