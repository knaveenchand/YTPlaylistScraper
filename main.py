from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import random
import uvicorn

app = FastAPI()

@app.get("/random_video_id")
async def get_random_video_id(playlist_url: str = Query(..., alias="playlist_url")):
    print(f"▶️ Received playlist URL: {playlist_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        try:
            print(f"🌐 Navigating to playlist: {playlist_url}")
            response = await page.goto(playlist_url, timeout=30000)
            print(f"🔄 Status: {response.status if response else 'No response'}")

            # Wait for either the videos or the error page
            await page.wait_for_selector("ytd-playlist-video-renderer", timeout=15000)

            print("✅ Playlist loaded, extracting video IDs...")
            elements = await page.query_selector_all("ytd-playlist-video-renderer")

            video_ids = []
            for el in elements:
                link = await el.query_selector("a#video-title")
                if link:
                    href = await link.get_attribute("href")
                    if href and "watch?v=" in href:
                        video_id = href.split("watch?v=")[-1].split("&")[0]
                        video_ids.append(video_id)

            if not video_ids:
                raise ValueError("No video IDs found.")

            chosen = random.choice(video_ids)
            print(f"🎯 Random video ID: {chosen}")
            return {"video_id": chosen}

        except Exception as e:
            print("❌ Error occurred:", str(e))
            html = await page.content()
            snippet = html[:1000]
            return JSONResponse(
                status_code=500,
                content={
                    "error": str(e),
                    "html_snippet": snippet
                }
            )
        finally:
            await browser.close()

# Local dev testing
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
