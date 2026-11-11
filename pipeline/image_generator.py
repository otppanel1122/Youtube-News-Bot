import os
import urllib.parse
import time
import requests
from PIL import Image

def download_news_image(prompt, output_path, max_retries=3):
    enhanced_prompt = f"{prompt}, professional photojournalism, high quality 8k photography, reuters documentary style, cinematic atmospheric lighting, 9:16 vertical"
    encoded = urllib.parse.quote(enhanced_prompt)
    seed = int(time.time() * 1000) % 1000000
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&model=flux&seed={seed}&nologo=true"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for attempt in range(max_retries):
        try:
            print(f"[Image] Generating news scene (attempt {attempt+1}): {output_path}...")
            resp = requests.get(url, headers=headers, timeout=45)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                with Image.open(output_path) as img:
                    img.verify()
                print(f"[Image] Successfully saved {output_path}")
                return True
        except Exception as e:
            print(f"[Image] Attempt {attempt+1} warning: {e}")
            time.sleep(3)
            
    # Fallback to high-contrast graphic placeholder if network timeout
    print(f"[Image] Creating stylized editorial fallback for {output_path}")
    from PIL import ImageDraw
    fallback_img = Image.new("RGB", (768, 1344), color=(15, 20, 30))
    draw = ImageDraw.Draw(fallback_img)
    draw.rectangle([40, 40, 728, 1304], outline=(220, 20, 60), width=6)
    fallback_img.save(output_path, "JPEG")
    return True

def generate_scene_images(scenes, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for idx, sc in enumerate(scenes, start=1):
        p = os.path.join(output_dir, f"scene_{idx}.jpg")
        download_news_image(sc, p)
        paths.append(p)
    return paths
