#!/usr/bin/env python3
"""
Test script to verify voice assistant integration components
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:3000"
PRODUCTS_API_URL = f"{BASE_URL}/api/products"
VOICE_CART_API_URL = f"{BASE_URL}/api/voice-cart"

def test_api_connection():
    """Test if the Next.js server is running and accessible"""
    print("🔍 Testing API connection...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Next.js server is running")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Next.js server is not accessible: {e}")
        print("💡 Please start the Next.js server with: npm run dev")
        return False

def test_products_api():
    """Test the products API endpoint"""
    print("\n🔍 Testing products API...")
    try:
        response = requests.get(PRODUCTS_API_URL, timeout=10)
        response.raise_for_status()
        products = response.json()
        
        if products:
            print(f"✅ Products API working - Found {len(products)} products")
            print("Sample products:")
            for i, product in enumerate(products[:3]):
                print(f"  {i+1}. {product['name']} - ${product['price']}")
            return True
        else:
            print("⚠️  Products API working but no products found")
            print("💡 Please seed the database with: node lib/seed.js")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Products API failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_voice_cart_api():
    """Test the voice cart API endpoint"""
    print("\n🔍 Testing voice cart API...")
    try:
        # First get a product to test with
        products_response = requests.get(PRODUCTS_API_URL, timeout=10)
        products = products_response.json()
        
        if not products:
            print("❌ No products available for cart test")
            return False
            
        test_product = products[0]
        test_payload = {
            "productId": test_product['id'],
            "email": "test-voice-assistant@example.com",
            "quantity": 1
        }
        
        response = requests.post(
            VOICE_CART_API_URL,
            json=test_payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print("✅ Voice cart API working")
            print(f"   Successfully added '{test_product['name']}' to cart")
            return True
        else:
            print(f"❌ Voice cart API failed: {result.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Voice cart API failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_python_dependencies():
    """Test if all required Python packages are available"""
    print("\n🔍 Testing Python dependencies...")
    
    required_packages = [
        ('speech_recognition', 'Speech Recognition'),
        ('pygame', 'Pygame (Audio)'),
        ('gtts', 'Google Text-to-Speech'),
        ('requests', 'HTTP Requests'),
        ('google.generativeai', 'Google Generative AI')
    ]
    
    missing_packages = []
    
    for package_name, display_name in required_packages:
        try:
            __import__(package_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - NOT INSTALLED")
            missing_packages.append(package_name)
    
    # Test PyAudio separately (it's part of speech_recognition)
    try:
        import pyaudio
        print("✅ PyAudio (Microphone access)")
    except ImportError:
        print("❌ PyAudio - NOT INSTALLED")
        missing_packages.append('PyAudio')
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_microphone():
    """Test microphone access"""
    print("\n🔍 Testing microphone access...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        # List available microphones
        mic_list = sr.Microphone.list_microphone_names()
        if mic_list:
            print(f"✅ Found {len(mic_list)} microphone(s)")
            print(f"   Default: {mic_list[0] if mic_list else 'None'}")
        else:
            print("⚠️  No microphones detected")
            
        # Test microphone initialization
        with sr.Microphone() as source:
            print("✅ Microphone access successful")
            return True
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Voice Assistant Integration Test")
    print("=" * 50)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Microphone Access", test_microphone),
        ("API Connection", test_api_connection),
        ("Products API", test_products_api),
        ("Voice Cart API", test_voice_cart_api),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Voice assistant is ready to use.")
        print("\nTo start the voice assistant:")
        print("1. Make sure Next.js server is running: npm run dev")
        print("2. Run the voice assistant: python test.py")
    else:
        print("⚠️  SOME TESTS FAILED. Please fix the issues above.")
        print("\nNext steps:")
        if not results.get("Python Dependencies", True):
            print("- Install missing Python packages")
        if not results.get("API Connection", True):
            print("- Start Next.js server: npm run dev")
        if not results.get("Products API", True):
            print("- Seed database: node lib/seed.js")
        if not results.get("Microphone Access", True):
            print("- Check microphone permissions and hardware")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
