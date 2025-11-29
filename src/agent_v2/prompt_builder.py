"""
Prompt Builder - Template Assembly Only (No Medical Logic)

Responsibility: Assemble the super prompt by substituting playbook and protocol
content into the template. NO medical interpretation, NO clinical logic.
"""

import json
import logging
from typing import Dict

from config.prompts.super_prompt import SUPER_PROMPT_TEMPLATE, OUTPUT_SCHEMA_JSON

# Logger - usar logger do agent_v2
from .logger import logger


class PromptBuilder:
    """
    Builds comprehensive analysis prompts by assembling template with content.
    
    Principle: Simple template substitution only.
    All medical intelligence is in the template, not in this code.
    """
    
    def __init__(self):
        """Initialize prompt builder with template."""
        self.template = SUPER_PROMPT_TEMPLATE
        logger.debug("PromptBuilder initialized with super prompt template")
    
    def build_analysis_prompt(self, playbook_content: str, protocol_json: Dict) -> str:
        """
        Build comprehensive analysis prompt for LLM.
        
        Simple template substitution - NO medical interpretation,
        NO content analysis, NO clinical logic.
        
        Args:
            playbook_content: Raw playbook text content
            protocol_json: Protocol dictionary (will be formatted as JSON)
            
        Returns:
            Complete prompt string ready for LLM
            
        Example:
            >>> builder = PromptBuilder()
            >>> playbook = "# Medical Guidelines..."
            >>> protocol = {"nodes": [...]}
            >>> prompt = builder.build_analysis_prompt(playbook, protocol)
            >>> "CLINICAL PLAYBOOK" in prompt
            True
        """
        # Format protocol as pretty JSON
        # NO validation, NO medical analysis - just formatting
        try:
            protocol_formatted = json.dumps(
                protocol_json,
                indent=2,
                ensure_ascii=False,
                sort_keys=False
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to format protocol JSON: {e}")
            # Fallback: convert to string representation
            protocol_formatted = str(protocol_json)
        
        # Simple template substitution
        # NO medical interpretation of content
        prompt = self.template.format(
            playbook_content=playbook_content,
            protocol_json=protocol_formatted,
            output_schema=OUTPUT_SCHEMA_JSON
        )
        
        # Log prompt metadata (not full content to save log space)
        prompt_size = len(prompt)
        prompt_hash = hash(prompt) % 1000000  # Simple hash for identification
        
        logger.info(
            f"Built analysis prompt: size={prompt_size} chars, "
            f"hash={prompt_hash}, playbook_size={len(playbook_content)} chars, "
            f"protocol_nodes={self._count_protocol_nodes(protocol_json)}"
        )
        
        # Return complete prompt - NO interpretation
        return prompt
    
    def _count_protocol_nodes(self, protocol_json: Dict) -> int:
        """
        Count protocol nodes for logging purposes only.
        
        Simple structure traversal - NO medical validation.
        """
        # Try common protocol structures
        if isinstance(protocol_json, dict):
            # Look for nodes in common locations
            if "nodes" in protocol_json:
                return len(protocol_json["nodes"]) if isinstance(protocol_json["nodes"], list) else 0
            if "protocol_tree" in protocol_json:
                tree = protocol_json["protocol_tree"]
                if isinstance(tree, dict) and "nodes" in tree:
                    return len(tree["nodes"]) if isinstance(tree["nodes"], list) else 0
            if "questions" in protocol_json:
                return len(protocol_json["questions"]) if isinstance(protocol_json["questions"], list) else 0
        
        # If structure unknown, return 0 (not an error, just unknown)
        return 0

