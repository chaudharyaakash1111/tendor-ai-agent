"""
Simple test script to verify the backend is working correctly.
"""
import requests
import sys

def test_backend():
    """Test if the backend server is running and responding."""
    try:
        # Test the root endpoint
        response = requests.get("http://127.0.0.1:8001/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running and responding correctly")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Backend server returned status code: {response.status_code}")
            return False
            
        # Test the tenders endpoint
        response = requests.get("http://127.0.0.1:8001/tenders", timeout=5)
        if response.status_code == 200:
            print("✅ Tenders endpoint is working")
            tenders = response.json()
            print(f"Found {len(tenders)} tenders in the database")
        else:
            print(f"❌ Tenders endpoint returned status code: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the backend server")
        print("Please make sure the server is running on http://127.0.0.1:8001")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

if __name__ == "__main__":
    print("Testing Tender Aggregator Backend...")
    success = test_backend()
    if success:
        print("\n🎉 All tests passed! The backend is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the backend server.")
        sys.exit(1)