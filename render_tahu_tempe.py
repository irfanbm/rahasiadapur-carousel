import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
from PIL import Image
import os, glob

HTML = "/home/ubuntu/rahasiadapur-carousel/kraft_tahu_tempe.html"
OUT_PNG = Path("/home/ubuntu/rahasiadapur-carousel/shots_tahu_tempe")
OUT_PNG.mkdir(exist_ok=True)

OUT_JPG_DIR = Path("/home/ubuntu/rahasiadapur-carousel/jpg/2026-09-30-1500/kraft-simpan-tahu-tempe")
OUT_JPG_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width":1080,"height":1440}, device_scale_factor=1)
        await page.goto(Path(HTML).as_uri())
        await page.wait_for_timeout(1000)
        n = await page.evaluate("document.querySelectorAll('.slide').length")
        for i in range(n):
            await page.evaluate(f"""
                document.querySelectorAll('.slide').forEach((c,idx)=>{{
                    c.style.display = idx==={i} ? 'block' : 'none';
                }});
            """)
            el = page.locator(".slide").nth(i)
            png_path = OUT_PNG / f"slide_{i+1:02d}.png"
            await el.screenshot(path=str(png_path))
            
            # Convert to JPG 88
            jpg_path = OUT_JPG_DIR / f"slide_{i+1:02d}.jpg"
            Image.open(png_path).convert("RGB").save(str(jpg_path), "JPEG", quality=88)
            print(f"Rendered & saved: {jpg_path}")
            
        await browser.close()
        print(f"Successfully processed {n} slides.")

asyncio.run(main())
