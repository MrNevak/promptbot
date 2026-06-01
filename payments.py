import aiohttp
from config import CRYPTOBOT_TOKEN

API_URL = "https://pay.crypt.bot/api"


async def create_invoice(amount: float, name: str, payload: str):
    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }

    data = {
        "asset": "USDT",
        "amount": str(amount),
        "description": name,
        "payload": payload
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/createInvoice", data=data, headers=headers) as r:
            return await r.json()