import streamlit as st
import feedparser
from bs4 import BeautifulSoup

# Page Configuration
st.set_page_config(page_title="Live News Crux", page_icon="📡", layout="centered")

def clean_html(raw_html):
    """Removes HTML tags and cleans up the summary text."""
    if not raw_html:
        return "No summary available."
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=' ').strip()
    return text if text else "No summary available."

def fetch_news(topic, limit):
    if topic:
        url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
    else:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(url)
    return feed.entries[:limit]

# App UI Header
st.title("📡 Live News Crux")
st.write("Get the latest breaking news and its short crux in real-time.")

# Sidebar Controls
st.sidebar.header("Settings")
topic_input = st.sidebar.text_input("Topic/Keyword (Optional)", value="")
limit_input = st.sidebar.slider("Number of Stories", min_value=3, max_value=15, value=5)

# Refresh Button
if st.sidebar.button("🔄 Refresh News"):
    st.rerun()

# Fetch and display news
entries = fetch_news(topic_input, limit_input)

if not entries:
    st.error("Could not fetch news. Please check your connection or keyword.")
else:
    st.success(f"🟢 Showing latest news for: **{topic_input or 'Top Stories'}**")
    st.markdown("---")

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
