"""
Alert Rules - Definições de regras para sugestões de alertas.

Este módulo contém as regras e templates para garantir que sugestões
de alertas sejam específicas e implementáveis no contexto do Daktus.

Problema resolvido:
- 71.4% das rejeições eram por "alertas genéricos" sem especificação
- Sugestões como "adicionar alerta visual" não são acionáveis
- Falta de JSON pronto para implementar

Solução:
- Definir 3 tipos de alertas com exemplos claros
- Antipadrões a evitar
- Templates JSON prontos para uso
"""

from typing import Dict, List

# =============================================================================
# REGRAS DE IMPLEMENTAÇÃO DE ALERTAS - Para inclusão no System Prompt
# =============================================================================

ALERT_IMPLEMENTATION_RULES = '''
## REGRAS CRÍTICAS PARA SUGESTÕES DE ALERTAS

Quando sugerir alertas ou avisos, você DEVE especificar um dos seguintes tipos:

### 1. MENSAGEM AO MÉDICO
**Quando usar:** Informações críticas que o médico precisa VER antes de finalizar a conduta
**Localização JSON:** `condutaDataNode.mensagem`
**Estrutura obrigatória:**
```json
{
  "id": "msg-medico-[identificador-unico]",
  "nome": "[Título da mensagem]",
  "condicional": "visivel",
  "condicao": "[expressão lógica Python-like]",
  "conteudo": "[HTML formatado com alerta]",
  "observacao": "[Referência bibliográfica]"
}
```

### 2. ORIENTAÇÃO AO PACIENTE
**Quando usar:** Informações educativas que o paciente deve receber
**Localização JSON:** `condutaDataNode.orientacao`
**Estrutura obrigatória:**
```json
{
  "id": "orientacao-[identificador-unico]",
  "nome": "[Título da orientação]",
  "condicional": "visivel",
  "condicao": "[expressão lógica]",
  "conteudo": "[HTML com orientação ao paciente]"
}
```

### 3. MENSAGEM DE ALERTA EM MEDICAMENTO
**Quando usar:** Avisos sobre prescrição, contraindicação ou obrigatoriedade
**Localização JSON:** Campo `mensagem` do medicamento específico
**Estrutura obrigatória:**
```json
{
  "id": "[id-do-medicamento]",
  "nome": "[Nome do medicamento]",
  "mensagem": "[Texto do alerta sobre o medicamento]",
  "condicao": "[expressão lógica]"
}
```

### ❌ ANTIPADRÕES - NUNCA USE ESTES TERMOS SEM ESPECIFICAÇÃO:
- "Adicionar alerta visual para [condição]"
- "Criar bloqueio de conduta para [situação]"
- "Implementar aviso crítico quando [X]"
- "Adicionar alerta de alta prioridade"

### ✅ SEMPRE INCLUA NAS SUGESTÕES DE ALERTA:
1. **Tipo exato** do alerta (mensagem médico, orientação paciente, ou alerta medicamento)
2. **Localização JSON precisa** (path completo)
3. **Condição lógica exata** (expressão Python-like)
4. **Conteúdo HTML formatado** pronto para uso
5. **Referência bibliográfica** quando aplicável
'''

# =============================================================================
# ANTIPADRÕES A DETECTAR
# =============================================================================

ALERT_ANTIPATTERNS: List[str] = [
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
]

# =============================================================================
# CAMPOS OBRIGATÓRIOS PARA SUGESTÕES DE SEGURANÇA
# =============================================================================

SECURITY_SUGGESTION_REQUIRED_FIELDS: List[str] = [
    "specific_location",
    "implementation_path",
]

IMPLEMENTATION_PATH_REQUIRED_FIELDS: List[str] = [
    "json_path",
    "modification_type",
    "proposed_value",
]

# =============================================================================
# TEMPLATES DE SUGESTÕES BEM ESTRUTURADAS
# =============================================================================

GOOD_ALERT_TEMPLATE = '''
### EXEMPLO DE SUGESTÃO DE ALERTA BEM ESTRUTURADA:

```json
{
  "id": "sug_XXX",
  "category": "seguranca",
  "priority": "alta",
  "title": "Adicionar MENSAGEM AO MÉDICO para [CONDIÇÃO]",
  "description": "A condição [X] requer atenção imediata do médico. Implementar mensagem ao médico no nó de conduta para alertar sobre [RISCO] e [AÇÃO NECESSÁRIA].",
  "rationale": "Diretriz [X] Classe [Y], Evidência [Z]. Risco de [COMPLICAÇÃO] se não manejado.",
  "implementation_effort": {
    "effort": "baixo",
    "estimated_time": "1h",
    "complexity": "simples"
  },
  "specific_location": {
    "node_id": "conduta-1754085461792",
    "field": "mensagem",
    "path": "nodes[14].data.condutaDataNode.mensagem"
  },
  "implementation_path": {
    "json_path": "nodes[14].data.condutaDataNode.mensagem",
    "modification_type": "add_message",
    "proposed_value": {
      "id": "msg-medico-[identificador]",
      "nome": "[Nome da mensagem]",
      "condicional": "visivel",
      "condicao": "[expressão lógica]",
      "conteudo": "[HTML formatado com alerta visual, referências e conduta]",
      "observacao": "[Referência bibliográfica]"
    }
  }
}
```
'''

GOOD_EXAM_AUTOMATION_TEMPLATE = '''
### EXEMPLO DE SUGESTÃO DE AUTOMAÇÃO DE EXAME:

```json
{
  "id": "sug_XXX",
  "category": "eficiencia",
  "priority": "media",
  "title": "Automatizar solicitação de [EXAME] em [CONDIÇÃO]",
  "description": "O exame [X] é indicado para avaliar [Y] quando [CONDIÇÃO]. Automatizar a solicitação deste exame para agilizar o diagnóstico e evitar omissões.",
  "rationale": "Diretriz [X] recomenda [EXAME] para [INDICAÇÃO]. Automatizar melhora adesão e reduz omissões.",
  "implementation_effort": {
    "effort": "baixo",
    "estimated_time": "2h",
    "complexity": "simples"
  },
  "specific_location": {
    "node_id": "[id-do-exame]",
    "field": "condicao",
    "path": "nodes[X].data.condutaDataNode.exame[Y].condicao"
  },
  "implementation_path": {
    "json_path": "nodes[X].data.condutaDataNode.exame[Y]",
    "modification_type": "modify_condition",
    "proposed_value": {
      "id": "exam-[identificador]",
      "nome": "[Nome do exame]",
      "condicional": "visivel",
      "condicao": "[expressão lógica COMPLETA]",
      "observacao": "[Justificativa clínica e referência]"
    }
  }
}
```
'''


def get_alert_rules_for_prompt() -> str:
    """
    Retorna as regras de implementação de alertas formatadas para o prompt.
    
    Returns:
        String com regras e templates para inclusão no system prompt
    """
    return ALERT_IMPLEMENTATION_RULES


def get_alert_examples_for_prompt() -> str:
    """
    Retorna exemplos de sugestões bem estruturadas para o prompt.
    
    Returns:
        String com templates de exemplo
    """
    return GOOD_ALERT_TEMPLATE + "\n" + GOOD_EXAM_AUTOMATION_TEMPLATE


def get_antipatterns() -> List[str]:
    """
    Retorna lista de antipadrões a detectar em sugestões.
    
    Returns:
        Lista de strings com termos problemáticos
    """
    return ALERT_ANTIPATTERNS.copy()


def contains_antipattern(text: str) -> tuple[bool, str]:
    """
    Verifica se um texto contém antipadrões de alertas genéricos.
    
    Args:
        text: Texto a verificar (título ou descrição da sugestão)
    
    Returns:
        (has_antipattern, matched_antipattern)
    """
    text_lower = text.lower()
    
    for antipattern in ALERT_ANTIPATTERNS:
        if antipattern in text_lower:
            return True, antipattern
    
    return False, ""
