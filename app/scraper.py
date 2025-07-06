#!/usr/bin/env python3
"""
AI News Collector Scraper Bot
Searches Google for AI news articles and stores them in MongoDB
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

# Load environment variables from config folder
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class AINewsScaper:
    def __init__(self):
        self.db = NewsDatabase()
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
            "AI breakthrough 2024",
            "machine learning news",
            "ChatGPT OpenAI news",
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

    def extract_article_info(self, url):
        """Extract title and classify AI tool type from an article URL"""
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
                if self.db.add_article(article):
                    new_articles_count += 1
                    
            print(f"✅ Successfully added {new_articles_count} new articles to database")
            print(f"📊 Total articles in database: {self.db.get_article_count()}")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            raise

if __name__ == "__main__":
    scraper = AINewsScaper()
    scraper.run_daily_scrape() 