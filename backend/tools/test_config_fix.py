from app.core.config import Settings
import os

def test_settings_cors():
    print("Testing Settings CORS parsing...")
    
    # Test 1: Empty string (Simulate Render issue)
    os.environ["BACKEND_CORS_ORIGINS"] = ""
    s1 = Settings()
    print(f"Empty env gives: {s1.BACKEND_CORS_ORIGINS}")
    assert len(s1.BACKEND_CORS_ORIGINS) >= 3 # Should fallback to defaults
    
    # Test 2: Comma separated
    os.environ["BACKEND_CORS_ORIGINS"] = "http://a.com, http://b.com"
    s2 = Settings()
    print(f"Comma env gives: {s2.BACKEND_CORS_ORIGINS}")
    assert "http://a.com/" in [str(x) for x in s2.BACKEND_CORS_ORIGINS]
    
    # Test 3: JSON list
    os.environ["BACKEND_CORS_ORIGINS"] = '["http://c.com"]'
    s3 = Settings()
    print(f"JSON env gives: {s3.BACKEND_CORS_ORIGINS}")
    assert "http://c.com/" in [str(x) for x in s3.BACKEND_CORS_ORIGINS]

    print("✅ Settings CORS tests passed!")

if __name__ == "__main__":
    test_settings_cors()
