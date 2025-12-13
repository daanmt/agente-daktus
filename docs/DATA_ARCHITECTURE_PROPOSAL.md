# 🏗️ PROPOSTA: Arquitetura de Dados Moderna

**Data**: 2025-12-11  
**Autor**: Arquiteto de Soluções + Product Manager  
**Contexto**: Sistema atual usa arquivos texto (memory_qa.md, TXTs), não escalável  
**Objetivo**: Propor arquitetura de dados eficiente, escalável e consultável  

---

## 📊 PROBLEMA ATUAL

### Sistema de Arquivos Atual

```
AgenteV2/
├── memory_qa.md                    # ❌ Texto livre, não consultável
├── reports/
│   ├── protocol_v1.0.0_20251211.txt    # ❌ Sem estrutura, não agregável
│   ├── protocol_v1.0.0_EDITED.json     # ✅ Estruturado mas sem metadata
│   └── protocol_v1.0.0_AUDIT.txt       # ❌ Texto livre
└── logs/                           # ❌ Não correlacionado com análises
```

### Problemas Identificados

| Problema | Impacto | Severidade |
|----------|---------|------------|
| **Dados não-consultáveis** | Impossível responder "quantas sugestões de segurança foram geradas no último mês?" | 🔴 ALTO |
| **Sem agregações** | Impossível calcular ROI, trending, padrões | 🔴 ALTO |
| **Sem histórico temporal** | Não sabemos se qualidade está melhorando | 🔴 ALTO |
| **Sem correlação** | Não conseguimos ligar feedback → regra → bloqueio | 🔴 ALTO |
| **Memory_qa.md frágil** | Parsing complexo, propenso a erro | ⚠️ MÉDIO |
| **Sem transações** | Inconsistências em caso de crash | ⚠️ MÉDIO |
| **Sem backup estruturado** | Perda de aprendizado se arquivo corrompe | ⚠️ MÉDIO |

---

## 🎯 OBJETIVOS DA NOVA ARQUITETURA

### Requisitos Funcionais

1. **Consultabilidade**: Queries SQL para responder perguntas de negócio
2. **Agregações**: Métricas de tendência, ROI, qualidade
3. **Rastreabilidade**: Ligar feedback → regra → bloqueio → sugestão
4. **Escalabilidade**: Suportar 1000+ análises sem degradação
5. **Integridade**: Transações ACID, sem inconsistências
6. **Backup**: Sistema de backup automatizado

### Requisitos Não-Funcionais

1. **Performance**: Queries <100ms para dashboards
2. **Compatibilidade**: Manter backward compatibility com sistema atual
3. **Migração**: Migrar dados históricos sem perda
4. **Simplicidade**: SQLite (sem servidor), fácil de gerenciar

---

## 🏗️ ARQUITETURA PROPOSTA: Híbrida (SQLite + Arquivos)

### Princípio de Design

**"Structured Data in DB, Artifacts in Files"**

- **SQLite**: Dados estruturados (análises, feedbacks, regras, métricas)
- **Arquivos**: Artifacts grandes (JSONs reconstruídos, relatórios audit)
- **Vínculo**: Foreign keys ligam DB records a file paths

### Diagrama de Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                    AGENTE DAKTUS QA                          │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   DATA LAYER (Hybrid)                        │
│                                                              │
│  ┌────────────────────────┐    ┌────────────────────────┐  │
│  │   SQLite Database      │    │    File System         │  │
│  │   (daktus.db)          │    │    (artifacts/)        │  │
│  │                        │    │                        │  │
│  │ - protocols            │───▶│ - protocol JSONs       │  │
│  │ - analyses             │───▶│ - audit reports        │  │
│  │ - suggestions          │    │ - edited protocols     │  │
│  │ - feedbacks            │    │                        │  │
│  │ - rules                │    │                        │  │
│  │ - metrics              │    │                        │  │
│  │ - sessions             │    │                        │  │
│  └────────────────────────┘    └────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 📐 SCHEMA DO BANCO DE DADOS

### Tabela 1: protocols

**Propósito**: Armazenar metadata de protocolos clínicos

```sql
CREATE TABLE protocols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_name TEXT NOT NULL,              -- "amil_ficha_cardiologia"
    version TEXT NOT NULL,                    -- "1.0.0", "1.0.1"
    specialty TEXT,                           -- "cardiologia", "pre-natal"
    company TEXT,                             -- "Amil", "Athena"
    
    -- File paths
    original_file_path TEXT NOT NULL,         -- "models_json/protocol.json"
    current_file_path TEXT NOT NULL,          -- "models_json/protocol_v1.0.1.json"
    
    -- Metadata
    node_count INTEGER,
    question_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Status
    status TEXT DEFAULT 'active',             -- 'active', 'archived', 'deprecated'
    
    UNIQUE(protocol_name, version)
);

CREATE INDEX idx_protocols_name ON protocols(protocol_name);
CREATE INDEX idx_protocols_status ON protocols(status);
```

**Queries úteis**:
```sql
-- Protocolos mais analisados
SELECT protocol_name, COUNT(*) as analysis_count
FROM analyses
GROUP BY protocol_name
ORDER BY analysis_count DESC;

-- Evolução de versões
SELECT protocol_name, version, created_at
FROM protocols
WHERE protocol_name = 'amil_ficha_cardiologia'
ORDER BY created_at;
```

---

### Tabela 2: playbooks

**Propósito**: Armazenar metadata de playbooks clínicos

```sql
CREATE TABLE playbooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playbook_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    specialty TEXT,
    
    -- Content metadata
    section_count INTEGER,
    word_count INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(playbook_name)
);
```

---

### Tabela 3: analyses

**Propósito**: Registrar cada execução de análise

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,                 -- UUID da sessão
    
    -- Protocol & Playbook
    protocol_id INTEGER NOT NULL,
    playbook_id INTEGER,                      -- NULL se sem playbook
    
    -- LLM
    model_used TEXT NOT NULL,                 -- "claude-sonnet-4.5"
    
    -- Results
    total_suggestions INTEGER DEFAULT 0,
    high_priority INTEGER DEFAULT 0,
    medium_priority INTEGER DEFAULT 0,
    low_priority INTEGER DEFAULT 0,
    
    -- Cost
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    actual_cost REAL DEFAULT 0.0,
    
    -- Timing
    duration_seconds REAL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    
    -- Status
    status TEXT DEFAULT 'pending',            -- 'pending', 'completed', 'failed', 'cancelled'
    error_message TEXT,
    
    -- Report paths
    report_txt_path TEXT,
    report_json_path TEXT,
    
    FOREIGN KEY (protocol_id) REFERENCES protocols(id),
    FOREIGN KEY (playbook_id) REFERENCES playbooks(id)
);

CREATE INDEX idx_analyses_session ON analyses(session_id);
CREATE INDEX idx_analyses_protocol ON analyses(protocol_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_date ON analyses(started_at);
```

**Queries úteis**:
```sql
-- Custo total por mês
SELECT 
    strftime('%Y-%m', started_at) as month,
    SUM(actual_cost) as total_cost,
    COUNT(*) as analysis_count
FROM analyses
WHERE status = 'completed'
GROUP BY month
ORDER BY month DESC;

-- Análises mais caras
SELECT 
    p.protocol_name,
    a.actual_cost,
    a.total_suggestions,
    a.model_used
FROM analyses a
JOIN protocols p ON a.protocol_id = p.id
WHERE a.status = 'completed'
ORDER BY a.actual_cost DESC
LIMIT 10;

-- Taxa de sucesso
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM analyses), 2) as percentage
FROM analyses
GROUP BY status;
```

---

### Tabela 4: suggestions

**Propósito**: Armazenar cada sugestão gerada

```sql
CREATE TABLE suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    
    -- Suggestion metadata
    suggestion_id TEXT NOT NULL,              -- "sug_001"
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,                            -- "seguranca", "economia", "eficiencia"
    priority TEXT,                            -- "alta", "media", "baixa"
    
    -- Impact scores
    safety_score INTEGER,                     -- 0-10
    economy_level TEXT,                       -- "L", "M", "A"
    efficiency_score INTEGER,                 -- 0-10
    usability_score INTEGER,                  -- 0-10
    
    -- Location
    node_id TEXT,
    question_uid TEXT,
    json_path TEXT,
    
    -- Playbook reference
    playbook_reference TEXT,
    playbook_reference_valid BOOLEAN,         -- Validado pelo Reference Validator
    
    -- Implementation
    modification_type TEXT,                   -- "add_option", "modify_condition", etc.
    proposed_value TEXT,
    
    -- User feedback
    feedback TEXT,                            -- "relevant", "irrelevant", "questionable", NULL
    feedback_comment TEXT,
    feedback_timestamp TIMESTAMP,
    
    -- Reconstruction
    applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

CREATE INDEX idx_suggestions_analysis ON suggestions(analysis_id);
CREATE INDEX idx_suggestions_feedback ON suggestions(feedback);
CREATE INDEX idx_suggestions_category ON suggestions(category);
CREATE INDEX idx_suggestions_applied ON suggestions(applied);
```

**Queries úteis**:
```sql
-- Taxa de aceitação por categoria
SELECT 
    category,
    COUNT(*) as total,
    SUM(CASE WHEN feedback = 'relevant' THEN 1 ELSE 0 END) as accepted,
    ROUND(SUM(CASE WHEN feedback = 'relevant' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as acceptance_rate
FROM suggestions
WHERE feedback IS NOT NULL
GROUP BY category
ORDER BY acceptance_rate DESC;

-- Sugestões mais rejeitadas (por padrão)
SELECT 
    title,
    COUNT(*) as rejection_count,
    GROUP_CONCAT(DISTINCT feedback_comment) as reasons
FROM suggestions
WHERE feedback = 'irrelevant'
GROUP BY title
HAVING rejection_count > 2
ORDER BY rejection_count DESC;

-- ROI por categoria (sugestões aplicadas / custo)
SELECT 
    s.category,
    COUNT(*) as applied_count,
    AVG(s.safety_score) as avg_safety,
    AVG(a.actual_cost) as avg_cost_per_analysis
FROM suggestions s
JOIN analyses a ON s.analysis_id = a.id
WHERE s.applied = TRUE
GROUP BY s.category;
```

---

### Tabela 5: rules

**Propósito**: Armazenar Hard Rules e Soft Rules aprendidas

```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT UNIQUE NOT NULL,             -- "fb_20251211_001"
    rule_type TEXT NOT NULL,                  -- "hard" ou "soft"
    
    -- Rule details
    classification TEXT NOT NULL,             -- "reference_whitelist", "forbidden_pattern", etc.
    condition TEXT NOT NULL,                  -- JSON string
    block_message TEXT,
    
    -- Source
    source TEXT NOT NULL,                     -- "user_feedback", "playbook_rule", "system_constraint"
    source_feedback_id INTEGER,               -- FK para feedback que gerou a regra
    
    -- Status
    active BOOLEAN DEFAULT TRUE,
    activation_count INTEGER DEFAULT 0,       -- Quantas vezes foi ativada
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP,
    
    FOREIGN KEY (source_feedback_id) REFERENCES suggestions(id)
);

CREATE INDEX idx_rules_type ON rules(rule_type);
CREATE INDEX idx_rules_active ON rules(active);
CREATE INDEX idx_rules_source ON rules(source);
```

**Queries úteis**:
```sql
-- Regras mais ativadas
SELECT 
    rule_id,
    classification,
    activation_count,
    block_message
FROM rules
WHERE active = TRUE
ORDER BY activation_count DESC
LIMIT 10;

-- Regras aprendidas com feedback
SELECT 
    r.rule_id,
    r.block_message,
    s.feedback_comment as original_feedback,
    r.activation_count,
    r.created_at
FROM rules r
LEFT JOIN suggestions s ON r.source_feedback_id = s.id
WHERE r.source = 'user_feedback'
ORDER BY r.created_at DESC;

-- Eficácia de regras (bloqueios / tentativas)
SELECT 
    rule_id,
    block_message,
    activation_count
FROM rules
WHERE activation_count > 0
ORDER BY activation_count DESC;
```

---

### Tabela 6: reconstructions

**Propósito**: Registrar cada reconstrução de protocolo

```sql
CREATE TABLE reconstructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    
    -- Protocol versions
    source_protocol_id INTEGER NOT NULL,
    source_version TEXT NOT NULL,
    target_version TEXT NOT NULL,              -- "1.0.1", "2.0.0"
    version_increment TEXT NOT NULL,           -- "PATCH", "MINOR", "MAJOR"
    
    -- Suggestions applied
    total_suggestions INTEGER DEFAULT 0,
    applied_suggestions INTEGER DEFAULT 0,
    failed_suggestions INTEGER DEFAULT 0,
    
    -- Files
    reconstructed_file_path TEXT NOT NULL,
    audit_report_path TEXT,
    
    -- Validation
    validation_status TEXT DEFAULT 'pending',  -- 'pending', 'passed', 'failed'
    validation_errors TEXT,                    -- JSON array
    
    -- Timing
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    
    -- Status
    status TEXT DEFAULT 'pending',             -- 'pending', 'completed', 'failed'
    error_message TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    FOREIGN KEY (source_protocol_id) REFERENCES protocols(id)
);

CREATE INDEX idx_reconstructions_analysis ON reconstructions(analysis_id);
CREATE INDEX idx_reconstructions_status ON reconstructions(status);
```

**Queries úteis**:
```sql
-- Taxa de sucesso de reconstrução
SELECT 
    validation_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reconstructions), 2) as percentage
FROM reconstructions
GROUP BY validation_status;

-- Protocolos com mais reconstruções
SELECT 
    p.protocol_name,
    COUNT(r.id) as reconstruction_count,
    AVG(r.applied_suggestions) as avg_applied
FROM reconstructions r
JOIN protocols p ON r.source_protocol_id = p.id
WHERE r.status = 'completed'
GROUP BY p.protocol_name
ORDER BY reconstruction_count DESC;

-- Evolução de versões
SELECT 
    p.protocol_name,
    r.source_version,
    r.target_version,
    r.version_increment,
    r.applied_suggestions,
    r.completed_at
FROM reconstructions r
JOIN protocols p ON r.source_protocol_id = p.id
WHERE r.status = 'completed'
ORDER BY p.protocol_name, r.completed_at;
```

---

### Tabela 7: sessions

**Propósito**: Agregar informações de sessão (análise + feedback + reconstrução)

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,          -- UUID
    
    -- User info (se aplicável)
    user_id TEXT,
    user_name TEXT,
    
    -- Session flow
    analysis_id INTEGER,
    reconstruction_id INTEGER,
    
    -- Timing
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds REAL,
    
    -- Status
    status TEXT DEFAULT 'active',             -- 'active', 'completed', 'abandoned'
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    FOREIGN KEY (reconstruction_id) REFERENCES reconstructions(id)
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_date ON sessions(started_at);
```

---

### Tabela 8: metrics

**Propósito**: Armazenar métricas agregadas para dashboards

```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,                -- "daily_cost", "acceptance_rate", "avg_suggestions"
    metric_date DATE NOT NULL,
    metric_value REAL NOT NULL,
    metric_metadata TEXT,                     -- JSON com detalhes extras
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(metric_type, metric_date)
);

CREATE INDEX idx_metrics_type_date ON metrics(metric_type, metric_date);
```

**Uso**:
```sql
-- Inserir métrica diária
INSERT INTO metrics (metric_type, metric_date, metric_value, metric_metadata)
VALUES (
    'daily_cost',
    DATE('now'),
    (SELECT SUM(actual_cost) FROM analyses WHERE DATE(started_at) = DATE('now')),
    json_object('analysis_count', (SELECT COUNT(*) FROM analyses WHERE DATE(started_at) = DATE('now')))
);

-- Trending de custo
SELECT 
    metric_date,
    metric_value as daily_cost
FROM metrics
WHERE metric_type = 'daily_cost'
ORDER BY metric_date DESC
LIMIT 30;
```

---

## 📦 CAMADA DE ABSTRAÇÃO: Data Access Layer (DAL)

### Arquitetura do DAL

```python
# src/agent/data/
├── __init__.py
├── database.py          # Conexão e inicialização
├── models.py            # SQLAlchemy models (opcional)
├── repositories/
│   ├── protocol_repo.py
│   ├── analysis_repo.py
│   ├── suggestion_repo.py
│   ├── rule_repo.py
│   └── metrics_repo.py
└── migrations/
    └── 001_initial_schema.sql
```

### Exemplo: AnalysisRepository

```python
# src/agent/data/repositories/analysis_repo.py

from typing import Optional, List
from datetime import datetime
import sqlite3
from pathlib import Path

class AnalysisRepository:
    """Repository para operações de análise."""
    
    def __init__(self, db_path: str = "daktus.db"):
        self.db_path = db_path
    
    def create(
        self,
        session_id: str,
        protocol_id: int,
        playbook_id: Optional[int],
        model_used: str
    ) -> int:
        """Cria nova análise e retorna ID."""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyses (
                    session_id, protocol_id, playbook_id, model_used, started_at, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, protocol_id, playbook_id, model_used, datetime.now(), 'pending'))
            
            return cursor.lastrowid
    
    def update_completion(
        self,
        analysis_id: int,
        total_suggestions: int,
        high_priority: int,
        medium_priority: int,
        low_priority: int,
        input_tokens: int,
        output_tokens: int,
        actual_cost: float,
        duration_seconds: float,
        report_txt_path: str,
        report_json_path: str
    ):
        """Atualiza análise ao completar."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE analyses SET
                    total_suggestions = ?,
                    high_priority = ?,
                    medium_priority = ?,
                    low_priority = ?,
                    input_tokens = ?,
                    output_tokens = ?,
                    actual_cost = ?,
                    duration_seconds = ?,
                    completed_at = ?,
                    status = 'completed',
                    report_txt_path = ?,
                    report_json_path = ?
                WHERE id = ?
            """, (
                total_suggestions, high_priority, medium_priority, low_priority,
                input_tokens, output_tokens, actual_cost, duration_seconds,
                datetime.now(), report_txt_path, report_json_path, analysis_id
            ))
    
    def get_by_id(self, analysis_id: int) -> Optional[dict]:
        """Busca análise por ID."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
    
    def get_recent(self, limit: int = 10) -> List[dict]:
        """Busca análises recentes."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM analyses
                ORDER BY started_at DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_by_month(self, year: int, month: int) -> float:
        """Calcula custo total do mês."""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(actual_cost) as total
                FROM analyses
                WHERE strftime('%Y', started_at) = ?
                  AND strftime('%m', started_at) = ?
                  AND status = 'completed'
            """, (str(year), f"{month:02d}"))
            
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0
```

---

## 🔄 MIGRAÇÃO: Sistema Atual → Novo Sistema

### Estratégia de Migração

**Fase 1: Dual-Write** (1-2 semanas)
- Sistema grava em AMBOS (arquivos + DB)
- Leitura ainda usa arquivos (backward compatibility)
- Zero breaking changes

**Fase 2: Dual-Read** (1 semana)
- Sistema tenta ler do DB primeiro
- Fallback para arquivos se não encontrar
- Validação de consistência

**Fase 3: DB-Only** (1 semana)
- Sistema usa apenas DB
- Arquivos mantidos apenas para artifacts (JSONs, PDFs)
- Migração histórica completa

### Script de Migração: memory_qa.md → Database

```python
# scripts/migrate_memory_to_db.py

import re
from datetime import datetime
from agent.data.repositories.rule_repo import RuleRepository

def parse_memory_qa(memory_path: str) -> List[dict]:
    """Parse memory_qa.md para extrair regras."""
    
    with open(memory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    rules = []
    
    # Exemplo de padrão:
    # ## Padrão: Invasão da Autonomia Médica
    # Frequência: 3
    # Descrição: Sugestões que tentam impor escolhas clínicas
    
    pattern = r'## Padrão: (.+?)\nFrequência: (\d+)\nDescrição: (.+?)(?=\n##|\Z)'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        pattern_name = match.group(1).strip()
        frequency = int(match.group(2))
        description = match.group(3).strip()
        
        rules.append({
            'rule_id': f"migrated_{pattern_name.lower().replace(' ', '_')}",
            'rule_type': 'soft',
            'classification': 'forbidden_pattern',
            'condition': {'pattern': pattern_name},
            'block_message': description,
            'source': 'user_feedback',
            'activation_count': frequency,
            'created_at': datetime.now()
        })
    
    return rules

def migrate():
    """Executa migração completa."""
    
    repo = RuleRepository()
    rules = parse_memory_qa('memory_qa.md')
    
    for rule in rules:
        repo.create(**rule)
        print(f"✅ Migrado: {rule['rule_id']}")
    
    print(f"\n🎉 Migração completa: {len(rules)} regras migradas")

if __name__ == "__main__":
    migrate()
```

---

## 📊 DASHBOARD & ANALYTICS

### Queries Úteis para Dashboard

#### 1. KPIs Principais
```sql
-- KPI: Custo total (mês atual)
SELECT SUM(actual_cost) as total_cost
FROM analyses
WHERE strftime('%Y-%m', started_at) = strftime('%Y-%m', 'now')
  AND status = 'completed';

-- KPI: Taxa de aceitação
SELECT 
    ROUND(
        SUM(CASE WHEN feedback = 'relevant' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) as acceptance_rate
FROM suggestions
WHERE feedback IS NOT NULL;

-- KPI: ROI (sugestões aplicadas / custo)
SELECT 
    COUNT(*) as applied_suggestions,
    SUM(a.actual_cost) as total_cost,
    ROUND(COUNT(*) * 1.0 / SUM(a.actual_cost), 2) as roi
FROM suggestions s
JOIN analyses a ON s.analysis_id = a.id
WHERE s.applied = TRUE;

-- KPI: Tempo médio de análise
SELECT 
    AVG(duration_seconds) as avg_seconds,
    ROUND(AVG(duration_seconds) / 60, 2) as avg_minutes
FROM analyses
WHERE status = 'completed';
```

#### 2. Trending (últimos 30 dias)
```sql
-- Custo diário
SELECT 
    DATE(started_at) as date,
    SUM(actual_cost) as daily_cost
FROM analyses
WHERE started_at >= DATE('now', '-30 days')
  AND status = 'completed'
GROUP BY DATE(started_at)
ORDER BY date;

-- Sugestões por categoria (últimos 30 dias)
SELECT 
    DATE(a.started_at) as date,
    s.category,
    COUNT(*) as count
FROM suggestions s
JOIN analyses a ON s.analysis_id = a.id
WHERE a.started_at >= DATE('now', '-30 days')
GROUP BY DATE(a.started_at), s.category
ORDER BY date, category;
```

#### 3. Top/Bottom Lists
```sql
-- Top 10 protocolos por custo
SELECT 
    p.protocol_name,
    COUNT(a.id) as analysis_count,
    SUM(a.actual_cost) as total_cost,
    AVG(a.actual_cost) as avg_cost
FROM analyses a
JOIN protocols p ON a.protocol_id = p.id
WHERE a.status = 'completed'
GROUP BY p.protocol_name
ORDER BY total_cost DESC
LIMIT 10;

-- Top 10 regras mais ativadas
SELECT 
    rule_id,
    block_message,
    activation_count
FROM rules
WHERE active = TRUE
ORDER BY activation_count DESC
LIMIT 10;

-- Piores categorias de sugestões (menor taxa de aceitação)
SELECT 
    category,
    COUNT(*) as total,
    SUM(CASE WHEN feedback = 'relevant' THEN 1 ELSE 0 END) as accepted,
    ROUND(
        SUM(CASE WHEN feedback = 'relevant' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) as acceptance_rate
FROM suggestions
WHERE feedback IS NOT NULL
GROUP BY category
ORDER BY acceptance_rate ASC
LIMIT 10;
```

---

## 🚀 IMPLEMENTAÇÃO: Roadmap

### FASE 1: Setup Inicial (1-2 dias)

**Tarefas**:
1. Criar schema inicial (`daktus.db`)
2. Criar Data Access Layer (repositories)
3. Criar scripts de migração
4. Testes unitários de repositories

**Entregáveis**:
- ✅ `src/agent/data/database.py`
- ✅ `src/agent/data/repositories/`
- ✅ `scripts/migrate_memory_to_db.py`
- ✅ `tests/test_repositories.py`

---

### FASE 2: Dual-Write (3-5 dias)

**Tarefas**:
1. Integrar AnalysisRepository em Enhanced Analyzer
2. Integrar SuggestionRepository em Feedback Collector
3. Integrar RuleRepository em Rules Engine
4. Manter escrita em arquivos (backward compatibility)

**Exemplo**:
```python
# src/agent/analysis/enhanced.py

from ..data.repositories.analysis_repo import AnalysisRepository

class EnhancedAnalyzer:
    def __init__(self, ...):
        self.analysis_repo = AnalysisRepository()
    
    def analyze(self, ...):
        # Criar registro de análise
        analysis_id = self.analysis_repo.create(
            session_id=self.session_id,
            protocol_id=self._get_protocol_id(),
            playbook_id=self._get_playbook_id(),
            model_used=self.model
        )
        
        # ... análise ...
        
        # Atualizar com resultados
        self.analysis_repo.update_completion(
            analysis_id=analysis_id,
            total_suggestions=len(suggestions),
            ...
        )
        
        # TAMBÉM grava arquivo TXT (dual-write)
        self._save_report_txt(...)
```

---

### FASE 3: Dual-Read (1-2 dias)

**Tarefas**:
1. Sistema tenta ler do DB primeiro
2. Fallback para arquivos se não encontrar
3. Validação de consistência

```python
def load_analysis_results(analysis_id: str):
    """Carrega resultados de análise."""
    
    # Tentar DB primeiro
    repo = AnalysisRepository()
    result = repo.get_by_id(analysis_id)
    
    if result:
        logger.info("✅ Loaded from database")
        return result
    
    # Fallback para arquivo TXT
    logger.warning("⚠️ Not found in DB, loading from TXT")
    return load_from_txt(f"reports/analysis_{analysis_id}.txt")
```

---

### FASE 4: DB-Only (1-2 dias)

**Tarefas**:
1. Remover fallbacks para arquivos
2. Migrar histórico completo
3. Validação final

---

### FASE 5: Dashboard (3-5 dias - OPCIONAL)

**Tarefas**:
1. Criar CLI de analytics
2. Ou criar dashboard web (Streamlit/Flask)

**Exemplo CLI**:
```bash
# Ver KPIs do mês
python -m agent.analytics kpis --month 2025-12

# Ver trending de custo
python -m agent.analytics trending --days 30

# Ver top protocolos
python -m agent.analytics top-protocols --limit 10
```

---

## 💰 ANÁLISE CUSTO-BENEFÍCIO

### Custos

| Item | Esforço | Custo |
|------|---------|-------|
| Setup inicial | 1-2 dias | 🟢 BAIXO |
| Dual-write | 3-5 dias | 🟡 MÉDIO |
| Migração | 2-3 dias | 🟡 MÉDIO |
| Dashboard | 3-5 dias | 🟡 MÉDIO (opcional) |
| **TOTAL** | **9-15 dias** | **MÉDIO** |

### Benefícios

| Benefício | Impacto | Valor |
|-----------|---------|-------|
| **Consultabilidade** | Responder perguntas de negócio em segundos | 🔴 ALTO |
| **Agregações** | KPIs, ROI, trending automáticos | 🔴 ALTO |
| **Rastreabilidade** | Audit trail completo | 🔴 ALTO |
| **Escalabilidade** | Suporta 1000+ análises | 🔴 ALTO |
| **Integridade** | Zero inconsistências | 🟡 MÉDIO |
| **Backup** | Backup estruturado | 🟡 MÉDIO |

### ROI Estimado

**Cenário**: 100 análises/mês

**Antes**:
- Tempo para responder "qual o custo do último mês?" → 30 min (parsing manual)
- Tempo para calcular ROI → 1 hora (cruzamento manual)
- Risco de inconsistência → ALTO

**Depois**:
- Tempo para responder "qual o custo do último mês?" → 2 segundos (SQL query)
- Tempo para calcular ROI → 2 segundos (SQL query)
- Risco de inconsistência → ZERO

**Economia**: 10-15 horas/mês em análise manual

---

## 🎯 RECOMENDAÇÃO FINAL

### Estratégia Sugerida

**OPÇÃO 1: Implementação Completa (RECOMENDADO)**
- Todas as 5 fases
- Timeline: 2-3 semanas
- Valor: ROI claro, sistema escalável

**OPÇÃO 2: MVP (Alternativa para validação rápida)**
- Apenas Fases 1-3 (Setup + Dual-write + Dual-read)
- Timeline: 1 semana
- Valor: Prova de conceito, valida arquitetura

**OPÇÃO 3: Gradual (Menor risco)**
- Começar apenas com `analyses` e `suggestions`
- Expandir para outras tabelas depois
- Timeline: 1-2 semanas iniciais

### Próximos Passos Imediatos

1. **Decisão de Go/No-Go**: Aprovar arquitetura proposta
2. **Priorização**: Definir qual opção (Completa/MVP/Gradual)
3. **Setup**: Criar schema inicial do DB
4. **Migração**: Script de migração de memory_qa.md
5. **Integração**: Dual-write nos componentes principais

---

## 📞 QUESTÕES EM ABERTO

1. **Dashboard**: Precisa de interface web ou CLI é suficiente?
2. **Backup**: Automatizar backup do SQLite (cron job)?
3. **Multi-user**: Sistema deve suportar múltiplos usuários simultaneamente?
4. **Cloud**: Planos de hospedar DB em cloud (S3, GCS)?
5. **Analytics avançado**: Precisa de ML/forecasting sobre os dados?

---

**FIM DA PROPOSTA**
