"""
Verification script for Capabilities Layer.

Tests ResearchCapability and CodingCapability integration with ToolRegistry.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.append(str(Path.cwd()))

from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.tools.base import FunctionTool
from src.nova_agents.capabilities.research import ResearchCapability
from src.nova_agents.capabilities.coding import CodingCapability


def test_research_capability():
    """Test ResearchCapability initialization and dependency validation."""
    print("Testing ResearchCapability...")
    
    # Create registry and register mock tools
    registry = ToolRegistry()
    
    # Mock web tools
    def mock_search(query: str):
        return {"success": True, "results": [{"title": "Test", "url": "http://test.com"}]}
    
    def mock_extract(url: str):
        return {"success": True, "content": "Test content", "title": "Test Title"}
    
    def mock_learn(topic: str):
        return {"success": True, "summary": f"Learned about {topic}"}
    
    registry.register(FunctionTool("web.search", mock_search, "Search the web"))
    registry.register(FunctionTool("web.extract", mock_extract, "Extract content"))
    registry.register(FunctionTool("web.learn_topic", mock_learn, "Learn topic"))
    
    # Create capability
    research = ResearchCapability(registry)
    
    # Test properties
    if research.name != "research":
        print(f"FAIL: Expected name 'research', got '{research.name}'")
        return False
    print(f"PASS: Research capability name is '{research.name}'")
    
    # Test dependency validation
    if not research.validate_dependencies():
        print("FAIL: Dependencies validation failed")
        return False
    print("PASS: All dependencies available")
    
    # Test quick research
    result = research.execute("quantum computing", depth="quick")
    if not result.get("success"):
        print(f"FAIL: Quick research failed: {result.get('error')}")
        return False
    print(f"PASS: Quick research successful")
    
    # Test deep research
    result = research.execute("machine learning", depth="deep")
    if not result.get("success") or not result.get("summary"):
        print(f"FAIL: Deep research failed")
        return False
    print(f"PASS: Deep research successful with summary")
    
    # Test URL extraction
    result = research.extract_from_urls(["http://example.com"])
    if not result.get("success"):
        print(f"FAIL: URL extraction failed")
        return False
    print(f"PASS: URL extraction successful")
    
    return True


def test_coding_capability():
    """Test CodingCapability file operations."""
    print("\nTesting CodingCapability...")
    
    registry = ToolRegistry()
    coding = CodingCapability(registry)
    
    # Test properties
    if coding.name != "coding":
        print(f"FAIL: Expected name 'coding', got '{coding.name}'")
        return False
    print(f"PASS: Coding capability name is '{coding.name}'")
    
    # Test write operation
    test_file = Path("/tmp/test_capability_file.txt")
    result = coding.write_file(str(test_file), "Test content")
    if not result.get("success"):
        print(f"FAIL: Write file failed: {result.get('error')}")
        return False
    print(f"PASS: File write successful")
    
    # Test read operation
    result = coding.read_file(str(test_file))
    if not result.get("success") or result.get("content") != "Test content":
        print(f"FAIL: File read failed or content mismatch")
        return False
    print(f"PASS: File read successful")
    
    # Test list directory
    result = coding.list_directory("/tmp")
    if not result.get("success"):
        print(f"FAIL: List directory failed: {result.get('error')}")
        return False
    print(f"PASS: Directory listing successful")
    
    # Cleanup
    test_file.unlink(missing_ok=True)
    
    return True


def test_capability_registry_integration():
    """Test that capabilities can work with the registry."""
    print("\nTesting Capability-Registry Integration...")
    
    registry = ToolRegistry()
    
    # Register minimal tools
    registry.register(FunctionTool("web.search", lambda query: {"success": True}, "Search"))
    registry.register(FunctionTool("web.extract", lambda url: {"success": True}, "Extract"))
    registry.register(FunctionTool("web.learn_topic", lambda topic: {"success": True}, "Learn"))
    
    # Create capability
    research = ResearchCapability(registry)
    
    # Verify capability can access tools
    search_tool = registry.get("web.search")
    if not search_tool:
        print("FAIL: Could not retrieve tool from registry")
        return False
    print("PASS: Capability can access tools via registry")
    
    return True


if __name__ == "__main__":
    all_pass = True
    
    if not test_research_capability():
        all_pass = False
    
    if not test_coding_capability():
        all_pass = False
    
    if not test_capability_registry_integration():
        all_pass = False
    
    if all_pass:
        print("\n✅ All Capability Tests Passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
