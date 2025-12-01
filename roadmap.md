# 🗺️ Roadmap - Agente Daktus QA

**Última Atualização**: 2025-11-30  
**Status Atual**: ✅ V2 Completa (Produção) | 🔥 V3 em Desenvolvimento Acelerado

---

## 🎯 Visão do Produto

**Missão**: Validação e correção automatizadas de protocolos clínicos contra playbooks baseados em evidências.

**Evolução**:
- **V2 (Atual)**: Validação inteligente via LLM → ✅ **Produção**
- **V3 (MVP - 2 Semanas)**: Correção automatizada de protocolos JSON → 🔥 **Transformacional**

**Transformação fundamental**: De **auditoria passiva** (identifica problemas) para **correção ativa** (resolve automaticamente).

---

## ✅ V2 - Status Atual (Resumo)

### O Que Funciona
- ✅ Validação de protocolos JSON contra playbooks (MD/PDF)
- ✅ Análise de gaps clínicos e sugestões de melhoria
- ✅ Arquitetura LLM-first, agnóstica a especialidades
- ✅ Performance: 60s latência, R$ 0,25-0,50/análise, 95% sucesso
- ✅ Prompt caching funcional (reduz até 90% do custo)

### Limitações Críticas (Resolvidas em V3)
1. ⚠️ **Protocolos JSON massivos (3k-5k linhas)** - gargalo principal
2. ⚠️ Correção manual (dias/semanas de implementação)
3. ⚠️ Sem priorização por impacto real
4. ⚠️ Sem aprendizado contínuo
5. ⚠️ ROI difícil de quantificar

---

## 🔥 V3 - Correção Automatizada (MVP 2 Semanas)

### Ganhos Esperados

| Métrica | V2 | V3 | Ganho |
|---------|----|----|-------|
| **Tempo de implementação** | Dias | Minutos | **-90%** |
| **Limite de protocolo JSON** | Quebra >3k linhas | Ilimitado | **∞** |
| **Precisão de sugestões** | ~80% | 90%+ (MVP) | **+10pp** |
| **ROI** | Subjetivo | Quantificado (scores) | **Mensurável** |
| **Prompt caching** | Parcial | Agressivo (100%) | **-50% custo** |

---

## 🚀 Fases de Desenvolvimento V3

### **FASE 4: Compactação de Protocolos JSON (CRÍTICA)**
**Prioridade**: 🔴 BLOQUEIO TÉCNICO #1 - CORE MVP

**Problema Real**: Protocolos JSON com 3k-5k linhas excedem janela de contexto, não playbooks.

**Solução**:
1. **JSONCompactor** - Reduz protocolo JSON ao essencial clínico
   - Remove redundâncias, metadados desnecessários
   - Mantém apenas: estrutura clínica, fluxos, variáveis, lógica de decisão
   - Preserva integridade para reconstrução posterior

2. **SmartChunking** (se JSON ainda for muito grande)
   - Divide protocolo por seções lógicas (síndromes, fluxos, tratamentos)
   - Processa incrementalmente
   - Reconstrói protocolo completo no final

3. **MemoryManager**
   - Mantém contexto essencial entre chunks
   - Evita reprocessar conteúdo
   - Raciocínio incremental

**Entregas**:
- ✅ Suporte a protocolos JSON ilimitados
- ✅ Processamento eficiente sem perda de qualidade
- ✅ Desbloqueia protocolos complexos (AVC, Sepse, Trauma, Onco)

**Validação**: Testar com 5 protocolos >3k linhas no dia 1

---

### **FASE 5: Auto-Apply de Melhorias (TRANSFORMACIONAL)**
**Prioridade**: 🔴 MUDANÇA DE PARADIGMA - CORE ENGINE V3

**Problema**: Implementação manual de melhorias = gargalo, erro humano, escalabilidade zero.

**Solução - Core Engine V3**:

```
Relatório V2 (sugestões) + Protocolo JSON Original
    ↓
Claude Sonnet 4.5 (auto-apply engine)
    ↓
Protocolo JSON corrigido + Diff completo + Rastreabilidade
    ↓
ConfidenceScoring (0-100% por mudança)
    ↓
Alta confiança (>90%) = Auto-apply + notificação
Média (70-90%) = Preview obrigatório
Baixa (<70%) = Apenas sugestão manual
```

**Entregas**:
1. **ImprovementApplicator**
   - Recebe sugestões + protocolo original
   - Gera protocolo corrigido automaticamente via Sonnet 4.5
   - Mantém rastreabilidade completa (diff + justificativa por mudança)

2. **StructuralValidator**
   - Valida integridade do JSON pós-correção
   - Garante que estrutura não quebrou
   - Testes automáticos de schema

3. **ConfidenceScoring Básico**
   - Score 0-100% por sugestão
   - Threshold fixo para MVP (>90% = auto-apply)
   - Refinamento futuro baseado em feedback

4. **DiffGenerator**
   - Mostra exatamente o que mudou
   - Formato legível (antes/depois)
   - Rastreabilidade clínica completa

**Impacto**:
- 🔥 Tempo de correção: Dias → Minutos (-90%)
- 🔥 Elimina erro humano na transcrição
- 🔥 Escala infinitamente (100+ protocolos/dia)
- 🔥 **ROI explode** - implementação instantânea

**Riscos e Mitigação**:
- ❌ Auto-apply errado → ✅ Validação estrutural automática + aprovação humana para baixa confiança
- ❌ Quebra de JSON → ✅ StructuralValidator obrigatório antes de salvar
- ❌ Perda de contexto clínico → ✅ Rastreabilidade completa via DiffGenerator

**Validação (DIA 1 - CRÍTICO)**:
1. Pegar 5-10 protocolos reais
2. Rodar V2 → gerar sugestões
3. Enviar para Sonnet 4.5 → aplicar melhorias
4. Medir: % sucesso, tipos de erro, tempo economizado
5. **Se >80% sucesso → implementar imediatamente**
6. **Se <80% sucesso → refinar prompt e repetir**

---

### **FASE 6: Prompt Caching Agressivo (CRÍTICA)**
**Prioridade**: 🔴 ECONOMIA - CORE MVP

**Problema**: Custo de tokens pode explodir com protocolos grandes e múltiplas análises.

**Solução - Prompt Caching 100%**:

1. **CacheStrategy**
   - Playbook sempre em cache (não muda entre análises)
   - Protocolo original em cache (base para comparações)
   - Instruções de sistema em cache (fixas)
   - Apenas sugestões e protocolo corrigido sem cache (únicos por análise)

2. **CacheMonitor**
   - Loga taxa de cache hit/miss
   - Rastreia economia de tokens
   - Alerta se cache não está funcionando

**Entregas**:
- ✅ Redução de 50-70% no custo por análise
- ✅ Cache automático em todas as chamadas LLM
- ✅ Monitoramento de eficiência

**Implementação**: Integrar em LLMClient, não módulo separado

---

### **FASE 7: Priorização por Impacto (QUICK WIN)**
**Prioridade**: 🟡 ROI QUANTIFICÁVEL - MVP VIA PROMPT

**Problema**: Sugestões sem ordem clara, cliente não sabe onde focar.

**Solução - MVP via Prompt (1 Dia)**:

Ajustar prompt V2 para incluir scores em cada sugestão:
- **Segurança do Paciente** (0-10) - risco de evento adverso se não corrigir
- **Impacto Financeiro** (Baixo/Médio/Alto) - economia estimada
- **Esforço de Implementação** (Baixo/Médio/Alto) - complexidade da correção

**Entregas**:
- ✅ Sugestões ranqueadas por impacto no relatório
- ✅ Cliente sabe exatamente onde focar
- ✅ ROI fica visível imediatamente

**Implementação**: Apenas ajuste de prompt, zero código novo

---

### **POST-MVP: Fases Futuras**

#### **FASE 8: Loop de Feedback (Vantagem Competitiva)**
**Prioridade**: 🟢 POST-MVP

- FeedbackCollector - rastreia aprovações/rejeições
- LearningEngine - fine-tuning baseado em decisões reais
- Precisão: 90% → 95%+ ao longo do uso

#### **FASE 9: ROI Calculator Robusto**
**Prioridade**: 🟢 POST-MVP

- Scores numéricos (R$/ano economizado)
- Cálculo de payback
- Dashboard de impacto acumulado

#### **FASE 10: Integração Zero-Fricção**
**Prioridade**: 🟢 POST-MVP

- API REST
- Integração com sistema de autoria Daktus
- Interface web drag-and-drop

#### **FASE 11: Análise de Custo e Tokens**
**Prioridade**: 🟢 FUTURO

- Rastreamento detalhado de custo por protocolo
- Otimização automática de custos
- Relatórios de eficiência de tokens

---

## 📅 Prioridades de Implementação MVP V3

### 🔥 CORE OBRIGATÓRIO (2 Semanas)

**Semana 1:**
1. **DIA 1**: Validar auto-apply (experimento Sonnet 4.5) ← CRÍTICO
2. **DIAS 2-4**: JSONCompactor + SmartChunking
3. **DIAS 5-7**: ImprovementApplicator + StructuralValidator

**Semana 2:**
4. **DIA 8**: Prompt Caching Agressivo integrado
5. **DIA 9**: Impact Scoring via prompt (quick win)
6. **DIA 10**: DiffGenerator básico
7. **DIAS 11-13**: Testes intensivos com protocolos reais
8. **DIA 14**: Apresentação para stakeholders

### 🎯 Nice-to-Have (se der tempo)
- Confidence scoring refinado
- Diff visual HTML
- Logs de auditoria detalhados

### 🟢 POST-MVP (após validação)
- Feedback loop completo
- ROI calculator robusto
- API + Integrações
- Análise de custo detalhada

---

## 🔥 Ações Imediatas (HOJE)

### 1. Validar Auto-Apply (DIA 1 - CRÍTICO)
**Ação**:
- Pegar 5-10 protocolos reais
- Rodar V2 → gerar sugestões
- Enviar para Sonnet 4.5 → aplicar melhorias automaticamente
- Revisar manualmente: funciona? quebra JSON? mantém lógica clínica?
- Medir: % sucesso, tipos de erro, tempo economizado

**Decisão**: 
- **Se >80% sucesso** → implementar Fase 5 imediatamente
- **Se <80% sucesso** → refinar prompt e tentar novamente (não desistir)

### 2. Implementar JSONCompactor (DIAS 2-4)
**Ação**:
- Criar módulo que reduz JSON ao essencial
- Testar com 3-5 protocolos >3k linhas
- Validar que compactação mantém toda lógica clínica
- Se ainda muito grande → implementar SmartChunking

### 3. Implementar Auto-Apply (DIAS 5-7)
**Ação**:
- ImprovementApplicator (core engine)
- StructuralValidator (garantir JSON válido)
- ConfidenceScoring básico (threshold fixo >90%)
- DiffGenerator básico (mostrar mudanças)

### 4. Integrar Prompt Caching 100% (DIA 8)
**Ação**:
- Garantir que playbook está sempre em cache
- Protocolo original em cache
- Instruções de sistema em cache
- Apenas output variável sem cache
- Validar economia de tokens em logs

### 5. Impact Scoring via Prompt (DIA 9 - QUICK WIN)
**Ação**:
- Ajustar prompt V2 para incluir scores (Segurança 0-10, Economia L/M/A, Esforço L/M/A)
- Rankear sugestões no relatório
- Zero código novo

### 6. Testar + Apresentar (DIAS 10-14)
**Ação**:
- Rodar V3 em 10-20 protocolos reais de múltiplas especialidades
- Validar que auto-apply funciona consistentemente
- Coletar feedback qualitativo
- Ajustar conforme necessário
- Preparar apresentação com casos de sucesso e métricas

---

## 📊 Métricas de Sucesso MVP V3

### Produto
- ✅ Protocolos JSON >3k linhas processados sem quebrar
- ✅ Tempo de implementação: dias → <10 minutos
- ✅ Taxa de auto-apply bem-sucedida >80%
- ✅ Zero regressões da V2

### Performance
- ✅ Prompt caching >70% (economia brutal de custo)
- ✅ Validação estrutural 100% (zero JSON quebrado salvo)
- ✅ Rastreabilidade completa (diff de todas as mudanças)

### Impacto
- ✅ 100% sugestões com score de impacto
- ✅ Stakeholders veem valor imediato e quantificável
- ✅ ROI demonstrável (tempo economizado + qualidade)

---

## 🎯 Definição de Sucesso

**MVP V3 é bem-sucedido se:**
1. ✅ Processa protocolos JSON gigantes (>3k linhas) sem quebrar
2. ✅ Auto-apply funciona em >80% dos casos
3. ✅ Tempo de implementação cai de dias para minutos
4. ✅ Prompt caching reduz custo em >50%
5. ✅ Stakeholders aprovam para produção
6. ✅ Zero regressões da V2

**Após MVP:**
- Decidir investimento em Fases 8-11 (feedback, ROI robusto, API)
- Planejar integração com sistema de autoria Daktus
- Escalar para produção completa

---

## 🧨 Princípios de Execução

**Velocidade acima de tudo:**
- ✅ Arquitetura V2 já é sólida - só adicionar módulos
- ✅ Usar Claude Code / Cursor para implementação rápida
- ✅ Testar com casos reais desde o dia 1
- ✅ Iterar rápido, validar diariamente
- ✅ MVP imperfeito hoje > produto perfeito em 3 meses

**Foco brutal:**
- 🔴 JSONCompactor + Auto-Apply + Prompt Caching = CORE
- 🟡 Impact Scoring = Quick win (1 dia)
- 🟢 Todo resto = POST-MVP

**Fail-fast:**
- Se auto-apply não funcionar no dia 1 → pivotar imediatamente
- Se JSON quebrar → StructuralValidator obrigatório
- Se custo explodir → validar prompt caching

---

**Para instruções de uso, veja [`README.md`](README.md)**  
**Para histórico de desenvolvimento, veja [`dev_history.md`](dev_history.md)**