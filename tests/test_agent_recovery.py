import pytest
from unittest.mock import MagicMock, patch
from src.agent_core.agent_loop import AgentLoop

@pytest.fixture
def mock_dependencies():
    client = MagicMock()
    tools = MagicMock()
    
    # Mock specific tools structure
    tools.tools = {}
    tools.installer_tools_instance = MagicMock()
    
    # Mock config
    config = MagicMock()
    config.workspace_dir = MagicMock()
    config.enable_autonomous_install = True
    config.offline_mode = False
    config.enable_auto_model_switch = False
    
    # Mock Memory
    memory = MagicMock()
    
    return client, tools, config, memory

def test_recovery_install_package(mock_dependencies):
    """Test recovery when a package is missing."""
    client, tools, config, memory = mock_dependencies
    
    # Setup mocks
    with patch('src.agent_core.config.Config') as MockConfig, \
         patch('src.agent_core.memory.MemoryManager') as MockMemory, \
         patch('src.agent_core.agent_loop.KnowledgeStore') as MockKS, \
         patch('src.agent_core.agent_loop.LearningAgent') as MockLA, \
         patch('src.agent_core.tool_selector.ToolSelector') as MockSelector, \
         patch('src.agent_core.agent_loop.SafetyPolicy') as MockSafety, \
         patch('src.agent_core.autonomy.ErrorPredictor') as MockEP, \
         patch('src.agent_core.autonomy.RollbackManager') as MockRM, \
         patch('src.agent_core.autonomy.IntentModel') as MockIM, \
         patch('src.agent_core.telemetry.TelemetryManager') as MockTM:
        
        MockConfig.from_env.return_value = config
        
        agent = AgentLoop(client, tools)
        agent.memory = memory # Inject mock memory
        agent.config = config # Inject mock config
        
        # Setup error
        error_msg = "ModuleNotFoundError: No module named 'requests'"
        tool_name = "test_tool"
        args = {}
        
        # Setup installer success
        tools.installer_tools_instance.execute.return_value = {"success": True}
        
        # Run recovery
        result = agent._handle_error_recovery(tool_name, args, error_msg)
        
        # Verify
        assert result is True
        tools.installer_tools_instance.execute.assert_called_with({"package": "requests"})
        memory.remember.assert_called()

def test_recovery_suggest_fix(mock_dependencies):
    """Test recovery when a fix is suggested but not actionable automatically."""
    client, tools, config, memory = mock_dependencies
    
    with patch('src.agent_core.config.Config') as MockConfig, \
         patch('src.agent_core.memory.MemoryManager'), \
         patch('src.agent_core.agent_loop.KnowledgeStore'), \
         patch('src.agent_core.agent_loop.LearningAgent'), \
         patch('src.agent_core.tool_selector.ToolSelector'), \
         patch('src.agent_core.agent_loop.SafetyPolicy'), \
         patch('src.agent_core.autonomy.ErrorPredictor'), \
         patch('src.agent_core.autonomy.RollbackManager'), \
         patch('src.agent_core.autonomy.IntentModel'), \
         patch('src.agent_core.telemetry.TelemetryManager'):
         
        MockConfig.from_env.return_value = config
        
        agent = AgentLoop(client, tools)
        agent.config = config
        
        # Setup error (TypeError)
        error_msg = 'TypeError: can only concatenate str (not "int") to str'
        
        # Run recovery
        result = agent._handle_error_recovery("test_tool", {}, error_msg)
        
        # Should return False because it just prints the suggestion
        assert result is False

def test_recovery_known_fix_from_memory(mock_dependencies):
    """Test recovery when memory has a known fix."""
    client, tools, config, memory = mock_dependencies
    
    with patch('src.agent_core.config.Config') as MockConfig, \
         patch('src.agent_core.memory.MemoryManager'), \
         patch('src.agent_core.agent_loop.KnowledgeStore'), \
         patch('src.agent_core.agent_loop.LearningAgent'), \
         patch('src.agent_core.tool_selector.ToolSelector'), \
         patch('src.agent_core.agent_loop.SafetyPolicy'), \
         patch('src.agent_core.autonomy.ErrorPredictor'), \
         patch('src.agent_core.autonomy.RollbackManager'), \
         patch('src.agent_core.autonomy.IntentModel'), \
         patch('src.agent_core.telemetry.TelemetryManager'):

        MockConfig.from_env.return_value = config
        
        agent = AgentLoop(client, tools)
        agent.memory = memory
        agent.config = config
        
        # Setup memory recall
        memory.recall.return_value = "Run this command"
        
        # Run recovery
        result = agent._handle_error_recovery("test_tool", {}, "some random error")
        
        assert result is True
        memory.recall.assert_called()