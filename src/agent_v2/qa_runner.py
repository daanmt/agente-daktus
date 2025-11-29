"""
Simplified QA Runner - Orchestration Only (No Medical Logic)

Responsibility: Coordinate the analysis workflow by calling modules in sequence.
NO medical interpretation, NO clinical logic, NO content analysis.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict

from .protocol_loader import load_protocol, load_playbook
from .prompt_builder import PromptBuilder
from .llm_client import LLMClient
from .output.validator import ResponseValidator

# Logger - usar logger do agent_v2
from .logger import logger


class SimplifiedQARunner:
    """
    Orchestrates complete QA analysis workflow using LLM only.
    
    Principle: Simple orchestration - coordinate modules, don't interpret.
    All clinical intelligence resides in the LLM, not in this code.
    
    Pipeline:
    1. Load playbook and protocol files (no interpretation)
    2. Build analysis prompt (template assembly)
    3. Send to LLM for comprehensive analysis (all intelligence here)
    4. Return structured results (no interpretation)
    """
    
    def __init__(self, model: str = None):
        """
        Initialize QA runner with required components.
        
        Args:
            model: LLM model identifier (optional, uses default if not provided)
        """
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient(model=model)
        self.validator = ResponseValidator()
        
        logger.info("SimplifiedQARunner initialized")
    
    def run_analysis_from_content(self, playbook_content: str, protocol_json: dict, model: str = None) -> Dict:
        """
        Run analysis from in-memory content (for CLI integration).
        
        This method allows the SimplifiedQARunner to be used with content
        already loaded in memory, avoiding the need for temporary files.
        
        Args:
            playbook_content: Playbook content as string
            protocol_json: Protocol JSON as dictionary
            model: Optional model override
            
        Returns:
            Complete analysis result (same format as run_analysis)
        """
        analysis_start_time = time.time()
        
        # Logging inicial robusto - captura erros desde o início
        try:
            logger.info(
                f"Analysis from content started: playbook_size={len(playbook_content)} chars, "
                f"protocol_nodes={self._count_protocol_nodes(protocol_json)}"
            )
            logger.info("Agent V2: All analysis centralized in super prompt")
        except Exception as log_err:
            # Se logging falha, usar print como fallback
            print(f"[ERROR] Failed to log analysis start: {log_err}")
            import traceback
            traceback.print_exc()
        
        try:
            # Override model if provided
            if model:
                try:
                    self.llm_client = LLMClient(model=model)
                    logger.debug(f"LLM client reinitialized with model: {model}")
                except Exception as e:
                    logger.error(f"Failed to reinitialize LLM client with model {model}: {e}", exc_info=True)
                    raise
            
            # Step 1: Build prompt directly from content
            prompt_start = time.time()
            try:
                prompt = self.prompt_builder.build_analysis_prompt(
                    playbook_content,
                    protocol_json
                )
                prompt_time_ms = int((time.time() - prompt_start) * 1000)
                
                logger.info(
                    f"Prompt built: size={len(prompt)} chars, "
                    f"build_time={prompt_time_ms}ms"
                )
            except Exception as e:
                logger.error(f"Failed to build prompt: {e}", exc_info=True)
                raise
            
            # Step 2: LLM analysis (ALL clinical intelligence here)
            llm_start = time.time()
            try:
                analysis_result = self.llm_client.analyze(prompt)
                llm_time_ms = int((time.time() - llm_start) * 1000)
                
                logger.info(
                    f"LLM analysis completed: latency={llm_time_ms}ms"
                )
            except Exception as e:
                llm_time_ms = int((time.time() - llm_start) * 1000)
                logger.error(
                    f"LLM analysis failed after {llm_time_ms}ms: {e}",
                    exc_info=True
                )
                raise
            
            # Step 3: Validate LLM response schema
            validation_start = time.time()
            try:
                is_valid, errors = self.validator.validate(analysis_result)
                if not is_valid:
                    error_msg = f"LLM response validation failed: {errors}"
                    logger.error(error_msg)
                    logger.error(f"Response keys: {list(analysis_result.keys())}")
                    raise ValueError(error_msg)
                
                completeness_ok, warnings = self.validator.validate_completeness(
                    analysis_result,
                    playbook_size=len(playbook_content)
                )
                if warnings:
                    for warning in warnings:
                        logger.warning(f"Completeness warning: {warning}")
                
            except Exception as e:
                logger.error(f"Response validation error: {e}", exc_info=True)
                raise
            
            validation_time_ms = int((time.time() - validation_start) * 1000)
            logger.debug(f"Response validated: validation_time={validation_time_ms}ms")
            
            # Step 4: Add metadata
            total_time_ms = int((time.time() - analysis_start_time) * 1000)
            
            if "metadata" not in analysis_result:
                analysis_result["metadata"] = {}
            
            analysis_result["metadata"].update({
                "processing_time_ms": total_time_ms,
                "stage_durations_ms": {
                    "prompt_build": prompt_time_ms,
                    "llm_call": llm_time_ms,
                    "validation": validation_time_ms
                },
                "playbook_size_bytes": len(playbook_content),
                "protocol_nodes_count": self._count_protocol_nodes(protocol_json),
                "timestamp": datetime.now().isoformat(),
                "architecture": "simplified_v2"
            })
            
            logger.info(
                f"Analysis from content completed: total_time={total_time_ms}ms, "
                f"entities_extracted={self._count_extracted_entities(analysis_result)}"
            )
            
            # MVP: Return simplified output format
            return {
                "analysis": analysis_result,
                "improvements": analysis_result.get("recommendations", []),
                "llm_raw": json.dumps(analysis_result, ensure_ascii=False, indent=2),
                "metadata": {
                    "duration_ms": total_time_ms,
                    "model": self.llm_client.model,
                    "status": "success"
                }
            }
            
        except Exception as e:
            total_time_ms = int((time.time() - analysis_start_time) * 1000)
            
            logger.error(
                f"Analysis from content failed: error={type(e).__name__}, "
                f"message={str(e)}, duration={total_time_ms}ms",
                exc_info=True
            )
            
            raise
    
    def run_analysis(self, playbook_path: str, protocol_path: str) -> Dict:
        """
        Run complete QA analysis using LLM only.
        
        This method coordinates the workflow:
        1. Load files (no interpretation)
        2. Build prompt (template only)
        3. LLM analysis (all intelligence here)
        4. Return results (structured output)
        
        NO medical validation, NO clinical interpretation, NO content analysis.
        
        Args:
            playbook_path: Path to playbook file (markdown, text, or PDF)
            protocol_path: Path to protocol JSON file
            
        Returns:
            Complete analysis result as dictionary with structure:
            {
                "clinical_extraction": {...},
                "structural_analysis": {...},
                "clinical_alignment": {...},
                "recommendations": [...],
                "quality_scores": {...},
                "metadata": {...}
            }
            
        Raises:
            FileNotFoundError: If input files don't exist
            ValueError: If input files are invalid
            Exception: If LLM analysis fails
            
        Example:
            >>> runner = SimplifiedQARunner()
            >>> result = runner.run_analysis("playbook.md", "protocol.json")
            >>> "clinical_extraction" in result
            True
        """
        analysis_start_time = time.time()
        
        logger.info(
            f"Analysis started: playbook={playbook_path}, "
            f"protocol={protocol_path}"
        )
        
        try:
            # Step 1: Load content (no interpretation)
            load_start = time.time()
            playbook_content = load_playbook(playbook_path) if playbook_path else ""
            protocol_data = load_protocol(protocol_path)
            load_time_ms = int((time.time() - load_start) * 1000)
            
            logger.info(
                f"Content loaded: playbook={len(playbook_content)} chars, "
                f"protocol_nodes={self._count_protocol_nodes(protocol_data)}, "
                f"load_time={load_time_ms}ms"
            )
            
            # Step 2: Build prompt (template assembly only)
            prompt_start = time.time()
            prompt = self.prompt_builder.build_analysis_prompt(
                playbook_content,
                protocol_data
            )
            prompt_time_ms = int((time.time() - prompt_start) * 1000)
            
            logger.info(
                f"Prompt built: size={len(prompt)} chars, "
                f"build_time={prompt_time_ms}ms"
            )
            
            # Step 3: LLM analysis (ALL clinical intelligence here)
            llm_start = time.time()
            analysis_result = self.llm_client.analyze(prompt)
            llm_time_ms = int((time.time() - llm_start) * 1000)
            
            logger.info(
                f"LLM analysis completed: latency={llm_time_ms}ms"
            )
            
            # Step 3.5: Validate LLM response schema
            validation_start = time.time()
            try:
                is_valid, errors = self.validator.validate(analysis_result)
                if not is_valid:
                    raise ValueError(f"LLM response validation failed: {errors}")
                
                # Check completeness
                completeness_ok, warnings = self.validator.validate_completeness(
                    analysis_result,
                    playbook_size=len(playbook_content)
                )
                if warnings:
                    for warning in warnings:
                        logger.warning(f"Completeness warning: {warning}")
                
            except Exception as e:
                logger.error(f"Response validation error: {e}")
                raise
            
            validation_time_ms = int((time.time() - validation_start) * 1000)
            logger.debug(f"Response validated: validation_time={validation_time_ms}ms")
            
            # Step 4: Add metadata (no interpretation)
            total_time_ms = int((time.time() - analysis_start_time) * 1000)
            
            # Ensure metadata exists
            if "metadata" not in analysis_result:
                analysis_result["metadata"] = {}
            
            # Add processing metadata
            analysis_result["metadata"].update({
                "processing_time_ms": total_time_ms,
                "stage_durations_ms": {
                    "load": load_time_ms,
                    "prompt_build": prompt_time_ms,
                    "llm_call": llm_time_ms
                },
                "playbook_size_bytes": len(playbook_content),
                "protocol_nodes_count": self._count_protocol_nodes(protocol_data),
                "timestamp": datetime.now().isoformat(),
                "architecture": "simplified_v2"
            })
            
            # Log completion
            logger.info(
                f"Analysis completed successfully: total_time={total_time_ms}ms, "
                f"entities_extracted={self._count_extracted_entities(analysis_result)}"
            )
            
            return analysis_result
            
        except Exception as e:
            total_time_ms = int((time.time() - analysis_start_time) * 1000)
            
            logger.error(
                f"Analysis failed: error={type(e).__name__}, "
                f"message={str(e)}, duration={total_time_ms}ms",
                exc_info=True
            )
            
            raise
    
    def _count_protocol_nodes(self, protocol_data: Dict) -> int:
        """Count protocol nodes for logging (simple structure traversal)."""
        if isinstance(protocol_data, dict):
            if "nodes" in protocol_data:
                return len(protocol_data["nodes"]) if isinstance(protocol_data["nodes"], list) else 0
            if "protocol_tree" in protocol_data:
                tree = protocol_data["protocol_tree"]
                if isinstance(tree, dict) and "nodes" in tree:
                    return len(tree["nodes"]) if isinstance(tree["nodes"], list) else 0
            if "questions" in protocol_data:
                return len(protocol_data["questions"]) if isinstance(protocol_data["questions"], list) else 0
        return 0
    
    def _count_extracted_entities(self, analysis_result: Dict) -> Dict[str, int]:
        """Count extracted entities for logging (simple counting)."""
        clinical = analysis_result.get("clinical_extraction", {})
        return {
            "syndromes": len(clinical.get("syndromes", [])),
            "exams": len(clinical.get("exams", [])),
            "treatments": len(clinical.get("treatments", [])),
            "red_flags": len(clinical.get("red_flags", []))
        }

