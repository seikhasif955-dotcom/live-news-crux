import streamlit as st
import feedparser
from bs4 import BeautifulSoup

# Page Configuration
st.set_page_config(page_title="Live News Crux", page_icon="📡", layout="centered")

def clean_html(raw_html):
    """Removes HTML tags and cleans up summary text."""
    if not raw_html:
        return "No summary available."
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=' ').strip()
    return text if text else "No summary available."

# News Feed URLs mapping for categories
CATEGORY_FEEDS = {
    "🔥 Top Stories": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "🌍 World News": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0oxWW5OamJHa3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "💼 Business & Tech": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0pRTVRGMGJHeXZNQ3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "🤖 AI & Technology": "https://news.google.com/rss/search?q=Artificial+Intelligence+Technology&hl=en-US&gl=US&ceid=US:en",
    "⚽ Sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0pRTVRGM2IzTXZNQ3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "🎬 Entertainment": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTR29SU2wyRmdDa0pRTVRGMmIzTXZNQ3RKMjluU3dKV1R5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
    "🧬 Health & Science": "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTR3dBSEpIUXRjSEp2Ykd3dEptVnVNZ2dBUAE?hl=en-US&gl=US&ceid=US:en",
}

def fetch_news(feed_url, limit):
    """Fetches articles from RSS feed."""
    feed = feedparser.parse(feed_url)
    return feed.entries[:limit]

# Initialize session state for tracking seen stories
if "seen_stories" not in st.session_state:
    st.session_state.seen_stories = set()

# App UI Header
st.title("📡 Live News Crux")
st.write("Real-time breaking news summaries tailored to your interest.")

# Sidebar Navigation
st.sidebar.header("🎯 Reader Preferences")

# Category Selector
category = st.sidebar.selectbox(
    "Choose a Category:",
    options=list(CATEGORY_FEEDS.keys())
)

# Optional Custom Search
custom_search = st.sidebar.text_input("Or Search Any Specific Keyword:", placeholder="e.g., Crypto, Climate, NASA")

# Number of stories slider
limit_input = st.sidebar.slider("Number of Stories", min_value=3, max_value=15, value=5)

# Refresh Button
refresh_clicked = st.sidebar.button("🔄 Refresh / Check for Latest")

# Determine URL source
if custom_search.strip():
    selected_url = f"https://news.google.com/rss/search?q={custom_search.strip()}&hl=en-US&gl=US&ceid=US:en"
    display_topic = f"Search: '{custom_search.strip()}'"
else:
    selected_url = CATEGORY_FEEDS[category]
    display_topic = category

# Fetch news entries
entries = fetch_news(selected_url, limit_input)

if not entries:
    st.error("Could not fetch news right now. Please check your connection or search query.")
else:
    # Check if there are new unseen stories
    current_ids = {getattr(entry, 'id', entry.link) for entry in entries}
    new_ids = current_ids - st.session_state.seen_stories

    # Show fresh status header
    if refresh_clicked and not new_ids:
        st.info("ℹ️ No new updates found at this moment. Showing latest existing news.")
    else:
        st.success(f"🟢 Showing latest news for: **{display_topic}**")

    # Update seen set
    st.session_state.seen_stories.update(current_ids)

    st.markdown("---")

    # Display Article Cards
    for index, entry in enumerate(entries, start=1):
        headline = entry.title
        summary = clean_html(getattr(entry, 'summary', ''))
        link = entry.link
        pub_date = getattr(entry, 'published', 'N/A')

        st.subheader(f"{index}. {headline}")
        st.caption(f"🕒 Published: {pub_date}")
        st.markdown(f"**💡 Crux:** {summary}")
        st.markdown(f"[🔗 Read Full Story]({link})")
        st.markdown("---")
