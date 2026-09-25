import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

HTML = "/home/ubuntu/carousel/hemat_gas_v12.html"
OUT = Path("/home/ubuntu/carousel/shots_hemat_gas")
OUT.mkdir(exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width":1440,"height":1080}, device_scale_factor=1)
        await page.goto(Path(HTML).as_uri())
        await page.wait_for_timeout(400)
        n = await page.evaluate("document.querySelectorAll('.slide').length")
        for i in range(n):
            await page.evaluate(f"""
                document.querySelectorAll('.slide').forEach((c,idx)=>{{
                    c.style.display = idx==={i} ? 'block' : 'none';
                }});
            """)
            el = page.locator(".slide").nth(i)
            await el.screenshot(path=str(OUT / f"slide_{i+1:02d}.png"))
        await browser.close()
        print(f"rendered {n} slides to {OUT}")

asyncio.run(main())
