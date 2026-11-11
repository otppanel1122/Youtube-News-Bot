import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
VIDEO_PRIVACY = os.getenv("VIDEO_PRIVACY", "public")

OUTPUT_DIR = os.path.join(os.getcwd(), "output")
TEMP_DIR = os.path.join(os.getcwd(), "temp")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

TARGET_COUNTRIES = {
    "USA": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "UK": "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en",
    "INDIA": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "JAPAN": "https://news.google.com/rss/search?q=Japan+breaking+news&hl=en-US&gl=US&ceid=US:en",
    "GERMANY": "https://news.google.com/rss/search?q=Germany+breaking+news&hl=en-US&gl=US&ceid=US:en",
    "FRANCE": "https://news.google.com/rss/search?q=France+breaking+news&hl=en-US&gl=US&ceid=US:en",
    "ITALY": "https://news.google.com/rss/search?q=Italy+breaking+news&hl=en-US&gl=US&ceid=US:en",
    "SINGAPORE": "https://news.google.com/rss/search?q=Singapore+breaking+news&hl=en-US&gl=US&ceid=US:en",
    "SWEDEN": "https://news.google.com/rss/search?q=Sweden+breaking+news&hl=en-US&gl=US&ceid=US:en",
    "SWITZERLAND": "https://news.google.com/rss/search?q=Switzerland+breaking+news&hl=en-US&gl=US&ceid=US:en",
}
