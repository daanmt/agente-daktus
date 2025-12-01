# 🔍 Agente Daktus QA

> Sistema de validação e correção automatizada de protocolos clínicos usando IA

**Versão Atual**: 2.3-production ✅  
**Próxima Versão**: 3.0-alpha (em desenvolvimento)  
**Status**: Pronto para Produção (v2) | Roadmap v3 Definido  
**Última Atualização**: 2025-11-30

---

## 🎯 O Que Faz

### Versão 2.x (Atual - Produção)

Valida protocolos clínicos (JSON) contra playbooks médicos (texto/PDF) para garantir:

- ✅ Consistência da lógica clínica
- ✅ Cobertura completa de sintomas
- ✅ Caminhos diagnósticos apropriados
- ✅ Recomendações baseadas em evidências
- ✅ Identificação de gaps e oportunidades de melhoria

**Entrada**: Protocolo clínico (JSON) + Playbook médico (Markdown/PDF)  
**Saída**: Relatório de validação clínica (texto + JSON) com análise de gaps e sugestões de melhoria priorizadas

### Versão 3.0 (Em Desenvolvimento)

**Evolução transformacional:** De auditoria passiva para correção ativa.

- ✅ Tudo da v2.x
- 🔥 **Auto-Apply de Melhorias** - Aplica correções automaticamente no JSON
- 🔥 **Chunking Inteligente** - Processa playbooks gigantes (50-200+ páginas)
- 🔥 **Priorização por Impacto** - Sugestões ranqueadas por ROI clínico-financeiro
- 🔥 **Loop de Feedback** - Aprende com decisões clínicas reais
- 🔥 **Workflow de Aprovação** - Preview, diff visual, rollback automático

**Resultado:** Redução de 90% no tempo de implementação de melhorias (de dias para minutos).

---

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar OpenRouter

Crie um arquivo `.env` na raiz do projeto:

```env
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui
```

**Obter chave de API**: https://openrouter.ai/keys

### 3. Executar Análise

```bash
python run_qa_cli.py
```

Siga as instruções:
1. Selecione o arquivo JSON do protocolo em `models_json/`
2. Selecione o arquivo do playbook (opcional mas recomendado)
3. Escolha o modelo LLM
4. Visualize os resultados em `reports/`

---

## 🏗️ Arquitetura

### Agent V2: Arquitetura Centrada em LLM (Produção)

**Princípios fundamentais**:
- **Zero lógica clínica no código** - toda inteligência clínica vem do LLM
- **Chamada única ao LLM** - análise abrangente via super prompt
- **Agnóstico a especialidades** - funciona identicamente para ORL, AVC, Pediatria, etc.
- **Foco em sugestões de melhoria** - recomendações acionáveis para aprimoramento do protocolo

**Pipeline de Execução**:
```
Playbook + Protocolo → protocol_loader (carregamento bruto)
    ↓
prompt_builder (montagem do super prompt com cache)
    ↓
llm_client → API OpenRouter (análise abrangente única)
    ↓
output/validator (validação de schema)
    ↓
pipeline.analyze() → Saída JSON unificada
    ↓
CLI Report Generator → reports/*.txt, reports/*.json
```

### Agent V3: Arquitetura de Correção Automatizada (Roadmap)

**Evolução transformacional** em 3 etapas:

```
ETAPA 1: PREPROCESSAMENTO INTELIGENTE
Playbook gigante → ChunkingEngine → Chunks semânticos
    ↓
SynthesisEngine → Playbook-Synth compactado (só essencial)
    ↓
MemoryManager → Contexto mantido entre chunks

ETAPA 2: ANÁLISE + CORREÇÃO
Protocolo JSON + Playbook-Synth → LLM (análise)
    ↓
Relatório de melhorias + Scores de impacto
    ↓
ImprovementApplicator → Protocolo JSON corrigido (auto-apply)
    ↓
ConfidenceScoring → Alta confiança = auto-apply | Baixa = preview

ETAPA 3: APROVAÇÃO + APRENDIZADO
Protocolo corrigido → ApprovalWorkflow (diff visual)
    ↓
Usuário aprova/rejeita → FeedbackCollector
    ↓
LearningEngine → Fine-tuning contínuo baseado em decisões reais
```

**Ganhos esperados v3:**
- 🔥 Tempo de implementação: dias → minutos (-90%)
- 🔥 Custo de tokens: -50-70% (chunking + cache)
- 🔥 Precisão: 80% → 95%+ (loop de feedback)
- 🔥 ROI quantificável: R$ economizados + eventos evitados

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Obrigatório
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui

# Opcional
LLM_MODEL=anthropic/claude-sonnet-4.5  # Modelo padrão v3
```

### Modelos Suportados

**Recomendados para v2/v3:**
- `anthropic/claude-sonnet-4.5` ⭐ (recomendado v3 - auto-apply)
- `anthropic/claude-sonnet-4-20250514` (alternativa)
- `google/gemini-2.5-flash-preview-09-2025` 🔧 (v2 padrão)

**Outros modelos disponíveis:**
- `anthropic/claude-3.5-haiku-20241022` (mais rápido, mais barato)
- `google/gemini-2.5-flash`, `google/gemini-2.5-pro`
- `openai/gpt-5-mini`, `openai/gpt-4.1-mini`, `openai/gpt-4o-mini`
- `x-ai/grok-2-1212`

**Total**: 12+ modelos disponíveis

---

## 📊 Formato de Saída

### V2 (Atual)

**Relatório em Texto** (`reports/*.txt`):
- Resumo da estrutura do protocolo
- Resumo da extração do playbook
- Validação clínica (cobertura, gaps)
- Análise de eficiência
- Sugestões de melhoria
- Métricas de qualidade

**Relatório em JSON** (`reports/*.json`):
- Dados estruturados completos
- Todos os resultados da análise
- Metadados (timestamps, modelo usado, tempos de processamento)
- Contagens de entidades (síndromes, exames, tratamentos)

### V3 (Futuro)

**Adições ao output:**
- ✅ Protocolo JSON corrigido (`reports/*_fixed.json`)
- ✅ Diff visual de mudanças (`reports/*_diff.html`)
- ✅ Scores de impacto por sugestão (Segurança 0-10, Economia R$, Esforço horas)
- ✅ ROI calculado de cada melhoria
- ✅ Rastreabilidade completa (qual fonte de evidência justifica cada mudança)
- ✅ Logs de aprovação/rejeição (feedback loop)

---

## 🔧 Solução de Problemas

### "API key não configurada"

**Causa**: `OPENROUTER_API_KEY` não configurado

**Solução**:
```bash
# Verifique se o .env existe
type .env  # Windows
cat .env   # Linux/Mac

# Ou crie manualmente
echo OPENROUTER_API_KEY=sk-or-v1-sua-chave > .env
```

### "Nenhum arquivo de protocolo encontrado"

**Causa**: Nenhum arquivo JSON em `models_json/`

**Solução**: Adicione arquivos JSON de protocolos no diretório `models_json/`

### "Playbook muito grande - context overflow"

**Causa (v2)**: Playbook >50 páginas excede janela de contexto

**Solução temporária**: Reduza playbook manualmente ou divida em seções

**Solução definitiva (v3)**: ChunkingEngine processará playbooks gigantes automaticamente

---

## 📚 Documentação

**Documentação Oficial** (consolidada em 3 arquivos principais):

- **Este arquivo** (`README.md`) - Visão geral e uso
- **`roadmap.md`** - Roadmap completo v2 → v3
- **`dev_history.md`** - Histórico de desenvolvimento (log append-only)

**Recursos Adicionais**:

- `REVIEW_CLAUDE.txt` - Especificação completa do Agent V2
- `src/agent_v2/` - Código-fonte do Agent V2

---

## 🎯 Princípios-Chave

### Princípios de Design do Agent V2/V3

1. **Zero Lógica Clínica no Código**
   - Todas as decisões clínicas vêm do LLM
   - Sem regras hardcoded, regex ou heurísticas
   - Código é pura orquestração

2. **Chamada Única ao LLM** (v2) → **Chunking Inteligente** (v3)
   - v2: Um super prompt abrangente
   - v3: Processamento incremental com síntese

3. **Agnóstico a Especialidades**
   - Mesmo caminho de código para todas as especialidades médicas
   - Sem lógica `if especialidade == "ORL"`
   - Conhecimento específico de especialidade nos playbooks, não no código

4. **De Passivo para Ativo** (v3)
   - v2: Identifica problemas
   - v3: Identifica + Corrige automaticamente

5. **Fail-Fast com Segurança**
   - Erros são registrados e propagados imediatamente
   - Auto-apply somente com alta confiança (>90%)
   - Aprovação humana obrigatória para mudanças críticas

6. **Aprendizado Contínuo** (v3)
   - Sistema aprende com decisões clínicas reais
   - Fine-tuning baseado em feedback
   - Precisão melhora ao longo do tempo

---

## 📈 Performance

### Agent V2 (Atual)
- **Latência p95**: ≤ 60 segundos
- **Custo por análise**: ~R$ 0,25-0,50 (depende do modelo)
- **Taxa de sucesso**: ≥ 95%
- **Cache de prompts**: Reduz até 90% do custo em análises repetidas

### Agent V3 (Expectativa)
- **Latência p95**: ≤ 90 segundos (chunking + auto-apply)
- **Custo por análise**: ~R$ 0,15-0,30 (-50% via chunking otimizado)
- **Taxa de sucesso**: ≥ 98%
- **Tempo de implementação de melhorias**: Dias → Minutos (-90%)
- **Precisão de sugestões**: 80% → 95%+ (após 3-6 meses de feedback)

---

## 🔗 Links Úteis

- **OpenRouter**: https://openrouter.ai
- **Chaves de API**: https://openrouter.ai/keys
- **Catálogo de Modelos**: https://openrouter.ai/models
- **Anthropic Claude**: https://www.anthropic.com/claude

---

## 📝 Uso Programático

### V2 (Atual)

```python
from agent_v2.pipeline import analyze

# Análise completa
resultado = analyze(
    protocol_path="models_json/protocolo.json",
    playbook_path="models_json/playbook.md",
    model="anthropic/claude-sonnet-4.5"
)

# Resultado contém:
# - protocol_analysis: análise estrutural e extração clínica
# - improvement_suggestions: sugestões de melhoria priorizadas
# - metadata: informações sobre processamento, modelo, qualidade
```

### V3 (Futuro)

```python
from agent_v3.pipeline import analyze_and_fix

# Análise + Correção automatizada
resultado = analyze_and_fix(
    protocol_path="models_json/protocolo.json",
    playbook_path="models_json/playbook_gigante.pdf",  # Suporta playbooks massivos
    model="anthropic/claude-sonnet-4.5",
    auto_apply=True,  # Aplica correções automaticamente
    confidence_threshold=0.90  # Só auto-apply se confiança >90%
)

# Resultado contém:
# - protocol_analysis: análise estrutural
# - improvement_suggestions: sugestões ranqueadas por impacto
# - fixed_protocol: protocolo JSON corrigido
# - changes_diff: diff visual de mudanças
# - impact_scores: scores de segurança, economia, esforço
# - metadata: custo, tempo, confiança de cada mudança
```

---

## 🎯 Próximos Passos

### Para Usuários (v2)
1. ✅ Use v2 em produção para validação de protocolos
2. ✅ Colete feedback sobre qualidade das sugestões
3. ⏳ Aguarde v3 para correção automatizada

### Para Desenvolvedores
1. 🔥 **Validar hipótese de auto-apply** (experimento 1 semana)
2. 🔥 **Implementar ChunkingEngine** (MVP 2 semanas)
3. 🔥 **Implementar ImprovementApplicator** (2-4 meses)
4. ⏳ Ver roadmap completo em `roadmap.md`

---

**Para o roadmap detalhado v2 → v3, veja [`roadmap.md`](roadmap.md)**  
**Para o histórico de desenvolvimento, veja [`dev_history.md`](dev_history.md)**