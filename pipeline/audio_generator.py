import os
import asyncio
import wave
import numpy as np
import edge_tts
import imageio_ffmpeg
import subprocess

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def generate_news_bgm(output_dir, duration=50.0):
    bgm_path = os.path.join(output_dir, "news_bgm.wav")
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    sig = np.zeros_like(t)
    
    # 1. Low dramatic bass pulse (120 BPM: beat every 0.5s)
    beat = 0.5
    for b in np.arange(0, duration, beat):
        dur_hit = 0.25
        t_hit = np.linspace(0, dur_hit, int(sr * dur_hit), endpoint=False)
        # Deep sub-kick + low synth pulse (55Hz / A1)
        hit = (np.sin(2 * np.pi * 55 * t_hit) + 0.3 * np.sin(2 * np.pi * 110 * t_hit)) * np.exp(-t_hit * 12.0)
        s_idx = int(b * sr)
        e_idx = min(s_idx + len(hit), len(sig))
        sig[s_idx:e_idx] += hit[:e_idx - s_idx] * 0.4
        
    # 2. Subtle high-tech news ticker tick on 16th notes (0.125s)
    for tick in np.arange(0, duration, 0.125):
        t_tick = np.linspace(0, 0.03, int(sr * 0.03), endpoint=False)
        tick_sound = np.sin(2 * np.pi * 3200 * t_tick) * np.exp(-t_tick * 100.0)
        s_idx = int(tick * sr)
        e_idx = min(s_idx + len(tick_sound), len(sig))
        sig[s_idx:e_idx] += tick_sound[:e_idx - s_idx] * 0.08
        
    max_val = np.max(np.abs(sig))
    if max_val > 0:
        sig = (sig / max_val) * 0.18 # Controlled background level
        
    audio_int16 = (sig * 32767).astype(np.int16)
    with wave.open(bgm_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
        
    return bgm_path

async def _synthesize_voice(text, voice_path):
    # AndrewNeural is an authoritative, rapid, documentary news anchor
    communicate = edge_tts.Communicate(text, "en-US-AndrewNeural", rate="+4%")
    submaker = edge_tts.SubMaker()
    
    with open(voice_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
                
    return submaker.cues

def generate_narration_and_audio(script_text, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    voice_path = os.path.join(output_dir, "news_voice.mp3")
    final_audio = os.path.join(output_dir, "final_audio.mp3")
    
    print("[Audio] Synthesizing news anchor narration...")
    cues = asyncio.run(_synthesize_voice(script_text, voice_path))
    
    subtitles = []
    for c in cues:
        s = c.start.total_seconds()
        e = c.end.total_seconds()
        subtitles.append((s, e, c.content))
        
    print(f"[Audio] Synthesized {len(subtitles)} sentence cues.")
    
    # Generate News BGM
    cmd_dur = [FFMPEG, "-i", voice_path, "-f", "null", "-"]
    res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, text=True)
    total_dur = 45.0
    for l in res.stderr.splitlines():
        if "Duration:" in l:
            parts = l.split("Duration:")[1].split(",")[0].strip().split(":")
            total_dur = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            break
            
    bgm_path = generate_news_bgm(output_dir, duration=total_dur + 3.0)
    
    # Mix
    cmd_mix = [
        FFMPEG, "-y",
        "-i", voice_path,
        "-i", bgm_path,
        "-filter_complex",
        "[1:a]volume=0.22[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        final_audio
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Audio] Final news audio mixed to {final_audio}")
    return final_audio, subtitles
