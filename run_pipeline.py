import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from pipeline.news_fetcher import evaluate_and_generate_news, save_history
from pipeline.image_generator import generate_scene_images
from pipeline.audio_generator import generate_narration_and_audio
from pipeline.video_renderer import render_news_short
from pipeline.youtube_uploader import upload_news_video
from pipeline.config import OUTPUT_DIR, TEMP_DIR

def run():
    print("=" * 60)
    print("🌍 24/7 GLOBAL BREAKING NEWS VIRAL MONITOR")
    print("=" * 60)
    
    # Step 1: Scan real-time news & evaluate viral heat
    story = evaluate_and_generate_news()
    if not story:
        print("\n✅ Heat check complete: No urgent breaking news at this time.")
        print("Standing by for next 30-minute automated scan. Exiting.")
        sys.exit(0)
        
    country = story.get("country", "WORLD")
    title = story.get("title", "Breaking News")
    print("\n🔥 HIGH-HEAT BREAKING NEWS DETECTED!")
    print(f"Nation: {country}")
    print(f"Title: {title}")
    print(f"Heat Score: {story.get('heat_score')}/100")
    print(f"Script: {story.get('script')}")
    
    timestamp = int(time.time())
    run_temp_dir = os.path.join(TEMP_DIR, f"news_run_{timestamp}")
    os.makedirs(run_temp_dir, exist_ok=True)
    
    # Step 2: Generate 9:16 Photojournalism Visuals
    print("\n[Step 2/4] Generating 9:16 Photojournalism Visuals...")
    image_paths = generate_scene_images(story["scenes"], run_temp_dir)
    
    # Step 3: Anchor Voiceover & Ticker Audio Synthesis
    print("\n[Step 3/4] Synthesizing News Anchor Audio & Subtitles...")
    audio_path, subtitles = generate_narration_and_audio(story["script"], run_temp_dir)
    
    # Step 4: Render Video with Breaking News Banner & Faststart
    print("\n[Step 4/4] Rendering 1080x1920 Breaking News Short...")
    output_mp4 = os.path.join(OUTPUT_DIR, f"news_short_{timestamp}.mp4")
    render_news_short(image_paths, subtitles, audio_path, output_mp4, country=country)
    
    # Step 5: Upload to YouTube Channel 2
    print("\n[Step 5/5] Uploading to YouTube Channel 2...")
    video_url = upload_news_video(
        output_mp4,
        title=title,
        description=story["description"],
        tags=story["tags"]
    )
    
    if video_url:
        save_history(title)
        print("\n" + "=" * 60)
        print(f"🎉 HIGH-HEAT BREAKING NEWS SHORT PUBLISHED: {video_url}")
        print("=" * 60)
    else:
        print(f"✅ Video created at: {output_mp4} (Upload skipped or pending credentials)")

if __name__ == "__main__":
    run()
