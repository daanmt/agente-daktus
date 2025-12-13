"""
Protocol Models - Modelos Pydantic para validação de protocolos clínicos.

Este módulo define os modelos de validação de estrutura de protocolos.

IMPORTANTE: Estes modelos devem ser FLEXÍVEIS o suficiente para aceitar
os formatos reais dos protocolos Daktus, que usam:
- IDs com UUID (não apenas node-\d+)
- Tipos customizados (custom, summary, conduct, não apenas question/decision/action/end)
- Estruturas de data variáveis (nem todos têm questions)

Versão: 2.0.0 - Flexibilizado para formatos reais
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Optional, Any


class Position(BaseModel):
    """Posição de um nó no canvas."""
    x: float
    y: float


class QuestionOption(BaseModel):
    """Opção de uma pergunta select/multiselect."""
    id: str
    label: str
    value: Optional[str] = None


class Question(BaseModel):
    """
    Pergunta em um nó.
    
    NOTA: Os campos obrigatórios foram flexibilizados porque os protocolos
    reais usam estruturas variadas.
    """
    id: str
    uid: Optional[str] = None  # Pode não existir em alguns formatos
    titulo: Optional[str] = None  # Nome alternativo para question
    tipo: Optional[str] = None  # Nome alternativo para type
    type: Optional[str] = None  # Tipo da pergunta
    question: Optional[str] = None  # Texto da pergunta
    options: Optional[List[Any]] = None  # Opções (pode ter formato variado)
    expressao: Optional[str] = None  # Conditional visibility
    opcional: Optional[bool] = None  # Campo opcional
    
    model_config = {"extra": "allow"}  # Permitir campos extras


class NodeData(BaseModel):
    """
    Dados de um nó.
    
    NOTA: Flexibilizado - nem todos os nós têm questions (ex: summary, conduct).
    """
    label: Optional[str] = None  # Label do nó
    descricao: Optional[str] = None  # Descrição (opcional)
    condicao: Optional[str] = None  # Condição de visibilidade
    questions: Optional[List[Any]] = None  # Questions (opcional - summary nodes não têm)
    condutaDataNode: Optional[Dict[str, Any]] = None  # Para nós de conduta
    clinicalExpressions: Optional[List[Any]] = None  # Expressões clínicas
    templateMarkdown: Optional[str] = None  # Para summary nodes
    
    model_config = {"extra": "allow"}  # Permitir campos extras


class ProtocolNode(BaseModel):
    """
    Nó do protocolo.
    
    NOTA: Aceita qualquer formato de ID e tipo, pois protocolos Daktus usam:
    - IDs como: node-219cf8a0-e2da-..., conduta-1234567890, summary-xxx
    - Tipos como: custom, summary, conduct (não apenas question/decision)
    """
    id: str  # Qualquer string é aceita
    type: str  # Qualquer tipo é aceito (custom, summary, conduct, etc.)
    position: Position
    data: NodeData
    
    model_config = {"extra": "allow"}


class Edge(BaseModel):
    """
    Aresta entre nós.
    
    NOTA: Aceita qualquer formato de source/target.
    """
    id: str
    source: str  # Qualquer string é aceita
    target: str  # Qualquer string é aceita
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    
    model_config = {"extra": "allow"}


class ProtocolMetadata(BaseModel):
    """Metadados do protocolo."""
    company: str
    name: str
    version: str  # Sem regex restritivo
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    lastModified: Optional[str] = None  # Formato alternativo
    changes: Optional[str] = None  # Descrição de mudanças
    
    model_config = {"extra": "allow"}


class Protocol(BaseModel):
    """
    Protocolo completo.
    
    Validação MÍNIMA - apenas garante estrutura básica.
    Validação detalhada é feita por outras funções quando necessário.
    """
    metadata: ProtocolMetadata
    nodes: List[ProtocolNode] = Field(..., min_length=1)
    edges: List[Edge] = []
    
    model_config = {"extra": "allow"}
    
    @model_validator(mode='after')
    def validate_edges_reference_existing_nodes(self):
        """Valida que edges referenciam nós existentes."""
        node_ids = {n.id for n in self.nodes}
        
        for edge in self.edges:
            if edge.source not in node_ids:
                raise ValueError(f"Edge references non-existent source node: {edge.source}")
            if edge.target not in node_ids:
                raise ValueError(f"Edge references non-existent target node: {edge.target}")
        
        return self
    
    @field_validator('nodes')
    @classmethod
    def validate_unique_node_ids(cls, v):
        """Valida que não há IDs duplicados."""
        ids = [n.id for n in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate node IDs")
        return v
