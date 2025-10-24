#!/usr/bin/env python3
"""
Test script for Eclipso Privacy Browser
Tests all major components and functionality
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5.QtWidgets imported successfully")
    except ImportError as e:
        print(f"❌ PyQt5.QtWidgets import failed: {e}")
        return False
    
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt5.QtWebEngineWidgets imported successfully")
    except ImportError as e:
        print(f"❌ PyQt5.QtWebEngineWidgets import failed: {e}")
        return False
    
    try:
        from browser import PrivacyBrowser
        print("✅ PrivacyBrowser class imported successfully")
    except ImportError as e:
        print(f"❌ PrivacyBrowser import failed: {e}")
        return False
    
    try:
        from privacy.enhanced_protector import EnhancedPrivacyProtector
        print("✅ EnhancedPrivacyProtector imported successfully")
    except ImportError as e:
        print(f"❌ EnhancedPrivacyProtector import failed: {e}")
        return False
    
    try:
        from privacy.fingerprint_protector import FingerPrintProtector
        print("✅ FingerPrintProtector imported successfully")
    except ImportError as e:
        print(f"❌ FingerPrintProtector import failed: {e}")
        return False
    
    try:
        from privacy.cookie_manager import cookie_manager
        print("✅ cookie_manager imported successfully")
    except ImportError as e:
        print(f"❌ cookie_manager import failed: {e}")
        return False
    
    return True

def test_privacy_components():
    """Test that privacy components can be instantiated"""
    print("\n🛡️ Testing privacy components...")
    
    try:
        from privacy.enhanced_protector import EnhancedPrivacyProtector
        privacy = EnhancedPrivacyProtector()
        print("✅ EnhancedPrivacyProtector instantiated successfully")
    except Exception as e:
        print(f"❌ EnhancedPrivacyProtector instantiation failed: {e}")
        return False
    
    try:
        from privacy.fingerprint_protector import FingerPrintProtector
        fingerprint = FingerPrintProtector()
        print("✅ FingerPrintProtector instantiated successfully")
    except Exception as e:
        print(f"❌ FingerPrintProtector instantiation failed: {e}")
        return False
    
    try:
        from privacy.cookie_manager import cookie_manager
        cookie_mgr = cookie_manager()
        print("✅ cookie_manager instantiated successfully")
    except Exception as e:
        print(f"❌ cookie_manager instantiation failed: {e}")
        return False
    
    return True

def test_browser_class():
    """Test that browser class can be created"""
    print("\n🌐 Testing browser class...")
    
    try:
        from browser import PrivacyBrowser
        # Note: We can't actually create the browser without QApplication
        print("✅ PrivacyBrowser class structure verified")
        print("✅ All required methods found:")
        
        # Check for required methods
        required_methods = [
            'setup_ui', 'create_toolbar', 'load_url', 'go_back', 
            'go_forward', 'refresh_page', 'add_to_history'
        ]
        
        for method in required_methods:
            if hasattr(PrivacyBrowser, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} - MISSING")
                return False
        
    except Exception as e:
        print(f"❌ Browser class test failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that all dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    try:
        import requests
        print(f"✅ requests {requests.__version__}")
    except ImportError:
        print("❌ requests not available")
        return False
    
    try:
        import bs4
        print(f"✅ beautifulsoup4 {bs4.__version__}")
    except ImportError:
        print("❌ beautifulsoup4 not available")
        return False
    
    try:
        from PIL import Image
        print(f"✅ Pillow {Image.__version__}")
    except ImportError:
        print("❌ Pillow not available")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Eclipso Privacy Browser - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_privacy_components,
        test_browser_class,
        test_dependencies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ Test {test.__name__} failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Browser is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
