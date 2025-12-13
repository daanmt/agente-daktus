"""
Suggestion Validator - Valida sugestões antes de apresentar ao usuário.

Este módulo filtra sugestões com antipadrões e duplicatas para
garantir qualidade das análises.

Problema resolvido:
- Sugestões de "alertas genéricos" sem especificação
- Sugestões duplicadas
- Falta de campos obrigatórios em sugestões de segurança

Solução:
- Validar antipadrões antes de apresentar
- Remover duplicatas por título normalizado
- Verificar campos obrigatórios
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado da validação de uma sugestão."""
    is_valid: bool
    error_message: str = ""
    warning_message: str = ""


class SuggestionValidator:
    """
    Valida sugestões antes de apresentar ao usuário.
    
    Detecta antipadrões, verifica campos obrigatórios e remove duplicatas.
    """
    
    # Antipadrões em sugestões de alerta - termos genéricos a evitar
    ALERT_ANTIPATTERNS = [
        "alerta visual",
        "bloqueio de conduta",
        "alerta crítico",
        "implementar aviso",
        "criar alerta",
        "adicionar alerta de alta prioridade",
        "alerta proeminente",
        "aviso crítico",
        "bloqueio até",
        "garantir bloqueio",
        "alerta e bloqueio",
    ]
    
    # Campos obrigatórios para sugestões de segurança bem especificadas
    SECURITY_REQUIRED_FIELDS = [
        "specific_location",
        "implementation_path",
    ]
    
    # Campos obrigatórios dentro de implementation_path
    IMPLEMENTATION_PATH_FIELDS = [
        "json_path",
        "modification_type",
        "proposed_value",
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Inicializa o validador.
        
        Args:
            strict_mode: Se True, rejeita sugestões com antipadrões mesmo 
                        que tenham campos obrigatórios. Se False, apenas 
                        verifica se campos obrigatórios estão presentes.
        """
        self.strict_mode = strict_mode
        self._validation_stats = {
            "total_validated": 0,
            "passed": 0,
            "failed_antipattern": 0,
            "failed_missing_fields": 0,
            "duplicates_removed": 0,
        }
    
    def validate_suggestion(self, suggestion: Dict) -> ValidationResult:
        """
        Valida uma sugestão individual.
        
        Args:
            suggestion: Dicionário com dados da sugestão
        
        Returns:
            ValidationResult com status e mensagens
        """
        self._validation_stats["total_validated"] += 1
        
        category = suggestion.get("category", "").lower()
        title = suggestion.get("title", "")
        description = suggestion.get("description", "")
        
        # Se não é sugestão de segurança, aceitar sem validação adicional
        if category != "seguranca":
            self._validation_stats["passed"] += 1
            return ValidationResult(is_valid=True)
        
        # Verificar antipadrões em título e descrição
        text_to_check = f"{title} {description}".lower()
        
        for antipattern in self.ALERT_ANTIPATTERNS:
            if antipattern in text_to_check:
                # Encontrou antipadrão - verificar se tem campos obrigatórios
                has_required_fields = self._has_required_fields(suggestion)
                
                if not has_required_fields:
                    self._validation_stats["failed_antipattern"] += 1
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Sugestão de alerta genérica sem especificação de implementação. "
                                     f"Antipadrão detectado: '{antipattern}'. "
                                     f"Deve incluir: specific_location, implementation_path com proposed_value"
                    )
                
                # Tem antipadrão mas tem campos - aceitar com warning
                if not self.strict_mode:
                    self._validation_stats["passed"] += 1
                    return ValidationResult(
                        is_valid=True,
                        warning_message=f"Sugestão usa termo genérico '{antipattern}' mas tem especificação completa"
                    )
                else:
                    self._validation_stats["failed_antipattern"] += 1
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Modo estrito: antipadrão '{antipattern}' detectado"
                    )
        
        # Sugestão de segurança sem antipadrão - verificar campos
        if not self._has_required_fields(suggestion):
            self._validation_stats["failed_missing_fields"] += 1
            return ValidationResult(
                is_valid=False,
                error_message="Sugestão de segurança sem campos obrigatórios: "
                             "specific_location, implementation_path"
            )
        
        # Sugestão válida
        self._validation_stats["passed"] += 1
        return ValidationResult(is_valid=True)
    
    def _has_required_fields(self, suggestion: Dict) -> bool:
        """
        Verifica se sugestão tem campos obrigatórios para implementação.
        
        Args:
            suggestion: Dicionário com dados da sugestão
        
        Returns:
            True se tem todos os campos obrigatórios
        """
        # Verificar specific_location
        if "specific_location" not in suggestion:
            return False
        
        # Verificar implementation_path
        if "implementation_path" not in suggestion:
            return False
        
        impl_path = suggestion.get("implementation_path", {})
        if not isinstance(impl_path, dict):
            return False
        
        # Verificar campos dentro de implementation_path
        for field in self.IMPLEMENTATION_PATH_FIELDS:
            if field not in impl_path:
                return False
        
        # Verificar proposed_value tem estrutura mínima
        proposed_value = impl_path.get("proposed_value", {})
        if not isinstance(proposed_value, dict):
            return False
        
        # Se é mensagem/orientação, deve ter conteúdo HTML
        mod_type = impl_path.get("modification_type", "")
        if mod_type in ["add_message", "add_orientation"]:
            if "conteudo" not in proposed_value:
                return False
        
        return True
    
    def filter_duplicates(self, suggestions: List[Dict]) -> List[Dict]:
        """
        Remove sugestões duplicadas baseado em título normalizado.
        
        Args:
            suggestions: Lista de sugestões
        
        Returns:
            Lista sem duplicatas
        """
        seen_titles = set()
        filtered = []
        duplicates_found = 0
        
        for sug in suggestions:
            # Normalizar título
            title = sug.get("title", "").strip().lower()
            
            # Remover pontuação e espaços extras para comparação
            title_normalized = " ".join(title.split())
            
            if title_normalized and title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                filtered.append(sug)
            else:
                duplicates_found += 1
                logger.debug(f"Duplicate suggestion removed: {title[:50]}...")
        
        self._validation_stats["duplicates_removed"] += duplicates_found
        
        if duplicates_found > 0:
            logger.info(f"Removed {duplicates_found} duplicate suggestions")
        
        return filtered
    
    def validate_and_filter(self, suggestions: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Valida e filtra lista de sugestões.
        
        Args:
            suggestions: Lista de sugestões a validar
        
        Returns:
            (valid_suggestions, rejected_suggestions)
        """
        # Primeiro remover duplicatas
        unique_suggestions = self.filter_duplicates(suggestions)
        
        valid = []
        rejected = []
        
        for sug in unique_suggestions:
            result = self.validate_suggestion(sug)
            
            if result.is_valid:
                # Adicionar warning como campo se houver
                if result.warning_message:
                    sug["_validation_warning"] = result.warning_message
                valid.append(sug)
            else:
                # Adicionar motivo da rejeição
                sug["_rejection_reason"] = result.error_message
                rejected.append(sug)
        
        # Log resumo
        if rejected:
            logger.warning(
                f"Suggestion validation: {len(valid)} passed, {len(rejected)} rejected"
            )
            for r in rejected[:5]:  # Log primeiras 5
                logger.warning(
                    f"  Rejected: {r.get('title', 'N/A')[:50]}... - "
                    f"{r.get('_rejection_reason', 'Unknown reason')}"
                )
        
        return valid, rejected
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas de validação.
        
        Returns:
            Dicionário com contadores de validação
        """
        return self._validation_stats.copy()
    
    def reset_stats(self) -> None:
        """Reseta estatísticas de validação."""
        self._validation_stats = {
            "total_validated": 0,
            "passed": 0,
            "failed_antipattern": 0,
            "failed_missing_fields": 0,
            "duplicates_removed": 0,
        }


def filter_suggestions_before_presentation(
    suggestions: List[Dict],
    strict_mode: bool = False
) -> List[Dict]:
    """
    Função de conveniência para filtrar sugestões antes de apresentar.
    
    Remove duplicatas e sugestões com antipadrões sem especificação.
    
    Args:
        suggestions: Lista de sugestões a filtrar
        strict_mode: Se True, rejeita qualquer antipadrão
    
    Returns:
        Lista de sugestões válidas
    """
    validator = SuggestionValidator(strict_mode=strict_mode)
    valid, rejected = validator.validate_and_filter(suggestions)
    
    stats = validator.get_stats()
    logger.info(
        f"Suggestion filtering complete: "
        f"{stats['passed']} valid, "
        f"{stats['duplicates_removed']} duplicates removed, "
        f"{stats['failed_antipattern'] + stats['failed_missing_fields']} rejected"
    )
    
    return valid
