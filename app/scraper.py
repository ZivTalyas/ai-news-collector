#!/usr/bin/env python3
"""
AI News Collector Scraper Bot
Searches Google for AI news articles and stores them in PostgreSQL
"""

import os
import re
import time
import requests
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup
from googlesearch import search
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.database import NewsDatabase
from dotenv import load_dotenv

# Load environment variables from config folder (if available)
try:
    load_dotenv(Path(__file__).parent.parent / 'config' / '.env')
except Exception:
    pass  # .env file might not exist in production/GitHub Actions

class AINewsScaper:
    def __init__(self, database_url_override=None):
        # Get database URL from multiple sources
        if database_url_override:
            db_url = database_url_override
        else:
            # Try to get from environment variable (GitHub Actions, production)
            db_url = os.getenv('DATABASE_URL')
            
            # If not found, show helpful error message
            if not db_url:
                print("❌ DATABASE_URL environment variable is required")
                print("💡 Solutions:")
                print("   1. Set DATABASE_URL in your environment")
                print("   2. Add DATABASE_URL to your .env file in config/")
                print("   3. Pass database_url_override when creating AINewsScaper")
                raise ValueError("DATABASE_URL environment variable is required")
        
        self.db = NewsDatabase(database_url_override=db_url)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # AI tool keywords for classification
        self.ai_tool_keywords = {
            'LLM': ['gpt', 'chatgpt', 'claude', 'gemini', 'llama', 'language model', 'large language model', 'llm'],
            'Computer Vision': ['computer vision', 'image recognition', 'opencv', 'yolo', 'object detection', 'image ai'],
            'Robotics': ['robot', 'robotics', 'autonomous', 'drone', 'self-driving', 'automation'],
            'Machine Learning': ['machine learning', 'ml', 'neural network', 'deep learning', 'tensorflow', 'pytorch'],
            'AI Tools': ['midjourney', 'dall-e', 'stable diffusion', 'copilot', 'ai assistant', 'ai tool'],
            'General AI': ['artificial intelligence', 'ai news', 'ai breakthrough', 'ai research']
        }

    def search_google_for_ai_news(self, max_results=10):
        """Search Google for recent AI news articles"""
        search_queries = [
            "AI news today",
            "artificial intelligence latest news",
            "machine learning news",
            "AI technology updates"
        ]
        
        articles = []
        seen_urls = set()
        
        for query in search_queries:
            if len(articles) >= max_results:
                break
                
            try:
                print(f"Searching for: {query}")
                # Search Google with site restrictions to trusted sources
                search_query = f"{query} site:techcrunch.com OR site:venturebeat.com OR site:theverge.com OR site:arstechnica.com OR site:wired.com"
                
                search_results = search(search_query, num_results=5, sleep_interval=1)
                
                for url in search_results:
                    if len(articles) >= max_results:
                        break
                        
                    if url in seen_urls:
                        continue
                        
                    seen_urls.add(url)
                    article = self.extract_article_info(url)
                    
                    if article:
                        articles.append(article)
                        print(f"✓ Found article: {article['title'][:50]}...")
                        
                time.sleep(2)  # Be respectful to search engines
                
            except Exception as e:
                print(f"Error searching for '{query}': {e}")
                continue
                
        return articles[:max_results]

    def is_article_url(self, url):
        """Check if URL looks like an individual article (not a category/tag page)"""
        # Skip URLs that are clearly not individual articles
        skip_patterns = [
            '/tag/', '/category/', '/page/', '/archive/', '/latest/',
            '/topics/', '/section/', '/author/', '/search/', '/feed/',
            '?page=', '&page=', '/page-', '/p/', '/recent/',
            '/all-posts', '/news-archive', '/blog-archive'
        ]
        
        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        
        # URL should look like an article (has some content after domain)
        path_parts = url.split('/')
        if len(path_parts) < 4:  # e.g., https://domain.com/article-title
            return False
            
        return True

    def extract_article_info(self, url):
        """Extract title and classify AI tool type from an article URL"""
        # First check if this looks like an individual article URL
        if not self.is_article_url(url):
            print(f"⚠️ Skipping non-article URL: {url}")
            return None
            
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title') or soup.find('h1')
            if not title_tag:
                return None
                
            title = title_tag.get_text().strip()
            
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            title = title.replace('\n', ' ').replace('\t', ' ')
            
            # Skip if title is too short or doesn't seem related to AI
            if len(title) < 10:
                return None
                
            # Skip if title indicates it's a listing/category page
            if any(indicator in title.lower() for indicator in ['latest news', 'all posts', 'archive', 'category', 'tag']):
                print(f"⚠️ Skipping category page: {title[:50]}...")
                return None
                
            # Check if article is AI-related
            content_text = soup.get_text().lower()
            title_lower = title.lower()
            
            ai_related = any(keyword in title_lower or keyword in content_text for keywords in self.ai_tool_keywords.values() for keyword in keywords)
            
            if not ai_related:
                return None
            
            # Classify AI tool type
            ai_tool_type = self.classify_ai_tool_type(title + " " + content_text[:1000])
            
            return {
                'title': title,
                'url': url,
                'type_of_ai_tool': ai_tool_type,
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting article from {url}: {e}")
            return None

    def classify_ai_tool_type(self, text):
        """Classify the type of AI tool based on content"""
        text_lower = text.lower()
        
        # Score each category based on keyword matches
        scores = {}
        for category, keywords in self.ai_tool_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                scores[category] = score
        
        if scores:
            # Return the category with the highest score
            return max(scores, key=scores.get)
        else:
            return 'General AI'

    def run_daily_scrape(self):
        """Main function to run the daily scraping job"""
        print("🤖 Starting AI News Scraper Bot...")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        
        try:
            # Search for articles
            articles = self.search_google_for_ai_news(max_results=10)
            
            if not articles:
                print("❌ No articles found")
                return
            
            print(f"\n📰 Found {len(articles)} articles to process")
            
            # Store articles in database
            new_articles_count = 0
            for article in articles:
                result = self.db.add_article(article)
                if result:
                    new_articles_count += 1
                    
            print(f"✅ Successfully added {new_articles_count} new articles to database")
            print(f"📊 Total articles in database: {self.db.get_article_count()}")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            raise

# Test function
if __name__ == "__main__":
    # Test the scraper
    try:
        print("🚀 Starting AI News Scraper...")
        
        # Check if we're in GitHub Actions
        if os.getenv('GITHUB_ACTIONS'):
            print("🔧 Running in GitHub Actions environment")
            
        # Check if DATABASE_URL is available
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL environment variable not found")
            print("💡 Make sure to set DATABASE_URL in:")
            print("   - GitHub Actions secrets (for CI/CD)")
            print("   - Your local .env file (for local testing)")
            print("   - Environment variables (for production)")
            sys.exit(1)
        
        print("✅ Database URL found, starting scraper...")
        scraper = AINewsScaper()
        scraper.run_daily_scrape()
        print("✅ Scraper completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Scraper failed: {e}")
        import traceback
        print(f"📋 Full error: {traceback.format_exc()}")
        sys.exit(1) 