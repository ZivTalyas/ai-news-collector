#!/usr/bin/env python3
"""
AI News Collector Dashboard
Streamlit app for displaying collected AI news articles with focus on today's news
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from database import NewsDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI News Today",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .today-header {
        font-size: 2rem;
        color: #ff6b6b;
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(90deg, #ff6b6b, #ffd93d);
        border-radius: 1rem;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .article-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #fafafa;
    }
    .today-article-card {
        border: 2px solid #ff6b6b;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #fff5f5, #fafafa);
        box-shadow: 0 2px 4px rgba(255, 107, 107, 0.1);
    }
    .ai-tool-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .timestamp {
        color: #666;
        font-size: 0.9rem;
    }
    .breaking-news {
        background-color: #ff4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .date-filter-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_articles(ai_tool_filter="All", limit=50, date_filter="All Time"):
    """Load articles from database with caching and date filtering"""
    try:
        db = NewsDatabase()
        
        if date_filter == "Today":
            # Get articles from today
            today = datetime.now(timezone.utc).date()
            start_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_date = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
            articles = db.get_articles_by_date_range(start_date, end_date)
        elif date_filter == "Yesterday":
            # Get articles from yesterday
            yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
            start_date = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_date = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.utc)
            articles = db.get_articles_by_date_range(start_date, end_date)
        elif date_filter == "Last 7 Days":
            # Get articles from last 7 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)
            articles = db.get_articles_by_date_range(start_date, end_date)
        else:
            # All time
            articles = db.get_articles(
                limit=limit,
                ai_tool_type=ai_tool_filter if ai_tool_filter != "All" else None
            )
        
        # Apply AI tool filter if not already applied
        if ai_tool_filter != "All" and date_filter != "All Time":
            articles = [a for a in articles if a.get('type_of_ai_tool') == ai_tool_filter]
        
        return articles[:limit]
        
    except Exception as e:
        st.error(f"Error loading articles: {e}")
        return []

@st.cache_data(ttl=300)
def load_stats():
    """Load database statistics with caching"""
    try:
        db = NewsDatabase()
        total_articles = db.get_article_count()
        ai_tool_types = db.get_ai_tool_types()
        latest_scrape = db.get_latest_scrape_time()
        
        # Get today's articles count
        today = datetime.now(timezone.utc).date()
        start_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_date = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        today_articles = db.get_articles_by_date_range(start_date, end_date)
        today_count = len(today_articles)
        
        return total_articles, ai_tool_types, latest_scrape, today_count
        
    except Exception as e:
        st.error(f"Error loading stats: {e}")
        return 0, [], None, 0

def format_datetime(iso_string):
    """Format ISO datetime string for display"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 3600:  # Less than 1 hour
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:  # Less than 24 hours
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
        elif diff.days == 1:
            return "Yesterday"
        else:
            return dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        return iso_string

def get_ai_tool_color(tool_type):
    """Get color for AI tool type badge"""
    colors = {
        'LLM': '#FF6B6B',
        'Computer Vision': '#4ECDC4',
        'Robotics': '#45B7D1',
        'Machine Learning': '#96CEB4',
        'AI Tools': '#FFEAA7',
        'General AI': '#DDA0DD'
    }
    return colors.get(tool_type, '#B0B0B0')

def is_today(iso_string):
    """Check if the article is from today"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        today = datetime.now(timezone.utc).date()
        return dt.date() == today
    except:
        return False

def is_recent(iso_string, hours=6):
    """Check if article is from the last N hours"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds() < hours * 3600
    except:
        return False

def main():
    # Header
    st.markdown('<h1 class="main-header">📰 AI News Today</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("📊 Dashboard Controls")
    
    # Load statistics
    total_articles, ai_tool_types, latest_scrape, today_count = load_stats()
    
    # Display key metrics in sidebar
    st.sidebar.markdown("### 📈 Statistics")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Today's News", today_count)
    with col2:
        st.metric("Total Articles", total_articles)
    
    if latest_scrape:
        latest_scrape_formatted = format_datetime(latest_scrape)
        st.sidebar.metric("Latest Scrape", latest_scrape_formatted)
    else:
        st.sidebar.warning("No articles found in database")
    
    # Filter controls
    st.sidebar.markdown("### 🔍 Filters")
    
    # Date filter
    date_options = ["Today", "Yesterday", "Last 7 Days", "All Time"]
    selected_date = st.sidebar.selectbox("📅 Date Range", date_options, index=0)
    
    # AI Tool Type filter
    ai_tool_options = ["All"] + sorted(ai_tool_types)
    selected_ai_tool = st.sidebar.selectbox("🤖 AI Tool Type", ai_tool_options)
    
    # Number of articles to display
    articles_limit = st.sidebar.slider("📊 Number of Articles", 10, 100, 50)
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Today's Headlines Section
    if selected_date == "Today" or selected_date == "All Time":
        st.markdown('<div class="today-header">🔥 Today\'s AI Headlines</div>', unsafe_allow_html=True)
        
        # Load today's articles specifically
        today_articles = load_articles("All", 10, "Today")
        
        if today_articles:
            st.markdown(f"### 📊 {len(today_articles)} articles found today")
            
            # Show today's articles with special styling
            for i, article in enumerate(today_articles[:5], 1):  # Show top 5 today
                breaking_badge = ""
                if is_recent(article['scraped_at'], 3):  # Last 3 hours
                    breaking_badge = '<span class="breaking-news">🔥 BREAKING</span>'
                
                st.markdown(f"""
                <div class="today-article-card">
                    {breaking_badge}
                    <h4>{article['title']}</h4>
                    <span class="ai-tool-badge" style="background-color: {get_ai_tool_color(article['type_of_ai_tool'])}">{article['type_of_ai_tool']}</span>
                    <p class="timestamp">📅 {format_datetime(article['scraped_at'])}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"🔗 [Read Full Article]({article['url']})")
                if i < len(today_articles):
                    st.markdown("---")
        else:
            st.info("🤖 No articles found for today yet. Run the scraper to collect fresh news!")
            if st.button("▶️ Run Scraper Now"):
                with st.spinner("Collecting today's AI news..."):
                    try:
                        import subprocess
                        result = subprocess.run(['python', 'scraper.py'], 
                                              capture_output=True, text=True, timeout=300)
                        
                        if result.returncode == 0:
                            st.success("✅ Scraper completed! Refreshing data...")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ Scraper failed: {result.stderr}")
                    except Exception as e:
                        st.error(f"❌ Error running scraper: {e}")
    
    # Main content area
    st.markdown("---")
    st.markdown("### 📰 All AI News")
    
    # Date filter info box
    if selected_date != "All Time":
        st.markdown(f"""
        <div class="date-filter-box">
            📅 <strong>Showing articles from: {selected_date}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Load and display articles
    articles = load_articles(selected_ai_tool, articles_limit, selected_date)
    
    if not articles:
        st.warning(f"No articles found for the selected filters ({selected_date}, {selected_ai_tool})")
        st.info("💡 **Tips**:")
        st.info("- Try changing the date range or AI tool filter")
        st.info("- Run the scraper to collect more articles")
        st.info("- Check if the scraper has run today")
    else:
        # Display article count
        filter_info = f"**{selected_date}**"
        if selected_ai_tool != "All":
            filter_info += f" • **{selected_ai_tool}**"
        
        st.info(f"📊 Found {len(articles)} articles • {filter_info}")
        
        # Display articles
        for i, article in enumerate(articles, 1):
            is_today_article = is_today(article['scraped_at'])
            card_class = "today-article-card" if is_today_article else "article-card"
            
            breaking_badge = ""
            if is_recent(article['scraped_at'], 6):  # Last 6 hours
                breaking_badge = '<span class="breaking-news">🆕 NEW</span>'
            
            st.markdown(f"""
            <div class="{card_class}">
                {breaking_badge}
                <h4>{article['title']}</h4>
                <span class="ai-tool-badge" style="background-color: {get_ai_tool_color(article['type_of_ai_tool'])}">{article['type_of_ai_tool']}</span>
                <p class="timestamp">📅 {format_datetime(article['scraped_at'])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Article link
            st.markdown(f"🔗 [Read Full Article]({article['url']})")
            
            # Separator
            if i < len(articles):
                st.markdown("---")
    
    # Footer with statistics
    if articles:
        st.markdown("### 📊 Article Analytics")
        
        # Create analytics
        df = pd.DataFrame(articles)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏷️ AI Tool Distribution")
            tool_counts = df['type_of_ai_tool'].value_counts()
            st.bar_chart(tool_counts)
        
        with col2:
            st.markdown("#### 📈 Article Breakdown")
            for tool_type, count in tool_counts.items():
                percentage = (count / len(articles)) * 100
                st.markdown(f"**{tool_type}**: {count} articles ({percentage:.1f}%)")
    
    # Auto-refresh notification
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏰ Auto-Refresh")
    st.sidebar.info("Data refreshes every 5 minutes automatically")
    
    # Scraper control
    st.sidebar.markdown("### 🤖 Scraper Control")
    if st.sidebar.button("▶️ Collect Fresh News", help="Run the scraper to get the latest AI news"):
        with st.spinner("🔍 Searching for fresh AI news..."):
            try:
                import subprocess
                result = subprocess.run(['python', 'scraper.py'], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    st.success("✅ Fresh news collected successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Scraper failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                st.error("❌ Scraper timed out (5 minutes)")
            except Exception as e:
                st.error(f"❌ Error running scraper: {e}")

if __name__ == "__main__":
    # Check if MongoDB URI is configured
    if not os.getenv('MONGO_URI'):
        st.error("❌ MONGO_URI environment variable not found!")
        st.info("Please set up your MongoDB Atlas connection string in the environment variables.")
        st.code("export MONGO_URI='your_mongodb_connection_string'", language="bash")
        st.stop()
    
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        st.info("Please check your database connection and try again.") 