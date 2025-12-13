"""
Wave 1 Tests - Clinical Safety Foundations
Testes para validadores AST Logic e LLM Contract
"""
import sys
from unittest.mock import MagicMock

# =============================================================================
# MOCK SETUP - Must be before any src.agent imports
# =============================================================================

# Create a proper mock for logger that behaves like a logger
logger_mock = MagicMock()
logger_mock.debug = MagicMock()
logger_mock.info = MagicMock()
logger_mock.warning = MagicMock()
logger_mock.error = MagicMock()

# Mock the entire src.agent.core module hierarchy
agent_core_mock = MagicMock()
agent_core_mock.logger = logger_mock
sys.modules['src.agent.core'] = agent_core_mock
sys.modules['src.agent.core.logger'] = MagicMock(logger=logger_mock)

# Patch the logger attribute directly 
import types
logger_module = types.ModuleType('src.agent.core.logger')
logger_module.logger = logger_mock
sys.modules['src.agent.core.logger'] = logger_module

# Mock config modules
config_mock = MagicMock()
config_mock.__path__ = []
sys.modules['config'] = config_mock
sys.modules['config.prompts'] = MagicMock()
sys.modules['src.config'] = config_mock
sys.modules['src.config.prompts'] = MagicMock()

# Mock LLM client
sys.modules['src.agent.core.llm_client'] = MagicMock()

# =============================================================================
# Now import the actual modules we want to test
# =============================================================================
import unittest
from pydantic import ValidationError

from src.agent.validators.logic_validator import (
    ConditionalExpressionValidator, 
    validate_protocol_conditionals
)
from src.agent.validators.llm_contract import EnhancedAnalysisResponse


class TestLogicValidator(unittest.TestCase):
    """Testes para o validador de expressões condicionais (AST-based)."""
    
    def test_safe_expression_passes(self):
        """Expressões seguras devem passar validação."""
        # Note: Constructor uses valid_uids and valid_option_ids
        validator = ConditionalExpressionValidator(
            valid_uids={"symptom_x", "age", "gender"},
            valid_option_ids={"yes", "no", "male", "female"}
        )
        
        # Expressões válidas
        safe_expressions = [
            "'yes' in symptom_x",
            "age > 18",
            "symptom_x == 'yes' and age > 18",
        ]
        
        for expr in safe_expressions:
            is_valid, warnings = validator.validate(expr)
            self.assertTrue(is_valid, f"Expression should be valid: {expr}. Errors: {warnings}")
    
    def test_unknown_uid_generates_warning(self):
        """Referências a UIDs desconhecidos geram warnings."""
        validator = ConditionalExpressionValidator(
            valid_uids={"symptom_x"},
            valid_option_ids={"yes"}
        )
        
        # Unknown UID generates warning, not error (is_valid=True, but warnings)
        is_valid, warnings = validator.validate("unknown_uid == 'yes'")
        # Syntax is valid, but unknown_uid generates warning
        self.assertTrue(is_valid)  # Syntax OK
        self.assertTrue(len(warnings) > 0)  # But has warnings
        self.assertTrue(any("unknown" in w.lower() for w in warnings))
    
    def test_dangerous_code_blocked(self):
        """Código perigoso (injection) deve ser bloqueado."""
        validator = ConditionalExpressionValidator(
            valid_uids=set(),
            valid_option_ids=set()
        )
        
        dangerous_inputs = [
            ("exec('print(1)')", "exec call"),
            ("eval('1+1')", "eval call"),
            ("open('/etc/passwd')", "open call"),
        ]
        
        for expr, desc in dangerous_inputs:
            is_valid, errors = validator.validate(expr)
            self.assertFalse(is_valid, f"Should block {desc}: {expr}")
    
    def test_empty_expression_passes(self):
        """Expressão vazia deve passar."""
        validator = ConditionalExpressionValidator(
            valid_uids=set(),
            valid_option_ids=set()
        )
        
        is_valid, warnings = validator.validate("")
        self.assertTrue(is_valid)
        self.assertEqual(len(warnings), 0)


class TestLLMContract(unittest.TestCase):
    """Testes para validação do contrato LLM."""
    
    def get_valid_suggestion(self, **overrides):
        """Helper para criar sugestão válida."""
        suggestion = {
            "id": "sug_001",
            "category": "seguranca",
            "priority": "alta",
            "title": "Adicionar validação de alergia",
            "description": "Descrição detalhada da sugestão",
            "rationale": "Justificativa baseada em evidências",
            "impact_scores": {"seguranca": 9, "economia": 5},
            "evidence": {
                "playbook_reference": "Seção 4.2, página 45: 'Sempre verificar histórico de alergias'"
            },
            "implementation_effort": {"complexity": "baixa"},
            "auto_apply_cost_estimate": {"tokens": 100},
            "specific_location": {"node_id": "node-1", "question_uid": "medication"}
        }
        suggestion.update(overrides)
        return suggestion
    
    def test_valid_response_parses(self):
        """Resposta LLM válida deve parsear corretamente."""
        llm_output = {
            "improvement_suggestions": [self.get_valid_suggestion()],
            "metadata": {"analysis_version": "3.0"}
        }
        
        resp = EnhancedAnalysisResponse(**llm_output)
        self.assertEqual(len(resp.improvement_suggestions), 1)
        self.assertEqual(resp.improvement_suggestions[0].priority, "alta")
    
    def test_generic_reference_rejected(self):
        """Referências genéricas de playbook devem ser rejeitadas."""
        generic_ref = "Based on general medical knowledge"
        
        llm_output = {
            "improvement_suggestions": [
                self.get_valid_suggestion(
                    evidence={"playbook_reference": generic_ref}
                )
            ],
            "metadata": {"analysis_version": "3.0"}
        }
        
        with self.assertRaises(ValidationError):
            EnhancedAnalysisResponse(**llm_output)


class TestProtocolConditionals(unittest.TestCase):
    """Testes de integração para validação de condicionais em protocolos."""
    
    def get_minimal_protocol(self):
        """Protocolo mínimo para testes."""
        return {
            "metadata": {
                "company": "Test",
                "name": "Test Protocol",
                "version": "1.0.0"
            },
            "nodes": [
                {
                    "id": "node-1",
                    "type": "custom",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "questions": [
                            {
                                "uid": "symptom_fever",
                                "nome": "Febre?",
                                "tipo": "select",
                                "options": [
                                    {"id": "sim", "label": "Sim"},
                                    {"id": "nao", "label": "Não"}
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "node-2",
                    "type": "conduct",
                    "position": {"x": 200, "y": 0},
                    "data": {
                        "condicao": "'sim' in symptom_fever"
                    }
                }
            ],
            "edges": []
        }
    
    def test_valid_conditional_passes(self):
        """Condicional válida deve passar."""
        protocol = self.get_minimal_protocol()
        is_valid, errors = validate_protocol_conditionals(protocol)
        self.assertTrue(is_valid, f"Should pass. Errors: {errors}")
    
    def test_dangerous_conditional_fails(self):
        """Condicional com código perigoso deve falhar."""
        protocol = self.get_minimal_protocol()
        protocol["nodes"][1]["data"]["condicao"] = "exec('rm -rf /')"
        
        is_valid, errors = validate_protocol_conditionals(protocol)
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)


if __name__ == '__main__':
    unittest.main()
