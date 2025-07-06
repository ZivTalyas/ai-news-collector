#!/usr/bin/env python3
"""
MongoDB Database Integration for AI News Collector
Handles storing and retrieving articles with deduplication
"""

import os
import sys
import ssl
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config folder
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class NewsDatabase:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_uri = os.getenv('MONGO_URI')
        if not self.mongo_uri:
            raise ValueError("MONGO_URI environment variable is required")
        
        try:
            # First attempt: MongoDB Atlas SSL/TLS configuration
            ssl_options = {
                'ssl': True,
                'ssl_cert_reqs': ssl.CERT_NONE,  # Skip SSL certificate verification
                'ssl_match_hostname': False,     # Don't verify hostname
                'serverSelectionTimeoutMS': 5000,
                'socketTimeoutMS': 10000,
                'connectTimeoutMS': 10000,
                'maxPoolSize': 10,
                'retryWrites': True
            }
            
            print("🔐 Attempting MongoDB connection with SSL configuration...")
            self.client = MongoClient(self.mongo_uri, **ssl_options)
            self.db = self.client['ai_news']
            self.collection = self.db['articles']
            
            # Create indexes for better performance and deduplication
            self.collection.create_index("url", unique=True)  # Prevent duplicate URLs
            self.collection.create_index("scraped_at")
            self.collection.create_index("type_of_ai_tool")
            
            # Test the connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas")
            
        except Exception as e:
            print(f"⚠️  First connection attempt failed: {e}")
            print("🔄 Trying alternative connection methods...")
            
            # Fallback 1: Try with different SSL options
            try:
                print("🔐 Attempting with alternative SSL configuration...")
                fallback_options = {
                    'tls': True,
                    'tlsAllowInvalidCertificates': True,
                    'tlsAllowInvalidHostnames': True,
                    'serverSelectionTimeoutMS': 10000,
                    'socketTimeoutMS': 20000,
                    'connectTimeoutMS': 20000,
                    'retryWrites': True
                }
                
                self.client = MongoClient(self.mongo_uri, **fallback_options)
                self.db = self.client['ai_news']
                self.collection = self.db['articles']
                
            except Exception as e2:
                print(f"⚠️  Second connection attempt failed: {e2}")
                
                # Fallback 2: Try with minimal options
                try:
                    print("🔐 Attempting with minimal SSL configuration...")
                    minimal_options = {
                        'serverSelectionTimeoutMS': 15000,
                        'socketTimeoutMS': 30000,
                        'connectTimeoutMS': 30000,
                    }
                    
                    self.client = MongoClient(self.mongo_uri, **minimal_options)
                    self.db = self.client['ai_news']
                    self.collection = self.db['articles']
                    
                except Exception as e3:
                    print(f"❌ All connection attempts failed:")
                    print(f"   1. SSL config: {e}")
                    print(f"   2. TLS config: {e2}")
                    print(f"   3. Minimal config: {e3}")
                    print("\n💡 Troubleshooting suggestions:")
                    print("   1. Check your MongoDB Atlas connection string")
                    print("   2. Verify your IP address is whitelisted (0.0.0.0/0)")
                    print("   3. Update your MongoDB Atlas cluster to latest version")
                    print("   4. Try updating pymongo: pip install --upgrade pymongo")
                    raise ConnectionError(f"Failed to connect to MongoDB after multiple attempts. Last error: {e3}")

    def add_article(self, article):
        """
        Add a new article to the database with deduplication
        Returns True if article was added, False if it already exists
        """
        try:
            # Add timestamp if not present
            if 'scraped_at' not in article:
                article['scraped_at'] = datetime.now(timezone.utc).isoformat()
            
            # Insert the article
            result = self.collection.insert_one(article)
            print(f"✅ Added article: {article['title'][:50]}...")
            return True
            
        except DuplicateKeyError:
            print(f"⚠️  Article already exists: {article['title'][:50]}...")
            return False
            
        except PyMongoError as e:
            print(f"❌ Database error adding article: {e}")
            return False
        
        except Exception as e:
            print(f"❌ Unexpected error adding article: {e}")
            return False

    def get_articles(self, limit=None, ai_tool_type=None, sort_by_date=True):
        """
        Retrieve articles from the database
        
        Args:
            limit: Maximum number of articles to return
            ai_tool_type: Filter by AI tool type
            sort_by_date: Sort by scraped_at date (newest first)
        """
        try:
            # Build query filter
            query_filter = {}
            if ai_tool_type and ai_tool_type != "All":
                query_filter['type_of_ai_tool'] = ai_tool_type
            
            # Build query
            cursor = self.collection.find(query_filter)
            
            # Sort by date if requested
            if sort_by_date:
                cursor = cursor.sort("scraped_at", -1)  # -1 for descending (newest first)
            
            # Apply limit
            if limit:
                cursor = cursor.limit(limit)
            
            return list(cursor)
            
        except PyMongoError as e:
            print(f"❌ Database error retrieving articles: {e}")
            return []
        
        except Exception as e:
            print(f"❌ Unexpected error retrieving articles: {e}")
            return []

    def get_article_count(self, ai_tool_type=None):
        """Get total count of articles"""
        try:
            query_filter = {}
            if ai_tool_type and ai_tool_type != "All":
                query_filter['type_of_ai_tool'] = ai_tool_type
                
            return self.collection.count_documents(query_filter)
            
        except PyMongoError as e:
            print(f"❌ Database error counting articles: {e}")
            return 0

    def get_latest_scrape_time(self):
        """Get the timestamp of the most recent scrape"""
        try:
            latest_article = self.collection.find().sort("scraped_at", -1).limit(1)
            latest_article = list(latest_article)
            
            if latest_article:
                return latest_article[0]['scraped_at']
            else:
                return None
                
        except PyMongoError as e:
            print(f"❌ Database error getting latest scrape time: {e}")
            return None

    def get_ai_tool_types(self):
        """Get all unique AI tool types in the database"""
        try:
            return self.collection.distinct("type_of_ai_tool")
            
        except PyMongoError as e:
            print(f"❌ Database error getting AI tool types: {e}")
            return []

    def delete_old_articles(self, days_to_keep=30):
        """Delete articles older than specified days"""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            cutoff_date_str = cutoff_date.isoformat()
            
            result = self.collection.delete_many({
                "scraped_at": {"$lt": cutoff_date_str}
            })
            
            print(f"🗑️  Deleted {result.deleted_count} old articles")
            return result.deleted_count
            
        except PyMongoError as e:
            print(f"❌ Database error deleting old articles: {e}")
            return 0

    def get_articles_by_date_range(self, start_date, end_date):
        """Get articles within a specific date range"""
        try:
            query_filter = {
                "scraped_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
            
            cursor = self.collection.find(query_filter).sort("scraped_at", -1)
            return list(cursor)
            
        except PyMongoError as e:
            print(f"❌ Database error getting articles by date range: {e}")
            return []

    def close_connection(self):
        """Close the database connection"""
        try:
            self.client.close()
            print("✅ Database connection closed")
        except Exception as e:
            print(f"❌ Error closing database connection: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
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