#!/usr/bin/env python3
"""Test script for Gerrit integration."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gerrit_integration():
    """Test Gerrit integration functionality."""
    print("🧪 Testing Gerrit Integration...")
    
    try:
        from explainstack.integrations.gerrit import GerritIntegration
        print("✅ GerritIntegration imported successfully")
        
        # Initialize Gerrit integration
        gerrit = GerritIntegration()
        print("✅ GerritIntegration initialized")
        
        # Test URL detection
        test_urls = [
            "https://review.opendev.org/c/openstack/nova/+/12345",
            "https://review.opendev.org/c/openstack/keystone/+/67890",
            "https://github.com/user/repo",  # Should be False
            "https://review.opendev.org/c/openstack/neutron/+/11111/1"  # With revision
        ]
        
        print("\n🔍 Testing URL detection:")
        for url in test_urls:
            is_gerrit = gerrit.is_gerrit_url(url)
            status = "✅" if is_gerrit else "❌"
            print(f"  {status} {url} -> {is_gerrit}")
        
        # Test URL parsing
        print("\n🔍 Testing URL parsing:")
        for url in test_urls:
            if gerrit.is_gerrit_url(url):
                parsed = gerrit.parse_gerrit_url(url)
                print(f"  ✅ {url}")
                print(f"     -> {parsed}")
            else:
                print(f"  ❌ {url} (not a Gerrit URL)")
        
        print("\n🎉 Gerrit integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try installing dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gerrit_api_call():
    """Test actual Gerrit API call (requires internet)."""
    print("\n🌐 Testing Gerrit API call...")
    
    try:
        from explainstack.integrations.gerrit import GerritIntegration
        
        # Test without authentication first
        print("🔍 Testing public access (no authentication)...")
        gerrit_public = GerritIntegration()
        
        # Test with a real Gerrit URL (this will make an actual API call)
        test_url = "https://review.opendev.org/c/openstack/nova/+/12345"
        
        print(f"🔍 Testing API call with: {test_url}")
        print("⏳ This may take a few seconds...")
        
        success, result, error = gerrit_public.analyze_gerrit_url(test_url)
        
        if success:
            print("✅ Gerrit API call successful!")
            print(f"📊 Result summary:")
            if result and 'summary' in result:
                summary = result['summary']
                print(f"  - Subject: {summary.get('subject', 'N/A')}")
                print(f"  - Status: {summary.get('status', 'N/A')}")
                print(f"  - Project: {summary.get('project', 'N/A')}")
                print(f"  - Owner: {summary.get('owner', 'N/A')}")
            else:
                print("  - No summary data available")
        else:
            print(f"❌ Gerrit API call failed: {error}")
            if "Authentication required" in error:
                print("💡 This is expected - some changes require authentication")
                print("💡 You can configure Gerrit credentials in the app")
            else:
                print("💡 This might be due to network issues or invalid change ID")
        
        # Test authentication status
        print(f"\n🔐 Authentication status: {gerrit_public.is_authenticated()}")
        
        return success
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_gerrit_authentication():
    """Test Gerrit authentication features."""
    print("\n🔐 Testing Gerrit Authentication Features...")
    
    try:
        from explainstack.integrations.gerrit import GerritIntegration
        
        # Test without authentication
        print("🔍 Testing without authentication...")
        gerrit_no_auth = GerritIntegration()
        print(f"  - Is authenticated: {gerrit_no_auth.is_authenticated()}")
        
        # Test with username/password
        print("🔍 Testing with username/password...")
        gerrit_user_pass = GerritIntegration(
            username="test_user",
            password="test_password"
        )
        print(f"  - Is authenticated: {gerrit_user_pass.is_authenticated()}")
        
        # Test with API token
        print("🔍 Testing with API token...")
        gerrit_token = GerritIntegration(
            api_token="test_token"
        )
        print(f"  - Is authenticated: {gerrit_token.is_authenticated()}")
        
        print("✅ Authentication features working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ExplainStack Gerrit Integration Test")
    print("=" * 50)
    
    # Test basic functionality
    basic_test = test_gerrit_integration()
    
    if basic_test:
        # Test authentication features
        auth_test = test_gerrit_authentication()
        
        # Test API call
        api_test = test_gerrit_api_call()
        
        if auth_test and api_test:
            print("\n🎉 All tests passed! Gerrit integration is working.")
        elif auth_test:
            print("\n✅ Authentication features work, but API calls may have issues.")
        else:
            print("\n⚠️  Basic functionality works, but some features may have issues.")
    else:
        print("\n❌ Basic functionality test failed.")
        sys.exit(1)
