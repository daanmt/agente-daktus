# 🧠 MEMÓRIA OPERACIONAL DO AGENTE: BOAS PRÁTICAS PARA MODIFICAÇÃO DE PROTOCOLOS CLÍNICOS

**Objetivo:** Este documento contém a "inteligência operacional" que deve guiar o agente em todas as tarefas de análise e modificação de protocolos clínicos JSON.

**Contexto:** Exportar expertise humana para automação inteligente

---

## 📋 ÍNDICE

1. Filosofia de trabalho
2. Workflow padrão (obrigatório)
3. Princípios de decisão
4. Red flags e quando parar
5. Padrões de qualidade
6. Checklist pré-deploy
7. Casos especiais e exceções

---

## 🎯 1. FILOSOFIA DE TRABALHO

### 1.1 Princípio fundamental: **"Primeiro entender, depois modificar"**

❌ **NUNCA fazer:**
- Modificar JSON sem analisar estrutura primeiro
- Adicionar item sem verificar se já existe
- Copiar estruturas de outros protocolos sem adaptar
- Aplicar mudanças sem validação

✅ **SEMPRE fazer:**
- Carregar JSON e inspecionar estrutura
- Buscar padrões existentes
- Validar antes e depois de modificações
- Documentar todas as mudanças

---

### 1.2 Hierarquia de prioridades

```
1. SEGURANÇA CLÍNICA (máxima prioridade)
   └─ Nunca introduzir erros que possam prejudicar pacientes
   └─ Gates de segurança são invioláveis
   └─ Red flags devem sempre bloquear condutas perigosas

2. CONSISTÊNCIA ESTRUTURAL
   └─ Manter padrões do JSON existente
   └─ IDs únicos e descritivos
   └─ Seguir nomenclatura estabelecida

3. EVIDÊNCIAS CIENTÍFICAS
   └─ Toda recomendação deve ter referência
   └─ Diretrizes recentes têm prioridade
   └─ Nível de evidência deve ser explícito

4. USABILIDADE MÉDICA
   └─ Fluxo intuitivo para médicos
   └─ Mensagens claras e acionáveis
   └─ Evitar complexidade desnecessária

5. RASTREABILIDADE
   └─ Metadata sempre atualizada
   └─ Mudanças documentadas
   └─ Versionamento claro
```

---

## 🔄 2. WORKFLOW PADRÃO (OBRIGATÓRIO)

### Fase 1: ANÁLISE INICIAL (sempre primeiro)

```python
# 1.1 CARREGAR E INSPECIONAR
protocol = load_json('protocolo.json')
print(f"Nodes: {len(protocol['nodes'])}")
print(f"Edges: {len(protocol['edges'])}")

# 1.2 IDENTIFICAR NODE-ALVO
target_node, target_idx = find_node_by_id(protocol, 'conduta-1754085461792')

# 1.3 BASELINE METRICS
baseline = validate_structure(protocol, "ANTES")

# 1.4 ENTENDER CONTEXTO
# Ler metadata, changes, lastModified
# Identificar versão atual
# Compreender escopo do protocolo
```

**⏱️ Tempo estimado:** 2-3 minutos  
**🚨 Se pular esta fase:** Alto risco de duplicação, inconsistência, erros estruturais

---

### Fase 2: BUSCA PRÉ-MODIFICAÇÃO (evita duplicação)

```python
# 2.1 VERIFICAR SE ITEM JÁ EXISTE
existing_exams = search_exams(conduct_node, ['bnp', 'ntprobnp'])

if existing_exams:
    print("⚠️ Item já existe:")
    for exam in existing_exams:
        print(f"  • {exam['nome']} (ID: {exam['id']})")
    
    # DECISÃO: Atualizar existente ou criar novo?
    # Se atualizar: usar str_replace ou dict update
    # Se novo: adicionar com ID diferente
else:
    print("✓ Item não existe, pode adicionar")

# 2.2 BUSCAR PADRÕES EXISTENTES
# Analisar estrutura de exames similares
# Copiar padrão de IDs, condições, observações
# Manter consistência
```

**⏱️ Tempo estimado:** 1-2 minutos  
**🚨 Se pular esta fase:** Duplicação, conflitos de ID, inconsistência estrutural

---

### Fase 3: MODIFICAÇÃO (seguir padrões)

```python
# 3.1 PREPARAR ESTRUTURA
# Seguir exatamente o padrão existente no JSON
exam_new = {
    "id": "exam-bnp-dm2-rastreamento",  # ID único, descritivo
    "nome": "BNP - Peptídeo Natriurético Tipo B",  # Nome completo
    "codigo": "40316130",  # Código TUSS correto
    "condicional": "visivel",  # Sempre "visivel" para condutas
    "condicao": "'diabetes' in comorbidades or 'dm2' in comorbidades",  # Condição Python-like
    "observacao": "Rastreamento IC estágio B em DM2 (ADA 2025). Valor de corte: ≥50 pg/mL."  # Referência + valor clínico
}

# 3.2 ADICIONAR
add_exam(conduct_node, exam_new)

# 3.3 ATUALIZAR PROTOCOL
protocol['nodes'][target_idx] = conduct_node

# 3.4 UPDATE METADATA
update_metadata(protocol, "BNP/NT-proBNP para rastreamento IC em DM2 (ADA 2025)")
```

**⏱️ Tempo estimado:** 3-5 minutos  
**🚨 Atenção:** IDs duplicados, sintaxe incorreta em condições, falta de referências

---

### Fase 4: VALIDAÇÃO (obrigatória antes de salvar)

```python
# 4.1 VALIDAR ESTRUTURA
after = validate_structure(protocol, "DEPOIS")

# Comparar baseline vs after
for key in baseline:
    diff = after[key] - baseline[key]
    if diff != 0:
        print(f"  {key}: {baseline[key]} → {after[key]} ({diff:+d})")

# 4.2 CHECK DUPLICATES
duplicates = check_duplicates(protocol)

if any(len(v) > 0 for v in duplicates.values()):
    print("🚨 DUPLICATAS DETECTADAS - NÃO SALVAR")
    # Fix duplicatas antes de prosseguir

# 4.3 VALIDAR CONDIÇÕES
issues = validate_conditions(protocol)

if issues:
    print(f"⚠️ {len(issues)} condições com possíveis problemas")
    # Revisar e corrigir

# 4.4 TESTE FUNCIONAL (se possível)
# Simular fluxo: paciente com diabetes deve ver BNP
# Simular fluxo: paciente sem diabetes NÃO deve ver BNP
```

**⏱️ Tempo estimado:** 2-3 minutos  
**🚨 Se pular esta fase:** Protocolo quebrado pode ser deployado, causando erros em produção

---

### Fase 5: SALVAMENTO (com backup)

```python
# 5.1 BACKUP DO ORIGINAL (sempre)
import shutil
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f'protocolo_backup_{timestamp}.json'
shutil.copy('protocolo.json', backup_file)
print(f"✓ Backup criado: {backup_file}")

# 5.2 SALVAR MODIFICADO
with open('protocolo.json', 'w', encoding='utf-8') as f:
    json.dump(protocol, f, ensure_ascii=False, indent=2)

print("✓ Protocolo atualizado salvo")

# 5.3 GERAR RELATÓRIO
# Listar todas as mudanças
# Métricas antes/depois
# Referências adicionadas
```

**⏱️ Tempo estimado:** 1 minuto  
**🚨 Atenção:** Sempre UTF-8, sempre indent 2, sempre backup

---

## 🧭 3. PRINCÍPIOS DE DECISÃO

### 3.1 Quando adicionar vs quando modificar?

**ADICIONAR novo item quando:**
- Item completamente novo (ex: BNP em DM2 nunca existiu)
- Funcionalidade nova de diretriz recente
- Expansão de escopo do protocolo

**MODIFICAR item existente quando:**
- Atualizar referência (diretriz antiga → nova)
- Corrigir erro (threshold incorreto)
- Melhorar texto (mensagem educativa)

**⚠️ NUNCA modificar se:**
- Não tem certeza do impacto
- Mudança pode quebrar fluxo existente
- Não consegue validar resultado

---

### 3.2 Como escolher o node correto?

```
CONDUCT NODE (conduta-1754085461792):
  ├─ Exames
  ├─ Mensagens educativas ao médico
  ├─ Orientações ao paciente
  └─ Prescrições

ANAMNESE NODE (node-1754054008885):
  ├─ Perguntas sobre sintomas
  ├─ História clínica
  └─ Motivo da consulta

CUSTOM NODES:
  ├─ Perguntas específicas de domínio
  ├─ Clinical expressions
  └─ Fluxos condicionais
```

**Regra simples:**
- **Exames/mensagens/orientações** → CONDUCT node
- **Perguntas ao paciente** → ANAMNESE ou CUSTOM nodes
- **Calculadoras/scores** → Clinical expressions no CUSTOM node

---

### 3.3 Como escrever condições corretas?

**✅ SINTAXE CORRETA:**
```python
# Comparação
"'diabetes' in comorbidades"  # Aspas simples na string, simples no Python

# Múltiplas condições
"'diabetes' in comorbidades or 'dm2' in comorbidades"

# Negação
"not('ecg_normal' in ecg_resultado)"

# Comparação numérica
"age >= 65"

# Condições complexas
"('fa' in comorbidades or 'flutter_atrial' in comorbidades) and 'dispneia' in main"
```

**❌ ERROS COMUNS:**
```python
# Uso de = ao invés de ==
"diabetes = true"  # ERRADO
"diabetes == true"  # CORRETO

# Aspas inconsistentes
"diabetes in comorbidades"  # ERRADO (falta aspas em 'diabetes')
"'diabetes' in comorbidades"  # CORRETO

# Sintaxe não-Python
"diabetes AND age > 65"  # ERRADO (AND maiúsculo)
"diabetes and age > 65"  # CORRETO
```

---

### 3.4 Como nomear IDs?

**Padrão obrigatório:**
```
EXAMES:
  exam-<nome>-<contexto>-<função>
  Exemplos:
    exam-bnp-dm2-rastreamento
    exam-troponina-sca-diagnostico
    exam-ecott-fa-avaliacao

MENSAGENS:
  msg-<tipo>-<tópico>-<função>
  Exemplos:
    msg-educativa-bnp-dm2-rastreamento
    msg-critico-sincope-esforco
    msg-alerta-estatina-dac

PERGUNTAS:
  P-<tópico>-<aspecto>
  Exemplos:
    P-sincope-contexto
    P-sincope-frequencia
    P-sincope-prodromos

ORIENTAÇÕES:
  orientacao-<tópico>-<público>
  Exemplos:
    orientacao-bnp-dm2-paciente
    orientacao-estatina-adesao-paciente
```

**Regra de ouro:** ID deve ser autoexplicativo. Outro desenvolvedor deve entender o que é só lendo o ID.

---

## 🚨 4. RED FLAGS E QUANDO PARAR

### 4.1 Red flags técnicos (PARAR IMEDIATAMENTE)

🔴 **Duplicação de IDs**
```
Se detect_duplicates() retornar qualquer item:
  → PARAR
  → Corrigir duplicatas
  → Validar novamente
  → Só então continuar
```

🔴 **JSON inválido**
```
Se json.load() falhar:
  → PARAR
  → Verificar sintaxe JSON
  → Usar validator online
  → Corrigir manualmente
```

🔴 **Condições com sintaxe incorreta**
```
Se validate_conditions() retornar erros:
  → PARAR
  → Revisar cada condição
  → Testar isoladamente
  → Corrigir antes de salvar
```

🔴 **Estrutura corrompida**
```
Se after_metrics mostrar quedas inesperadas:
  (ex: nodes: 18 → 15)
  → PARAR
  → Reverter para backup
  → Identificar o que deu errado
  → Refazer com cuidado
```

---

### 4.2 Red flags clínicos (ESCALAR PARA HUMANO)

🟡 **Segurança do paciente em risco**
```
Situações que requerem validação médica:
  - Adicionar/remover gates de segurança
  - Modificar thresholds de risco (ex: PREVENT)
  - Alterar indicações de exames obrigatórios
  - Mudar condutas críticas (estatina em DAC, etc)

AÇÃO:
  → Implementar mudança
  → Marcar para revisão médica
  → NÃO deployar sem aprovação
```

🟡 **Diretrizes conflitantes**
```
Se encontrar:
  - AHA 2024 vs ESC 2020 com recomendações diferentes
  - SBC 2025 vs ACC/AHA 2025 divergentes

AÇÃO:
  → Documentar conflito
  → Escolher diretriz mais recente E mais específica
  → Adicionar nota explicativa
  → Marcar para revisão médica
```

🟡 **Ausência de evidências**
```
Se modificação não tem referência bibliográfica:
  → PARAR
  → Buscar evidências
  → Se não encontrar: não implementar
  → Escalar para médico se crítico
```

---

## ✅ 5. PADRÕES DE QUALIDADE

### 5.1 Checklist: Exame bem estruturado

```json
{
  "id": "exam-bnp-dm2-rastreamento",  ✓ ID único, descritivo
  "nome": "BNP - Peptídeo Natriurético Tipo B",  ✓ Nome completo oficial
  "codigo": "40316130",  ✓ Código TUSS correto
  "condicional": "visivel",  ✓ Sempre "visivel"
  "condicao": "'diabetes' in comorbidades or 'dm2' in comorbidades",  ✓ Condição clara
  "observacao": "Rastreamento de IC estágio B em DM2 (ADA 2025). Valor de corte: ≥50 pg/mL anormal. Se elevado: realizar ECOTT + avaliar com cardiologista."  ✓ Referência + valores + conduta
}
```

**Validação:**
- [ ] ID único (não duplicado)
- [ ] Nome oficial do exame
- [ ] Código TUSS existe e está correto
- [ ] Condição sintaxe correta
- [ ] Observação inclui: referência, valores clínicos, conduta se alterado

---

### 5.2 Checklist: Mensagem educativa bem estruturada

```json
{
  "id": "msg-educativa-bnp-dm2-rastreamento",  ✓
  "nome": "BNP/NT-proBNP em DM2: Rastreamento IC Estágio B (ADA 2025)",  ✓ Título claro
  "condicional": "visivel",  ✓
  "condicao": "'diabetes' in comorbidades or 'dm2' in comorbidades",  ✓
  "conteudo": "<p><strong>📋 NOVIDADE DIRETRIZ ADA 2025</strong></p>
    <p>Recomendação: Considerar dosagem de peptídeos natriuréticos...</p>
    
    <p><strong>Valores de corte anormais:</strong></p>
    <ul><li>BNP ≥50 pg/mL</li><li>NT-proBNP ≥125 pg/mL</li></ul>
    
    <p><strong>Se peptídeos natriuréticos elevados:</strong></p>
    <ol>
      <li>Solicitar ecocardiograma transtorácico</li>
      <li>Avaliar doença cardíaca estrutural</li>
      <li>Encaminhar para cardiologista</li>
      <li>Implementar estratégia terapêutica preventiva</li>
    </ol>
    
    <p><em>American Diabetes Association. Diabetes Care. 2025;48(Suppl 1):S207-S238.</em></p>"
}
```

**Estrutura ideal mensagem educativa:**
1. **Título destacado** (novidade, alerta, etc)
2. **Contexto clínico** (por que importante)
3. **Valores/critérios objetivos**
4. **Conduta clara** (o que fazer)
5. **Referência bibliográfica** (diretriz específica)

**Validação:**
- [ ] Título claro e acionável
- [ ] Valores objetivos (quando aplicável)
- [ ] Conduta explícita (passos numerados)
- [ ] Referência bibliográfica completa
- [ ] HTML bem formatado (tags fechadas, listas corretas)

---

### 5.3 Checklist: Pergunta bem estruturada

```json
{
  "id": "P-sincope-frequencia-ambulatorial",  ✓
  "nodeId": "node-1754054008885",  ✓ Node correto
  "uid": "sincope_frequencia",  ✓ UID único
  "titulo": "<p><strong>Frequência dos episódios:</strong></p>",  ✓ Título claro
  "descricao": "<p>Diferenciar primeiro episódio (mais preocupante) de episódios recorrentes</p>",  ✓ Justificativa clínica
  "condicional": "visivel",  ✓
  "expressao": "sincope_presente in ['pre_sincope', 'sincope']",  ✓ Condição correta
  "select": "choice",  ✓ Tipo correto
  "options": [
    {
      "id": "episodio_unico_primeira_vez",  ✓ ID descritivo
      "label": "Primeiro episódio (primeira vez na vida)",  ✓ Label claro
      "flag_risk": "medium",  ✓ Estratificação
      "alert": "Primeiro episódio merece investigação mais ampla"  ✓ Orientação clínica
    },
    // ... mais opções
  ]
}
```

**Validação:**
- [ ] UID único
- [ ] Título claro para médico
- [ ] Descrição explica rationale clínico
- [ ] Expressão condicional correta
- [ ] Opções com IDs descritivos
- [ ] Labels claros (sem ambiguidade)
- [ ] Flags de risco quando aplicável
- [ ] Alerts/notes educativos

---

## 📋 6. CHECKLIST PRÉ-DEPLOY

### 6.1 Validação técnica (obrigatório)

```
✓ Estrutural:
  [ ] JSON válido (load sem erros)
  [ ] Nodes: count consistente
  [ ] Edges: count consistente
  [ ] Metadata atualizada

✓ Duplicação:
  [ ] Zero duplicatas em exam IDs
  [ ] Zero duplicatas em message IDs
  [ ] Zero duplicatas em question UIDs
  [ ] Zero duplicatas em node IDs

✓ Sintaxe:
  [ ] Condições validadas (validate_conditions)
  [ ] Expressões Python-like corretas
  [ ] HTML bem formatado em mensagens

✓ Referências:
  [ ] Todas as modificações têm referências
  [ ] Diretrizes citadas corretamente
  [ ] Níveis de evidência explícitos
```

---

### 6.2 Validação clínica (escalar para médico)

```
✓ Segurança:
  [ ] Gates de segurança validados
  [ ] Red flags implementados corretamente
  [ ] Condutas críticas revisadas

✓ Evidências:
  [ ] Diretrizes 2024-2025 priorizadas
  [ ] Conflitos de diretrizes resolvidos
  [ ] Valores de corte corretos

✓ Usabilidade:
  [ ] Fluxo testado end-to-end
  [ ] Mensagens claras e acionáveis
  [ ] Orientações compreensíveis

✓ Casos de teste:
  [ ] Paciente típico (caminho feliz)
  [ ] Paciente com red flag (bloqueio)
  [ ] Paciente com múltiplas comorbidades
```

---

### 6.3 Documentação (obrigatório)

```
✓ Metadata:
  [ ] changes: descrição clara
  [ ] lastModified: timestamp correto
  [ ] version: incrementada corretamente

✓ Changelog separado:
  [ ] Lista todas as modificações
  [ ] Justificativa de cada mudança
  [ ] Referências bibliográficas

✓ Relatório de testes:
  [ ] Casos testados documentados
  [ ] Resultados esperados vs obtidos
  [ ] Bugs identificados e corrigidos
```

---

## 🔧 7. CASOS ESPECIAIS E EXCEÇÕES

### 7.1 Lidando com múltiplas versões

**Problema:** Protocolo tem versões diferentes em clientes diferentes (DOT, Amil, Inclua)

**Solução:**
```python
# Usar feature flags ao invés de versões separadas
{
  "version": "2.0.0",
  "features": {
    "prevent_calculator": {
      "enabled": ["Inclua", "Amil"],
      "disabled": ["DOT"]
    },
    "mrpa_option": {
      "enabled": ["Inclua"],
      "disabled": ["DOT", "Amil"]
    }
  }
}
```

**Regra:**
- NUNCA manter JSONs completamente separados por cliente
- Usar feature flags para diferenças
- Manter core protocol unificado

---

### 7.2 Lidando com diretrizes conflitantes

**Exemplo:** AHA 2024 recomenda X, mas ESC 2020 recomenda Y

**Decisão framework:**
```
1. Priorizar diretriz MAIS RECENTE
   (AHA 2024 > ESC 2020)

2. Priorizar diretriz MAIS ESPECÍFICA
   (Cardiologia > Medicina Geral)

3. Priorizar diretriz NACIONAL se empate
   (SBC > ESC para Brasil)

4. Se ainda incerto:
   → Implementar opção MAIS CONSERVADORA
   → Documentar conflito
   → Marcar para revisão médica
```

---

### 7.3 Lidando com dados ausentes/incompletos

**Problema:** Calculadora PREVENT precisa de eGFR, mas protocolo não coleta

**Solução:**
```python
# Adicionar disclaimer quando dados faltantes
{
  "id": "prevent-disclaimer-dados-faltantes",
  "condition": "prevent_egfr == null",
  "alert": {
    "type": "warning",
    "title": "⚠️ Cálculo de risco parcial",
    "message": "eGFR não disponível. O risco apresentado é ESTIMATIVA PARCIAL. Para cálculo preciso, solicite creatinina."
  }
}
```

**Regra:**
- NUNCA calcular score com dados críticos faltando SEM disclaimer
- SEMPRE indicar ao médico que cálculo é parcial
- SUGERIR exames faltantes

---

### 7.4 Lidando com edge cases clínicos

**Exemplo:** Paciente jovem (<30 anos) com diabetes - PREVENT não se aplica

**Solução:**
```python
# Adicionar validação de aplicabilidade
{
  "id": "prevent-applicability-check",
  "condition": "age < 30 or age > 79",
  "alert": {
    "type": "info",
    "message": "Calculadora PREVENT validada para 30-79 anos. Para pacientes fora desta faixa, usar julgamento clínico."
  }
}
```

**Regra:**
- SEMPRE verificar critérios de inclusão/exclusão de scores
- SEMPRE alertar quando score não se aplica
- OFERECER alternativas quando possível

---

## 🎓 8. APRENDIZADO CONTÍNUO

### 8.1 Quando adicionar nova técnica a esta memória

**Triggers:**
- Problema recorrente encontrado 3+ vezes
- Nova classe de erro descoberta
- Padrão mais eficiente identificado
- Feedback de validação clínica

**Processo:**
1. Documentar problema encontrado
2. Documentar solução aplicada
3. Validar que solução funciona
4. Adicionar a este documento (seção apropriada)
5. Atualizar exemplos de código

---

### 8.2 Métricas de qualidade a monitorar

```
📊 Métricas técnicas:
  - Taxa de duplicação (meta: 0%)
  - Taxa de erros sintaxe condições (meta: 0%)
  - Taxa de validação pré-deploy (meta: 100%)
  - Tempo médio por modificação

📊 Métricas clínicas:
  - Taxa de aprovação médica (meta: >90%)
  - Bugs clínicos em produção (meta: 0 críticos)
  - Feedback negativo usuários (meta: <5%)

📊 Métricas de processo:
  - Aderência ao workflow padrão (meta: 100%)
  - Documentação completa (meta: 100%)
  - Backup antes de modificar (meta: 100%)
```

---

## 📝 CONCLUSÃO: O QUE TORNA UM AGENTE "INTELIGENTE"

### Características de um agente de alta qualidade:

✅ **Análise antes de ação**
- Nunca modifica sem entender
- Sempre busca padrões existentes
- Valida premissas antes de prosseguir

✅ **Rigor técnico**
- Zero tolerância para duplicação
- Validação em múltiplas camadas
- Backup obrigatório

✅ **Consciência clínica**
- Prioriza segurança do paciente
- Respeita hierarquia de evidências
- Escala quando incerto

✅ **Rastreabilidade**
- Documenta todas as decisões
- Metadata sempre atualizada
- Changelog detalhado

✅ **Aprendizado**
- Atualiza esta memória com novos padrões
- Monitora métricas de qualidade
- Melhora continuamente

---

## 🔗 INTEGRAÇÃO COM SISTEMA DE MEMÓRIA

### Como usar este documento no agente:

1. **Pré-execução:** Carregar esta memória operacional
2. **Durante execução:** Consultar princípios e checklists
3. **Pós-execução:** Validar contra padrões de qualidade
4. **Feedback loop:** Atualizar memória com novos aprendizados

### Estrutura de prompts para o agente:

```
SYSTEM PROMPT:
  "Você é um agente especializado em modificação de protocolos clínicos.
   Antes de qualquer modificação, você DEVE seguir o workflow padrão
   documentado em MEMÓRIA_OPERACIONAL.md. Priorize SEMPRE segurança
   clínica sobre eficiência. Quando em dúvida, escale para humano."

PRE-TASK PROMPT:
  "Carregue a memória operacional e identifique:
   1. Qual fase do workflow se aplica a esta tarefa
   2. Quais validações são obrigatórias
   3. Quais red flags monitorar
   4. Qual padrão de qualidade aplicar"

POST-TASK PROMPT:
  "Execute checklist pré-deploy completo:
   1. Validação técnica (estrutura, duplicatas, sintaxe)
   2. Validação clínica (segurança, evidências, usabilidade)
   3. Documentação (metadata, changelog, relatório)
   
   Se QUALQUER item falhar: NÃO DEPLOYAR, reportar problema"
```

---

**Documento gerado:** Dezembro de 2025  
**Versão:** 1.0.0  
**Próxima revisão:** Após 100 execuções do agente  
**Status:** Template base - expandir conforme novos aprendizados

---

## 📚 APÊNDICE: COMANDOS RÁPIDOS

### Análise rápida
```python
# Quick check do protocolo
python -c "import json; p=json.load(open('protocol.json')); print(f'Nodes: {len(p[\"nodes\"])}, Exams: {len([e for n in p[\"nodes\"] if \"condutaDataNode\" in n[\"data\"] for e in n[\"data\"][\"condutaDataNode\"].get(\"exame\",[])])}')"
```

### Busca rápida de duplicatas
```python
# Check exam ID duplicates
python -c "import json; p=json.load(open('protocol.json')); ids=[e['id'] for n in p['nodes'] if 'condutaDataNode' in n['data'] for e in n['data']['condutaDataNode'].get('exame',[])]; print('Duplicates:', [i for i in ids if ids.count(i)>1])"
```

### Validação JSON
```bash
# Validate JSON syntax
python -m json.tool protocol.json > /dev/null && echo "✓ JSON válido" || echo "✗ JSON inválido"
```

---

**Este documento é vivo.** Atualize-o sempre que descobrir novos padrões, problemas ou soluções.
