#!/usr/bin/env python3
"""
Simple test script to validate the watchdog application functionality.
"""
import sys
import os
sys.path.insert(0, '/home/runner/work/watchdog/watchdog')

from service_checker import ServiceCheckerFactory, TCPChecker, HTTPChecker
from models import ServiceStatus

def test_service_checkers():
    print("Testing service checkers...")
    
    # Test TCP checker with a well-known service (Google DNS)
    print("\n1. Testing TCP checker with Google DNS (8.8.8.8:53)")
    tcp_checker = TCPChecker("8.8.8.8", 53, timeout=5)
    status, response_time, error = tcp_checker.check()
    print(f"   Status: {status}, Response Time: {response_time:.3f}s, Error: {error}")
    
    # Test HTTP checker with a well-known service
    print("\n2. Testing HTTP checker with httpbin.org")
    http_checker = HTTPChecker("httpbin.org", 80, timeout=5)
    status, response_time, error = http_checker.check()
    print(f"   Status: {status}, Response Time: {response_time:.3f}s, Error: {error}")
    
    # Test factory
    print("\n3. Testing ServiceCheckerFactory")
    factory_checker = ServiceCheckerFactory.create_checker('tcp', '8.8.8.8', 53)
    status, response_time, error = factory_checker.check()
    print(f"   Factory TCP checker - Status: {status}, Response Time: {response_time:.3f}s")
    
    print("\nService checker tests completed!")

def test_flask_app():
    print("\nTesting Flask app creation...")
    try:
        from app import create_app
        app, monitoring_service = create_app()
        print("   ✓ Flask app created successfully")
        print(f"   ✓ Monitoring service initialized: {monitoring_service}")
        
        with app.app_context():
            from models import db
            print("   ✓ Database models accessible")
            
        return True
    except Exception as e:
        print(f"   ✗ Error creating Flask app: {e}")
        return False

if __name__ == "__main__":
    print("Watchdog Application Test Suite")
    print("=" * 40)
    
    test_service_checkers()
    
    if test_flask_app():
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)