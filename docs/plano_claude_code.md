🗺️ PLANO DE IMPLEMENTAÇÃO: Agente Daktus QA - Próximas 4-6 Semana

 Data: 2025-12-11
 Status Atual: Production-Ready (Wave 1-3 completas, bugs corrigidos)
 Objetivo: Sistema pronto para compartilhar com colegas em PRÓXIMAS SEMANAS
 Estratégia: Roadmap balanceado (UX + Testes + Performance + SQLite MVP)

 ---
 📊 CONTEXTO VALIDADO

 Situação Atual

 ✅ Sistema Production-Ready - Todos os 6 bugs críticos corrigidos
 ✅ Wave 2 Completa - Learning system 100% implementado e integrado
 ✅ Arquitetura Estável - memory_qa.md gerenciável (185KB)
 ⚠️ UX com pain points - 5 problemas críticos de experiência
 ❌ Testes insuficientes - Score 4.4/10, Wave 2 sem testes
 🚀 Performance otimizável - 40% melhoria possível

 Prioridades Estratégicas (do usuário)

 1. Urgência: Compartilhar com colegas em próximas semanas
 2. Balance: UX + Testes + Performance (todas igualmente)
 3. Risco: Balanceado (iteração rápida com testes críticos)
 4. SQLite: MVP rápido (1 semana validação)

 ---
 🎯 ROADMAP DE 5 SEMANAS

 SEMANA 1 → Quick Wins (UX crítico para adoção)
 SEMANA 2 → Fundações (Testes + CI/CD para confiança)
 SEMANA 3 → Performance (40% speedup, 30% cost reduction)
 SEMANA 4 → SQLite MVP (Validar arquitetura híbrida)
 SEMANA 5 → Dashboard (Opcional - apresentação stakeholders)

 ---
 FASE 1: QUICK WINS (Semana 1) - CRÍTICO

 Objetivo: Sistema estável, pronto para compartilhar
 Duração: 5-7 dias
 KPI de Sucesso: Taxa de abandono <10% (vs 40% atual)

 1.1 Eliminação de Exits Abruptos ⚠️ URGENTE

 Problema: 8x sys.exit() sem retry → usuários abandonam
 Impacto: 60% dos usuários frustrados

 Implementação:
 # src/agent/core/error_recovery.py (NOVO)
 class ErrorRecovery:
     def handle_error(error, context, max_retries=3):
         """Retry com backoff, nunca aborta sem aviso"""
         # Retry logic
         # User prompt para continuar ou cancelar
         # Logging estruturado

 Arquivos:
 - src/agent/core/error_recovery.py (CRIAR)
 - src/agent/cli/interactive_cli.py (MODIFICAR - remover 5x sys.exit)
 - src/agent/core/llm_client.py (MODIFICAR - adicionar retry)

 Validação: Zero sys.exit sem opção de retry

 ---
 1.2 Config File Externalizável 📋

 Problema: Modelos/diretórios hardcoded → impossível customizar
 Impacto: 55%

 Implementação:
 # config.yaml (NOVO - raiz do projeto)
 models:
   default: "google/gemini-2.5-flash-lite"
   available:
     - id: "google/gemini-2.5-flash-lite"
       name: "Gemini 2.5 Flash Lite"
       cost: [0.075, 0.30]

 directories:
   protocols: "models_json"
   reports: "reports"

 analysis:
   suggestion_range: [5, 50]
   timeout_seconds: 120

 Arquivos:
 - config.yaml (CRIAR)
 - src/agent/core/config_loader.py (CRIAR - Pydantic validation)
 - src/agent/cli/interactive_cli.py (MODIFICAR - usar config)

 Validação: Zero hardcoded values no código

 ---
 1.3 Feedback Visual de Progresso 💭

 Problema: Análises 40-60s sem feedback
 Impacto: 50%

 Implementação:
 - Spinners com context
 - Progress bars multi-etapa
 - ETA baseado em histórico
 - Thinking messages: "Analisando 245 nós..."

 Arquivos:
 - src/agent/cli/display_manager.py (MODIFICAR - ETA, thinking)
 - src/agent/analysis/enhanced.py (MODIFICAR - emit progress)

 Validação: Operações >5s têm feedback, abandono <5%

 ---
 1.4 Session Recovery 🔄

 Problema: Crash = perda total de progresso
 Impacto: 45%

 Implementação:
 - Checkpoints automáticos a cada etapa
 - Graceful degradation
 - Offline mode básico

 Arquivos:
 - src/agent/core/session_state.py (CRIAR - persist state)
 - src/agent/cli/interactive_cli.py (MODIFICAR - checkpoints)

 Validação: Recovery >80%, zero perda total

 ---
 FASE 2: FUNDAÇÕES (Semana 2) - CRÍTICO

 Objetivo: Confiança total, zero regressões
 Duração: 5-7 dias
 KPI de Sucesso: >80% cobertura, CI verde

 2.1 Testes Wave 2 ✅

 Problema: 0% cobertura em rules_engine, feedback_learner

 Implementação:
 # tests/test_rules_engine.py (CRIAR ~200 linhas)
 def test_rule_blocks_invalid_suggestion()
 def test_learned_rule_persists()
 def test_rule_engine_performance()

 # tests/test_feedback_learner.py (CRIAR ~250 linhas)
 def test_learns_from_rejections()
 def test_keyword_extraction()

 # tests/test_reference_validator.py (CRIAR ~150 linhas)
 def test_validates_playbook_reference()
 def test_detects_hallucination()

 # tests/test_change_verifier.py (CRIAR ~100 linhas)
 def test_verifies_changes_applied()
 def test_detects_fake_applications()

 Arquivos:
 - tests/test_rules_engine.py (CRIAR)
 - tests/test_feedback_learner.py (CRIAR)
 - tests/test_reference_validator.py (CRIAR)
 - tests/test_change_verifier.py (CRIAR)

 Validação: >80% cobertura Wave 2, testes <30s

 ---
 2.2 Testes Applicator ✅

 Problema: 0% cobertura em protocol_reconstructor

 Implementação:
 # tests/test_protocol_reconstructor.py (CRIAR ~300 linhas)
 def test_reconstructs_valid_protocol()
 def test_preserves_original()
 def test_handles_conflicting_suggestions()
 def test_validates_output()

 # tests/test_version_utils.py (CRIAR ~100 linhas)
 def test_increments_version()
 def test_generates_unique_filename()

 Arquivos:
 - tests/test_protocol_reconstructor.py (CRIAR)
 - tests/test_version_utils.py (CRIAR)
 - tests/fixtures/ (CRIAR - protocolos sintéticos)

 Validação: >70% cobertura Applicator

 ---
 2.3 CI/CD Setup 🔄

 Problema: Sem CI/CD → risco de deploy quebrado

 Implementação:
 # .github/workflows/ci.yml (CRIAR)
 name: CI
 on: [push, pull_request]
 jobs:
   test:
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v3
       - uses: actions/setup-python@v4
       - run: pytest --cov=src --cov-report=xml
       - uses: codecov/codecov-action@v3

 # .github/workflows/lint.yml (CRIAR)
 name: Lint
 jobs:
   lint:
     steps:
       - run: black --check src/
       - run: mypy src/

 Arquivos:
 - .github/workflows/ci.yml (CRIAR)
 - .github/workflows/lint.yml (CRIAR)

 Validação: CI <5min, badge no README

 ---
 2.4 Linting + Type Checking 🎨

 Problema: Sem black/mypy → código inconsistente

 Implementação:
 # pyproject.toml (CRIAR)
 [tool.black]
 line-length = 100
 target-version = ['py311']

 [tool.mypy]
 python_version = "3.11"
 warn_return_any = true
 disallow_untyped_defs = true

 Arquivos:
 - pyproject.toml (CRIAR)
 - .pre-commit-config.yaml (CRIAR)

 Validação: 100% formatado, zero type errors críticos

 ---
 FASE 3: PERFORMANCE (Semana 3) - ALTO ROI

 Objetivo: -40% tempo, -30% custo
 Duração: 5-7 dias
 KPI de Sucesso: Análise <30s, custo <$0.10

 3.1 Prompt Caching 💰

 Problema: 60% dos tokens repetidos
 Impacto: -30% custo

 Implementação:
 - Usar cache OpenRouter para playbook + memory_qa
 - Estruturar prompts: [CACHED: static] [DYNAMIC: protocol]
 - TTL de 5 minutos

 Arquivos:
 - src/agent/core/prompt_cache.py (CRIAR)
 - src/agent/core/llm_client.py (MODIFICAR)
 - src/config/prompts/enhanced_analysis_prompt.py (MODIFICAR)

 Validação: Cache hit >60%, -30% custo

 ---
 3.2 Lazy Loading ⚡

 Problema: Todos protocolos carregados no startup
 Impacto: -20% startup, -40% memória

 Implementação:
 - Carregar metadata no startup
 - JSON completo on-demand
 - LRU cache (3 últimos)

 Arquivos:
 - src/agent/core/protocol_loader.py (MODIFICAR)

 Validação: Startup <1s, memória <50MB

 ---
 3.3 Paralelização de Validações ⚡⚡

 Problema: Validações sequenciais
 Impacto: -40% validação

 Implementação:
 async def validate_protocol(protocol):
     results = await asyncio.gather(
         validate_structure(protocol),
         validate_logic(protocol),
         validate_references(protocol)
     )

 Arquivos:
 - src/agent/validators/protocol_validator.py (MODIFICAR - async)
 - src/agent/analysis/enhanced.py (MODIFICAR)

 Validação: 15s → 9s validação

 ---
 3.4 Embedding Cache 🧠

 Problema: Embeddings recalculados sempre
 Impacto: -20% similarity search

 Implementação:
 - Cache em embeddings_cache.pkl
 - Invalidação por file hash
 - Numpy memmap para grandes volumes

 Arquivos:
 - src/agent/feedback/memory_engine.py (MODIFICAR)

 Validação: Cache hit >90%, -20% tempo

 ---
 FASE 4: SQLITE MVP (Semana 4) - VALIDAÇÃO

 Objetivo: Validar arquitetura híbrida
 Duração: 5-7 dias
 KPI de Sucesso: Analytics básico funcionando

 4.1 Schema + Setup 📊

 Implementação:
 -- src/agent/db/schema.sql (CRIAR)
 CREATE TABLE protocols (
     id INTEGER PRIMARY KEY,
     name TEXT NOT NULL,
     version TEXT,
     created_at TIMESTAMP
 );

 CREATE TABLE analyses (
     id INTEGER PRIMARY KEY,
     protocol_id INTEGER,
     model TEXT,
     cost_usd REAL,
     suggestions_count INTEGER,
     created_at TIMESTAMP
 );

 -- + 3 mais tabelas

 Arquivos:
 - src/agent/db/schema.sql (CRIAR)
 - src/agent/db/connection.py (CRIAR)
 - src/agent/db/migrations.py (CRIAR)

 Validação: Schema valida, migration funciona

 ---
 4.2 Dual-Write 🔄

 Implementação:
 - Escrever em arquivo E DB
 - Transações garantem consistência
 - Rollback automático se DB falha

 Arquivos:
 - src/agent/db/writer.py (CRIAR)
 - src/agent/cli/interactive_cli.py (MODIFICAR)

 Validação: 100% em ambos, zero inconsistências

 ---
 4.3 Queries Básicas 📈

 Implementação:
 # src/agent/db/queries.py (CRIAR)
 def get_monthly_cost():
     """Custo mensal"""

 def get_acceptance_rate_by_category():
     """Taxa de aceitação por categoria"""

 def get_protocol_evolution(protocol_id):
     """Evolução do protocolo"""

 Arquivos:
 - src/agent/db/queries.py (CRIAR)
 - notebooks/analytics_demo.ipynb (CRIAR)

 Validação: 10 queries úteis, <100ms

 ---
 FASE 5: DASHBOARD (Semana 5) - OPCIONAL

 Objetivo: UX para stakeholders
 Duração: 5 dias
 KPI de Sucesso: Dashboard acessível, 10+ visualizações

 5.1 Streamlit Dashboard 🎨

 Implementação:
 # dashboard/app.py (CRIAR)
 import streamlit as st

 st.title("Agente Daktus QA - Analytics")

 # Páginas:
 # 1. Overview (métricas agregadas)
 # 2. Analyses (lista + filtros)
 # 3. Suggestions (exploração)
 # 4. Rules (aprendizado)

 Arquivos:
 - dashboard/app.py (CRIAR)
 - dashboard/pages/ (CRIAR - 4 páginas)
 - dashboard/utils/ (CRIAR - helpers)

 Validação: Dashboard em localhost:8501, export funciona

 ---
 📋 RESUMO EXECUTIVO

 Timeline

 | Fase | Semana   | Foco            | Prioridade |
 |------|----------|-----------------|------------|
 | 1    | Semana 1 | Quick Wins (UX) | CRÍTICO    |
 | 2    | Semana 2 | Testes + CI/CD  | CRÍTICO    |
 | 3    | Semana 3 | Performance     | ALTO       |
 | 4    | Semana 4 | SQLite MVP      | MÉDIO      |
 | 5    | Semana 5 | Dashboard       | OPCIONAL   |

 Total: 4-5 semanas (core) + 1 semana (opcional)

 ---
 Impacto Esperado

 Após Fase 1 (1 semana):
 - ✅ Sistema pronto para compartilhar
 - ✅ Zero crashes abruptos
 - ✅ Config externalizável
 - 📊 Taxa de abandono <10%

 Após Fase 2 (2 semanas):
 - ✅ Confiança total (>80% cobertura)
 - ✅ CI/CD automático
 - ✅ Zero regressões

 Após Fase 3 (3 semanas):
 - ✅ -40% tempo de análise
 - ✅ -30% custo
 - 📊 Análise <30s, custo <$0.10

 Após Fase 4 (4 semanas):
 - ✅ Analytics funcionais
 - ✅ Arquitetura escalável validada

 Após Fase 5 (5 semanas):
 - ✅ Dashboard profissional
 - ✅ Pronto para stakeholders

 ---
 Arquivos Críticos por Fase

 Fase 1 (7 arquivos):
 - src/agent/core/error_recovery.py (NOVO)
 - config.yaml (NOVO)
 - src/agent/core/config_loader.py (NOVO)
 - src/agent/core/session_state.py (NOVO)
 - src/agent/cli/interactive_cli.py (MODIFICAR)
 - src/agent/cli/display_manager.py (MODIFICAR)
 - src/agent/core/llm_client.py (MODIFICAR)

 Fase 2 (10 arquivos):
 - tests/test_rules_engine.py (NOVO)
 - tests/test_feedback_learner.py (NOVO)
 - tests/test_reference_validator.py (NOVO)
 - tests/test_change_verifier.py (NOVO)
 - tests/test_protocol_reconstructor.py (NOVO)
 - tests/test_version_utils.py (NOVO)
 - .github/workflows/ci.yml (NOVO)
 - .github/workflows/lint.yml (NOVO)
 - pyproject.toml (NOVO)
 - .pre-commit-config.yaml (NOVO)

 Fase 3 (5 arquivos):
 - src/agent/core/prompt_cache.py (NOVO)
 - src/agent/core/llm_client.py (MODIFICAR)
 - src/agent/core/protocol_loader.py (MODIFICAR)
 - src/agent/validators/protocol_validator.py (MODIFICAR)
 - src/agent/feedback/memory_engine.py (MODIFICAR)

 Fase 4 (6 arquivos):
 - src/agent/db/schema.sql (NOVO)
 - src/agent/db/connection.py (NOVO)
 - src/agent/db/migrations.py (NOVO)
 - src/agent/db/writer.py (NOVO)
 - src/agent/db/queries.py (NOVO)
 - notebooks/analytics_demo.ipynb (NOVO)

 Fase 5 (4+ arquivos):
 - dashboard/app.py (NOVO)
 - dashboard/pages/overview.py (NOVO)
 - dashboard/pages/analyses.py (NOVO)
 - dashboard/pages/suggestions.py (NOVO)

 ---
 Riscos e Mitigações

 | Risco                  | Probabilidade | Impacto | Mitigação                                  |
 |------------------------|---------------|---------|--------------------------------------------|
 | Fase 1 atrasa adoção   | MÉDIO         | ALTO    | Buffer de 2 dias, priorizar exits + config |
 | Testes demorados       | MÉDIO         | MÉDIO   | Mocks extensivos, fixtures pequenas        |
 | SQLite scope creep     | BAIXO         | ALTO    | MVP rigoroso, apenas 5 tabelas             |
 | Dashboard complexidade | ALTO          | BAIXO   | Streamlit (framework simples)              |

 ---
 🚀 PRÓXIMOS PASSOS

 1. ✅ Aprovação do plano (VOCÊ ESTÁ AQUI)
 2. ⏳ Iniciar Fase 1 - Quick Wins
 3. ⏳ Daily check-ins - Acompanhar progresso
 4. ⏳ Review ao final de cada fase
 5. ⏳ Deploy em produção - Após Fase 2

 ---
 💡 RECOMENDAÇÕES FINAIS

 Core (Fases 1-4): OBRIGATÓRIO - 4 semanas
 Fase 5 (Dashboard): OPCIONAL mas RECOMENDADO - +1 semana
 Total: 5 semanas para sistema enterprise-ready

 Ritmo Sugerido: Balanceado (com buffer de 2 dias/fase)

 Este plano é flexível e será revisado ao final de cada fase com base no progresso real e feedback.