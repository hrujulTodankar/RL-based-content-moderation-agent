import asyncio
import json
import sys

import httpx

try:
    from app.main import app
except Exception as e:
    print("Failed to import FastAPI app:", e)
    sys.exit(1)


async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Health check
        r1 = await client.get("/")
        print("GET / ->", r1.status_code, json.dumps(r1.json(), ensure_ascii=False))

        # Moderate sample content
        mod_payload = {
            "content_id": "sample-content-123",
            "content_data": "This is a wonderful post!",
            "content_type": "text",
        }
        r2 = await client.post("/moderate", json=mod_payload)
        print("POST /moderate ->", r2.status_code, json.dumps(r2.json(), ensure_ascii=False))

        # Feedback
        fb_payload = {
            "content_id": "sample-content-123",
            "user_id": "user-1",
            "feedback_type": "positive",
            "comment": "Looks good",
        }
        r3 = await client.post("/feedback", json=fb_payload)
        print("POST /feedback ->", r3.status_code, json.dumps(r3.json(), ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
