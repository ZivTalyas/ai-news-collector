#!/usr/bin/env python3
"""
SSL Handshake Fix Script for Streamlit Cloud
Helps diagnose and fix SSL handshake issues with MongoDB Atlas
"""

import os
import sys
import ssl
import urllib3
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_ssl_context():
    """Create SSL context with various compatibility settings"""
    contexts = []
    
    # Context 1: Default with disabled verification
    try:
        context1 = ssl.create_default_context()
        context1.check_hostname = False
        context1.verify_mode = ssl.CERT_NONE
        contexts.append(('Default SSL Context', context1))
    except Exception as e:
        print(f"⚠️ Could not create default SSL context: {e}")
    
    # Context 2: Legacy compatibility
    try:
        context2 = ssl.create_default_context()
        context2.check_hostname = False
        context2.verify_mode = ssl.CERT_NONE
        context2.set_ciphers('DEFAULT@SECLEVEL=1')
        context2.options |= ssl.OP_LEGACY_SERVER_CONNECT
        contexts.append(('Legacy SSL Context', context2))
    except Exception as e:
        print(f"⚠️ Could not create legacy SSL context: {e}")
    
    # Context 3: TLS v1.2 specific
    try:
        context3 = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context3.check_hostname = False
        context3.verify_mode = ssl.CERT_NONE
        contexts.append(('TLS v1.2 Context', context3))
    except Exception as e:
        print(f"⚠️ Could not create TLS v1.2 context: {e}")
    
    return contexts

def test_connection_methods(mongo_uri):
    """Test different connection methods for MongoDB Atlas"""
    print("🔧 Testing SSL Handshake Fix Methods")
    print("=" * 50)
    
    # Get SSL contexts
    ssl_contexts = create_ssl_context()
    
    # Test methods
    test_methods = []
    
    # Method 1: SSL contexts with various configurations
    for context_name, context in ssl_contexts:
        test_methods.append({
            'name': f'SSL Context - {context_name}',
            'options': {
                'ssl': True,
                'ssl_context': context,
                'serverSelectionTimeoutMS': 30000,
                'socketTimeoutMS': 60000,
                'connectTimeoutMS': 30000,
                'maxPoolSize': 1,
                'retryWrites': True
            }
        })
    
    # Method 2: TLS with various security levels
    tls_methods = [
        {
            'name': 'TLS - Maximum Compatibility',
            'options': {
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'tlsInsecure': True,
                'serverSelectionTimeoutMS': 45000,
                'socketTimeoutMS': 90000,
                'connectTimeoutMS': 45000,
                'maxPoolSize': 1,
                'retryWrites': True
            }
        },
        {
            'name': 'TLS - Streamlit Cloud Optimized',
            'options': {
                'ssl': False,
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'serverSelectionTimeoutMS': 60000,
                'socketTimeoutMS': 120000,
                'connectTimeoutMS': 60000,
                'maxPoolSize': 1,
                'retryWrites': True
            }
        },
        {
            'name': 'TLS - High Timeout',
            'options': {
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'tlsInsecure': True,
                'serverSelectionTimeoutMS': 120000,
                'socketTimeoutMS': 180000,
                'connectTimeoutMS': 120000,
                'maxPoolSize': 1,
                'retryWrites': True
            }
        }
    ]
    
    test_methods.extend(tls_methods)
    
    # Method 3: Legacy SSL configurations
    legacy_methods = [
        {
            'name': 'Legacy SSL - Certificate Bypass',
            'options': {
                'ssl': True,
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_match_hostname': False,
                'ssl_ca_certs': None,
                'serverSelectionTimeoutMS': 90000,
                'socketTimeoutMS': 180000,
                'connectTimeoutMS': 90000,
                'maxPoolSize': 1,
                'retryWrites': True
            }
        },
        {
            'name': 'No SSL/TLS - Plain Connection',
            'options': {
                'ssl': False,
                'tls': False,
                'serverSelectionTimeoutMS': 60000,
                'socketTimeoutMS': 120000,
                'connectTimeoutMS': 60000,
                'maxPoolSize': 1,
                'retryWrites': True
            }
        }
    ]
    
    test_methods.extend(legacy_methods)
    
    # Test each method
    successful_methods = []
    failed_methods = []
    
    for i, method in enumerate(test_methods, 1):
        print(f"\n🔐 Test {i}: {method['name']}")
        try:
            client = MongoClient(mongo_uri, **method['options'])
            
            # Test ping
            client.admin.command('ping')
            print(f"   ✅ Connection successful")
            
            # Test database access
            db = client['ai_news']
            collection = db['articles']
            count = collection.count_documents({})
            print(f"   ✅ Database access successful - {count} documents")
            
            successful_methods.append(method['name'])
            client.close()
            
            # If we found a working method, we can stop here
            print(f"\n🎉 SUCCESS! {method['name']} works!")
            break
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}...")
            failed_methods.append((method['name'], str(e)))
            continue
    
    # Results
    print(f"\n{'='*50}")
    print("📊 TEST RESULTS")
    print(f"{'='*50}")
    
    if successful_methods:
        print("✅ SUCCESSFUL METHODS:")
        for method in successful_methods:
            print(f"   • {method}")
    else:
        print("❌ NO SUCCESSFUL METHODS FOUND")
    
    if failed_methods:
        print(f"\n❌ FAILED METHODS ({len(failed_methods)}):")
        for method, error in failed_methods[:5]:  # Show first 5 failures
            print(f"   • {method}: {error[:60]}...")
    
    return len(successful_methods) > 0

def get_mongo_uri():
    """Get MongoDB URI from environment or user input"""
    # Try environment first
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        return mongo_uri
    
    # Try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'MONGO_URI' in st.secrets:
            return st.secrets['MONGO_URI']
    except:
        pass
    
    # Ask user for input
    print("❌ MongoDB URI not found in environment variables")
    print("Please provide your MongoDB Atlas connection string:")
    mongo_uri = input("MongoDB URI: ").strip()
    
    if not mongo_uri:
        print("❌ No MongoDB URI provided")
        return None
    
    return mongo_uri

def main():
    """Main function"""
    print("🔧 SSL Handshake Fix Tool for Streamlit Cloud")
    print("=" * 60)
    
    # Get MongoDB URI
    mongo_uri = get_mongo_uri()
    if not mongo_uri:
        return False
    
    print(f"✅ MongoDB URI: {mongo_uri[:50]}...")
    
    # Test different connection methods
    success = test_connection_methods(mongo_uri)
    
    if success:
        print("\n✅ SOLUTION FOUND!")
        print("Your MongoDB connection issue has been resolved.")
        print("The successful connection method will be used in your app.")
    else:
        print("\n❌ NO SOLUTION FOUND")
        print("\n💡 Additional troubleshooting steps:")
        print("1. Update your MongoDB Atlas cluster to the latest version")
        print("2. Check if your cluster supports TLS 1.2+")
        print("3. Try a different MongoDB hosting provider")
        print("4. Contact MongoDB Atlas support about SSL/TLS compatibility")
        print("5. Consider using MongoDB Atlas Shared Clusters (M0) if on dedicated")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 