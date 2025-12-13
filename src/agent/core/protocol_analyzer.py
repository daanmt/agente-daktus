"""
Protocol Analyzer - Ferramentas de análise estrutural de protocolos clínicos.

Este módulo contém funções utilitárias para analisar e validar
protocolos JSON, baseadas no relatório técnico de ferramentas Python.

Funções incluídas:
- find_node_by_id: Encontrar node específico
- search_exams: Buscar exames por nome/código
- search_questions: Buscar perguntas por UID
- validate_structure: Métricas estruturais antes/depois
- check_duplicates: Verificar duplicação de IDs
- validate_conditions: Validar sintaxe de condições
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class StructureMetrics:
    """Métricas estruturais de um protocolo."""
    nodes: int = 0
    edges: int = 0
    exams: int = 0
    messages: int = 0
    orientations: int = 0
    questions: int = 0
    clinical_expressions: int = 0


@dataclass
class DuplicateReport:
    """Relatório de duplicatas encontradas."""
    exam_ids: List[str]
    message_ids: List[str]
    question_uids: List[str]
    node_ids: List[str]
    
    @property
    def has_duplicates(self) -> bool:
        return any([
            self.exam_ids,
            self.message_ids,
            self.question_uids,
            self.node_ids
        ])


@dataclass
class ConditionIssue:
    """Problema encontrado em uma condição."""
    type: str  # 'exam', 'message', 'question'
    id: str
    issue: str
    condition: str


class ProtocolAnalyzer:
    """
    Analisador de protocolos clínicos JSON.
    
    Fornece ferramentas para inspeção, busca e validação de protocolos.
    """
    
    def __init__(self, protocol: Dict):
        """
        Inicializa o analisador.
        
        Args:
            protocol: Protocolo JSON carregado
        """
        self.protocol = protocol
        self._conduct_node: Optional[Dict] = None
        self._conduct_idx: Optional[int] = None
    
    # =========================================================================
    # BUSCA E LOCALIZAÇÃO
    # =========================================================================
    
    def find_node_by_id(self, node_id: str) -> Tuple[Optional[Dict], Optional[int]]:
        """
        Encontra node específico por ID.
        
        Args:
            node_id: ID do node a buscar
        
        Returns:
            tuple: (node, index) ou (None, None) se não encontrado
        """
        for i, node in enumerate(self.protocol.get('nodes', [])):
            if node.get('id') == node_id:
                return node, i
        return None, None
    
    def get_conduct_node(self) -> Tuple[Optional[Dict], Optional[int]]:
        """
        Retorna o node de conduta (cached).
        
        Returns:
            tuple: (conduct_node, index)
        """
        if self._conduct_node is None:
            # Tentar encontrar pelo padrão de ID
            for i, node in enumerate(self.protocol.get('nodes', [])):
                node_id = node.get('id', '')
                if node_id.startswith('conduta-') or node.get('type') == 'conduct':
                    self._conduct_node = node
                    self._conduct_idx = i
                    break
        
        return self._conduct_node, self._conduct_idx
    
    def search_exams(
        self,
        search_terms: List[str],
        conduct_node: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca exames no conduct node.
        
        Args:
            search_terms: Lista de termos a buscar (case-insensitive)
            conduct_node: Node de conduta (opcional, usa cached se não fornecido)
        
        Returns:
            Lista de exames encontrados
        """
        if conduct_node is None:
            conduct_node, _ = self.get_conduct_node()
        
        if not conduct_node:
            return []
        
        conduct_data = conduct_node.get('data', {}).get('condutaDataNode', {})
        exams = conduct_data.get('exame', [])
        
        found_exams = []
        for exam in exams:
            nome = exam.get('nome', '').lower()
            codigo = str(exam.get('codigo', '')).lower()
            exam_id = exam.get('id', '').lower()
            
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in nome or term_lower in codigo or term_lower in exam_id:
                    found_exams.append(exam)
                    break
        
        return found_exams
    
    def search_messages(
        self,
        search_terms: List[str],
        conduct_node: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca mensagens no conduct node.
        
        Args:
            search_terms: Lista de termos a buscar
            conduct_node: Node de conduta (opcional)
        
        Returns:
            Lista de mensagens encontradas
        """
        if conduct_node is None:
            conduct_node, _ = self.get_conduct_node()
        
        if not conduct_node:
            return []
        
        conduct_data = conduct_node.get('data', {}).get('condutaDataNode', {})
        messages = conduct_data.get('mensagem', [])
        
        found_messages = []
        for msg in messages:
            nome = msg.get('nome', '').lower()
            conteudo = msg.get('conteudo', '').lower()
            msg_id = msg.get('id', '').lower()
            
            for term in search_terms:
                term_lower = term.lower()
                if term_lower in nome or term_lower in conteudo or term_lower in msg_id:
                    found_messages.append(msg)
                    break
        
        return found_messages
    
    def search_questions(
        self,
        uid: Optional[str] = None,
        text_contains: Optional[str] = None
    ) -> List[Tuple[Dict, Dict]]:
        """
        Busca perguntas em todos os nodes.
        
        Args:
            uid: UID exato da pergunta (opcional)
            text_contains: Texto a buscar no título (opcional)
        
        Returns:
            Lista de (node, question) tuples
        """
        results = []
        
        for node in self.protocol.get('nodes', []):
            questions = node.get('data', {}).get('questions') or []
            
            for q in questions:
                match = False
                
                if uid and q.get('uid') == uid:
                    match = True
                
                if text_contains:
                    titulo = q.get('titulo', '').lower()
                    if text_contains.lower() in titulo:
                        match = True
                
                if match:
                    results.append((node, q))
        
        return results
    
    def search_clinical_expressions(
        self,
        search_terms: List[str]
    ) -> List[Dict]:
        """
        Busca expressões clínicas em todos os nodes.
        
        Args:
            search_terms: Termos a buscar (nomes de scores, etc)
        
        Returns:
            Lista de expressões encontradas com info do node
        """
        found = []
        
        for node in self.protocol.get('nodes', []):
            expressions = node.get('data', {}).get('clinicalExpressions', [])
            
            for expr in expressions:
                name = expr.get('name', '').lower()
                desc = expr.get('description', '').lower()
                
                for term in search_terms:
                    term_lower = term.lower()
                    if term_lower in name or term_lower in desc:
                        found.append({
                            'node_id': node.get('id'),
                            'expression': expr,
                            'matched_term': term
                        })
                        break
        
        return found
    
    # =========================================================================
    # VALIDAÇÃO ESTRUTURAL
    # =========================================================================
    
    def validate_structure(self, label: str = "Current") -> StructureMetrics:
        """
        Valida e conta elementos estruturais do protocolo.
        
        Args:
            label: Rótulo para logging (ex: "ANTES", "DEPOIS")
        
        Returns:
            StructureMetrics com contagens
        """
        metrics = StructureMetrics(
            nodes=len(self.protocol.get('nodes', [])),
            edges=len(self.protocol.get('edges', []))
        )
        
        for node in self.protocol.get('nodes', []):
            data = node.get('data', {})
            
            # Contar conduct items
            conduct_data = data.get('condutaDataNode', {})
            if conduct_data:
                metrics.exams += len(conduct_data.get('exame', []))
                metrics.messages += len(conduct_data.get('mensagem', []))
                metrics.orientations += len(conduct_data.get('orientacao', []))
            
            # Contar questions
            q_list = data.get('questions') or []
            metrics.questions += len(q_list)
            
            # Contar clinical expressions
            metrics.clinical_expressions += len(data.get('clinicalExpressions', []))
        
        logger.info(
            f"Structure [{label}]: nodes={metrics.nodes}, edges={metrics.edges}, "
            f"exams={metrics.exams}, messages={metrics.messages}, "
            f"questions={metrics.questions}"
        )
        
        return metrics
    
    def check_duplicates(self) -> DuplicateReport:
        """
        Verifica duplicação de IDs em todo o protocolo.
        
        Returns:
            DuplicateReport com listas de IDs duplicados
        """
        report = DuplicateReport(
            exam_ids=[],
            message_ids=[],
            question_uids=[],
            node_ids=[]
        )
        
        # Check node IDs
        node_ids = [n.get('id') for n in self.protocol.get('nodes', [])]
        seen = set()
        for nid in node_ids:
            if nid in seen:
                report.node_ids.append(nid)
            seen.add(nid)
        
        # Check conduct items
        for node in self.protocol.get('nodes', []):
            conduct_data = node.get('data', {}).get('condutaDataNode', {})
            
            if conduct_data:
                # Exams
                exam_ids = [e.get('id') for e in conduct_data.get('exame', [])]
                seen_exams = set()
                for eid in exam_ids:
                    if eid in seen_exams:
                        report.exam_ids.append(eid)
                    seen_exams.add(eid)
                
                # Messages
                msg_ids = [m.get('id') for m in conduct_data.get('mensagem', [])]
                seen_msgs = set()
                for mid in msg_ids:
                    if mid in seen_msgs:
                        report.message_ids.append(mid)
                    seen_msgs.add(mid)
            
            # Questions
            questions = node.get('data', {}).get('questions') or []
            q_uids = [q.get('uid') for q in questions if isinstance(q, dict)]
            seen_q = set()
            for quid in q_uids:
                if quid in seen_q:
                    report.question_uids.append(quid)
                seen_q.add(quid)
        
        if report.has_duplicates:
            logger.warning(f"Duplicates found: {report}")
        else:
            logger.info("No duplicates found")
        
        return report
    
    def validate_conditions(self) -> List[ConditionIssue]:
        """
        Valida sintaxe de condições em exames/mensagens/perguntas.
        
        Returns:
            Lista de ConditionIssue com problemas encontrados
        """
        issues = []
        
        for node in self.protocol.get('nodes', []):
            # Check conduct conditions
            conduct_data = node.get('data', {}).get('condutaDataNode', {})
            
            if conduct_data:
                # Exams
                for exam in conduct_data.get('exame', []):
                    cond = exam.get('condicao', '')
                    if cond:
                        issue = self._validate_condition_syntax(cond)
                        if issue:
                            issues.append(ConditionIssue(
                                type='exam',
                                id=exam.get('id', 'unknown'),
                                issue=issue,
                                condition=cond
                            ))
                
                # Messages
                for msg in conduct_data.get('mensagem', []):
                    cond = msg.get('condicao', '')
                    if cond:
                        issue = self._validate_condition_syntax(cond)
                        if issue:
                            issues.append(ConditionIssue(
                                type='message',
                                id=msg.get('id', 'unknown'),
                                issue=issue,
                                condition=cond
                            ))
            
            # Questions
            questions = node.get('data', {}).get('questions') or []
            for q in questions:
                if not isinstance(q, dict):
                    continue
                expr = q.get('expressao', '')
                if expr:
                    issue = self._validate_condition_syntax(expr)
                    if issue:
                        issues.append(ConditionIssue(
                            type='question',
                            id=q.get('uid', 'unknown'),
                            issue=issue,
                            condition=expr
                        ))
        
        if issues:
            logger.warning(f"Found {len(issues)} condition issues")
        else:
            logger.info("All conditions validated")
        
        return issues
    
    def _validate_condition_syntax(self, condition: str) -> Optional[str]:
        """
        Valida sintaxe de uma condição.
        
        Args:
            condition: String da condição a validar
        
        Returns:
            Mensagem de erro ou None se válida
        """
        # Check for = instead of ==
        if re.search(r'[^!=<>]=[^=]', condition):
            return "Possível uso de = ao invés de =="
        
        # Check for missing quotes in 'in' expressions
        if re.search(r'\b\w+\s+in\s+\w+\b', condition):
            # Verificar se tem aspas antes do 'in'
            if not re.search(r"['\"][\w]+['\"]\s+in\s+", condition):
                return "Possível falta de aspas em expressão 'in'"
        
        # Check for uppercase AND/OR (should be lowercase)
        if re.search(r'\b(AND|OR)\b', condition):
            return "Uso de AND/OR em maiúsculas (deve ser and/or)"
        
        return None
    
    # =========================================================================
    # ANÁLISE DE VIÉS
    # =========================================================================
    
    def analyze_message_bias(
        self,
        keywords_list: List[str],
        conduct_node: Optional[Dict] = None
    ) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
        """
        Analisa viés de mensagens (ex: PS vs ambulatorial).
        
        Args:
            keywords_list: Lista de keywords a buscar
            conduct_node: Node de conduta (opcional)
        
        Returns:
            (keyword_counts, found_message_ids)
        """
        if conduct_node is None:
            conduct_node, _ = self.get_conduct_node()
        
        if not conduct_node:
            return {}, {}
        
        conduct_data = conduct_node.get('data', {}).get('condutaDataNode', {})
        messages = conduct_data.get('mensagem', [])
        
        keyword_counts = {kw: 0 for kw in keywords_list}
        found_messages = {kw: [] for kw in keywords_list}
        
        for msg in messages:
            conteudo = msg.get('conteudo', '').lower()
            nome = msg.get('nome', '').lower()
            
            for kw in keywords_list:
                if kw.lower() in conteudo or kw.lower() in nome:
                    keyword_counts[kw] += 1
                    found_messages[kw].append(msg.get('id', 'unknown'))
        
        return keyword_counts, found_messages
    
    # =========================================================================
    # COMPARAÇÃO ANTES/DEPOIS
    # =========================================================================
    
    def compare_metrics(
        self,
        before: StructureMetrics,
        after: StructureMetrics
    ) -> Dict[str, int]:
        """
        Compara métricas antes e depois de modificações.
        
        Args:
            before: Métricas antes
            after: Métricas depois
        
        Returns:
            Dict com diferenças (campo -> diferença)
        """
        diffs = {}
        
        for field in ['nodes', 'edges', 'exams', 'messages', 'orientations', 'questions']:
            before_val = getattr(before, field, 0)
            after_val = getattr(after, field, 0)
            diff = after_val - before_val
            
            if diff != 0:
                diffs[field] = diff
                logger.info(f"  {field}: {before_val} → {after_val} ({diff:+d})")
        
        return diffs


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def analyze_protocol(protocol: Dict) -> Dict[str, Any]:
    """
    Executa análise completa do protocolo.
    
    Args:
        protocol: Protocolo JSON
    
    Returns:
        Dict com métricas, duplicatas e issues
    """
    analyzer = ProtocolAnalyzer(protocol)
    
    metrics = analyzer.validate_structure("Analysis")
    duplicates = analyzer.check_duplicates()
    condition_issues = analyzer.validate_conditions()
    
    return {
        "metrics": metrics,
        "duplicates": duplicates,
        "condition_issues": condition_issues,
        "has_issues": duplicates.has_duplicates or len(condition_issues) > 0
    }
