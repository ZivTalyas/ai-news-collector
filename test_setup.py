#!/usr/bin/env python3
"""
Test Setup Script for AI News Collector
Verifies that all components are working correctly
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing Python imports...")
    
    try:
        import requests
        import beautifulsoup4
        import pymongo
        import streamlit
        import googlesearch
        import pandas
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        print("❌ MONGO_URI not found in environment variables")
        print("💡 Copy env_template.txt to .env and add your MongoDB connection string")
        return False
    
    if "mongodb+srv://" not in mongo_uri:
        print("⚠️  MONGO_URI doesn't look like a MongoDB Atlas connection string")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_database_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from database import NewsDatabase
        db = NewsDatabase()
        count = db.get_article_count()
        print(f"✅ Database connection successful - {count} articles in database")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Check your MONGO_URI and network connection")
        return False

def test_scraper_basic():
    """Test basic scraper functionality (without actually scraping)"""
    print("\n🔍 Testing scraper components...")
    
    try:
        from scraper import AINewsScaper
        scraper = AINewsScaper()
        
        # Test AI tool classification
        test_text = "OpenAI releases new ChatGPT model with improved language understanding"
        tool_type = scraper.classify_ai_tool_type(test_text)
        
        if tool_type:
            print(f"✅ AI classification working - detected: {tool_type}")
            return True
        else:
            print("❌ AI classification failed")
            return False
            
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🤖 AI News Collector - Setup Test\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment),
        ("Database Connection", test_database_connection),
        ("Scraper Components", test_scraper_basic)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Next steps:")
        print("   1. Run the scraper: python scraper.py")
        print("   2. Start the dashboard: streamlit run dashboard.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    run_all_tests() 