# 🚀 V3 Implementation Plan - Auto-Apply Pipeline

**Status**: ✅ Validação Crítica Completa - GO para implementação
**Data de Início**: 2025-12-01
**Prazo Estimado**: 10-15 dias úteis
**Última Atualização**: 2025-12-01

---

## 📊 Resultados da Validação Crítica (DIA 1)

### Métricas Atingidas
- ✅ **Taxa de sucesso**: 100% (3/3 protocolos testados)
- ✅ **Tempo de correção**: Segundos (vs dias manualmente)
- ✅ **Qualidade**: JSON válido, estrutura preservada, mudanças rastreáveis
- ✅ **Custo**: $0.0029-$0.012 por protocolo (viável em escala)

### Protocolos Testados
1. **ORL (Amil)** - 65KB, 6 melhorias, Sonnet 4.5, $0.012
2. **Reumatologia** - 113KB, 5 melhorias + 4 nós, Sonnet 4.5, $0.012
3. **Testosterona (UNIMED)** - 15KB, 5 melhorias, Grok 4 Fast, $0.0029

### Decisão
**✅ PROSSEGUIR COM IMPLEMENTAÇÃO COMPLETA** - ROI comprovado, viabilidade técnica validada.

---

## 🎯 Arquitetura Alvo V3

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT V3 PIPELINE                            │
│                  (Análise + Correção Ativa)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────┐
    │  ETAPA 1: Análise (V2)                       │
    │  - Protocolo JSON + Playbook                 │
    │  - Análise estrutural + clínica              │
    │  - Geração de sugestões priorizadas          │
    └──────────────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────┐
    │  ETAPA 2: Auto-Apply (V3 - NOVO)             │
    │  - Aplicação automática de melhorias         │
    │  - Validação estrutural                      │
    │  - Incremento de versão (MAJOR.MINOR.PATCH)  │
    │  - Geração de diff                           │
    └──────────────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────┐
    │  ETAPA 3: Confidence Scoring                 │
    │  - Score 0-100% por mudança                  │
    │  - >90% = Auto-apply                         │
    │  - 70-90% = Preview obrigatório              │
    │  - <70% = Manual                             │
    └──────────────────────────────────────────────┘
                                │
                                ▼
    ┌──────────────────────────────────────────────┐
    │  OUTPUT                                      │
    │  - Protocolo corrigido (vX.Y.Z++)            │
    │  - Diff de mudanças                          │
    │  - Relatório de validação                    │
    │  - Métricas de custo/tempo                   │
    └──────────────────────────────────────────────┘
```

---

## 📅 Cronograma de Implementação

### **FASE 1: ImprovementApplicator - Wrapper Reutilizável (3-5 dias)**

**Objetivo**: Encapsular toda lógica de auto-apply em módulo reutilizável e testado.

**Entregas**:
- ✅ `src/agent_v3/applicator/improvement_applicator.py`
- ✅ `src/agent_v3/applicator/llm_client.py`
- ✅ Função principal: `apply_improvements(protocol_json, suggestions, model) -> dict`

**Funcionalidades**:
1. **Cost Estimation**
   - Estimar tokens de input/output
   - Calcular custo em USD por modelo
   - Retornar estimativa antes de executar

2. **Auto-Apply via LLM**
   - Prompt engineering para aplicação precisa
   - Suporte a múltiplos modelos (Grok 4 Fast, Sonnet 4.5)
   - Max tokens configurável (1M para protocolos grandes)
   - Timeout adequado (120s+)

3. **JSON Parsing Robusto**
   - Extração de JSON de resposta markdown
   - Tratamento de JSON incompleto/truncado
   - Validação sintática

4. **Version Management**
   - Extração de versão atual do protocolo
   - Incremento automático (MAJOR.MINOR.PATCH)
   - PATCH++ para correções/melhorias
   - MINOR++ para features novas
   - MAJOR++ para breaking changes

5. **Output Filename Generation**
   - Extração de base name do protocolo
   - Formato: `{base_name}_{vX.Y.Z}_{timestamp}.json`
   - Preservação de identificadores únicos

**Testes**:
- ✅ 3+ protocolos de diferentes tamanhos
- ✅ Validação de JSON válido
- ✅ Validação de estrutura preservada
- ✅ Validação de incremento correto de versão

**Dependências**: Nenhuma

**Critério de Sucesso**: 100% dos testes passando, código reutilizável e bem documentado.

---

### **FASE 2: StructuralValidator - Garantia de Qualidade (2-3 dias)**

**Objetivo**: Garantir que protocolos corrigidos são válidos e não quebraram.

**Entregas**:
- ✅ `src/agent_v3/validator/structural_validator.py`
- ✅ `src/agent_v3/validator/schema_validator.py`

**Validações Obrigatórias**:

1. **JSON Syntax Validation**
   - Protocolo é um dict válido
   - Todas as chaves são strings
   - Estrutura aninhada correta

2. **Schema Preservation**
   - Chaves principais preservadas (nodes, metadata, etc.)
   - Estrutura de nós intacta
   - IDs únicos mantidos

3. **Data Integrity**
   - Referências entre nós válidas
   - Tipos de dados corretos
   - Campos obrigatórios presentes

4. **Change Detection**
   - Detectar se houve mudanças reais
   - Evitar salvar se nada mudou
   - Log de todas as mudanças

**Output**:
```python
{
    "valid_json": bool,
    "structure_preserved": bool,
    "changes_detected": bool,
    "errors": [],
    "warnings": []
}
```

**Testes**:
- ✅ Protocolo válido deve passar
- ✅ Protocolo com chave removida deve falhar
- ✅ Protocolo sem mudanças deve detectar
- ✅ JSON malformado deve falhar

**Dependências**: Nenhuma

**Critério de Sucesso**: Zero protocolos quebrados salvos, 100% de detecção de erros estruturais.

---

### **FASE 3: Pipeline Integration - V2 + V3 Unificado (3-5 dias)**

**Objetivo**: Integrar V2 (análise) + V3 (auto-apply) em pipeline único e coeso.

**Entregas**:
- ✅ `src/agent_v3/pipeline.py` (implementação completa)
- ✅ Função: `analyze_and_fix(protocol_path, playbook_path, model, auto_apply, confidence_threshold) -> dict`

**Fluxo do Pipeline**:

```python
def analyze_and_fix(protocol_path, playbook_path, model="x-ai/grok-4-fast",
                    auto_apply=True, confidence_threshold=0.90):
    """
    Pipeline completo V2 → V3

    1. Rodar V2 → análise + sugestões
    2. [SE auto_apply=True] Aplicar melhorias via ImprovementApplicator
    3. Validar protocolo corrigido via StructuralValidator
    4. [FUTURO] Score de confiança via ConfidenceScorer
    5. Gerar diff via DiffGenerator
    6. Retornar output unificado
    """
```

**Flags de Controle**:
- `auto_apply`: True/False - Aplicar correções automaticamente?
- `confidence_threshold`: 0.0-1.0 - Threshold mínimo para auto-apply (padrão: 0.90)
- `model`: String - Modelo LLM para auto-apply (padrão: "x-ai/grok-4-fast")

**Output Unificado**:
```python
{
    # Análise V2
    "protocol_analysis": {
        "structural": {...},
        "clinical_extraction": {...}
    },
    "improvement_suggestions": [...],

    # Correção V3
    "fixed_protocol": {...},  # Protocolo corrigido
    "changes_diff": [...],    # Diff de mudanças
    "validation": {...},      # Resultado da validação

    # Metadados
    "metadata": {
        "v2_analysis_time_ms": 0,
        "v3_apply_time_ms": 0,
        "cost_estimation": {...},
        "cost_actual": {...},
        "model_used": "...",
        "auto_applied": True/False,
        "validation_passed": True/False,
        "version_incremented": "v0.1.2 → v0.1.3"
    }
}
```

**Testes de Integração**:
- ✅ Pipeline completo com 3+ protocolos
- ✅ Modo auto_apply=True
- ✅ Modo auto_apply=False (só análise)
- ✅ Validação de outputs corretos
- ✅ Validação de timings e custos

**Dependências**: FASE 1, FASE 2

**Critério de Sucesso**: Pipeline completo funcional, outputs corretos, zero regressões da V2.

---

### **FASE 4: DiffGenerator - Rastreabilidade Completa (2-3 dias)**

**Objetivo**: Mostrar exatamente o que mudou no protocolo de forma legível.

**Entregas**:
- ✅ `src/agent_v3/diff/diff_generator.py`
- ✅ `src/agent_v3/diff/formatter.py`

**Funcionalidades**:

1. **Structural Diff**
   - Nós adicionados
   - Nós removidos
   - Nós modificados
   - Mudanças em edges

2. **Field-Level Diff**
   - Campo por campo (antes/depois)
   - Highlight de mudanças
   - Contexto clínico

3. **Rastreabilidade**
   - Qual sugestão gerou qual mudança
   - Justificativa clínica
   - Fonte de evidência (playbook)

**Output Format**:
```python
[
    {
        "change_type": "node_added|node_modified|node_removed|edge_added|...",
        "node_id": "...",
        "field": "...",
        "before": "...",
        "after": "...",
        "reason": "Sugestão #2: ...",
        "confidence": 0.95
    },
    ...
]
```

**Testes**:
- ✅ Detectar adições corretas
- ✅ Detectar modificações corretas
- ✅ Detectar remoções corretas
- ✅ Formato legível e claro

**Dependências**: FASE 3

**Critério de Sucesso**: Diff completo e legível, rastreabilidade 100%.

---

### **FASE 5: Confidence Scoring - Decisões Inteligentes (3-4 dias)**

**Objetivo**: Atribuir scores de confiança para cada mudança e decidir automaticamente.

**Entregas**:
- ✅ `src/agent_v3/scoring/confidence_scorer.py`

**Heurísticas de Confiança** (MVP):

**Alta Confiança (90-100%)** - Auto-apply:
- Adição de nós faltantes (sem conflitos)
- Correção de typos
- Melhorias de nomenclatura
- Adição de campos opcionais

**Média Confiança (70-89%)** - Preview obrigatório:
- Modificação de condições lógicas
- Alteração de fluxos existentes
- Remoção de nós

**Baixa Confiança (<70%)** - Manual apenas:
- Mudanças que afetam lógica crítica
- Conflitos com estrutura existente
- Mudanças ambíguas

**Output**:
```python
{
    "suggestion_id": "...",
    "confidence_score": 0.95,  # 0-1
    "confidence_level": "high|medium|low",
    "action": "auto_apply|preview_required|manual_only",
    "reasoning": "..."
}
```

**Integração com Pipeline**:
- Se score < confidence_threshold → não aplicar automaticamente
- Gerar relatório com sugestões não aplicadas
- Usuário pode revisar e aplicar manualmente

**Testes**:
- ✅ Scores coerentes com tipos de mudança
- ✅ Decisões corretas de auto-apply
- ✅ Rastreabilidade de reasoning

**Dependências**: FASE 3

**Critério de Sucesso**: Scores precisos, decisões seguras, zero mudanças perigosas auto-aplicadas.

---

### **FASE 6: CLI Unificado - Interface do Usuário (1-2 dias)**

**Objetivo**: CLI profissional para executar pipeline V2+V3.

**Entregas**:
- ✅ `run_v3_cli.py` ou atualização de `run_qa_cli.py`

**Features**:
1. Seleção de protocolo (JSON)
2. Seleção de playbook (MD/PDF) - opcional
3. Seleção de modelo LLM
4. **NOVO**: Modo de operação (análise-only vs auto-apply)
5. **NOVO**: Confidence threshold configurável
6. **NOVO**: Preview de mudanças antes de aplicar
7. **NOVO**: Estimativa de custo pré-execução

**Fluxo**:
```
1. Selecione o protocolo: [lista]
2. Selecione o playbook (opcional): [lista]
3. Selecione o modelo: [lista]
4. Modo de operação:
   [ ] Análise apenas (V2)
   [x] Análise + Auto-apply (V3)
5. Confidence threshold: [0.90]
6. [Estimativa de custo: $0.0029]
7. Continuar? (s/n): s
8. [Processando...]
9. ✅ Concluído! Protocolo corrigido salvo em: ...
```

**Testes**:
- ✅ Fluxo completo funcional
- ✅ Validação de inputs
- ✅ Tratamento de erros
- ✅ Mensagens claras

**Dependências**: FASE 3

**Critério de Sucesso**: Interface intuitiva, fluxo claro, zero confusão.

---

### **FASE 7: Testes Intensivos - Validação em Escala (2-3 dias)**

**Objetivo**: Testar V3 com protocolos reais de múltiplas especialidades.

**Protocolos para Testar** (mínimo 15-20):
- ✅ Diversos tamanhos (10KB - 500KB)
- ✅ Múltiplas especialidades (ORL, Cardio, Neuro, Pediatria, etc.)
- ✅ Diferentes níveis de complexidade
- ✅ Casos edge (protocolos muito grandes, muito pequenos, etc.)

**Validações**:
1. Taxa de sucesso >95%
2. Zero JSON quebrado
3. Custo médio <$0.02 por protocolo
4. Tempo médio <60 segundos
5. Qualidade de mudanças alta (revisão manual de 20%)

**Correções**:
- Bugs encontrados devem ser corrigidos imediatamente
- Iterações rápidas
- Re-teste após correções

**Dependências**: FASES 1-6

**Critério de Sucesso**: >95% sucesso, zero erros críticos, stakeholders aprovam.

---

### **FASE 8: Production Deploy - Lançamento (1 dia)**

**Objetivo**: Deploy em produção com monitoramento.

**Entregas**:
1. Documentação de uso atualizada
2. README.md com instruções V3
3. Exemplos de uso
4. Guia de troubleshooting
5. Deploy script (se aplicável)

**Monitoramento Inicial**:
- Taxa de sucesso
- Custo médio
- Feedback dos usuários
- Bugs reportados

**Critério de Sucesso**: Sistema em produção, usuários usando, feedback positivo.

---

## 🎯 Métricas de Sucesso do MVP V3

### Obrigatórias
- ✅ Taxa de auto-apply bem-sucedida >95%
- ✅ Suporta protocolos JSON ilimitados
- ✅ Tempo: dias → <10 minutos (-99%)
- ✅ Zero JSON quebrado salvo
- ✅ Rastreabilidade completa (diff + versionamento)

### Desejáveis
- 🎯 Custo médio <$0.02 por protocolo
- 🎯 Confidence scoring funcional
- 🎯 Diff visual legível
- 🎯 Logs de auditoria

---

## 🔗 Dependências Técnicas

### Bibliotecas Python
- `openai` ou `anthropic` - LLM clients (ou via OpenRouter)
- `requests` - HTTP client para OpenRouter
- `jsonschema` - Validação de schema
- `python-dotenv` - Env vars
- Já instaladas no projeto atual

### Serviços Externos
- OpenRouter API (já configurado)
- Modelos LLM: Grok 4 Fast (principal), Claude Sonnet 4.5 (backup)

### Conhecimento Necessário
- JSON manipulation (básico)
- Prompt engineering para auto-apply (crítico)
- Error handling robusto
- Testing (pytest)

---

## 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Auto-apply quebra JSON | Médio | Crítico | StructuralValidator obrigatório antes de salvar |
| Custo explode em escala | Baixo | Alto | Monitoring de custo, fallback para modelo mais barato |
| Mudanças clínicas incorretas | Baixo | Crítico | Confidence scoring + preview obrigatório para baixa confiança |
| Performance lenta | Baixo | Médio | Timeout adequado, processamento assíncrono (futuro) |
| Resistência dos usuários | Médio | Médio | Demo clara, benefícios quantificados, feedback loop |

---

## 📚 Recursos

- **Validação DIA 1**: `test_v3_auto_apply.py` (código de referência)
- **Documentação V2**: `src/agent_v2/README.md`
- **Roadmap completo**: `roadmap.md`
- **Dev history**: `dev_history.md`

---

## ✅ Checklist de Implementação

### FASE 1: ImprovementApplicator
- [ ] Criar módulo `improvement_applicator.py`
- [ ] Implementar cost estimation
- [ ] Implementar auto-apply via LLM
- [ ] Implementar version management
- [ ] Implementar output filename generation
- [ ] Escrever testes unitários
- [ ] Documentar API

### FASE 2: StructuralValidator
- [ ] Criar módulo `structural_validator.py`
- [ ] Implementar validações obrigatórias
- [ ] Escrever testes unitários
- [ ] Documentar critérios de validação

### FASE 3: Pipeline Integration
- [ ] Implementar `pipeline.py` completo
- [ ] Integrar V2 + V3
- [ ] Implementar flags de controle
- [ ] Output unificado
- [ ] Testes de integração

### FASE 4: DiffGenerator
- [ ] Criar módulo `diff_generator.py`
- [ ] Implementar structural diff
- [ ] Implementar field-level diff
- [ ] Rastreabilidade completa
- [ ] Testes

### FASE 5: Confidence Scoring
- [ ] Criar módulo `confidence_scorer.py`
- [ ] Implementar heurísticas MVP
- [ ] Integração com pipeline
- [ ] Testes

### FASE 6: CLI Unificado
- [ ] Atualizar CLI existente ou criar novo
- [ ] Implementar novo fluxo
- [ ] Testes de UX

### FASE 7: Testes Intensivos
- [ ] Selecionar 15-20 protocolos
- [ ] Executar bateria de testes
- [ ] Corrigir bugs encontrados
- [ ] Re-testar

### FASE 8: Production Deploy
- [ ] Atualizar documentação
- [ ] Deploy
- [ ] Monitoramento inicial
- [ ] Coleta de feedback

---

**Status Atual**: ✅ Validação completa - Pronto para FASE 1
**Próximo Marco**: ImprovementApplicator funcional (3-5 dias)
