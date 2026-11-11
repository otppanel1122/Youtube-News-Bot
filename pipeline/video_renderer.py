import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH = 1080
HEIGHT = 1920
FPS = 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def get_fonts():
    font_candidates = [
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for p in font_candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, 58), ImageFont.truetype(p, 42)
    default = ImageFont.load_default()
    return default, default

FONT_SUB, FONT_BANNER = get_fonts()

def wrap_text(text, max_chars=25):
    words = text.split()
    lines, curr_line, curr_len = [], [], 0
    for w in words:
        if curr_len + len(w) + (1 if curr_line else 0) <= max_chars:
            curr_line.append(w)
            curr_len += len(w) + (1 if len(curr_line) > 1 else 0)
        else:
            if curr_line:
                lines.append(" ".join(curr_line))
            curr_line = [w]
            curr_len = len(w)
    if curr_line:
        lines.append(" ".join(curr_line))
    return lines

def create_ken_burns_frame(base_img, progress):
    zoom = 1.0 + 0.08 * progress
    w, h = base_img.size
    crop_w, crop_h = w / zoom, h / zoom
    left = (w - crop_w) / 2.0
    top = (h - crop_h) / 2.0
    cropped = base_img.crop((int(left), int(top), int(left + crop_w), int(top + crop_h)))
    return cropped.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

def draw_news_overlays(img, text, country):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # 1. Top Breaking News Banner
    banner_text = f"BREAKING NEWS | {country.upper()}"
    bbox = overlay_draw.textbbox((0, 0), banner_text, font=FONT_BANNER)
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    
    pad_x, pad_y = 30, 16
    bx0 = (WIDTH - bw) // 2 - pad_x
    by0 = 220
    bx1 = (WIDTH + bw) // 2 + pad_x
    by1 = by0 + bh + pad_y * 2
    
    # Red breaking news badge with white border
    overlay_draw.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill=(210, 15, 30, 235), outline=(255, 255, 255, 220), width=3)
    overlay_draw.text(((WIDTH - bw) // 2, by0 + pad_y - 2), banner_text, font=FONT_BANNER, fill=(255, 255, 255, 255))
    
    # 2. Dynamic Subtitles in safe zone
    if text:
        lines = wrap_text(text, max_chars=24)
        line_spacing = 10
        line_bboxes = [overlay_draw.textbbox((0, 0), line.upper(), font=FONT_SUB) for line in lines]
        line_heights = [bb[3] - bb[1] for bb in line_bboxes]
        line_widths = [bb[2] - bb[0] for bb in line_bboxes]
        total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)
        max_text_w = max(line_widths)
        
        center_y = 1380
        start_y = center_y - total_text_h // 2
        
        s_pad_x, s_pad_y = 36, 20
        box_x0 = (WIDTH - max_text_w) // 2 - s_pad_x
        box_y0 = start_y - s_pad_y
        box_x1 = (WIDTH + max_text_w) // 2 + s_pad_x
        box_y1 = start_y + total_text_h + s_pad_y
        
        overlay_draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=24, fill=(10, 15, 25, 215))
        
        curr_y = start_y
        for i, line in enumerate(lines):
            t_str = line.upper()
            lw = line_widths[i]
            lx = (WIDTH - lw) // 2
            
            # High-impact news color highlighting
            if any(w in t_str for w in ["BREAKING", "CRISIS", "URGENT", "SHOCK", "WAR", "BILLION", "EMERGENCY"]):
                text_color = (255, 50, 50, 255) # Red highlight
            elif i == 0 and len(lines) > 1:
                text_color = (255, 230, 0, 255) # Yellow highlight
            else:
                text_color = (255, 255, 255, 255)
                
            overlay_draw.text((lx, curr_y), t_str, font=FONT_SUB, fill=text_color, stroke_width=5, stroke_fill=(0, 0, 0, 255))
            curr_y += line_heights[i] + line_spacing
            
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    return img

def render_news_short(image_paths, subtitles, audio_path, output_mp4, country="WORLD"):
    print("[Video] Initializing News Short rendering...")
    cmd_dur = [FFMPEG, "-i", audio_path, "-f", "null", "-"]
    res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, text=True)
    total_duration = 45.0
    for l in res.stderr.splitlines():
        if "Duration:" in l:
            parts = l.split("Duration:")[1].split(",")[0].strip().split(":")
            total_duration = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            break
            
    print(f"[Video] Detected duration: {total_duration:.2f}s")
    total_frames = int(total_duration * FPS)
    
    num_scenes = len(image_paths)
    scene_dur = total_duration / num_scenes
    loaded_imgs = [Image.open(p).convert("RGB") for p in image_paths]
    
    cmd_ff = [
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.2",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-ar", "44100",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        output_mp4
    ]
    
    proc = subprocess.Popen(cmd_ff, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        sc_idx = min(int(t / scene_dur), num_scenes - 1)
        sc_t = t - (sc_idx * scene_dur)
        progress = max(0.0, min(1.0, sc_t / scene_dur))
        
        # 1. Ken burns frame
        f_img = create_ken_burns_frame(loaded_imgs[sc_idx], progress)
        
        # 2. Subtitle text
        active_text = None
        for s, e, txt in subtitles:
            if s <= t <= e:
                active_text = txt
                break
                
        f_img = draw_news_overlays(f_img, active_text, country)
        bgr = np.array(f_img)[:, :, ::-1].tobytes()
        proc.stdin.write(bgr)
        
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        raise RuntimeError("FFmpeg rendering failed")
        
    cmd_verify = [FFMPEG, "-v", "error", "-i", output_mp4, "-f", "null", "-"]
    res_verify = subprocess.run(cmd_verify, stderr=subprocess.PIPE, text=True)
    if not res_verify.stderr:
        print("[Video] Verified: News Short is 100% healthy with valid MOOV atom (+faststart).")
    print(f"[Video] Successfully rendered {output_mp4} ({os.path.getsize(output_mp4) / 1024 / 1024:.2f} MB)")
    return output_mp4
