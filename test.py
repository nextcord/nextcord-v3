import asyncio

from nextcord.http import HTTPClient, Route

http = HTTPClient("ODYwMjQ2NTAzNTM2OTg0MDc0.YN4c_Q.zexAuYAvbOig2FyXgFR4cDeE2qY")

async def main():
    route = Route("POST", "/channels/{channel_id}/messages", channel_id=917135962474176582)
    for i in range(10):
        loop.create_task(http.request(route, json={"content": f"Ratelimit test: {i}"}))

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
