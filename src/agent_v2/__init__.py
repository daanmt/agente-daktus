"""
Agent V2: Simplified LLM-Centric QA Architecture

This module implements a pure LLM-driven agent architecture where:
- Agent coordinates workflow only (no clinical logic)
- LLM performs all clinical analysis and interpretation
- Zero hardcoded medical knowledge in code

Agent V2 is now the ONLY pipeline - no legacy, no fallbacks.
"""

__version__ = "2.0.0"

# Main pipeline function - this is the entry point
from .pipeline import analyze

# Protocol/Playbook loading utilities
from .protocol_loader import load_protocol, load_playbook

# Core components (for advanced usage)
from .prompt_builder import PromptBuilder
from .llm_client import LLMClient
from .output.validator import ResponseValidator

__all__ = [
    "analyze",  # Main entry point - USE THIS
    "load_protocol",
    "load_playbook",
    "PromptBuilder", 
    "LLMClient",
    "ResponseValidator",
]
