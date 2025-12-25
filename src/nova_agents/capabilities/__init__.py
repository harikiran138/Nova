"""Capabilities package - High-level agent behaviors."""

from src.nova_agents.capabilities.base import Capability, BaseCapability
from src.nova_agents.capabilities.research import ResearchCapability
from src.nova_agents.capabilities.coding import CodingCapability

__all__ = ['Capability', 'BaseCapability', 'ResearchCapability', 'CodingCapability']

