#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Helps diagnose and fix SSL/TLS connection issues
"""

import os
import sys
import ssl
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add parent directory to path to import from app
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

def test_python_ssl():
    """Test Python SSL configuration"""
    print("🔍 Testing Python SSL Configuration...")
    try:
        print(f"   ✅ Python SSL version: {ssl.OPENSSL_VERSION}")
        print(f"   ✅ SSL module available: {ssl.HAS_SNI}")
        print(f"   ✅ TLS v1.2 support: {ssl.HAS_TLSv1_2}")
        print(f"   ✅ TLS v1.3 support: {ssl.HAS_TLSv1_3}")
        return True
    except Exception as e:
        print(f"   ❌ SSL configuration issue: {e}")
        return False

def test_connection_method(mongo_uri, method_name, options):
    """Test a specific connection method"""
    print(f"\n🔐 Testing {method_name}...")
    try:
        client = MongoClient(mongo_uri, **options)
        # Test the connection
        client.admin.command('ping')
        print(f"   ✅ {method_name} - SUCCESS!")
        
        # Test database access
        db = client['ai_news']
        collection = db['articles']
        count = collection.count_documents({})
        print(f"   ✅ Found {count} articles in database")
        
        client.close()
        return True, None
        
    except Exception as e:
        print(f"   ❌ {method_name} - FAILED: {e}")
        return False, str(e)

def main():
    """Main function to test MongoDB connection"""
    print("🚀 MongoDB Connection Diagnostic Tool")
    print("=" * 50)
    
    # Check environment variables
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("❌ MONGO_URI environment variable not found!")
        print("💡 Make sure you have a .env file in the config/ directory")
        return False
    
    print(f"✅ Found MongoDB URI: {mongo_uri[:50]}...")
    
    # Test Python SSL
    if not test_python_ssl():
        print("\n❌ Python SSL configuration has issues")
        return False
    
    # Test different connection methods
    test_methods = [
        {
            'name': 'Default Connection',
            'options': {}
        },
        {
            'name': 'SSL with Certificate Verification Disabled',
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
            'name': 'TLS with Invalid Certificates Allowed',
            'options': {
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'serverSelectionTimeoutMS': 10000,
                'socketTimeoutMS': 20000,
                'connectTimeoutMS': 20000,
            }
        },
        {
            'name': 'Minimal Configuration',
            'options': {
                'serverSelectionTimeoutMS': 15000,
                'socketTimeoutMS': 30000,
                'connectTimeoutMS': 30000,
            }
        },
        {
            'name': 'Legacy SSL (TLS 1.0/1.1)',
            'options': {
                'ssl': True,
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_match_hostname': False,
                'ssl_ca_certs': None,
                'serverSelectionTimeoutMS': 15000,
                'socketTimeoutMS': 30000,
                'connectTimeoutMS': 30000,
            }
        }
    ]
    
    successful_methods = []
    failed_methods = []
    
    for method in test_methods:
        success, error = test_connection_method(
            mongo_uri, 
            method['name'], 
            method['options']
        )
        
        if success:
            successful_methods.append(method['name'])
        else:
            failed_methods.append((method['name'], error))
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 CONNECTION TEST RESULTS")
    print("=" * 50)
    
    if successful_methods:
        print("✅ SUCCESSFUL METHODS:")
        for method in successful_methods:
            print(f"   • {method}")
    else:
        print("❌ NO SUCCESSFUL CONNECTIONS")
    
    if failed_methods:
        print("\n❌ FAILED METHODS:")
        for method, error in failed_methods:
            print(f"   • {method}: {error[:100]}...")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if successful_methods:
        print("✅ At least one connection method worked!")
        print("   Your database.py file has been updated with fallback methods.")
        print("   The dashboard should now work properly.")
    else:
        print("❌ No connection methods worked. Try these solutions:")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("   1. Update pymongo to latest version:")
        print("      pip install --upgrade pymongo")
        print("\n   2. Check MongoDB Atlas settings:")
        print("      • Go to MongoDB Atlas dashboard")
        print("      • Network Access → Add IP Address → 0.0.0.0/0")
        print("      • Database Access → Verify user has readWrite permissions")
        print("\n   3. Verify your connection string:")
        print("      • Should start with mongodb+srv://")
        print("      • Should include username, password, and cluster name")
        print("      • Should end with ?retryWrites=true&w=majority")
        print("\n   4. Update your Python SSL:")
        print("      • Update system certificates")
        print("      • Try: pip install --upgrade certifi")
        print("\n   5. Alternative: Use MongoDB Compass to test connection")
        print("      • Download MongoDB Compass")
        print("      • Use same connection string to test")
    
    return len(successful_methods) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 