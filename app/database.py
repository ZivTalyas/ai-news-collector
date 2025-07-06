#!/usr/bin/env python3
"""
MongoDB Database Integration for AI News Collector
Handles storing and retrieving articles with deduplication
"""

import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config folder
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class NewsDatabase:
    def __init__(self, mongo_uri_override=None):
        """Initialize MongoDB connection with modern TLS options"""
        # Use override URI if provided (for Streamlit Cloud)
        if mongo_uri_override:
            self.mongo_uri = mongo_uri_override
        else:
            self.mongo_uri = os.getenv('MONGO_URI')
        
        if not self.mongo_uri:
            raise ValueError("MONGO_URI environment variable is required")
        
        try:
            # Modern MongoDB connection with TLS settings for Streamlit Cloud
            connection_options = {
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'serverSelectionTimeoutMS': 30000,
                'socketTimeoutMS': 60000,
                'connectTimeoutMS': 30000,
                'maxPoolSize': 1,
                'retryWrites': True,
                'w': 'majority'
            }
            
            print("🔐 Connecting to MongoDB Atlas with modern TLS options...")
            self.client = MongoClient(self.mongo_uri, **connection_options)
            self.db = self.client['ai_news']
            self.collection = self.db['articles']
            
            # Test the connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas successfully")
            
            # Create indexes for better performance and deduplication
            try:
                self.collection.create_index("url", unique=True)
                self.collection.create_index("scraped_at")
                self.collection.create_index("type_of_ai_tool")
                print("✅ Database indexes created successfully")
            except Exception as index_error:
                print(f"⚠️ Could not create indexes: {index_error}")
                
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise Exception(f"Failed to connect to MongoDB Atlas from Streamlit Cloud.\n\nThis is likely due to SSL/TLS compatibility issues between Streamlit Cloud's \nPython environment and your MongoDB Atlas cluster.\n\nOriginal error: {str(e)}\n\nSolutions:\n1. Update your MongoDB Atlas cluster to the latest version\n2. Ensure your cluster uses TLS 1.2+\n3. Try a different MongoDB hosting provider\n4. Contact Streamlit Cloud support if the issue persists")

    def add_article(self, article):
        """Add a new article to the database with deduplication"""
        try:
            # Ensure scraped_at is a datetime object
            if isinstance(article.get('scraped_at'), str):
                article['scraped_at'] = datetime.fromisoformat(article['scraped_at'].replace('Z', '+00:00'))
            elif not isinstance(article.get('scraped_at'), datetime):
                article['scraped_at'] = datetime.now(timezone.utc)
            
            # Add to database
            result = self.collection.insert_one(article)
            print(f"✅ Added article: {article['title'][:50]}...")
            return result.inserted_id
            
        except DuplicateKeyError:
            print(f"⚠️ Article already exists: {article['title'][:50]}...")
            return None
        except Exception as e:
            print(f"❌ Error adding article: {e}")
            raise
    
    def get_articles(self, limit=None, ai_tool_type=None, sort_by_date=True):
        """Retrieve articles from the database"""
        try:
            # Build query
            query = {}
            if ai_tool_type:
                query['type_of_ai_tool'] = ai_tool_type
            
            # Build cursor
            cursor = self.collection.find(query)
            
            # Sort by date if requested
            if sort_by_date:
                cursor = cursor.sort('scraped_at', -1)
            
            # Apply limit
            if limit:
                cursor = cursor.limit(limit)
            
            # Convert to list
            articles = list(cursor)
            
            # Convert datetime objects to ISO strings for JSON serialization
            for article in articles:
                if isinstance(article.get('scraped_at'), datetime):
                    article['scraped_at'] = article['scraped_at'].isoformat()
            
            return articles
            
        except Exception as e:
            print(f"❌ Error retrieving articles: {e}")
            raise
    
    def get_article_count(self, ai_tool_type=None):
        """Get total number of articles"""
        try:
            query = {}
            if ai_tool_type:
                query['type_of_ai_tool'] = ai_tool_type
            
            return self.collection.count_documents(query)
            
        except Exception as e:
            print(f"❌ Error getting article count: {e}")
            return 0
    
    def get_latest_scrape_time(self):
        """Get the timestamp of the most recent scrape"""
        try:
            latest_article = self.collection.find_one(
                {},
                sort=[('scraped_at', -1)]
            )
            
            if latest_article:
                scraped_at = latest_article['scraped_at']
                if isinstance(scraped_at, datetime):
                    return scraped_at.isoformat()
                return scraped_at
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting latest scrape time: {e}")
            return None
    
    def get_ai_tool_types(self):
        """Get all unique AI tool types"""
        try:
            return self.collection.distinct('type_of_ai_tool')
        except Exception as e:
            print(f"❌ Error getting AI tool types: {e}")
            return []
    
    def delete_old_articles(self, days_to_keep=30):
        """Delete articles older than specified days"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            result = self.collection.delete_many({
                'scraped_at': {'$lt': cutoff_date}
            })
            
            print(f"🗑️ Deleted {result.deleted_count} old articles")
            return result.deleted_count
            
        except Exception as e:
            print(f"❌ Error deleting old articles: {e}")
            return 0
    
    def get_articles_by_date_range(self, start_date, end_date):
        """Get articles within a specific date range"""
        try:
            query = {
                'scraped_at': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            articles = list(self.collection.find(query).sort('scraped_at', -1))
            
            # Convert datetime objects to ISO strings
            for article in articles:
                if isinstance(article.get('scraped_at'), datetime):
                    article['scraped_at'] = article['scraped_at'].isoformat()
            
            return articles
            
        except Exception as e:
            print(f"❌ Error getting articles by date range: {e}")
            return []
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            print("🔌 MongoDB connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

# Test function
if __name__ == "__main__":
    # Test the database connection
    try:
        db = NewsDatabase()
        print(f"📊 Total articles in database: {db.get_article_count()}")
        print(f"🏷️  AI tool types: {db.get_ai_tool_types()}")
        
        latest_scrape = db.get_latest_scrape_time()
        if latest_scrape:
            print(f"🕒 Latest scrape: {latest_scrape}")
        else:
            print("🕒 No articles in database yet")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}") 