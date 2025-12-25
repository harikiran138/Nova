import pytest
from unittest.mock import MagicMock, patch
from src.nova_agents.tools.vision_tools import VisionTool

class TestVisionTool:
    @pytest.fixture
    def tool(self):
        return VisionTool()

    def test_image_analysis_mock(self, tool):
        """Test image analysis with a mock response."""
        with patch('src.nova_agents.tools.vision_tools.VisionTool.analyze_image') as mock_analyze:
            mock_analyze.return_value = {"labels": ["cat", "pet"], "confidence": 0.95}
            
            result = tool.execute({"image_path": "cat.jpg"})
            
            assert result["success"] is True
            assert "cat" in result["result"]["labels"]

    def test_missing_file(self, tool):
        """Test error handling for missing file."""
        result = tool.execute({"image_path": "non_existent.jpg"})
        assert result["success"] is False
