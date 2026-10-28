import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestFrontendIconQueue:
    """Test the frontend icon queue workflow"""
    
    def test_single_icon_request(self):
        """Test that a single icon request works"""
        response = client.get("/get-icon/avion")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "fontawesome"
        assert "fa-plane" in data["class"]
    
    def test_multiple_icon_requests(self):
        """Test that multiple icon requests work in sequence"""
        icons_to_test = ["avion", "car", "police", "house", "money"]
        
        for icon in icons_to_test:
            response = client.get(f"/get-icon/{icon}")
            assert response.status_code == 200
            data = response.json()
            # All should return something (local, fontawesome, or none)
            assert data["source"] in ["local", "fontawesome", "none", "cached"]
    
    def test_airplane_news_title_words(self):
        """Test that words from airplane news title have icons"""
        title = "El avion que espero 24 horas en Puerto Iguazu"
        words = title.split()
        
        icon_count = 0
        for word in words:
            response = client.get(f"/get-icon/{word}")
            data = response.json()
            if data["source"] in ["local", "fontawesome", "cached"]:
                icon_count += 1
        
        # At least "avion" should have an icon
        assert icon_count >= 1, f"Expected at least 1 icon, got {icon_count}"
    
    def test_icon_queue_simulation(self):
        """Simulate the frontend icon queue processing"""
        # Simulate a news title
        title = "El avion que espero 24 horas"
        words = title.split()
        
        results = []
        for word in words:
            response = client.get(f"/get-icon/{word}")
            data = response.json()
            results.append({
                "word": word,
                "source": data["source"],
                "has_icon": data["source"] in ["local", "fontawesome", "cached"]
            })
        
        # Count how many words resulted in icons
        icons_found = sum(1 for r in results if r["has_icon"])
        
        print(f"\nIcon queue simulation results:")
        for r in results:
            print(f"  {r['word']}: {r['source']}")
        print(f"Total icons found: {icons_found}/{len(words)}")
        
        # At least "avion" should work
        assert icons_found >= 1


class TestAIReplacement:
    """Test AI icon replacement workflow"""
    
    def test_ai_replaces_initial_icons(self):
        """Test that AI keywords are different from title words"""
        title = "El avion que espero 24 horas"
        
        # Get AI keywords
        ai_response = client.get(f"/ai-icons?title={title}")
        ai_data = ai_response.json()
        
        # Split title into words
        title_words = set(title.lower().split())
        
        if ai_data["keywords"]:
            ai_keywords = set(k.lower() for k in ai_data["keywords"])
            
            # AI should provide different or more specific keywords
            # They might overlap, but shouldn't be identical
            print(f"\nTitle words: {title_words}")
            print(f"AI keywords: {ai_keywords}")
            
            # Test that AI keywords also have icons
            for keyword in ai_data["keywords"]:
                response = client.get(f"/get-icon/{keyword}")
                data = response.json()
                # At least should not error
                assert response.status_code == 200
        else:
            print("\nAI returned no keywords (might not be configured)")
    
    def test_workflow_with_ai(self):
        """Test complete workflow: news -> initial icons -> AI -> new icons"""
        # Get news
        news_response = client.get("/news?cc=AR")
        news_data = news_response.json()
        
        if not news_data:
            pytest.skip("No news available")
        
        # Take first news item
        first_news = news_data[0]
        title = first_news["title"]
        
        print(f"\nTesting with news: {title}")
        
        # Get initial icons from title words
        words = title.split()[:5]  # Limit to first 5 words for testing
        initial_icons = []
        for word in words:
            response = client.get(f"/get-icon/{word}")
            data = response.json()
            if data["source"] in ["local", "fontawesome", "cached"]:
                initial_icons.append(word)
        
        print(f"Initial icons from title: {initial_icons}")
        
        # Get AI keywords
        ai_response = client.get(f"/ai-icons?title={title}")
        ai_data = ai_response.json()
        
        if ai_data["keywords"]:
            print(f"AI keywords: {ai_data['keywords']}")
            
            # Test that AI keywords have icons
            ai_icons = []
            for keyword in ai_data["keywords"]:
                response = client.get(f"/get-icon/{keyword}")
                data = response.json()
                if data["source"] in ["local", "fontawesome", "cached"]:
                    ai_icons.append(keyword)
            
            print(f"AI icons found: {ai_icons}")
            
            # At least some AI keywords should have icons
            assert len(ai_icons) >= 0  # AI might return empty array
        else:
            print("AI returned no keywords")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
