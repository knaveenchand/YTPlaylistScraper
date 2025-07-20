from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import random
import uvicorn

app = FastAPI()

@app.get("/random_video_id")
async def get_random_video_id(playlist_url: str = Query(..., description="Full YouTube playlist URL")):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(playlist_url)
            await page.wait_for_selector("ytd-playlist-video-renderer", timeout=10000)

            elements = await page.query_selector_all("ytd-playlist-video-renderer a#video-title")
            video_ids = set()
            for el in elements:
                href = await el.get_attribute("href")
                if href and "watch?v=" in href:
                    vid_id = href.split("watch?v=")[1].split("&")[0]
                    video_ids.add(vid_id)

            await browser.close()

            if not video_ids:
                return JSONResponse(status_code=404, content={"error": "No video IDs found."})

            return {"video_id": random.choice(list(video_ids))}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
