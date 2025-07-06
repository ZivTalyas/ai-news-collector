#!/usr/bin/env python3
"""
AI News Collector Dashboard
Modern, minimalist Streamlit app for displaying AI news with focus on today's updates
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.database import NewsDatabase
from dotenv import load_dotenv

# Load environment variables from config folder (for local development)
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

# Page configuration
st.set_page_config(
    page_title="AI News Today",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_database_url():
    """Get PostgreSQL DATABASE_URL from environment variables or Streamlit secrets"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            return st.secrets['DATABASE_URL']
    except:
        pass
    
    # Fall back to environment variables (for local development)
    return os.getenv('DATABASE_URL')

def load_css():
    """Load custom CSS from external file"""
    css_path = Path(__file__).parent.parent / 'static' / 'dashboard.css'
    if css_path.exists():
        with open(css_path, 'r') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found. Using default styling.")

# Load custom CSS
load_css()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_articles(ai_tool_filter="All", limit=50, date_filter="All Time"):
    """Load articles from database with caching and date filtering"""
    try:
        # Pass the PostgreSQL DATABASE_URL explicitly to the database
        database_url = get_database_url()
        if not database_url:
            st.error("❌ PostgreSQL connection string not found. Please configure DATABASE_URL in Streamlit secrets.")
            return []
        
        db = NewsDatabase(database_url_override=database_url)
        
        if date_filter == "Today":
            today = datetime.now(timezone.utc).date()
            start_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_date = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
            articles = db.get_articles_by_date_range(start_date, end_date)
        elif date_filter == "Yesterday":
            yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
            start_date = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_date = datetime.combine(yesterday, datetime.max.time()).replace(tzinfo=timezone.utc)
            articles = db.get_articles_by_date_range(start_date, end_date)
        elif date_filter == "Last 7 Days":
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)
            articles = db.get_articles_by_date_range(start_date, end_date)
        else:
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
        # Show more detailed error for debugging
        st.error(f"Detailed error: {str(e)}")
        return []

@st.cache_data(ttl=300)
def load_stats():
    """Load database statistics with caching"""
    try:
        database_url = get_database_url()
        if not database_url:
            st.error("❌ PostgreSQL connection string not found. Please configure DATABASE_URL in Streamlit secrets.")
            return 0, [], None, 0
        
        db = NewsDatabase(database_url_override=database_url)
        total_articles = db.get_article_count()
        ai_tool_types = db.get_ai_tool_types()
        latest_scrape = db.get_latest_scrape_time()
        
        # Get today's articles count
        today = datetime.now(timezone.utc).date()
        start_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_date = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        today_articles = db.get_articles_by_date_range(start_date, end_date)
        today_count = len(today_articles)
        
        # Debug information (remove this in production)
        if st.checkbox("🔍 Show Debug Info", value=False):
            st.write(f"Debug: Found {total_articles} total articles, {today_count} today")
            st.write(f"Database: PostgreSQL")
            st.write(f"AI Tool Types: {ai_tool_types}")
            st.write(f"Latest Scrape: {latest_scrape}")
        
        return total_articles, ai_tool_types, latest_scrape, today_count
        
    except Exception as e:
        st.error(f"Error loading stats: {e}")
        st.error(f"Detailed error: {str(e)}")
        return 0, [], None, 0

def format_time_ago(iso_string):
    """Format time as 'X minutes ago' or 'X hours ago'"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    except:
        return "Unknown"

def get_ai_tool_badge_class(tool_type):
    """Get CSS class for AI tool badge"""
    badge_map = {
        'LLM': 'badge-primary',
        'Computer Vision': 'badge-secondary',
        'Robotics': 'badge-success',
        'Machine Learning': 'badge-warning',
        'AI Tools': 'badge-primary',
        'General AI': 'badge-secondary'
    }
    return badge_map.get(tool_type, 'badge-secondary')

def is_recent(iso_string, hours=3):
    """Check if article is from the last N hours"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds() < hours * 3600
    except:
        return False

def is_today(iso_string):
    """Check if the article is from today"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        today = datetime.now(timezone.utc).date()
        return dt.date() == today
    except:
        return False

def render_article_card(article, featured=False):
    """Render a single article card"""
    card_class = "article-card featured" if featured else "article-card"
    
    # Determine badges
    badges = []
    
    # AI tool badge
    badge_class = get_ai_tool_badge_class(article['type_of_ai_tool'])
    badges.append(f'<span class="badge {badge_class}">{article["type_of_ai_tool"]}</span>')
    
    # Breaking news badge
    if is_recent(article['scraped_at'], 3):
        badges.append('<span class="badge badge-breaking">Breaking</span>')
    elif is_recent(article['scraped_at'], 12):
        badges.append('<span class="badge badge-success">New</span>')
    
    badges_html = ' '.join(badges)
    time_ago = format_time_ago(article['scraped_at'])
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="article-meta">
            {badges_html}
            <span class="timestamp">⏰ {time_ago}</span>
        </div>
        <h3 class="article-title">{article['title']}</h3>
        <div class="article-meta">
            <a href="{article['url']}" target="_blank" class="article-link">
                📖 Read Full Article →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('''
    <div class="main-header">🤖 AI News Today</div>
    <div class="subtitle">Stay updated with the latest AI developments</div>
    ''', unsafe_allow_html=True)
    
    # Load statistics
    total_articles, ai_tool_types, latest_scrape, today_count = load_stats()
    
    # Today's Section
    if today_count > 0:
        st.markdown(f'''
        <div class="today-section">
            <div class="today-header">Today's AI Headlines</div>
            <div class="today-stats">
                <div class="stat-item">
                    <span class="stat-number">{today_count}</span>
                    <span class="stat-label">Articles Today</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_articles}</span>
                    <span class="stat-label">Total Articles</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(ai_tool_types)}</span>
                    <span class="stat-label">AI Categories</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">🔍 Filters</h3>', unsafe_allow_html=True)
        
        # Date filter
        date_options = ["Today", "Yesterday", "Last 7 Days", "All Time"]
        selected_date = st.selectbox("📅 Time Range", date_options, index=0)
        
        # AI Tool Type filter
        ai_tool_options = ["All"] + sorted(ai_tool_types)
        selected_ai_tool = st.selectbox("🏷️ Category", ai_tool_options)
        
        # Number of articles
        articles_limit = st.slider("📊 Articles to Show", 10, 100, 30)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistics
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">📈 Statistics</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Today", today_count)
        with col2:
            st.metric("Total", total_articles)
        
        if latest_scrape:
            latest_time = format_time_ago(latest_scrape)
            st.markdown(f"🕒 **Last Update**: {latest_time}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="sidebar-title">🔄 Actions</h3>', unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Data", type="secondary"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🗑️ Clear Cache", help="Clear cached data if dashboard shows wrong info"):
            st.cache_data.clear()
            st.success("Cache cleared! Refreshing...")
            st.rerun()
        
        if st.button("🤖 Collect News", type="primary"):
            with st.spinner("Collecting fresh AI news..."):
                try:
                    # Import scraper directly instead of subprocess
                    from app.scraper import AINewsScaper
                    
                    # Create scraper instance and run
                    database_url = get_database_url()
                    scraper = AINewsScaper(database_url_override=database_url)
                    scraper.run_daily_scrape()
                    
                    st.success("✅ News collected successfully!")
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Collection failed: {str(e)}")
                    # Show more detailed error for debugging
                    st.error(f"Error details: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    articles = load_articles(selected_ai_tool, articles_limit, selected_date)
    
    # Auto-fallback: if no articles for today, show recent articles
    if not articles and selected_date == "Today":
        st.info("📰 No articles found for today. Showing recent articles instead.")
        articles = load_articles(selected_ai_tool, articles_limit, "Last 7 Days")
        selected_date = "Last 7 Days"  # Update display text
    
    if not articles:
        # Check if database is completely empty
        if total_articles == 0:
            st.markdown('''
            <div class="empty-state">
                <div class="empty-state-icon">🚀</div>
                <h3>Welcome to AI News Collector!</h3>
                <p>Your database is empty. Let's collect some fresh AI news to get started.</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Auto-collect news on first load
            if st.button("🚀 Get Started - Collect AI News", type="primary"):
                with st.spinner("🔍 Collecting fresh AI news for you..."):
                    try:
                        from app.scraper import AINewsScaper
                        database_url = get_database_url()
                        scraper = AINewsScaper(database_url_override=database_url)
                        scraper.run_daily_scrape()
                        st.success("✅ News collected! Refreshing...")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Collection failed: {str(e)}")
                        st.error("You can try again or check your internet connection.")
        else:
            # Empty state for filtered results
            st.markdown('''
            <div class="empty-state">
                <div class="empty-state-icon">📰</div>
                <h3>No articles found</h3>
                <p>Try adjusting your filters or collect fresh news</p>
            </div>
            ''', unsafe_allow_html=True)
        
        if st.button("▶️ Collect Fresh News", type="primary"):
            with st.spinner("🔍 Searching for AI news..."):
                try:
                    # Import scraper directly instead of subprocess
                    from app.scraper import AINewsScaper
                    
                    # Create scraper instance and run
                    database_url = get_database_url()
                    scraper = AINewsScaper(database_url_override=database_url)
                    scraper.run_daily_scrape()
                    
                    st.success("✅ News collected!")
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Collection failed: {str(e)}")
                    st.error(f"Error details: {e}")
    else:
        # Articles header
        filter_text = f"**{selected_date}**"
        if selected_ai_tool != "All":
            filter_text += f" • **{selected_ai_tool}**"
        
        st.markdown(f'''
        <div class="filter-section">
            <div class="filter-title">📰 Articles ({len(articles)})</div>
            <p>Showing {filter_text}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Featured articles (today's articles get special treatment)
        today_articles = [a for a in articles if is_today(a['scraped_at'])]
        other_articles = [a for a in articles if not is_today(a['scraped_at'])]
        
        # Show today's articles first with featured styling
        if today_articles and selected_date in ["Today", "All Time"]:
            st.markdown("### 🔥 Today's Headlines")
            for article in today_articles[:5]:  # Show top 5 today's articles
                render_article_card(article, featured=True)
        
        # Show other articles
        if other_articles or (today_articles and len(today_articles) > 5):
            if today_articles and selected_date in ["Today", "All Time"]:
                st.markdown("### 📚 More Articles")
                remaining_today = today_articles[5:] if len(today_articles) > 5 else []
                for article in remaining_today + other_articles:
                    render_article_card(article)
            else:
                for article in other_articles:
                    render_article_card(article)
        
        # Analytics section
        if len(articles) > 5:
            st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
            st.markdown("### 📊 Analytics")
            
            # Create analytics
            df = pd.DataFrame(articles)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏷️ Category Distribution")
                tool_counts = df['type_of_ai_tool'].value_counts()
                st.bar_chart(tool_counts)
            
            with col2:
                st.markdown("#### 📈 Category Breakdown")
                for tool_type, count in tool_counts.items():
                    percentage = (count / len(articles)) * 100
                    st.markdown(f"**{tool_type}**: {count} articles ({percentage:.1f}%)")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🤖 **AI News Collector**")
        st.markdown("Modern dashboard for AI news")
    
    with col2:
        st.markdown("🔄 **Auto-Refresh**")
        st.markdown("Data updates every 5 minutes")
    
    with col3:
        st.markdown("☁️ **Cloud-Powered**")
        st.markdown("PostgreSQL + Streamlit")

if __name__ == "__main__":
    main() 