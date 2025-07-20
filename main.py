from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import random
import traceback

app = FastAPI()

@app.get("/random_video_id")
async def get_random_video_id(playlist_url: str = Query(..., description="Full YouTube playlist URL")):
    print(f"🔍 Received request for playlist: {playlist_url}")
    
    try:
        async with async_playwright() as p:
            print("🚀 Launching browser...")
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            print("🌐 Navigating to playlist page...")
            await page.goto(playlist_url)
            await page.wait_for_timeout(2000)  # wait for content to load

            print("⏳ Waiting for playlist items to appear...")
            try:
                await page.wait_for_selector("ytd-playlist-video-renderer", timeout=10000)
            except Exception as selector_error:
                html = await page.content()
                snippet = html[:1000].replace('\n', '')
                await browser.close()
                return JSONResponse(status_code=500, content={
                    "error": "Selector 'ytd-playlist-video-renderer' not found.",
                    "html_snippet": snippet
                })

            print("✅ Playlist items found. Extracting video IDs...")
            video_elements = await page.query_selector_all("ytd-playlist-video-renderer")

            if not video_elements:
                await browser.close()
                return JSONResponse(status_code=404, content={"error": "No videos found in playlist."})

            video_ids = []
            for el in video_elements:
                href = await el.eval_on_selector("a#video-title", "el => el.href")
                print(f"🔗 Found href: {href}")
                if href:
                    if "watch?v=" in href:
                        video_id = href.split("watch?v=")[-1].split("&")[0]
                        video_ids.append(video_id)

            await browser.close()

            if not video_ids:
                return JSONResponse(status_code=404, content={"error": "No video IDs extracted from playlist."})

            selected_video_id = random.choice(video_ids)
            print(f"🎲 Selected video ID: {selected_video_id}")
            return {"video_id": selected_video_id}

    except Exception as e:
        print("🔥 Unhandled exception occurred:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
