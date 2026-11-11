import os
import json
import time
import random
import urllib.request
import xml.etree.ElementTree as ET
import requests
from pipeline.config import GEMINI_API_KEY, TARGET_COUNTRIES

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("[History] Warning reading history:", e)
    return {
        "last_upload_timestamp": 0,
        "covered_topics": []
    }

def save_history(title):
    history = load_history()
    history["last_upload_timestamp"] = int(time.time())
    if "covered_topics" not in history:
        history["covered_topics"] = []
    history["covered_topics"].append(title)
    if len(history["covered_topics"]) > 60:
        history["covered_topics"] = history["covered_topics"][-60:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        print(f"[History] Recorded '{title}' into history.json")
    except Exception as e:
        print("[History] Error saving history:", e)

def fetch_top_headlines(max_per_country=3):
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    countries = list(TARGET_COUNTRIES.items())
    random.shuffle(countries)
    
    # Query countries to gather current landscape
    for country, url in countries[:7]:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                items = root.findall("./channel/item")
                for item in items[:max_per_country]:
                    title_elem = item.find("title")
                    if title_elem is not None and title_elem.text:
                        headlines.append({
                            "country": country,
                            "title": title_elem.text.strip()
                        })
        except Exception as e:
            print(f"[News] Notice: could not fetch news for {country}: {e}")
            
    return headlines

PROMPT_TEMPLATE = """
You are an expert viral news editor and AI breaking-news monitor.
Here are the latest live headlines collected across major world powers (USA, UK, Germany, France, Italy, India, Japan, Singapore, Sweden, Switzerland):

{headlines_text}

Previously covered topics (DO NOT REPEAT OR COVER THESE AGAIN):
{history_text}

Context:
- Current required heat threshold: {threshold}/100.
(A heat score of 80-100 means extraordinary breaking urgency, major conflict, unexpected market shock, sudden resignation, or historic crisis. 50-79 is significant daily developments.)

YOUR TASKS:
1. Identify the single MOST VIRAL, highest-heat breaking news topic among the headlines that hasn't been covered yet.
2. Rate its virality heat score from 1 to 100 based on shock value, global interest, and timeliness.
3. If the score is BELOW {threshold}, set "eligible": false.
4. If the score is AT OR ABOVE {threshold}, set "eligible": true and generate a complete viral 35-45 second Short script (85-105 words, high-tempo, dramatic hook, hard facts, outro question) and 5 detailed photorealistic documentary scene prompts.

Return ONLY a JSON object with this EXACT schema:
{{
  "heat_score": 85,
  "eligible": true,
  "country": "NAME_OF_COUNTRY",
  "title": "Dramatic Urgent Headline with Flag Emoji #Shorts #News",
  "description": "2-3 sentence overview with hashtags",
  "tags": ["news", "breaking news", "world news", "country_name", "shorts"],
  "script": "The 85-105 word spoken narration text.",
  "scenes": [
    "Scene 1: Detailed cinematic photo prompt, 9:16 vertical, photorealistic news photojournalism",
    "Scene 2...",
    "Scene 3...",
    "Scene 4...",
    "Scene 5..."
  ]
}}
"""

def evaluate_and_generate_news():
    history = load_history()
    last_ts = history.get("last_upload_timestamp", 0)
    hours_since_last = (time.time() - last_ts) / 3600.0 if last_ts > 0 else 999.0
    
    # Schedule Logic:
    # If >= 10 hours since last video, window is open for the guaranteed 2 daily shorts (threshold = 55)
    # If < 10 hours, only post if genuine high-heat breaking news spike occurs (threshold = 80)
    if hours_since_last >= 10.0:
        threshold = 55
        mode = "Scheduled Daily News Window"
    else:
        threshold = 80
        mode = "Breaking Viral Heat Monitor"
        
    print(f"\n[Monitor] Mode: {mode}")
    print(f"[Monitor] Hours since last upload: {hours_since_last:.1f}h | Heat threshold: {threshold}/100")
    
    headlines = fetch_top_headlines()
    if not headlines:
        print("[News] No headlines fetched from RSS feeds.")
        return None
        
    headlines_text = "\n".join([f"- [{h['country']}] {h['title']}" for h in headlines])
    history_text = "\n".join([f"- {h}" for h in history.get("covered_topics", [])[-15:]])
    
    prompt = PROMPT_TEMPLATE.format(
        headlines_text=headlines_text,
        history_text=history_text,
        threshold=threshold
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "response_mime_type": "application/json"}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(text)
            
            score = result.get("heat_score", 0)
            eligible = result.get("eligible", False)
            print(f"[Monitor] Evaluated Top Story: '{result.get('title')}'")
            print(f"[Monitor] Heat Score: {score}/100 | Threshold: {threshold} | Eligible: {eligible}")
            
            if eligible and score >= threshold:
                return result
            else:
                print(f"[Monitor] Story heat score ({score}) did not meet threshold ({threshold}). Standing by for next 30-min scan.")
                return None
        else:
            print(f"[News] Gemini API status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print("[News] Error evaluating news with Gemini:", e)
        
    return None
