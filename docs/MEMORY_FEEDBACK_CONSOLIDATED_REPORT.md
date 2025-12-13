# 🔴 RELATÓRIO CONSOLIDADO: Sistema de Memória & Feedback

**Data**: 2025-12-11  
**Para**: Claude Code (continuação da implementação)  
**Contexto**: Sistema de aprendizado não está funcionando efetivamente  
**Prioridade**: CRÍTICA  

---

## 📊 SUMÁRIO EXECUTIVO

### Problema Central
O agente **não aprende efetivamente** com o feedback do usuário, resultando em:
- ❌ Sugestões rejeitadas continuam reaparecendo
- ❌ Desperdício de 40-60% dos tokens em sugestões irrelevantes
- ❌ Usuário revisa os mesmos erros repetidamente
- ❌ ROI do sistema degradando ao longo do tempo

### Estado Atual (Dev History Review)
**Waves Completas** (segundo roadmap.md):
- ✅ Wave 1: Clinical Safety Foundations (Pydantic, AST validation, LLM contracts)
- ✅ Wave 2: Memory & Learning (declarado completo, mas COM BUGS)
- ✅ Wave 3: Observability & Cost Control (cost tracking, audit reports)

**Discrepância Identificada**:
O roadmap declara Wave 2 completa, mas `proud-seeking-newt.md` documenta **3 bugs críticos** que quebram o learning loop:

1. **Reconstruction Display Bug** - Mudanças mostram "N/A" em vez de valores reais
2. **Learning System Not Working** - Padrões de rejeição não são aplicados
3. **Feedback UX Too Complex** - 7 opções confundem usuário (deve ser 3)

---

## 🔍 ANÁLISE DETALHADA DOS PROBLEMAS

### Problema 1: Reconstruction Display Bug

**Sintoma**:
```
MUDANÇAS APLICADAS
~ MODIFIED: N/A
  N/A
```

**Causa Raiz** (proud-seeking-newt.md):
```python
# Producer (protocol_reconstructor.py:366-395)
changes.append({
    "suggestion_id": ...,  # ❌ Chave errada
    "title": ...,          # ❌ Chave errada
})

# Consumer (display_manager.py:254-310)
change_type = change.get("type", "modified")  # ✅ Chave esperada
location = change.get("location", "N/A")      # ✅ Chave esperada
```

**Status**: 🔴 NÃO CORRIGIDO (não encontrado em dev_history.md)

**Impacto**: Usuário não vê quais mudanças foram aplicadas → zero confiança

**Localização para Claude Code**:
- `src/agent/applicator/protocol_reconstructor.py` (linhas 366-395)
- `src/agent/cli/display_manager.py` (linhas 254-310)

---

### Problema 2: Learning System Not Working (CRÍTICO)

**Sintoma**: Sugestões rejeitadas continuam reaparecendo

**4 Causas Raízes Identificadas**:

#### 2.1 Threshold Muito Alto
```python
# enhanced.py:335
active_filters = self.memory_qa.get_active_filters(min_frequency=3)
# Pattern com frequency=1 é IGNORADO porque 1 < 3
```

**Status**: 🟡 PARCIALMENTE CORRIGIDO
- Roadmap menciona "Threshold=1 para ativação imediata" (linha 45)
- Mas proud-seeking-newt.md indica que ainda está em 3
- **Verificação necessária**: Claude Code deve confirmar o valor atual

#### 2.2 Filtros Não Sempre no Prompt
```python
# enhanced.py:335-340
filter_instructions = self._build_filter_instructions(active_filters)
# ❌ Construído mas NEM SEMPRE incluído no prompt
```

**Status**: 🔴 NÃO CORRIGIDO

#### 2.3 Post-Filtering Apenas por Keywords
```python
# enhanced.py:581-684
if keyword.lower() in text_to_check:  # ❌ Busca literal apenas
    should_keep = False

# Blocklist: ["desnecessário", "redundante", "irrelevante"]
# Padrão "médico deve ter opção de prescrever" → NÃO DETECTADO
```

**Status**: 🔴 NÃO CORRIGIDO

#### 2.4 Relatórios EDITED Não São Usados
```
Fluxo Atual (QUEBRADO):
┌─────────────────────────────────────────────────┐
│ Análise 1 → Feedback → EDITED report gerado   │
│                            ↓                    │
│ Análise 2 usa ORIGINAL (❌) não EDITED (✅)    │
└─────────────────────────────────────────────────┘
```

**Status**: 🔴 NÃO CORRIGIDO

**Impacto Combinado**: Sistema não aprende, desperdiça tokens, frustra usuário

---

### Problema 3: Feedback UX Too Complex

**Atual**: 7 opções (S/N/E/C/P/Q)  
**Necessário**: 3 opções (Relevante/Irrelevante/Sair)

**Status**: 🔴 NÃO CORRIGIDO

**Localização para Claude Code**:
- `src/agent/feedback/feedback_collector.py` (linhas 150-250)

---

## 🏗️ ARQUITETURA: Estado Atual vs Desejado

### Estado Atual (Arquivos que DEVEM Existir segundo Roadmap)

**Wave 2 - Memory & Learning (declarado completo)**:
```
src/agent/learning/
├── rules_engine.py         # ❓ Existência a verificar
├── feedback_learner.py     # ❓ Existência a verificar
└── models.py               # ❓ Não mencionado

src/agent/validators/
└── reference_validator.py  # ❓ Existência a verificar

src/agent/applicator/
└── change_verifier.py      # ❓ Existência a verificar
```

**Ações para Claude Code**:
1. Verificar se estes arquivos existem
2. Se existem, verificar se têm bugs de implementação
3. Se não existem, criar conforme especificação deste relatório

---

### Estado Desejado (Arquitetura Completa)

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENTE DAKTUS QA                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              MEMORY & LEARNING SYSTEM                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Layer 1: HARD RULES (Blocking)                       │  │
│  │ - Reference whitelist (playbook only)                │  │
│  │ - Structural constraints (JSON schema)               │  │
│  │ - Forbidden patterns (autonomy invasion)             │  │
│  │ → BLOQUEIA antes de gerar sugestão                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Layer 2: SOFT RULES (Filtering)                      │  │
│  │ - Pattern-based filters (semantic matching)          │  │
│  │ - Confidence scoring                                 │  │
│  │ → FILTRA sugestões geradas                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Layer 3: LEARNING CORPUS (Context)                   │  │
│  │ - Historical feedback (memory_qa.md)                 │  │
│  │ - Best practices                                     │  │
│  │ → ENRIQUECE contexto do LLM                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 PLANO DE AÇÃO PARA CLAUDE CODE

### FASE 0: Verificação e Emergency Fixes (2-4 horas)

#### Tarefa 0.1: Auditoria de Arquivos
```bash
# Verificar existência dos arquivos Wave 2
ls -la src/agent/learning/
ls -la src/agent/validators/
ls -la src/agent/applicator/change_verifier.py

# Se não existirem, criar estrutura base
mkdir -p src/agent/learning
mkdir -p src/agent/validators
```

#### Tarefa 0.2: Fix #1 - Reconstruction Display
**Arquivo**: `src/agent/applicator/protocol_reconstructor.py`  
**Linhas**: 366-395

**Mudança**:
```python
# ANTES:
changes.append({
    "suggestion_id": sug.get("id", "N/A"),
    "title": sug.get("title", "N/A"),
    "category": sug.get("category", "N/A"),
    "status": "applied"
})

# DEPOIS:
changes.append({
    "type": "modified",  # ou determinar do tipo de mudança
    "location": f"Node: {node_id} | Question: {question_uid}",
    "description": sug.get('description', sug.get('title', 'N/A'))[:200]
})
```

**Teste**:
```bash
# Executar reconstrução
python run_agent.py

# Verificar que "MUDANÇAS APLICADAS" mostra valores reais
# NÃO deve mostrar "N/A"
```

---

#### Tarefa 0.3: Fix #2.1 - Lower Threshold
**Arquivo**: `src/agent/analysis/enhanced.py`  
**Linha**: 335

**Mudança**:
```python
# ANTES:
active_filters = self.memory_qa.get_active_filters(min_frequency=3)

# DEPOIS:
min_freq = int(os.getenv("MEMORY_MIN_FREQUENCY", "1"))
active_filters = self.memory_qa.get_active_filters(min_frequency=min_freq)
```

**Verificação**:
```python
# Após feedback negativo, verificar memory_qa.md
# Pattern deve ter frequency=1
# E na próxima análise, active_filters deve incluí-lo
```

---

#### Tarefa 0.4: Fix #2.2 - Garantir Filtros no Prompt
**Arquivo**: `src/agent/analysis/enhanced.py`  
**Linhas**: 368-371

**Mudança**:
```python
# ANTES (condicional):
if active_filters:
    prompt += filter_instructions

# DEPOIS (sempre):
prompt += f"""
---
FILTROS ATIVOS (Baseados em Feedback do Usuário):
{filter_instructions if active_filters else "Nenhum filtro ativo ainda."}
---
"""
```

---

#### Tarefa 0.5: Fix #2.3 - Pattern-Based Filtering
**Arquivo**: `src/agent/analysis/enhanced.py`  
**Linhas**: 581-684 (método `_apply_post_filters`)

**Adicionar novo método**:
```python
def _matches_rejection_pattern(self, suggestion: dict) -> tuple[bool, str]:
    """Detecta padrões semânticos de rejeição."""
    text = f"{suggestion.get('title', '')} {suggestion.get('description', '')}".lower()
    
    patterns = {
        "autonomy_invasion": [
            "priorizar", "deve usar", "preferir", "em vez de",
            "substituir por", "trocar por", "obrigatoriamente"
        ],
        "out_of_scope": [
            "não está no playbook", "adicionar medicamento",
            "introduzir novo", "implementar funcionalidade",
            "tooltip", "interface", "nova tela"
        ],
        "already_implemented": [
            "já existe", "já implementado", "já temos",
            "já está presente"
        ]
    }
    
    for pattern_name, keywords in patterns.items():
        if any(kw in text for kw in keywords):
            return True, pattern_name
    
    return False, ""
```

**Integrar no `_apply_post_filters`**:
```python
# Após keyword filtering, adicionar:
is_pattern_match, pattern_name = self._matches_rejection_pattern(sug)
if is_pattern_match:
    filtered.append({
        **sug,
        "filter_reason": f"Padrão de rejeição: {pattern_name}"
    })
    logger.warning(f"⚠️ Sugestão bloqueada por padrão: {sug['id']} ({pattern_name})")
    continue
```

---

#### Tarefa 0.6: Fix #2.4 - Usar Relatórios EDITED
**Arquivo**: `src/agent/cli/interactive_cli.py`  
**Seção**: Carregamento de protocolo

**Adicionar função**:
```python
def load_protocol_smart(protocol_path: Path) -> dict:
    """Carrega versão EDITED se existir, caso contrário ORIGINAL."""
    
    # Tentar versão EDITED primeiro
    edited_path = protocol_path.parent / f"{protocol_path.stem}_EDITED{protocol_path.suffix}"
    
    if edited_path.exists():
        logger.info(f"✅ Usando versão EDITED: {edited_path.name}")
        return load_json(edited_path)
    
    logger.info(f"ℹ️ Versão EDITED não encontrada, usando ORIGINAL")
    return load_json(protocol_path)
```

**Usar no lugar de `load_json` direto**

---

#### Tarefa 0.7: Fix #3 - Simplificar Feedback UX
**Arquivo**: `src/agent/feedback/feedback_collector.py`  
**Linhas**: 150-250

**Mudança**:
```python
# ANTES:
print("""
S - Sim (Relevante)
N - Não (Irrelevante)
E - Editar sugestão
C - Adicionar comentário
P - Pular (marcar como relevante)
Q - Sair do feedback (retornar ao pipeline)
""")

# DEPOIS:
print("""
┌─────────────────────────────────────┐
│  S - Relevante                      │
│  N - Irrelevante (com comentário)   │
│  Q - Sair do feedback               │
└─────────────────────────────────────┘
""")

# Se N selecionado:
if choice == "N":
    comment = input("💬 Por que irrelevante? (opcional): ").strip()
    # Salvar feedback com comment
```

---

### FASE 1: Verificar Implementação Wave 2 (4-6 horas)

Se os arquivos NÃO existirem, criar conforme especificação abaixo.

#### Tarefa 1.1: Data Models
**Arquivo**: `src/agent/learning/models.py` (CRIAR)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

class HardRule(BaseModel):
    """Regra que BLOQUEIA sugestão automaticamente."""
    rule_id: str = Field(..., description="ID único da regra")
    rule_type: Literal[
        "reference_whitelist",
        "structural_constraint",
        "forbidden_pattern",
        "clinical_safety"
    ]
    condition: dict  # JSON-serializable validation logic
    block_message: str
    created_at: datetime = Field(default_factory=datetime.now)
    source: Literal["user_feedback", "playbook_rule", "system_constraint"]
    active: bool = True
    
class SoftRule(BaseModel):
    """Regra que FILTRA sugestões pós-geração."""
    rule_id: str
    pattern: str
    confidence_threshold: float = 0.8
    filter_reason: str
    created_at: datetime = Field(default_factory=datetime.now)
    source: str
    frequency: int = 0
    
class ValidationResult(BaseModel):
    """Resultado de validação de sugestão."""
    blocked: bool
    violated_rules: List[str] = []
    reason: Optional[str] = None
    suggestion_id: Optional[str] = None
```

---

#### Tarefa 1.2: Rules Engine
**Arquivo**: `src/agent/learning/rules_engine.py` (CRIAR ou CORRIGIR)

**Funcionalidade esperada**:
- Carregar regras de arquivo JSON (`memory/hard_rules.json`)
- Validar sugestões contra todas as Hard Rules
- Bloquear sugestões que violam regras
- Adicionar/remover regras dinamicamente
- Salvar regras atualizadas

**Ver especificação completa no relatório de planejamento anterior**

---

#### Tarefa 1.3: Reference Validator
**Arquivo**: `src/agent/validators/reference_validator.py` (CRIAR ou CORRIGIR)

**Funcionalidade esperada**:
- Indexar seções do playbook (headers markdown)
- Validar que referências existem no playbook
- Fuzzy matching para sugestões (threshold 85%)
- Blacklist de referências genéricas ("N/A", "geral", "diversos")

---

#### Tarefa 1.4: Feedback Learner
**Arquivo**: `src/agent/learning/feedback_learner.py` (CRIAR ou CORRIGIR)

**Funcionalidade esperada**:
- Processar feedback S/N/Q
- Extrair padrões generalizáveis de feedback N
- Converter padrões em Hard Rules
- Adicionar regras ao Rules Engine
- Usar LLM para generalização

---

#### Tarefa 1.5: Change Verifier
**Arquivo**: `src/agent/applicator/change_verifier.py` (CRIAR ou CORRIGIR)

**Funcionalidade esperada**:
- Validar protocolo reconstruído contra schema Pydantic
- Validar condicionais via AST
- Verificar cross-references (UIDs válidos)
- Verificar que Hard Rules foram respeitadas
- Verificar que mudanças foram aplicadas

---

### FASE 2: Integração e Testes (2-3 horas)

#### Tarefa 2.1: Integrar Rules Engine em Enhanced Analyzer
**Arquivo**: `src/agent/analysis/enhanced.py`

```python
from ..learning.rules_engine import RulesEngine

class EnhancedAnalyzer:
    def __init__(self, ...):
        self.rules_engine = RulesEngine("memory/hard_rules.json")
    
    def _apply_hard_rules(self, suggestions: List[dict]) -> tuple[List[dict], List[dict]]:
        """Aplica hard rules ANTES de retornar sugestões."""
        valid = []
        blocked = []
        
        for sug in suggestions:
            result = self.rules_engine.validate_suggestion(sug)
            if result.blocked:
                blocked.append({**sug, "block_reason": result.reason})
            else:
                valid.append(sug)
        
        logger.info(f"✅ Hard Rules: {len(valid)} válidas, {len(blocked)} bloqueadas")
        return valid, blocked
```

---

#### Tarefa 2.2: Integrar Reference Validator
**Arquivo**: `src/agent/analysis/enhanced.py`

```python
from ..validators.reference_validator import ReferenceValidator, PlaybookIndex

class EnhancedAnalyzer:
    def __init__(self, ...):
        if self.playbook_path:
            playbook_index = PlaybookIndex(self.playbook_path)
            self.ref_validator = ReferenceValidator(playbook_index)
```

---

#### Tarefa 2.3: Integrar Feedback Learner
**Arquivo**: `src/agent/feedback/feedback_collector.py`

```python
from ..learning.feedback_learner import FeedbackLearner

class FeedbackCollector:
    def __init__(self, ...):
        self.feedback_learner = FeedbackLearner(llm_client, rules_engine)
    
    def collect_feedback(self, suggestions: List[dict]) -> dict:
        for sug in suggestions:
            feedback = self._get_user_choice()
            
            if feedback == "N":
                comment = input("💬 Por que irrelevante? (opcional): ").strip()
                
                # Aprender com feedback
                new_rules = self.feedback_learner.process_feedback(sug, "N", comment)
                
                for rule in new_rules:
                    self.rules_engine.add_rule(rule)
                    logger.info(f"📚 Nova regra aprendida: {rule.rule_id}")
```

---

#### Tarefa 2.4: Integrar Change Verifier no Reconstructor
**Arquivo**: `src/agent/applicator/protocol_reconstructor.py`

```python
from .change_verifier import ChangeVerifier

class ProtocolReconstructor:
    def reconstruct(self, ...):
        # ... reconstrução ...
        
        # VALIDAÇÃO FINAL
        verifier = ChangeVerifier()
        report = verifier.verify_reconstruction(
            original_protocol=self.original_protocol,
            reconstructed_protocol=assembled_protocol,
            applied_suggestions=approved_suggestions,
            hard_rules=self.rules_engine.hard_rules
        )
        
        if not report.valid:
            logger.error("❌ PROTOCOLO INVÁLIDO - Não será salvo!")
            logger.error(f"Violações: {report.violations}")
            return None
        
        logger.info(f"✅ VALIDAÇÃO PASSOU")
        return assembled_protocol
```

---

### FASE 3: Testes End-to-End (1-2 horas)

#### Teste 1: Reconstruction Display
```bash
# Executar análise completa com reconstrução
python run_agent.py

# Verificar "MUDANÇAS APLICADAS" mostra valores reais
# ✅ SUCESSO: Location e description exibidos
# ❌ FALHA: Ainda mostra "N/A"
```

---

#### Teste 2: Learning System
```bash
# Run 1: Análise inicial
python run_agent.py
# Notar sugestão sug_010

# Fornecer feedback negativo
# Razão: "autonomy invasion - priorizar X sobre Y"

# Verificar memory_qa.md
# Pattern deve ter frequency=1

# Run 2: Nova análise
python run_agent.py
# sug_010 (tipo autonomy invasion) NÃO deve aparecer
# Logs devem mostrar "Bloqueado por padrão: autonomy_invasion"

# ✅ SUCESSO: Sugestão não aparece
# ❌ FALHA: Sugestão ainda aparece
```

---

#### Teste 3: Feedback UX
```bash
# Executar análise com feedback
python run_agent.py

# Verificar apenas 3 opções: S/N/Q
# ✅ SUCESSO: 3 opções
# ❌ FALHA: 7 opções
```

---

## 🎯 CRITÉRIOS DE SUCESSO

### Fase 0 (Emergency Fixes)
- ✅ Display mostra mudanças reais (não "N/A")
- ✅ Threshold = 1 (padrões ativam imediatamente)
- ✅ Filtros SEMPRE no prompt
- ✅ Pattern-based filtering funciona
- ✅ Relatórios EDITED são usados
- ✅ Feedback tem 3 opções apenas

### Fase 1 (Wave 2 Verification)
- ✅ Todos os arquivos Wave 2 existem
- ✅ Rules Engine funcional
- ✅ Reference Validator funcional
- ✅ Feedback Learner funcional
- ✅ Change Verifier funcional

### Fase 2 (Integration)
- ✅ Rules Engine integrado em Enhanced Analyzer
- ✅ Reference Validator integrado
- ✅ Feedback Learner integrado
- ✅ Change Verifier integrado

### Fase 3 (End-to-End)
- ✅ Sugestões rejeitadas NÃO reaparecem
- ✅ Token waste reduzido 40-60%
- ✅ Usuário vê mudanças aplicadas
- ✅ Protocolos inválidos são bloqueados

---

## 🚨 RISCOS E MITIGAÇÕES

### Risco 1: Arquivos Wave 2 não existem
**Mitigação**: Criar usando especificações deste relatório

### Risco 2: Mudanças quebram pipeline existente
**Mitigação**: 
- Fazer em branch separado
- Testar cada componente isoladamente
- Integração progressiva

### Risco 3: Performance degradada
**Mitigação**:
- Cachear rules engine
- Lazy loading de validators
- Benchmark antes/depois

---

## 📚 REFERÊNCIAS

**Documentos de Contexto**:
- `proud-seeking-newt.md` - Documentação detalhada dos bugs
- `dev_history.md` - Histórico de implementação
- `roadmap.md` - Status das Waves
- `memory_qa.md` - Sistema de memória atual

**Arquivos Chave**:
- `src/agent/analysis/enhanced.py` - Analyzer principal
- `src/agent/applicator/protocol_reconstructor.py` - Reconstrutor
- `src/agent/feedback/feedback_collector.py` - Coleta de feedback
- `src/agent/cli/interactive_cli.py` - CLI

---

## 📞 PRÓXIMOS PASSOS

1. **Claude Code**: Iniciar com Fase 0 (Emergency Fixes)
2. **Prioridade**: Fix #2 (Learning System) é o mais crítico
3. **Validação**: Testar cada fix antes de prosseguir
4. **Comunicação**: Reportar progresso a cada tarefa completada

---

**FIM DO RELATÓRIO**
