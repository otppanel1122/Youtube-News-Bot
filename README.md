# 🌍 24/7 Global Breaking News YouTube Shorts Autonomous Monitor

Autonomous 24/7 AI-driven pipeline that checks breaking news wires every **30 minutes** across the **USA, UK, Germany, France, Italy, India, Japan, Singapore, Sweden, and Switzerland**, rates virality and breaking heat via **Gemini 3.8 Flash**, and automatically publishes high-heat Shorts to YouTube without manual intervention.

---

## ⚡ How the 30-Minute Heat Engine Works

```
Every 30 Minutes (GitHub Actions Cron: */30 * * * *)
           │
           ▼
[1] Live News Wire Scan ────► Ingests top RSS feeds across 10 countries
           │
           ▼
[2] Gemini 3.8 Flash    ────► Scores top story (1-100) and checks against history.json
           │
      ┌────┴────────────────────────┐
      ▼                             ▼
Heat < Threshold              Heat >= Threshold (or Scheduled Window)
(No urgent news)              (High-Heat Breaking News!)
      │                             │
Graceful exit (~5s)           1. Generates 9:16 Photojournalism Visuals
                              2. Synthesizes Neural News Anchor Voice
                              3. Composites 1080x1920 video with Red Breaking Banner
                              4. Uploads to YouTube Channel
                              5. Saves topic to history.json & pushes back to repo
```

---

## 🕒 Smart Scheduling & Thresholds
* **Breaking News Spike:** If an unexpected crisis, conflict escalation, or major market surprise occurs (Heat Score ≥ 80), it is **instantly generated and uploaded** during the 30-minute check.
* **Guaranteed Daily News:** If more than 10 hours have passed since the last upload, the threshold lowers to 55 to ensure you automatically get your **2 daily flagship news shorts** (morning & evening) even on slower news days.
