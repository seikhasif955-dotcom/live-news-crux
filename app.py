import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import urllib.parse

# Page Setup
st.set_page_config(page_title="NewsPulse 3D | Live Crux", page_icon="⚡", layout="wide")

# Custom CSS & 3D Interactive Canvas Script
st.markdown("""
<style>
    /* Hide default Streamlit header elements for a clean app look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #050508;
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
        overflow-x: hidden;
    }

    /* 3D Interactive Background Canvas */
    #bg-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
    }

    /* Ensure content sits above the 3D background */
    .block-container {
        position: relative;
        z-index: 2;
    }

    /* 3D Animated Gradient Title Header */
    .title-glow {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ff4b4b 0%, #7928ca 50%, #00dfd8 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-text 5s linear infinite;
        margin-bottom: 0.2rem;
        text-shadow: 0 10px 30px rgba(121, 40, 202, 0.3);
    }

    @keyframes gradient-text {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    /* 3D Pulsing Live Badge */
    .live-badge {
        display: inline-block;
        background: rgba(255, 75, 75, 0.1);
        color: #ff4b4b;
        border: 1px solid rgba(255, 75, 75, 0.3);
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.15);
    }
    
    .pulse-dot {
        height: 8px;
        width: 8px;
        background-color: #ff4b4b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
    }

    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }

    /* 3D Glassmorphism News Cards with Perspective Tilt */
    .news-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        transform-style: preserve-3d;
        transform: perspective(1000px);
        transition: transform 0.4s cubic-bezier(0.1, 0.7, 0.1, 1), border-color 0.4s ease, box-shadow 0.4s ease;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .news-card:hover {
        transform: perspective(1000px) translateY(-8px) rotateX(2deg) rotateY(2deg);
        border-color: rgba(0, 223, 216, 0.4);
        box-shadow: 0 25px 50px rgba(0, 223, 216, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .card-title {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 800;
        line-height: 1.4;
        margin-bottom: 10px;
    }

    .card-time {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 14px;
    }

    .card-crux {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 18px;
    }

    .card-link {
        display: inline-flex;
        align-items: center;
        color: #00dfd8;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }

    .card-link:hover {
        color: #ff4b4b;
        transform: translateX(4px);
    }
</style>

<!-- 3D Interactive Background Particles Script -->
<canvas id="bg-canvas"></canvas>
<script>
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    let mouse = { x: width / 2, y: height / 2 };
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    const particles = [];
    for(let i = 0; i < 60; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2 + 1,
            vx: (Math.random() - 0.5) * 0.6,
            vy: (Math.random() - 0.5) * 0.6,
            color: Math.random() > 0.5 ? '#00dfd8' : '#7928ca'
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        particles.forEach(p => {
            p.x += p.vx + (mouse.x - width/2) * 0.0002;
            p.y += p.vy + (mouse.y - height/2) * 0.0002;
            
            if(p.x < 0) p.x = width;
            if(p.x > width) p.x = 0;
            if(p.y < 0) p.y = height;
            if(p.y > height) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.shadowBlur = 15;
            ctx.shadowColor = p.color;
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
</script>
""", unsafe_allow_html=True)

def clean_html(raw_html):
    if not raw_html:
        return "No short summary available."
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=' ').strip()
    return text if text else "No short summary available."

# Category Feeds Mapping
CATEGORY_QUERIES = {
    "🔥 Top Stories": "",
    "🌍 World News": "world news",
    "💼 Business & Tech": "business technology news",
    "🤖 AI & Technology": "artificial intelligence tech",
    "⚽ Sports": "sports news",
    "🎬 Entertainment": "entertainment movie celebrity news",
    "🧬 Health & Science": "health science medical news"
}

def fetch_news(feed_url, limit):
    feed = feedparser.parse(feed_url)
    return feed.entries[:limit]

# Session State
if "seen_stories" not in st.session_state:
    st.session_state.seen_stories = set()

# Main Header Area
st.markdown('<div class="title-glow">⚡ NewsPulse 3D</div>', unsafe_allow_html=True)
st.markdown('<div class="live-badge"><span class="pulse-dot"></span>3D IMMERSIVE LIVE FEED</div>', unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("🎯 Preferences")
category = st.sidebar.selectbox("Category", options=list(CATEGORY_QUERIES.keys()))
custom_search = st.sidebar.text_input("Custom Keyword Search", placeholder="e.g. NVIDIA, Tesla, Crypto")
limit_input = st.sidebar.slider("Number of Stories", min_value=3, max_value=15, value=5)
refresh_clicked = st.sidebar.button("🔄 Check For Latest Updates")

# Build URL safely
if custom_search.strip():
    query = custom_search.strip()
    display_topic = f"Search: '{query}'"
else:
    query = CATEGORY_QUERIES[category]
    display_topic = category

if query == "":
    selected_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
else:
    encoded_query = urllib.parse.quote(query)
    selected_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

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

    # Render 3D Cards
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
            <a href="{link}" target="_blank" class="card-link">Read full story on original publisher &rarr;</a>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
