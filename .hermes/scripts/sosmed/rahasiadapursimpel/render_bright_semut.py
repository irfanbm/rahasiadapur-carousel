import os, glob
from playwright.sync_api import sync_playwright
from PIL import Image

shots_dir = "shots_bright_semut"
jpg_dir = "jpg/bright_v1"
os.makedirs(shots_dir, exist_ok=True)
os.makedirs(jpg_dir, exist_ok=True)

html_path = os.path.abspath("tips_bebas_semut_bright.html")

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
        
        # Convert PNG to JPG 88 quality
        img = Image.open(png_path).convert("RGB")
        img.save(jpg_path, "JPEG", quality=88)
        print(f"Rendered slide {i:02d} -> {jpg_path}")

    browser.close()

print(f"Done rendering {len(slides)} slides.")
