import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from pipeline.news_fetcher import generate_news_story
from pipeline.image_generator import generate_scene_images
from pipeline.audio_generator import generate_narration_and_audio
from pipeline.video_renderer import render_news_short
from pipeline.youtube_uploader import upload_news_video
from pipeline.config import OUTPUT_DIR, TEMP_DIR

def run():
    print("=" * 60)
    print("🌍 STARTING GLOBAL BREAKING NEWS SHORTS PIPELINE")
    print("=" * 60)
    
    timestamp = int(time.time())
    run_temp_dir = os.path.join(TEMP_DIR, f"news_run_{timestamp}")
    os.makedirs(run_temp_dir, exist_ok=True)
    
    # 1. Fetch live news & select viral hot topic
    print("\n[Step 1/5] Scanning Global Headlines & Crafting Viral News Short...")
    story = generate_news_story()
    country = story.get("country", "WORLD")
    print(f"Target Country: {country}")
    print(f"Title: {story['title']}")
    print(f"Script: {story['script']}")
    
    # 2. Generate 9:16 Photojournalism Scene Images
    print("\n[Step 2/5] Generating 9:16 Photojournalism Visuals...")
    image_paths = generate_scene_images(story["scenes"], run_temp_dir)
    
    # 3. Anchor Voiceover & Ticker Audio Synthesis
    print("\n[Step 3/5] Synthesizing News Anchor Audio & Subtitles...")
    audio_path, subtitles = generate_narration_and_audio(story["script"], run_temp_dir)
    
    # 4. Render Video with Breaking News Banner & Dynamic Captions
    print("\n[Step 4/5] Rendering 1080x1920 Breaking News Short...")
    output_mp4 = os.path.join(OUTPUT_DIR, f"news_short_{timestamp}.mp4")
    render_news_short(image_paths, subtitles, audio_path, output_mp4, country=country)
    
    # 5. Upload to Channel 2
    print("\n[Step 5/5] Uploading to YouTube Channel 2...")
    video_url = upload_news_video(
        output_mp4,
        title=story["title"],
        description=story["description"],
        tags=story["tags"]
    )
    
    print("\n" + "=" * 60)
    if video_url:
        print(f"🎉 NEWS SHORT PUBLISHED: {video_url}")
    else:
        print(f"✅ Video created at: {output_mp4} (Upload skipped or pending credentials)")
    print("=" * 60)

if __name__ == "__main__":
    run()
