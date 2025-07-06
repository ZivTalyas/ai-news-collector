#!/usr/bin/env python3
"""
Dashboard Fix Script
Clears cache and restarts dashboard properly
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def kill_streamlit():
    """Kill any running Streamlit processes"""
    try:
        subprocess.run(['pkill', '-f', 'streamlit'], check=False)
        print("🔄 Stopped existing Streamlit processes")
        time.sleep(2)
    except:
        pass

def clear_streamlit_cache():
    """Clear Streamlit cache directory"""
    try:
        cache_dir = Path.home() / '.streamlit'
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            print("🗑️  Cleared Streamlit cache directory")
    except Exception as e:
        print(f"⚠️  Could not clear cache directory: {e}")

def test_database():
    """Test database connection and show stats"""
    try:
        from app.database import NewsDatabase
        from datetime import datetime, timezone
        
        db = NewsDatabase()
        total = db.get_article_count()
        
        # Get today's articles
        today = datetime.now(timezone.utc).date()
        start_date = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_date = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        today_articles = db.get_articles_by_date_range(start_date, end_date)
        
        print(f"📊 Database Status:")
        print(f"   Total articles: {total}")
        print(f"   Today's articles: {len(today_articles)}")
        print(f"   Today's date (UTC): {today}")
        
        if today_articles:
            print(f"   Latest article: {today_articles[0]['title'][:50]}...")
            print(f"   Latest date: {today_articles[0]['scraped_at']}")
        
        return total > 0
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def start_dashboard():
    """Start the dashboard"""
    try:
        print("🚀 Starting AI News Collector Dashboard...")
        os.chdir(Path(__file__).parent.parent)
        subprocess.run([sys.executable, 'run_dashboard.py'])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def main():
    print("🔧 AI News Collector Dashboard Fix")
    print("=" * 40)
    
    # Kill existing processes
    kill_streamlit()
    
    # Clear cache
    clear_streamlit_cache()
    
    # Test database
    if not test_database():
        print("❌ Database connection failed!")
        print("💡 Make sure your DATABASE_URL is configured in config/.env")
        return
    
    print("\n✅ Database connection successful!")
    print("🔄 Starting fresh dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    
    # Start dashboard
    start_dashboard()

if __name__ == "__main__":
    main() 