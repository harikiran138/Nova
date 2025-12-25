from src.nova_ai.knowledge_base import KnowledgeBase
from src.nova_agents.tools.knowledge_tools import IndexingTool as _IndexingTool, LookupTool as _LookupTool

class IndexingTool(_IndexingTool):
    def __init__(self):
        super().__init__()
        # Override KB to the symbol in this shim module, so tests can patch here
        self.kb = KnowledgeBase()

class LookupTool(_LookupTool):
    def __init__(self):
        super().__init__()
        self.kb = KnowledgeBase()

__all__ = ["IndexingTool","LookupTool","KnowledgeBase"]
