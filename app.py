import streamlit as st
import feedparser
from bs4 import BeautifulSoup

# Page Setup
st.set_page_config(page_title="NewsPulse | Live Crux", page_icon="⚡", layout="wide")

# Custom CSS for Modern, Animated UI
st.markdown("""
<style>
    /* Dark Theme Canvas */
    .stApp {
        background: linear-gradient(135deg, #0d0e15 0%, #1a1c29 100%);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated Gradient Title Header */
    .title-glow {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #7928ca, #00dfd8);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-text 4s linear infinite;
        margin-bottom: 0.2rem;
    }

    @keyframes gradient-text {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    /* Live Pulse Badge */
    .live-badge {
        display: inline-block;
        background: rgba(255, 75, 75, 0.15);
        color: #ff4b4b;
        border: 1px solid rgba(255, 75, 75, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    .pulse-dot {
        height: 8px;
        width: 8px;
        background-color: #ff4b4b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
    }

    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 75, 75, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }

    /* Glassmorphism News Cards */
    .news-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Animated Hover Effect */
    .news-card:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(0, 223, 216, 0.4);
        box-shadow: 0 12px 30px rgba(0, 223, 216, 0.15);
    }

    .card-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.4;
        margin-bottom: 8px;
    }

    .card-time {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-bottom: 12px;
    }

    .card-crux {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    .card-link {
        display: inline-block;
        color: #00dfd8;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: color 0.2s ease;
    }

    .card-link:hover {
        color: #7928ca;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

def clean_html(raw_html):
    """Removes HTML tags and cleans up summary text."""
    if not raw_html:
        return "No short summary available."
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=' ').strip()
    return text if text else "No short summary available."

# Category Feeds Map
CATEGORY_FEEDS = {
    "🔥 Top Stories": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "🌍 World News": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0oxWW5OamJHa3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "💼 Business & Tech": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0pRTVRGMGJHeXZNQ3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "🤖 AI & Technology": "https://news.google.com/rss/search?q=Artificial+Intelligence+Technology&hl=en-US&gl=US&ceid=US:en",
    "⚽ Sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0pRTVRGM2IzTXZNQ3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "🎬 Entertainment": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0pRTVRGM2IzTXZNQ3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "🧬 Health & Science": "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTR3dBSEpIUXRjSEp2Ykd3dEptVnVNZ2dBUAE?hl=en-US&gl=US&ceid=US:en",
}

def fetch_news(feed_url, limit):
    feed = feedparser.parse(feed_url)
    return feed.entries[:limit]

# Session State
if "seen_stories" not in st.session_state:
    st.session_state.seen_stories = set()

# Main Header Area
st.markdown('<div class="title-glow">⚡ NewsPulse</div>', unsafe_allow_html=True)
st.markdown('<div class="live-badge"><span class="pulse-dot"></span>LIVE INTERNET FEED</div>', unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("🎯 Preferences")
category = st.sidebar.selectbox("Category", options=list(CATEGORY_FEEDS.keys()))
custom_search = st.sidebar.text_input("Custom Keyword Search", placeholder="e.g. NVIDIA, Tesla, Crypto")
limit_input = st.sidebar.slider("Number of Stories", min_value=3, max_value=15, value=5)
refresh_clicked = st.sidebar.button("🔄 Check For Latest Updates")

# Handle Feed Link
if custom_search.strip():
    selected_url = f"https://news.google.com/rss/search?q={custom_search.strip()}&hl=en-US&gl=US&ceid=US:en"
    display_topic = f"Search: '{custom_search.strip()}'"
else:
    selected_url = CATEGORY_FEEDS[category]
    display_topic = category

# Fetch Data
entries = fetch_news(selected_url, limit_input)

if not entries:
    st.error("Unable to fetch news feeds right now.")
else:
    current_ids = {getattr(entry, 'id', entry.link) for entry in entries}
    new_ids = current_ids - st.session_state.seen_stories

    if refresh_clicked and not new_ids:
        st.info("ℹ️ You are viewing the latest news available right now.")
    
    st.session_state.seen_stories.update(current_ids)

    # Render Animated Custom Cards
    for entry in entries:
        headline = entry.title
        summary = clean_html(getattr(entry, 'summary', ''))
        link = entry.link
        pub_date = getattr(entry, 'published', 'N/A')

        card_html = f"""
        <div class="news-card">
            <div class="card-title">📌 {headline}</div>
            <div class="card-time">🕒 {pub_date}</div>
            <div class="card-crux">💡 <b>Crux:</b> {summary}</div>
            <a href="{link}" target="_blank" class="card-link">Read full story on original publisher →</a>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
