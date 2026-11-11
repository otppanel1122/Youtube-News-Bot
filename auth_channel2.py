import os
import sys
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if not CLIENT_ID or not CLIENT_SECRET:
    CLIENT_ID = input("Enter YouTube Client ID: ").strip()
    CLIENT_SECRET = input("Enter YouTube Client Secret: ").strip()

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8085/"]
    }
}

def authenticate():
    print("=" * 60, flush=True)
    print("[AUTH] CHANNEL 2 (NEWS CHANNEL) YOUTUBE AUTHENTICATION", flush=True)
    print("=" * 60, flush=True)
    print("\nStarting local authentication server on port 8085...", flush=True)
    
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES, redirect_uri="http://localhost:8085/")
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    print("\n[AUTH LINK] Click this link to authorize Channel 2:", flush=True)
    print(auth_url, flush=True)
    print("\nWaiting for browser callback on http://localhost:8085/ ...\n", flush=True)
    
    creds = flow.run_local_server(port=8085, prompt="consent", access_type="offline")
    refresh_token = creds.refresh_token
    
    print("\n" + "=" * 60, flush=True)
    print("[SUCCESS] CHANNEL 2 AUTHENTICATION SUCCESSFUL!", flush=True)
    print(f"CHANNEL 2 YOUTUBE_REFRESH_TOKEN:\n{refresh_token}", flush=True)
    print("=" * 60, flush=True)
    
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines() if not l.startswith("YOUTUBE_REFRESH_TOKEN=")]
    lines.append(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")
    with open(".env", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Saved credentials to .env file.", flush=True)
    return refresh_token

if __name__ == "__main__":
    authenticate()
