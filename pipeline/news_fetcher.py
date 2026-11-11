import os
import json
import random
import urllib.request
import xml.etree.ElementTree as ET
import requests
from pipeline.config import GEMINI_API_KEY, TARGET_COUNTRIES

def fetch_top_headlines(max_per_country=3):
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Randomly shuffle country check order to ensure fair coverage across runs
    countries = list(TARGET_COUNTRIES.items())
    random.shuffle(countries)
    
    for country, url in countries[:6]: # Sample 6 countries per run
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

def load_history():
    history_file = "history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(topic_title):
    history_file = "history.json"
    history = load_history()
    history.append(topic_title)
    if len(history) > 50:
        history = history[-50:]
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print("[News] History save error:", e)

PROMPT_TEMPLATE = """
You are an expert investigative international news anchor and viral video producer.
Here is a list of live breaking news headlines across key world nations (USA, UK, Germany, France, Italy, India, Japan, Singapore, Sweden, Switzerland):

{headlines_text}

Previously covered topics to avoid repeating:
{history_text}

TASK:
1. Analyze these headlines and identify the single HIGHEST-HEAT, most urgent, dramatic, or globally consequential breaking news topic.
2. Produce a rapid-fire, captivating 35-45 second news Short script.
3. Word count: exactly 85 to 105 words. (Fast, authoritative news anchor pace).
4. Structure:
   - Hook (0-5s): Red alert / breaking headline statement that shocks or grips the viewer.
   - Core Development (5-25s): The key facts, numbers, high-stakes decisions, and geopolitical implications.
   - Global Fallout (25-35s): Why this matters to citizens and the world economy/politics.
   - Outro (35-40s): Thought-provoking question asking viewers for their opinion ("Leave your thoughts below and subscribe for breaking updates.").
5. Provide exactly 5 distinct visual scene descriptions for AI photorealistic editorial/documentary image generation (9:16 vertical, highly detailed, dramatic newsroom/documentary style).

Return ONLY a JSON object matching this schema:
{{
  "country": "NAME_OF_COUNTRY",
  "title": "Shocking/Urgent Headline with Flag Emoji #Shorts #News",
  "description": "2-3 sentence overview of the breaking event with relevant news hashtags.",
  "tags": ["news", "breaking news", "world news", "current affairs", "country_name", "shorts"],
  "script": "The 85-105 word spoken narration text.",
  "scenes": [
    "Scene 1: Detailed cinematic editorial photo prompt, 9:16 vertical, photorealistic news photojournalism",
    "Scene 2...",
    "Scene 3...",
    "Scene 4...",
    "Scene 5..."
  ]
}}
"""

def generate_news_story():
    print("[News] Fetching live headlines across target nations...")
    headlines = fetch_top_headlines()
    history = load_history()
    
    headlines_text = "\n".join([f"- [{h['country']}] {h['title']}" for h in headlines])
    history_text = "\n".join([f"- {h}" for h in history[-10:]])
    
    prompt = PROMPT_TEMPLATE.format(headlines_text=headlines_text, history_text=history_text)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75, "response_mime_type": "application/json"}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            story = json.loads(text)
            print(f"[News] Selected High-Heat Story ({story.get('country')}): {story.get('title')}")
            save_history(story.get("title"))
            return story
        else:
            print(f"[News] Gemini API error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print("[News] Error generating story via Gemini:", e)
        
    # Fallback high-heat template
    fallback = {
        "country": "USA",
        "title": "🚨 URGENT: Major Global Economic Shift Underway 🇺🇸 #Shorts #News",
        "description": "Breaking international updates as global central banks convene over currency volatility. #news #worldnews #economy",
        "tags": ["breaking news", "world news", "usa", "economy", "geopolitics", "shorts"],
        "script": (
            "Breaking news from Washington. Global financial markets are reacting sharply as new international trade "
            "regulations take effect across major economies. Officials in Europe and Asia are holding emergency meetings "
            "to assess the currency impact and supply chain shifts. Experts warn that supply routes between the West "
            "and Pacific allies could face unprecedented realignments by the end of this quarter. "
            "Is the global economy heading toward a reset? Drop your opinion below and subscribe for daily breaking reports."
        ),
        "scenes": [
            "Press conference at the US Capitol with flashing camera lights and international microphones, cinematic news lighting, 9:16 vertical",
            "Global stock market digital trading board glowing with red and green numbers in modern financial center, 9:16 vertical",
            "International leaders sitting at a diplomatic summit table discussing urgent global affairs, photorealistic news photo, 9:16 vertical",
            "Huge container cargo ships crossing busy international shipping channel at dusk, dramatic lighting, 9:16 vertical",
            "World map glowing with trade and communication network lines on digital screen in news control room, 9:16 vertical"
        ]
    }
    return fallback
