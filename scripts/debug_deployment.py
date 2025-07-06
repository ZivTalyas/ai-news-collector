#!/usr/bin/env python3
"""
Deployment Debug Script
Helps diagnose issues with the deployed Streamlit app
"""

import os
import sys
import ssl
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def check_environment():
    """Check environment variables and Streamlit secrets"""
    print("🔍 Checking Environment Variables...")
    
    # Check if running in Streamlit Cloud
    try:
        import streamlit as st
        print("✅ Streamlit available - likely running in Streamlit Cloud")
        
        # Check for secrets
        try:
            if hasattr(st, 'secrets') and 'MONGO_URI' in st.secrets:
                mongo_uri = st.secrets['MONGO_URI']
                print("✅ Found MONGO_URI in Streamlit secrets")
                return mongo_uri
            else:
                print("❌ MONGO_URI not found in Streamlit secrets")
        except Exception as e:
            print(f"❌ Error accessing Streamlit secrets: {e}")
    except ImportError:
        print("⚠️  Streamlit not available - likely running locally")
    
    # Check environment variables
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        print("✅ Found MONGO_URI in environment variables")
        return mongo_uri
    else:
        print("❌ MONGO_URI not found in environment variables")
    
    return None

def test_mongodb_connection(mongo_uri):
    """Test MongoDB connection with various methods"""
    print("\n🔍 Testing MongoDB Connection...")
    
    if not mongo_uri:
        print("❌ No MongoDB URI provided")
        return False
    
    print(f"✅ Connection string: {mongo_uri[:50]}...")
    
    # Test different connection methods
    methods = [
        {
            'name': 'Default Connection',
            'options': {}
        },
        {
            'name': 'SSL Configuration',
            'options': {
                'ssl': True,
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_match_hostname': False,
                'serverSelectionTimeoutMS': 5000,
                'socketTimeoutMS': 10000,
                'connectTimeoutMS': 10000,
            }
        },
        {
            'name': 'TLS Configuration',
            'options': {
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'serverSelectionTimeoutMS': 10000,
                'socketTimeoutMS': 20000,
                'connectTimeoutMS': 20000,
            }
        }
    ]
    
    for method in methods:
        try:
            print(f"\n🔐 Testing {method['name']}...")
            client = MongoClient(mongo_uri, **method['options'])
            
            # Test ping
            client.admin.command('ping')
            print(f"   ✅ Connection successful")
            
            # Test database access
            db = client['ai_news']
            collection = db['articles']
            
            # Count documents
            count = collection.count_documents({})
            print(f"   ✅ Found {count} articles in database")
            
            # Get sample documents
            if count > 0:
                sample = collection.find().limit(1)
                sample_doc = list(sample)[0]
                print(f"   ✅ Sample article: {sample_doc.get('title', 'No title')[:50]}...")
                print(f"   ✅ Sample date: {sample_doc.get('scraped_at', 'No date')}")
                
                # Get today's articles
                today = datetime.now(timezone.utc).date()
                today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
                today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
                
                today_count = collection.count_documents({
                    'scraped_at': {
                        '$gte': today_start.isoformat(),
                        '$lte': today_end.isoformat()
                    }
                })
                print(f"   ✅ Today's articles: {today_count}")
                
                # Get AI tool types
                ai_types = collection.distinct('type_of_ai_tool')
                print(f"   ✅ AI tool types: {ai_types}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    print("\n❌ All connection methods failed")
    return False

def check_data_format():
    """Check if data format matches expected format"""
    print("\n🔍 Checking Data Format...")
    
    # This would be called after successful connection
    # Implementation depends on successful connection test
    pass

def main():
    """Main debug function"""
    print("🔧 AI News Collector - Deployment Debug Tool")
    print("=" * 60)
    
    # Step 1: Check environment
    mongo_uri = check_environment()
    
    if not mongo_uri:
        print("\n❌ MongoDB URI not found!")
        print("\n💡 Solutions:")
        print("   1. For Streamlit Cloud: Add MONGO_URI to app secrets")
        print("   2. For local: Add MONGO_URI to config/.env")
        print("   3. Get connection string from MongoDB Atlas")
        return False
    
    # Step 2: Test MongoDB connection
    if not test_mongodb_connection(mongo_uri):
        print("\n❌ MongoDB connection failed!")
        print("\n💡 Solutions:")
        print("   1. Check MongoDB Atlas IP whitelist (0.0.0.0/0)")
        print("   2. Verify database user permissions")
        print("   3. Check connection string format")
        print("   4. Update pymongo: pip install --upgrade pymongo")
        return False
    
    print("\n✅ All checks passed!")
    print("\n🎉 Your deployment should be working now!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 