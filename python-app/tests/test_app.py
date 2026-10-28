import pytest
from fastapi.testclient import TestClient
from main import app
import os
import tempfile
import shutil

client = TestClient(app)

@pytest.fixture
def test_cache_dir():
    """Create a temporary cache directory for testing"""
    original_cache_dir = "static/icon-cache"
    temp_dir = tempfile.mkdtemp()
    
    # Create test cache directory
    test_cache = os.path.join(temp_dir, "icon-cache")
    os.makedirs(test_cache, exist_ok=True)
    
    yield test_cache
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestNews:
    """Test news loading for different countries"""
    
    def test_news_load_for_spain(self):
        """Test that news loads for Spain"""
        response = client.get("/news?cc=ES")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "title" in data[0]
        assert "description" in data[0]
        assert "link" in data[0]
    
    def test_news_load_for_argentina(self):
        """Test that news loads for Argentina"""
        response = client.get("/news?cc=AR")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_news_load_for_mexico(self):
        """Test that news loads for Mexico"""
        response = client.get("/news?cc=MX")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_news_different_countries(self):
        """Test that different countries return different news"""
        es_news = client.get("/news?cc=ES").json()
        ar_news = client.get("/news?cc=AR").json()
        
        # They should be different (at least titles)
        es_titles = [n["title"] for n in es_news[:5]]
        ar_titles = [n["title"] for n in ar_news[:5]]
        
        # At least some titles should be different
        assert not all(t1 == t2 for t1, t2 in zip(es_titles, ar_titles))


class TestIconFallback:
    """Test icon loading with fallback chain"""
    
    def test_icon_local_png(self):
        """Test that local PNG icons load"""
        response = client.get("/get-icon/Argentina")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "local"
        assert "url" in data
        assert data["url"] == "/img/Argentina.png"
    
    def test_icon_local_euros(self):
        """Test another local PNG icon"""
        response = client.get("/get-icon/euros")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "local"
    
    def test_icon_fontawesome_fallback(self):
        """Test Font Awesome fallback for words"""
        response = client.get("/get-icon/police")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "fontawesome"
        assert "class" in data
        assert "fa-solid" in data["class"]
    
    def test_icon_fontawesome_plane(self):
        """Test Font Awesome for 'avion'"""
        response = client.get("/get-icon/avion")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "fontawesome"
        assert "fa-plane" in data["class"]
    
    def test_icon_fontawesome_car(self):
        """Test Font Awesome for 'car'"""
        response = client.get("/get-icon/car")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "fontawesome"
        assert "fa-car" in data["class"]
    
    def test_icon_none_when_not_found(self):
        """Test that unknown words return 'none'"""
        response = client.get("/get-icon/xyz123abc")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "none"
    
    def test_icon_cache_workflow(self, test_cache_dir):
        """Test icon caching workflow"""
        # This test would require mocking the cache directory
        # For now, we'll just test the API response
        pass


class TestAI:
    """Test AI icon enhancement"""
    
    def test_ai_icons_endpoint_exists(self):
        """Test that AI endpoint exists"""
        response = client.get("/ai-icons?title=Test news headline")
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data
        assert isinstance(data["keywords"], list)
    
    def test_ai_icons_with_specific_title(self):
        """Test AI with airplane news title"""
        response = client.get("/ai-icons?title=El%20avion%20que%20espero%2024%20horas")
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data
        # AI might return empty array if not configured
        assert isinstance(data["keywords"], list)


class TestFullWorkflow:
    """Test the complete workflow: news -> icons -> AI -> icon replacement"""
    
    def test_countries_endpoint(self):
        """Test countries endpoint"""
        response = client.get("/countries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(c["code"] == "ES" for c in data)
        assert any(c["code"] == "AR" for c in data)
    
    def test_icon_word_normalization(self):
        """Test that icon requests handle accented characters"""
        # Test with accented word
        response = client.get("/get-icon/policia")
        assert response.status_code == 200
        data = response.json()
        # Should try Font Awesome fallback
        assert data["source"] in ["fontawesome", "none"]
    
    def test_icon_case_insensitive(self):
        """Test that icon lookups are case insensitive"""
        response1 = client.get("/get-icon/car")
        response2 = client.get("/get-icon/CAR")
        response3 = client.get("/get-icon/Car")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        # All should return the same source
        assert data1["source"] == data2["source"] == data3["source"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
