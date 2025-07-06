#!/usr/bin/env python3
"""
MongoDB Database Integration for AI News Collector
Handles storing and retrieving articles with deduplication
"""

import os
import sys
import ssl
import urllib3
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pathlib import Path
from dotenv import load_dotenv

# Disable SSL warnings for Streamlit Cloud compatibility
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create SSL context for Streamlit Cloud compatibility
def create_ssl_context():
    """Create SSL context that works with Streamlit Cloud"""
    try:
        # Create SSL context with more permissive settings
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Additional settings for compatibility
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        
        return context
    except Exception as e:
        print(f"⚠️ Could not create custom SSL context: {e}")
        return None

# Load environment variables from config folder
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class NewsDatabase:
    def __init__(self, mongo_uri_override=None):
        """Initialize MongoDB connection"""
        # Use override URI if provided (for Streamlit Cloud)
        if mongo_uri_override:
            self.mongo_uri = mongo_uri_override
        else:
            self.mongo_uri = os.getenv('MONGO_URI')
        
        if not self.mongo_uri:
            raise ValueError("MONGO_URI environment variable is required")
        
        # Detect if running in Streamlit Cloud
        is_streamlit_cloud = os.getenv('STREAMLIT_SHARING_MODE') is not None or 'streamlit' in str(os.getenv('HOME', ''))
        
        try:
            # Streamlit Cloud optimized connection
            if is_streamlit_cloud:
                print("🔐 Attempting MongoDB connection optimized for Streamlit Cloud...")
                
                # Try with custom SSL context first
                ssl_context = create_ssl_context()
                if ssl_context:
                    try:
                        streamlit_options = {
                            'ssl': True,
                            'ssl_context': ssl_context,
                            'serverSelectionTimeoutMS': 30000,
                            'socketTimeoutMS': 60000,
                            'connectTimeoutMS': 30000,
                            'maxPoolSize': 1,
                            'retryWrites': True,
                            'w': 'majority'
                        }
                        
                        self.client = MongoClient(self.mongo_uri, **streamlit_options)
                        self.db = self.client['ai_news']
                        self.collection = self.db['articles']
                        
                        # Test the connection
                        self.client.admin.command('ping')
                        print("✅ Connected to MongoDB Atlas (Streamlit Cloud with custom SSL)")
                        
                    except Exception as ssl_error:
                        print(f"⚠️ Custom SSL context failed: {ssl_error}")
                        # Fall back to TLS options
                        streamlit_options = {
                            'tls': True,
                            'tlsAllowInvalidCertificates': True,
                            'tlsAllowInvalidHostnames': True,
                            'tlsInsecure': True,
                            'serverSelectionTimeoutMS': 30000,
                            'socketTimeoutMS': 60000,
                            'connectTimeoutMS': 30000,
                            'maxPoolSize': 1,
                            'retryWrites': True,
                            'w': 'majority'
                        }
                        
                        self.client = MongoClient(self.mongo_uri, **streamlit_options)
                        self.db = self.client['ai_news']
                        self.collection = self.db['articles']
                        
                        # Test the connection
                        self.client.admin.command('ping')
                        print("✅ Connected to MongoDB Atlas (Streamlit Cloud TLS fallback)")
                
                else:
                    # No custom SSL context, use TLS options directly
                    streamlit_options = {
                        'tls': True,
                        'tlsAllowInvalidCertificates': True,
                        'tlsAllowInvalidHostnames': True,
                        'tlsInsecure': True,
                        'serverSelectionTimeoutMS': 30000,
                        'socketTimeoutMS': 60000,
                        'connectTimeoutMS': 30000,
                        'maxPoolSize': 1,
                        'retryWrites': True,
                        'w': 'majority'
                    }
                    
                    self.client = MongoClient(self.mongo_uri, **streamlit_options)
                    self.db = self.client['ai_news']
                    self.collection = self.db['articles']
                    
                    # Test the connection
                    self.client.admin.command('ping')
                    print("✅ Connected to MongoDB Atlas (Streamlit Cloud optimized)")
                
            else:
                # Local development connection
                print("🔐 Attempting MongoDB connection with SSL configuration...")
                ssl_options = {
                    'ssl': True,
                    'ssl_cert_reqs': ssl.CERT_NONE,
                    'ssl_match_hostname': False,
                    'serverSelectionTimeoutMS': 5000,
                    'socketTimeoutMS': 10000,
                    'connectTimeoutMS': 10000,
                    'maxPoolSize': 10,
                    'retryWrites': True
                }
                
                self.client = MongoClient(self.mongo_uri, **ssl_options)
                self.db = self.client['ai_news']
                self.collection = self.db['articles']
                
                # Test the connection
                self.client.admin.command('ping')
                print("✅ Connected to MongoDB Atlas")
            
            # Create indexes for better performance and deduplication
            try:
                self.collection.create_index("url", unique=True)
                self.collection.create_index("scraped_at")
                self.collection.create_index("type_of_ai_tool")
            except Exception as index_error:
                print(f"⚠️ Could not create indexes: {index_error}")
                
        except Exception as e:
            print(f"⚠️ Primary connection attempt failed: {e}")
            print("🔄 Trying fallback connection methods...")
            
            # Fallback methods for different environments
            fallback_methods = [
                {
                    'name': 'Streamlit Cloud Fallback 1',
                    'options': {
                        'ssl': False,
                        'tls': True,
                        'tlsAllowInvalidCertificates': True,
                        'tlsAllowInvalidHostnames': True,
                        'serverSelectionTimeoutMS': 45000,
                        'socketTimeoutMS': 90000,
                        'connectTimeoutMS': 45000,
                        'maxPoolSize': 1,
                        'retryWrites': True
                    }
                },
                {
                    'name': 'Streamlit Cloud Fallback 2',
                    'options': {
                        'tls': True,
                        'tlsAllowInvalidCertificates': True,
                        'tlsAllowInvalidHostnames': True,
                        'tlsInsecure': True,
                        'ssl_cert_reqs': ssl.CERT_NONE,
                        'ssl_match_hostname': False,
                        'serverSelectionTimeoutMS': 60000,
                        'socketTimeoutMS': 120000,
                        'connectTimeoutMS': 60000,
                        'maxPoolSize': 1,
                        'retryWrites': True
                    }
                },
                {
                    'name': 'Minimal Connection',
                    'options': {
                        'serverSelectionTimeoutMS': 60000,
                        'socketTimeoutMS': 120000,
                        'connectTimeoutMS': 60000,
                        'maxPoolSize': 1,
                        'retryWrites': True
                    }
                },
                {
                    'name': 'Legacy SSL',
                    'options': {
                        'ssl': True,
                        'ssl_cert_reqs': ssl.CERT_NONE,
                        'ssl_match_hostname': False,
                        'ssl_ca_certs': None,
                        'serverSelectionTimeoutMS': 60000,
                        'socketTimeoutMS': 120000,
                        'connectTimeoutMS': 60000,
                        'maxPoolSize': 1,
                        'retryWrites': True
                    }
                }
            ]
            
            connection_successful = False
            for method in fallback_methods:
                try:
                    print(f"🔐 Attempting {method['name']}...")
                    self.client = MongoClient(self.mongo_uri, **method['options'])
                    self.db = self.client['ai_news']
                    self.collection = self.db['articles']
                    
                    # Test the connection
                    self.client.admin.command('ping')
                    print(f"✅ Connected to MongoDB Atlas ({method['name']})")
                    connection_successful = True
                    break
                    
                except Exception as fallback_error:
                    print(f"   ❌ {method['name']} failed: {fallback_error}")
                    continue
            
            if not connection_successful:
                print(f"❌ All connection attempts failed")
                print("\n💡 Streamlit Cloud SSL Troubleshooting:")
                print("   1. This error is common in Streamlit Cloud due to SSL/TLS differences")
                print("   2. Try updating your MongoDB Atlas cluster to the latest version")
                print("   3. Check if your cluster is using TLS 1.2+ (required)")
                print("   4. Verify your connection string format")
                print("   5. Consider using a different MongoDB hosting provider if issues persist")
                
                # Create a more informative error for Streamlit Cloud
                error_message = f"""
                Failed to connect to MongoDB Atlas from Streamlit Cloud.
                
                This is likely due to SSL/TLS compatibility issues between Streamlit Cloud's 
                Python environment and your MongoDB Atlas cluster.
                
                Original error: {str(e)}
                
                Solutions:
                1. Update your MongoDB Atlas cluster to the latest version
                2. Ensure your cluster uses TLS 1.2+
                3. Try a different MongoDB hosting provider
                4. Contact Streamlit Cloud support if the issue persists
                """
                
                raise ConnectionError(error_message)

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