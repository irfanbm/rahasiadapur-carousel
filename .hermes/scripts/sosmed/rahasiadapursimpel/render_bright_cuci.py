import os
from playwright.sync_api import sync_playwright
from PIL import Image

shots_dir = "shots_bright_cuci"
jpg_dir = "jpg/2026-09-25-1600/bright-cuci-piring-kilat"
os.makedirs(shots_dir, exist_ok=True)
os.makedirs(jpg_dir, exist_ok=True)

html_path = os.path.abspath("cuci_piring_bright_v1.html")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1440})
    page.goto(f"file://{html_path}")
    page.wait_for_load_state("networkidle")

    slides = page.query_selector_all(".slide")
    print(f"Found {len(slides)} slides")

    for i, slide in enumerate(slides, start=1):
        png_path = os.path.join(shots_dir, f"slide_{i:02d}.png")
        jpg_path = os.path.join(jpg_dir, f"slide_{i:02d}.jpg")
        slide.screenshot(path=png_path)
        img = Image.open(png_path).convert("RGB")
        img.save(jpg_path, "JPEG", quality=88)
        print(f"Rendered slide {i:02d} -> {jpg_path}")
