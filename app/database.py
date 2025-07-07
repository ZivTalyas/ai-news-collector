#!/usr/bin/env python3
"""
PostgreSQL Database Integration for AI News Collector
Handles storing and retrieving articles with deduplication
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config folder
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class NewsDatabase:
    def __init__(self, database_url_override=None):
        """Initialize PostgreSQL connection"""
        # Use override URL if provided (for Streamlit Cloud)
        if database_url_override:
            self.database_url = database_url_override
        else:
            self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Debug: Check DATABASE_URL format (mask sensitive parts)
        if os.getenv('GITHUB_ACTIONS'):
            # In GitHub Actions, show first/last parts for debugging
            url_len = len(self.database_url)
            if url_len > 20:
                debug_url = self.database_url[:15] + "***" + self.database_url[-10:]
                print(f"🔍 DATABASE_URL format: {debug_url}")
                print(f"🔍 URL length: {url_len}")
                print(f"🔍 Starts with postgresql://: {self.database_url.startswith('postgresql://')}")
                print(f"🔍 Contains sslmode=require: {'sslmode=require' in self.database_url}")
            else:
                print(f"🔍 DATABASE_URL too short: {url_len} chars")
        
        # Clean up the URL (remove extra quotes if present)
        self.database_url = self.database_url.strip().strip("'\"")
        
        # Ensure proper format
        if not self.database_url.startswith('postgresql://'):
            print(f"⚠️ DATABASE_URL doesn't start with postgresql://")
            print(f"⚠️ Current start: {self.database_url[:20]}...")
            if self.database_url.startswith('postgres://'):
                print("🔧 Converting postgres:// to postgresql://")
                self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        try:
            print("🔐 Connecting to PostgreSQL database...")
            self.conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                sslmode='require'
            )
            self.conn.autocommit = False
            print("✅ Connected to PostgreSQL successfully")
            
            # Create tables and indexes
            self._create_tables()
            print("✅ Database tables and indexes ready")
            
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            raise Exception(f"Failed to connect to PostgreSQL database.\n\nOriginal error: {str(e)}\n\nSolutions:\n1. Check your DATABASE_URL environment variable\n2. Ensure your PostgreSQL database is running and accessible\n3. Verify database credentials and permissions\n4. Check network connectivity to your database server")
    
    def _create_tables(self):
        """Create necessary tables and indexes"""
        try:
            cursor = self.conn.cursor()
            
            # Create articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    type_of_ai_tool TEXT NOT NULL,
                    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON articles(scraped_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_type_of_ai_tool ON articles(type_of_ai_tool)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)')
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            print(f"⚠️ Could not create tables: {e}")
            raise
    
    def add_article(self, article):
        """Add a new article to the database with deduplication"""
        try:
            cursor = self.conn.cursor()
            
            # Ensure scraped_at is a datetime object
            if isinstance(article.get('scraped_at'), str):
                try:
                    scraped_at = datetime.fromisoformat(article['scraped_at'].replace('Z', '+00:00'))
                except ValueError:
                    scraped_at = datetime.now(timezone.utc)
            elif isinstance(article.get('scraped_at'), datetime):
                scraped_at = article['scraped_at']
            else:
                scraped_at = datetime.now(timezone.utc)
            
            # Insert the article
            cursor.execute('''
                INSERT INTO articles (title, url, type_of_ai_tool, scraped_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (
                article['title'],
                article['url'],
                article['type_of_ai_tool'],
                scraped_at
            ))
            
            result = cursor.fetchone()
            self.conn.commit()
            
            print(f"✅ Added article: {article['title'][:50]}...")
            return result['id']
            
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print(f"⚠️ Article already exists: {article['title'][:50]}...")
            return None
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error adding article: {e}")
            raise
    
    def get_articles(self, limit=None, ai_tool_type=None, sort_by_date=True):
        """Retrieve articles from the database"""
        try:
            cursor = self.conn.cursor()
            
            # Build query
            query = "SELECT * FROM articles"
            params = []
            
            if ai_tool_type:
                query += " WHERE type_of_ai_tool = %s"
                params.append(ai_tool_type)
            
            # Sort by date if requested
            if sort_by_date:
                query += " ORDER BY scraped_at DESC"
            
            # Apply limit
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            cursor.execute(query, params)
            articles = cursor.fetchall()
            
            # Convert to list of dictionaries and format datetime
            result = []
            for article in articles:
                article_dict = dict(article)
                # Convert datetime to ISO string for JSON serialization
                if isinstance(article_dict.get('scraped_at'), datetime):
                    article_dict['scraped_at'] = article_dict['scraped_at'].isoformat()
                result.append(article_dict)
            
            return result
            
        except Exception as e:
            print(f"❌ Error retrieving articles: {e}")
            raise
    
    def get_article_count(self, ai_tool_type=None):
        """Get total number of articles"""
        try:
            cursor = self.conn.cursor()
            
            if ai_tool_type:
                cursor.execute('SELECT COUNT(*) FROM articles WHERE type_of_ai_tool = %s', (ai_tool_type,))
            else:
                cursor.execute('SELECT COUNT(*) FROM articles')
            
            result = cursor.fetchone()
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"❌ Error getting article count: {e}")
            return 0
    
    def get_latest_scrape_time(self):
        """Get the timestamp of the most recent scrape"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT scraped_at FROM articles ORDER BY scraped_at DESC LIMIT 1')
            result = cursor.fetchone()
            
            if result:
                scraped_at = result['scraped_at']
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
            cursor = self.conn.cursor()
            cursor.execute('SELECT DISTINCT type_of_ai_tool FROM articles ORDER BY type_of_ai_tool')
            results = cursor.fetchall()
            return [row['type_of_ai_tool'] for row in results]
            
        except Exception as e:
            print(f"❌ Error getting AI tool types: {e}")
            return []
    
    def delete_old_articles(self, days_to_keep=30):
        """Delete articles older than specified days"""
        try:
            cursor = self.conn.cursor()
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            cursor.execute('DELETE FROM articles WHERE scraped_at < %s', (cutoff_date,))
            deleted_count = cursor.rowcount
            self.conn.commit()
            
            print(f"🗑️ Deleted {deleted_count} old articles")
            return deleted_count
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error deleting old articles: {e}")
            return 0
    
    def get_articles_by_date_range(self, start_date, end_date):
        """Get articles within a specific date range"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM articles 
                WHERE scraped_at >= %s AND scraped_at <= %s
                ORDER BY scraped_at DESC
            ''', (start_date, end_date))
            
            articles = cursor.fetchall()
            
            # Convert to list of dictionaries and format datetime
            result = []
            for article in articles:
                article_dict = dict(article)
                # Convert datetime to ISO string for JSON serialization
                if isinstance(article_dict.get('scraped_at'), datetime):
                    article_dict['scraped_at'] = article_dict['scraped_at'].isoformat()
                result.append(article_dict)
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting articles by date range: {e}")
            return []
    
    def close_connection(self):
        """Close the PostgreSQL connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            print("🔌 PostgreSQL connection closed")
    
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