# 🔧 GUIA TÉCNICO: Implementação dos Aprendizados do Feedback

**Data:** 12 de dezembro de 2025  
**Base:** Feedback sobre 31 sugestões da Ficha Cardiologia v2.0.0  
**Objetivo:** Fornecer instruções técnicas concretas para melhorar o agente

---

## 🎯 PROBLEMA CRÍTICO IDENTIFICADO

**Antipadrão #1: Alertas Genéricos**

**Quantidade de rejeições:** 10 de 14 (71.4% das rejeições)

**Problema raiz:** O agente está sugerindo "alertas visuais", "bloqueios de conduta" e "alertas críticos" de forma genérica, sem especificar o mecanismo correto de implementação no contexto do Daktus.

---

## 🛠️ SOLUÇÃO: Atualização do System Prompt

### Adicionar ao System Prompt do Agente:

```markdown
## REGRAS PARA SUGESTÕES DE ALERTAS

Quando sugerir alertas ou avisos, você DEVE especificar um dos seguintes tipos:

### 1. Mensagem ao Médico
**Quando usar:** Informações críticas que o médico precisa VER antes de finalizar a conduta
**Localização JSON:** `condutaDataNode.mensagem`
**Exemplo:**
```json
{
  "id": "msg-medico-sincope-esforco",
  "nome": "Alerta Síncope de Esforço",
  "condicional": "visivel",
  "condicao": "sincope_contexto == 'contexto_esforco'",
  "conteudo": "<p><strong>🚨 RED FLAG CRÍTICA: Síncope de Esforço</strong></p><p>Investigação cardiológica OBRIGATÓRIA antes de qualquer liberação para atividade física.</p><ul><li>Solicitar: ECG, ECOTT, Teste Ergométrico</li><li>Aguardar resultados antes de liberar paciente</li><li>Risco: Morte súbita (5-30% se não investigado)</li></ul>",
  "observacao": "ESC Guidelines 2018 - Classe I, Evidência B"
}
```

### 2. Orientação ao Paciente
**Quando usar:** Informações educativas que o paciente deve receber
**Localização JSON:** `condutaDataNode.orientacao`
**Exemplo:**
```json
{
  "id": "orientacao-paciente-dm2-bnp",
  "nome": "Orientação sobre rastreamento de IC em DM2",
  "condicional": "visivel",
  "condicao": "('dm2_nid' in comorbidades or 'dm2_id' in comorbidades)",
  "conteudo": "<h3>Por que estou solicitando BNP/NT-proBNP?</h3><p>Pacientes com diabetes têm maior risco de desenvolver insuficiência cardíaca silenciosa...</p>"
}
```

### 3. Mensagem de Alerta em Medicamento
**Quando usar:** Avisos sobre prescrição, contraindicação ou obrigatoriedade de medicamento
**Localização JSON:** `medicamentos[id='X'].mensagem` ou campo específico de alerta
**Exemplo:**
```json
{
  "id": "estatina-atorvastatina-80mg",
  "nome": "Atorvastatina 80mg",
  "mensagem": "⚠️ ESTATINA DE ALTA INTENSIDADE OBRIGATÓRIA EM DAC. Meta LDL <70 mg/dL (ideal <55 mg/dL). Evidência 1A para redução de mortalidade.",
  "condicao": "'dac' in comorbidades and 'estatinas' not in muc"
}
```

### ❌ O QUE NÃO FAZER

**Evite sugestões vagas como:**
- "Adicionar alerta visual para [condição]"
- "Criar bloqueio de conduta para [situação]"
- "Implementar aviso crítico quando [X]"

**Sempre especifique:**
- Tipo exato do alerta (mensagem ao médico, orientação, ou alerta em medicamento)
- Localização JSON precisa
- Condição lógica exata
- Conteúdo HTML formatado e pronto para uso
```

---

## 📊 TEMPLATE DE SUGESTÃO CORRETA

### Para Alertas de Segurança:

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
      "conteudo": "[HTML formatado]",
      "observacao": "[Referência bibliográfica]"
    }
  }
}
```

---

## 🎯 TEMPLATE DE SUGESTÃO CORRETA - Automação de Exames

### Para Eficiência/Automação:

```json
{
  "id": "sug_XXX",
  "category": "eficiencia",
  "priority": "media",
  "title": "Automatizar solicitação de [EXAME] em [CONDIÇÃO]",
  "description": "O exame [X] é indicado para avaliar [Y] quando [CONDIÇÃO]. Automatizar a solicitação deste exame quando [CONDIÇÃO_ESPECÍFICA] for detectada para agilizar o diagnóstico e evitar omissões.",
  "rationale": "Diretriz [X] recomenda [EXAME] para [INDICAÇÃO]. Automatizar melhora adesão e reduz omissões.",
  "implementation_effort": {
    "effort": "baixo",
    "estimated_time": "2h",
    "complexity": "simples"
  },
  "specific_location": {
    "node_id": "[id do exame]",
    "field": "condicao",
    "path": "nodes[X].data.condutaDataNode.exame[Y].condicao"
  },
  "implementation_path": {
    "json_path": "nodes[X].data.condutaDataNode.exame[Y]",
    "modification_type": "modify_condition",
    "proposed_value": {
      "condicional": "visivel",
      "condicao": "[expressão lógica COMPLETA]",
      "observacao": "[Justificativa clínica e referência]"
    }
  }
}
```

---

## 🚀 AÇÕES IMEDIATAS PARA IMPLEMENTAR

### 1. Atualizar Prompt do Agente (PRIORIDADE MÁXIMA)

**Arquivo:** `agent/analysis/prompts.py` ou equivalente

**Adicionar seção:**
```python
ALERT_IMPLEMENTATION_RULES = """
## REGRAS PARA SUGESTÕES DE ALERTAS

Quando sugerir alertas, você DEVE especificar um dos seguintes tipos:

1. MENSAGEM AO MÉDICO (condutaDataNode.mensagem)
   - Use para informações críticas que o médico precisa VER
   - Sempre forneça o JSON completo pronto para implementar

2. ORIENTAÇÃO AO PACIENTE (condutaDataNode.orientacao)
   - Use para informações educativas para o paciente
   - Sempre forneça o HTML formatado

3. MENSAGEM DE ALERTA EM MEDICAMENTO (medicamentos[id].mensagem)
   - Use para avisos sobre prescrição/contraindicação
   - Sempre especifique o medicamento exato

❌ NUNCA sugira apenas "adicionar alerta visual" sem especificar o tipo e localização.
"""
```

---

### 2. Criar Validador de Sugestões (PRIORIDADE ALTA)

**Arquivo:** `agent/analysis/suggestion_validator.py`

```python
class SuggestionValidator:
    """Valida sugestões antes de apresentar ao usuário"""
    
    ALERT_ANTIPATTERNS = [
        "alerta visual",
        "bloqueio de conduta",
        "alerta crítico",
        "implementar aviso",
        "criar alerta"
    ]
    
    ALERT_REQUIRED_FIELDS = [
        "specific_location",
        "implementation_path",
        "proposed_value"
    ]
    
    def validate_alert_suggestion(self, suggestion: dict) -> tuple[bool, str]:
        """
        Valida se uma sugestão de alerta está bem especificada
        
        Returns:
            (is_valid, error_message)
        """
        if suggestion.get("category") != "seguranca":
            return True, ""
        
        # Check for antipatterns in title or description
        title_lower = suggestion.get("title", "").lower()
        desc_lower = suggestion.get("description", "").lower()
        
        for antipattern in self.ALERT_ANTIPATTERNS:
            if antipattern in title_lower or antipattern in desc_lower:
                # Check if it has required fields
                if not all(field in suggestion for field in self.ALERT_REQUIRED_FIELDS):
                    return False, f"Sugestão de alerta genérica sem especificação de implementação. Deve incluir: {', '.join(self.ALERT_REQUIRED_FIELDS)}"
                
                # Check if proposed_value has proper structure
                proposed = suggestion.get("implementation_path", {}).get("proposed_value", {})
                if not isinstance(proposed, dict) or "conteudo" not in proposed:
                    return False, "Sugestão de alerta sem conteúdo HTML especificado"
        
        return True, ""
    
    def filter_duplicates(self, suggestions: list[dict]) -> list[dict]:
        """Remove sugestões duplicadas"""
        seen_titles = set()
        filtered = []
        
        for sug in suggestions:
            title_normalized = sug.get("title", "").strip().lower()
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                filtered.append(sug)
        
        return filtered
```

---

### 3. Adicionar Filtro Pré-Apresentação (PRIORIDADE ALTA)

**Arquivo:** `agent/cli/interactive_cli.py` ou equivalente

```python
def filter_suggestions_before_presentation(suggestions: list[dict]) -> list[dict]:
    """
    Filtra sugestões antes de apresentar ao usuário
    Remove sugestões inválidas ou duplicadas
    """
    validator = SuggestionValidator()
    
    # Remove duplicatas
    suggestions = validator.filter_duplicates(suggestions)
    
    # Valida alertas
    valid_suggestions = []
    rejected = []
    
    for sug in suggestions:
        is_valid, error_msg = validator.validate_alert_suggestion(sug)
        if is_valid:
            valid_suggestions.append(sug)
        else:
            rejected.append({
                "suggestion": sug,
                "reason": error_msg
            })
    
    # Log rejected suggestions for debugging
    if rejected:
        logger.warning(f"Rejected {len(rejected)} invalid suggestions:")
        for r in rejected:
            logger.warning(f"  - {r['suggestion']['title']}: {r['reason']}")
    
    return valid_suggestions
```

---

### 4. Criar Exemplos de Referência (PRIORIDADE MÉDIA)

**Arquivo:** `agent/analysis/examples/good_alert_suggestions.json`

```json
{
  "examples": [
    {
      "title": "Exemplo 1: Mensagem ao Médico para Síncope de Esforço",
      "suggestion": {
        "id": "sug_example_001",
        "category": "seguranca",
        "priority": "alta",
        "title": "Adicionar MENSAGEM AO MÉDICO para Síncope de Esforço",
        "description": "Implementar mensagem ao médico no nó de conduta alertando sobre risco de morte súbita quando síncope de esforço for detectada.",
        "specific_location": {
          "node_id": "conduta-1754085461792",
          "field": "mensagem",
          "path": "nodes[14].data.condutaDataNode.mensagem"
        },
        "implementation_path": {
          "json_path": "nodes[14].data.condutaDataNode.mensagem",
          "modification_type": "add_message",
          "proposed_value": {
            "id": "msg-medico-sincope-esforco",
            "nome": "RED FLAG: Síncope de Esforço",
            "condicional": "visivel",
            "condicao": "sincope_contexto == 'contexto_esforco'",
            "conteudo": "<div style='background: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 10px 0;'><h3 style='color: #d32f2f; margin-top: 0;'>🚨 RED FLAG CRÍTICA: Síncope de Esforço</h3><p><strong>Risco de morte súbita: 5-30% se não investigado</strong></p><h4>Investigação OBRIGATÓRIA:</h4><ul><li>✓ ECG 12 derivações</li><li>✓ Ecocardiograma Transtorácico</li><li>✓ Teste Ergométrico ou Cintilografia</li><li>✓ Avaliação cardiologista</li></ul><p><strong>❌ BLOQUEIO:</strong> NÃO liberar para atividade física até investigação completa</p></div>",
            "observacao": "ESC Guidelines on Syncope 2018 - Classe I, Evidência B"
          }
        }
      }
    },
    {
      "title": "Exemplo 2: Automação de Solicitação de Exame",
      "suggestion": {
        "id": "sug_example_002",
        "category": "eficiencia",
        "priority": "media",
        "title": "Automatizar solicitação de Holter em Palpitações",
        "description": "Automatizar a solicitação de Holter 24h quando o paciente relatar palpitações, para agilizar diagnóstico de arritmias.",
        "specific_location": {
          "node_id": "holter-exam-node",
          "field": "condicao",
          "path": "nodes[X].data.condutaDataNode.exame[Y].condicao"
        },
        "implementation_path": {
          "json_path": "nodes[X].data.condutaDataNode.exame[Y]",
          "modification_type": "modify_condition",
          "proposed_value": {
            "id": "exam-holter-24h",
            "nome": "Holter de 24 horas",
            "condicional": "visivel",
            "condicao": "'palpitacao' in main or selected_any(ecg_pergunta, 'fa_ecg', 'esv_ecg', 'essv_ecg', 'bav_ecg', 'outras_arritmias_ecg')",
            "observacao": "Indicado para investigação de arritmias em pacientes com palpitações ou alterações no ECG. ACC/AHA Guidelines 2017."
          }
        }
      }
    }
  ]
}
```

---

## 📈 MÉTRICAS PARA MONITORAR

### Após Implementação das Melhorias:

**1. Taxa de Aceitação de Sugestões de Segurança**
- **Meta:** Aumentar de 41.2% para >70%
- **Como medir:** Feedback humano em análises futuras

**2. Taxa de Sugestões Duplicadas**
- **Meta:** <5% de duplicatas
- **Como medir:** Validador automático

**3. Taxa de Sugestões com Antipadrões**
- **Meta:** 0% de alertas genéricos
- **Como medir:** Validador automático

**4. Tempo de Implementação de Sugestões**
- **Meta:** Reduzir tempo médio de implementação em 50%
- **Como medir:** Tempo desde sugestão até implementação

---

## 🧪 TESTES ANTES DE DEPLOY

### Checklist de Validação:

```markdown
## Teste 1: Validação de Alertas
- [ ] Gerar 10 sugestões de alerta
- [ ] Verificar que 100% especificam tipo (mensagem/orientação/alerta medicamento)
- [ ] Verificar que 100% incluem JSON completo pronto para implementar
- [ ] Verificar que 0% usam termos genéricos ("alerta visual", "bloqueio")

## Teste 2: Validação de Duplicatas
- [ ] Gerar análise de protocolo grande (>100 nodes)
- [ ] Verificar taxa de duplicatas <5%
- [ ] Comparar títulos e descrições para identificar similares

## Teste 3: Validação de Automação de Exames
- [ ] Gerar 10 sugestões de automação
- [ ] Verificar que 100% incluem expressão lógica completa
- [ ] Verificar que 100% incluem justificativa clínica com referência
- [ ] Verificar que 100% especificam localização JSON exata

## Teste 4: Regressão
- [ ] Executar análise na mesma ficha de cardiologia
- [ ] Comparar com feedback anterior
- [ ] Verificar que sugestões rejeitadas não reaparecem
```

---

## 📚 DOCUMENTAÇÃO ADICIONAL NECESSÁRIA

### 1. Guia de Boas Práticas para Sugestões
**Arquivo:** `docs/SUGGESTION_BEST_PRACTICES.md`
- Incluir todos os templates deste documento
- Adicionar exemplos de boas e más sugestões
- Explicar o contexto do Daktus (mensagens/orientações/alertas)

### 2. Atualizar README do Agente
**Arquivo:** `README.md`
- Adicionar seção sobre "Como o agente sugere alertas"
- Explicar os três tipos de alertas
- Link para exemplos

### 3. Changelog
**Arquivo:** `CHANGELOG.md`
```markdown
## [v3.1.0] - 2025-12-13
### Changed
- **BREAKING:** Atualizadas regras de sugestão de alertas
- Agora todas as sugestões de alerta devem especificar tipo e localização JSON
- Adicionado validador automático de sugestões antes de apresentação

### Added
- Validador de antipadrões para alertas genéricos
- Filtro de sugestões duplicadas
- Exemplos de referência para boas sugestões
- Documentação de boas práticas

### Fixed
- Corrigida alta taxa de rejeição de sugestões de segurança (41.2% → esperado >70%)
- Eliminadas sugestões duplicadas
- Melhorada especificidade de sugestões de alertas
```

---

## 🎯 CRONOGRAMA DE IMPLEMENTAÇÃO

### Sprint 1 (1-2 dias): Correções Críticas
- [ ] Atualizar system prompt com regras de alertas
- [ ] Criar validador básico de antipadrões
- [ ] Testar com ficha de cardiologia

### Sprint 2 (2-3 dias): Validação e Filtros
- [ ] Implementar filtro de duplicatas
- [ ] Adicionar validação pré-apresentação
- [ ] Criar suite de testes automatizados

### Sprint 3 (1-2 dias): Documentação e Exemplos
- [ ] Criar guia de boas práticas
- [ ] Adicionar exemplos de referência
- [ ] Atualizar README e docs

### Sprint 4 (1 dia): Deploy e Monitoramento
- [ ] Deploy em ambiente de testes
- [ ] Executar análise completa na ficha de cardiologia
- [ ] Coletar feedback e ajustar
- [ ] Deploy em produção

**Total estimado:** 5-8 dias de desenvolvimento

---

## ✅ CRITÉRIOS DE SUCESSO

### Implementação considerada bem-sucedida se:

1. **Taxa de aceitação de sugestões de segurança >70%**
2. **Zero sugestões com antipadrões de alertas genéricos**
3. **Taxa de duplicatas <5%**
4. **100% das sugestões de alerta incluem JSON pronto para implementar**
5. **Feedback do time médico positivo sobre especificidade das sugestões**

---

**Documento gerado:** 12 de dezembro de 2025  
**Autor:** Dan (baseado em análise técnica do feedback)  
**Versão:** 1.0  
**Status:** Pronto para implementação
