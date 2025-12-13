# 🔧 RELATÓRIO TÉCNICO: FERRAMENTAS E TÉCNICAS PYTHON

**Contexto:** Análise e modificação automatizada de protocolos clínicos (JSON)  
**Caso de uso:** Ficha Cardiologia v2.0.0 - Implementação BNP em DM2 + Síncope ambulatorial  
**Data:** Dezembro de 2025

---

## 📋 ÍNDICE

1. Padrões de análise estrutural
2. Técnicas de busca e localização
3. Métodos de modificação
4. Estratégias de validação
5. Código reutilizável (templates)
6. Boas práticas operacionais

---

## 🔍 1. PADRÕES DE ANÁLISE ESTRUTURAL

### 1.1 Carregar e inspecionar JSON

```python
import json

# Carregamento seguro
with open('protocolo.json', 'r', encoding='utf-8') as f:
    protocol = json.load(f)

# Inspeção estrutural básica
print(f"Nodes: {len(protocol['nodes'])}")
print(f"Edges: {len(protocol['edges'])}")
print(f"Metadata: {protocol.get('metadata', {})}")

# Listar todos os IDs de nodes
node_ids = [node['id'] for node in protocol['nodes']]
print(f"Node IDs: {node_ids}")
```

**Quando usar:**
- Início de qualquer tarefa (entender estrutura)
- Antes de modificações (baseline)
- Após modificações (validação)

---

### 1.2 Encontrar node específico por ID

```python
def find_node_by_id(protocol, node_id):
    """
    Encontra node específico por ID
    
    Returns:
        tuple: (node, index) ou (None, None)
    """
    for i, node in enumerate(protocol['nodes']):
        if node['id'] == node_id:
            return node, i
    return None, None

# Uso
conduct_node, conduct_idx = find_node_by_id(protocol, 'conduta-1754085461792')
if conduct_node:
    print(f"✓ Conduct node encontrado no índice {conduct_idx}")
```

**Quando usar:**
- Para modificar um node específico
- Para adicionar exames/mensagens/orientações
- Para ler estrutura de um node

---

### 1.3 Listar tipos de nodes

```python
# Contar nodes por tipo
node_types = {}
for node in protocol['nodes']:
    node_type = node.get('type', 'unknown')
    node_types[node_type] = node_types.get(node_type, 0) + 1

print("\n📊 Distribuição de node types:")
for node_type, count in sorted(node_types.items()):
    print(f"  {node_type}: {count}")
```

**Output esperado:**
```
📊 Distribuição de node types:
  anamnese: 2
  conduct: 1
  custom: 14
  start: 1
```

**Quando usar:**
- Entender arquitetura do protocolo
- Validar se todos nodes necessários existem

---

## 🔎 2. TÉCNICAS DE BUSCA E LOCALIZAÇÃO

### 2.1 Buscar exames por nome/código

```python
def search_exams(conduct_node, search_terms):
    """
    Busca exames no conduct node
    
    Args:
        conduct_node: Node de conduta
        search_terms: Lista de termos a buscar (case-insensitive)
    
    Returns:
        list: Exames encontrados
    """
    exams = conduct_node['data']['condutaDataNode'].get('exame', [])
    
    found_exams = []
    for exam in exams:
        nome = exam.get('nome', '').lower()
        codigo = str(exam.get('codigo', '')).lower()
        
        for term in search_terms:
            if term.lower() in nome or term.lower() in codigo:
                found_exams.append(exam)
                break
    
    return found_exams

# Uso
bnp_exams = search_exams(conduct_node, ['bnp', 'natriurético', 'pro-bnp'])

if bnp_exams:
    print(f"\n✓ {len(bnp_exams)} exames BNP encontrados:")
    for exam in bnp_exams:
        print(f"  • {exam.get('nome', 'N/A')}")
else:
    print("\n❌ BNP não encontrado")
```

**Quando usar:**
- Verificar se exame já existe antes de adicionar
- Validar implementações anteriores
- Evitar duplicação

---

### 2.2 Buscar perguntas por UID ou texto

```python
def search_questions(protocol, uid=None, text_contains=None):
    """
    Busca perguntas em todos os nodes
    
    Args:
        uid: UID exato da pergunta (opcional)
        text_contains: Texto a buscar no título (opcional)
    
    Returns:
        list: [(node, question), ...]
    """
    results = []
    
    for node in protocol['nodes']:
        if 'questions' not in node['data']:
            continue
            
        for q in node['data']['questions']:
            match = False
            
            if uid and q.get('uid') == uid:
                match = True
            
            if text_contains:
                titulo = q.get('titulo', '').lower()
                if text_contains.lower() in titulo:
                    match = True
            
            if match:
                results.append((node, q))
    
    return results

# Uso
sincope_questions = search_questions(protocol, text_contains='síncope')

print(f"\n📋 Perguntas sobre síncope: {len(sincope_questions)}")
for node, q in sincope_questions:
    print(f"  • UID: {q.get('uid', 'N/A')}")
    print(f"    Node: {node['data'].get('label', 'N/A')}")
    print(f"    Tipo: {q.get('select', 'N/A')}")
```

**Quando usar:**
- Verificar se pergunta já existe
- Encontrar onde inserir novas perguntas
- Validar fluxo de perguntas condicionais

---

### 2.3 Buscar por viés/keywords em mensagens

```python
def analyze_message_bias(conduct_node, keywords_list):
    """
    Analisa viés de mensagens (ex: PS vs ambulatorial)
    
    Args:
        keywords_list: Lista de keywords a buscar
    
    Returns:
        dict: {'keyword': count, ...}
    """
    messages = conduct_node['data']['condutaDataNode'].get('mensagem', [])
    
    keyword_counts = {kw: 0 for kw in keywords_list}
    found_messages = {kw: [] for kw in keywords_list}
    
    for msg in messages:
        conteudo = msg.get('conteudo', '').lower()
        nome = msg.get('nome', '').lower()
        
        for kw in keywords_list:
            if kw.lower() in conteudo or kw.lower() in nome:
                keyword_counts[kw] += 1
                found_messages[kw].append(msg.get('id', 'unknown'))
    
    return keyword_counts, found_messages

# Uso: Detectar viés PS
ps_keywords = ['urgência', 'emergência', 'imediato', 'pronto socorro']
ambulatorial_keywords = ['ambulatorial', 'retorno', 'seguimento', 'acompanhamento']

ps_counts, ps_msgs = analyze_message_bias(conduct_node, ps_keywords)
amb_counts, amb_msgs = analyze_message_bias(conduct_node, ambulatorial_keywords)

print(f"\n📊 Análise de viés:")
print(f"  Mensagens com viés PS: {sum(ps_counts.values())}")
print(f"  Mensagens com viés Ambulatorial: {sum(amb_counts.values())}")
```

**Quando usar:**
- Verificar adequação do protocolo ao contexto (PS vs ambulatorial)
- Auditar mensagens inconsistentes
- Validar após modificações

---

### 2.4 Buscar scores clínicos (EXIL, OESIL, etc)

```python
def search_clinical_scores(protocol, score_names):
    """
    Busca scores clínicos em perguntas e expressões
    
    Args:
        score_names: Lista de nomes de scores (ex: ['exil', 'oesil', 'prevent'])
    
    Returns:
        dict: {'questions': [...], 'expressions': [...]}
    """
    found = {'questions': [], 'expressions': []}
    
    for node in protocol['nodes']:
        # Buscar em questions
        if 'questions' in node['data']:
            for q in node['data']['questions']:
                titulo = q.get('titulo', '').lower()
                uid = q.get('uid', '').lower()
                
                for score in score_names:
                    if score.lower() in titulo or score.lower() in uid:
                        found['questions'].append({
                            'node': node['id'],
                            'uid': q.get('uid'),
                            'score': score
                        })
        
        # Buscar em clinical expressions
        if 'clinicalExpressions' in node['data']:
            for expr in node['data']['clinicalExpressions']:
                name = expr.get('name', '').lower()
                desc = expr.get('description', '').lower()
                
                for score in score_names:
                    if score.lower() in name or score.lower() in desc:
                        found['expressions'].append({
                            'node': node['id'],
                            'name': expr.get('name'),
                            'score': score
                        })
    
    return found

# Uso
scores_to_check = ['exil', 'oesil', 'prevent', 'grace', 'timi']
found_scores = search_clinical_scores(protocol, scores_to_check)

print(f"\n🔍 Scores encontrados:")
print(f"  Questions: {len(found_scores['questions'])}")
print(f"  Expressions: {len(found_scores['expressions'])}")
```

**Quando usar:**
- Verificar se scores de PS estão presentes (viés)
- Validar implementação de novas calculadoras
- Auditar consistência de scores

---

## ✏️ 3. MÉTODOS DE MODIFICAÇÃO

### 3.1 Adicionar exame ao conduct node

```python
def add_exam(conduct_node, exam_data):
    """
    Adiciona exame ao conduct node
    
    Args:
        exam_data: Dict com estrutura do exame
            {
                "id": "exam-id-unique",
                "nome": "Nome do exame",
                "codigo": "TUSS_CODE",
                "condicional": "visivel",
                "condicao": "diabetes in comorbidades",
                "observacao": "Texto explicativo"
            }
    
    Returns:
        bool: True se adicionado com sucesso
    """
    exams = conduct_node['data']['condutaDataNode']['exame']
    
    # Verificar duplicação por ID
    existing_ids = [e.get('id') for e in exams]
    if exam_data['id'] in existing_ids:
        print(f"⚠️ Exame {exam_data['id']} já existe")
        return False
    
    # Adicionar
    exams.append(exam_data)
    
    print(f"✓ Exame adicionado: {exam_data['nome']}")
    print(f"  ID: {exam_data['id']}")
    print(f"  Código TUSS: {exam_data.get('codigo', 'N/A')}")
    print(f"  Condição: {exam_data.get('condicao', 'sempre')}")
    
    return True

# Uso
exam_bnp = {
    "id": "exam-bnp-dm2-rastreamento",
    "nome": "BNP - Peptídeo Natriurético Tipo B",
    "codigo": "40316130",
    "condicional": "visivel",
    "condicao": "'diabetes' in comorbidades or 'dm2' in comorbidades",
    "observacao": "Rastreamento de IC estágio B em DM2 (ADA 2025). Valor de corte: ≥50 pg/mL anormal."
}

success = add_exam(conduct_node, exam_bnp)
```

**Quando usar:**
- Implementar novos exames de diretrizes
- Adicionar rastreamentos
- Expandir protocolo

---

### 3.2 Adicionar mensagem educativa

```python
def add_message(conduct_node, message_data):
    """
    Adiciona mensagem educativa ao médico
    
    Args:
        message_data: Dict com estrutura da mensagem
            {
                "id": "msg-id-unique",
                "nome": "Título da mensagem",
                "condicional": "visivel",
                "condicao": "diabetes in comorbidades",
                "conteudo": "<p>HTML content</p>"
            }
    
    Returns:
        bool: True se adicionado com sucesso
    """
    messages = conduct_node['data']['condutaDataNode']['mensagem']
    
    # Verificar duplicação
    existing_ids = [m.get('id') for m in messages]
    if message_data['id'] in existing_ids:
        print(f"⚠️ Mensagem {message_data['id']} já existe")
        return False
    
    # Adicionar
    messages.append(message_data)
    
    print(f"✓ Mensagem adicionada: {message_data['nome'][:60]}...")
    print(f"  ID: {message_data['id']}")
    print(f"  Condição: {message_data.get('condicao', 'sempre')}")
    
    return True

# Uso
msg_bnp = {
    "id": "msg-educativa-bnp-dm2-rastreamento",
    "nome": "BNP/NT-proBNP em DM2: Rastreamento IC Estágio B (ADA 2025)",
    "condicional": "visivel",
    "condicao": "'diabetes' in comorbidades",
    "conteudo": """<p><strong>📋 NOVIDADE DIRETRIZ ADA 2025</strong></p>
<p>Recomendação: Considerar dosagem de peptídeos natriuréticos...</p>"""
}

success = add_message(conduct_node, msg_bnp)
```

**Quando usar:**
- Educar médicos sobre novas diretrizes
- Alertas clínicos importantes
- Explicar raciocínio de condutas

---

### 3.3 Adicionar pergunta condicional

```python
def add_question(node, question_data, insert_after_uid=None):
    """
    Adiciona pergunta a um node, opcionalmente após outra pergunta
    
    Args:
        question_data: Dict com estrutura da pergunta
        insert_after_uid: UID da pergunta após a qual inserir (opcional)
    
    Returns:
        bool: True se adicionado com sucesso
    """
    questions = node['data']['questions']
    
    # Verificar duplicação
    existing_uids = [q.get('uid') for q in questions]
    if question_data['uid'] in existing_uids:
        print(f"⚠️ Pergunta {question_data['uid']} já existe")
        return False
    
    # Inserir após pergunta específica ou no final
    if insert_after_uid:
        for i, q in enumerate(questions):
            if q.get('uid') == insert_after_uid:
                questions.insert(i + 1, question_data)
                print(f"✓ Pergunta inserida após {insert_after_uid}")
                return True
        
        # Se não encontrou, adicionar no final
        print(f"⚠️ UID {insert_after_uid} não encontrado, adicionando no final")
    
    questions.append(question_data)
    print(f"✓ Pergunta adicionada: {question_data['uid']}")
    
    return True

# Uso
question_freq = {
    "id": "P-sincope-frequencia-ambulatorial",
    "nodeId": "node-1754054008885",
    "uid": "sincope_frequencia",
    "titulo": "<p><strong>Frequência dos episódios:</strong></p>",
    "descricao": "<p>Diferenciar primeiro episódio de episódios recorrentes</p>",
    "condicional": "visivel",
    "expressao": "sincope_presente in ['pre_sincope', 'sincope']",
    "select": "choice",
    "options": [
        {
            "id": "episodio_unico_primeira_vez",
            "label": "Primeiro episódio (primeira vez na vida)",
            "flag_risk": "medium"
        },
        # ... mais opções
    ]
}

success = add_question(anamnese_node, question_freq, insert_after_uid='sincope_contexto')
```

**Quando usar:**
- Expandir estratificação de risco
- Adicionar perguntas condicionais
- Melhorar coleta de dados clínicos

---

### 3.4 Update de metadata

```python
def update_metadata(protocol, change_description):
    """
    Atualiza metadata com descrição de mudanças
    
    Args:
        change_description: String descrevendo a mudança
    """
    if 'metadata' not in protocol:
        protocol['metadata'] = {}
    
    # Adicionar timestamp
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    # Append to changes
    current_changes = protocol['metadata'].get('changes', '')
    protocol['metadata']['changes'] = f"{current_changes} {change_description}"
    
    # Update lastModified
    protocol['metadata']['lastModified'] = timestamp
    
    print(f"✓ Metadata atualizada:")
    print(f"  Mudança: {change_description}")
    print(f"  Timestamp: {timestamp}")

# Uso
update_metadata(protocol, "BNP/NT-proBNP para rastreamento IC em DM2 (ADA 2025).")
```

**Quando usar:**
- Sempre ao modificar o protocolo
- Rastreabilidade de mudanças
- Documentação automática

---

## ✅ 4. ESTRATÉGIAS DE VALIDAÇÃO

### 4.1 Validação estrutural antes/depois

```python
def validate_structure(protocol, label="Current"):
    """
    Valida estrutura básica do protocolo
    
    Returns:
        dict: Métricas estruturais
    """
    metrics = {
        'nodes': len(protocol.get('nodes', [])),
        'edges': len(protocol.get('edges', [])),
        'exams': 0,
        'messages': 0,
        'orientations': 0,
        'questions': 0
    }
    
    # Contar conduct node items
    for node in protocol['nodes']:
        if node['id'] == 'conduta-1754085461792':
            conduct_data = node['data']['condutaDataNode']
            metrics['exams'] = len(conduct_data.get('exame', []))
            metrics['messages'] = len(conduct_data.get('mensagem', []))
            metrics['orientations'] = len(conduct_data.get('orientacao', []))
        
        # Contar questions
        if 'questions' in node['data']:
            metrics['questions'] += len(node['data']['questions'])
    
    print(f"\n📊 Estrutura {label}:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    return metrics

# Uso
baseline = validate_structure(protocol, "ANTES")

# ... fazer modificações ...

after = validate_structure(protocol, "DEPOIS")

# Comparar
print(f"\n📈 Mudanças:")
for key in baseline:
    diff = after[key] - baseline[key]
    if diff != 0:
        print(f"  {key}: {baseline[key]} → {after[key]} ({diff:+d})")
```

**Quando usar:**
- Antes e depois de qualquer modificação
- Validar que mudanças foram aplicadas
- Detectar mudanças não intencionais

---

### 4.2 Validação de duplicação

```python
def check_duplicates(protocol):
    """
    Verifica duplicação de IDs em todo o protocolo
    
    Returns:
        dict: {'exams': [...], 'messages': [...], 'questions': [...]}
    """
    duplicates = {
        'exam_ids': [],
        'message_ids': [],
        'question_uids': [],
        'node_ids': []
    }
    
    # Check node IDs
    node_ids = [n['id'] for n in protocol['nodes']]
    seen = set()
    for nid in node_ids:
        if nid in seen:
            duplicates['node_ids'].append(nid)
        seen.add(nid)
    
    # Check conduct items
    for node in protocol['nodes']:
        if 'condutaDataNode' in node['data']:
            conduct = node['data']['condutaDataNode']
            
            # Exams
            exam_ids = [e.get('id') for e in conduct.get('exame', [])]
            seen_exams = set()
            for eid in exam_ids:
                if eid in seen_exams:
                    duplicates['exam_ids'].append(eid)
                seen_exams.add(eid)
            
            # Messages
            msg_ids = [m.get('id') for m in conduct.get('mensagem', [])]
            seen_msgs = set()
            for mid in msg_ids:
                if mid in seen_msgs:
                    duplicates['message_ids'].append(mid)
                seen_msgs.add(mid)
        
        # Questions
        if 'questions' in node['data']:
            q_uids = [q.get('uid') for q in node['data']['questions']]
            seen_q = set()
            for quid in q_uids:
                if quid in seen_q:
                    duplicates['question_uids'].append(quid)
                seen_q.add(quid)
    
    # Report
    has_duplicates = any(len(v) > 0 for v in duplicates.values())
    
    if has_duplicates:
        print("\n⚠️ DUPLICATAS DETECTADAS:")
        for key, items in duplicates.items():
            if items:
                print(f"  {key}: {items}")
    else:
        print("\n✓ Nenhuma duplicata detectada")
    
    return duplicates

# Uso
check_duplicates(protocol)
```

**Quando usar:**
- Após adicionar novos itens
- Antes de salvar protocolo
- Debug de problemas de renderização

---

### 4.3 Validação de condições

```python
def validate_conditions(protocol):
    """
    Valida sintaxe de condições em exames/mensagens/perguntas
    
    Returns:
        list: Condições com possíveis erros
    """
    issues = []
    
    # Common patterns to check
    patterns = {
        'syntax_error': r'[^!=<>]=[^=]',  # Single = instead of ==
        'missing_quotes': r'\w+\s+in\s+\w+',  # Missing quotes around strings
    }
    
    for node in protocol['nodes']:
        # Check conduct conditions
        if 'condutaDataNode' in node['data']:
            conduct = node['data']['condutaDataNode']
            
            for exam in conduct.get('exame', []):
                cond = exam.get('condicao', '')
                if cond and cond != '':
                    # Basic validation
                    if "= '" in cond or '= "' in cond:
                        issues.append({
                            'type': 'exam',
                            'id': exam.get('id'),
                            'issue': 'Possível uso de = ao invés de ==',
                            'condition': cond
                        })
        
        # Check question expressions
        if 'questions' in node['data']:
            for q in node['data']['questions']:
                expr = q.get('expressao', '')
                if expr:
                    # Check for common mistakes
                    if ' = ' in expr and ' == ' not in expr:
                        issues.append({
                            'type': 'question',
                            'uid': q.get('uid'),
                            'issue': 'Possível uso de = ao invés de ==',
                            'expression': expr
                        })
    
    if issues:
        print(f"\n⚠️ {len(issues)} possíveis problemas em condições:")
        for issue in issues[:5]:  # Show first 5
            print(f"  • {issue['type']}: {issue.get('id') or issue.get('uid')}")
            print(f"    {issue['issue']}")
    else:
        print("\n✓ Condições validadas")
    
    return issues

# Uso
validate_conditions(protocol)
```

**Quando usar:**
- Após adicionar condições complexas
- Debug de perguntas que não aparecem
- QA antes de deploy

---

## 📦 5. CÓDIGO REUTILIZÁVEL (TEMPLATES)

### 5.1 Template: Pipeline completo de modificação

```python
import json
from datetime import datetime

def protocol_modification_pipeline(
    input_file,
    output_file,
    modifications_func,
    description
):
    """
    Pipeline completo: Load → Validate → Modify → Validate → Save
    
    Args:
        input_file: Caminho do JSON de entrada
        output_file: Caminho do JSON de saída
        modifications_func: Função que recebe protocol e retorna modified protocol
        description: Descrição das modificações (para metadata)
    """
    print("=" * 80)
    print(f"PIPELINE: {description}")
    print("=" * 80)
    
    # 1. LOAD
    print("\n1. CARREGANDO PROTOCOLO...")
    with open(input_file, 'r', encoding='utf-8') as f:
        protocol = json.load(f)
    print(f"✓ Carregado: {input_file}")
    
    # 2. VALIDATE BEFORE
    print("\n2. VALIDAÇÃO INICIAL...")
    before_metrics = validate_structure(protocol, "ANTES")
    
    # 3. MODIFY
    print("\n3. APLICANDO MODIFICAÇÕES...")
    try:
        protocol = modifications_func(protocol)
        print("✓ Modificações aplicadas")
    except Exception as e:
        print(f"❌ Erro durante modificações: {e}")
        return False
    
    # 4. VALIDATE AFTER
    print("\n4. VALIDAÇÃO FINAL...")
    after_metrics = validate_structure(protocol, "DEPOIS")
    
    print(f"\n📈 MUDANÇAS:")
    for key in before_metrics:
        diff = after_metrics[key] - before_metrics[key]
        if diff != 0:
            print(f"  {key}: {before_metrics[key]} → {after_metrics[key]} ({diff:+d})")
    
    # 5. CHECK DUPLICATES
    print("\n5. VERIFICANDO DUPLICATAS...")
    check_duplicates(protocol)
    
    # 6. UPDATE METADATA
    print("\n6. ATUALIZANDO METADATA...")
    update_metadata(protocol, description)
    
    # 7. SAVE
    print("\n7. SALVANDO PROTOCOLO...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(protocol, f, ensure_ascii=False, indent=2)
    print(f"✓ Salvo: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ PIPELINE CONCLUÍDO COM SUCESSO")
    print("=" * 80)
    
    return True

# EXEMPLO DE USO
def my_modifications(protocol):
    """Define modificações específicas"""
    
    # Encontrar conduct node
    conduct_node, conduct_idx = find_node_by_id(protocol, 'conduta-1754085461792')
    
    # Adicionar BNP
    exam_bnp = {
        "id": "exam-bnp-dm2-rastreamento",
        "nome": "BNP - Peptídeo Natriurético Tipo B",
        "codigo": "40316130",
        "condicional": "visivel",
        "condicao": "'diabetes' in comorbidades",
        "observacao": "Rastreamento IC estágio B (ADA 2025)"
    }
    add_exam(conduct_node, exam_bnp)
    
    # Update protocol with modified node
    protocol['nodes'][conduct_idx] = conduct_node
    
    return protocol

# Executar pipeline
success = protocol_modification_pipeline(
    input_file='protocolo_v1.json',
    output_file='protocolo_v2.json',
    modifications_func=my_modifications,
    description="Adicionar BNP/NT-proBNP para rastreamento IC em DM2 (ADA 2025)"
)
```

---

### 5.2 Template: Análise de gaps (briefing vs implementação)

```python
def analyze_implementation_gaps(protocol, briefing_items):
    """
    Compara briefing com implementação atual
    
    Args:
        briefing_items: Lista de dicts com itens do briefing
            [{
                'item': 'BNP em DM2',
                'search_terms': ['bnp', 'ntprobnp'],
                'search_location': 'exams',
                'expected_count': 2
            }, ...]
    
    Returns:
        dict: Status de implementação de cada item
    """
    results = {}
    
    conduct_node, _ = find_node_by_id(protocol, 'conduta-1754085461792')
    
    for briefing_item in briefing_items:
        item_name = briefing_item['item']
        
        if briefing_item['search_location'] == 'exams':
            found = search_exams(conduct_node, briefing_item['search_terms'])
            
            status = {
                'found': len(found),
                'expected': briefing_item.get('expected_count', 1),
                'implemented': len(found) >= briefing_item.get('expected_count', 1)
            }
            
            results[item_name] = status
        
        elif briefing_item['search_location'] == 'questions':
            found = search_questions(protocol, text_contains=briefing_item['search_terms'][0])
            
            status = {
                'found': len(found),
                'expected': briefing_item.get('expected_count', 1),
                'implemented': len(found) >= briefing_item.get('expected_count', 1)
            }
            
            results[item_name] = status
    
    # Report
    print("\n📋 ANÁLISE DE GAPS - BRIEFING vs IMPLEMENTAÇÃO")
    print("=" * 80)
    
    for item_name, status in results.items():
        icon = "✅" if status['implemented'] else "❌"
        print(f"{icon} {item_name}")
        print(f"   Esperado: {status['expected']} | Encontrado: {status['found']}")
    
    return results

# Uso
briefing = [
    {
        'item': 'BNP em DM2 (ADA 2025)',
        'search_terms': ['bnp', 'ntprobnp'],
        'search_location': 'exams',
        'expected_count': 2
    },
    {
        'item': 'Síncope - Frequência',
        'search_terms': ['frequência', 'sincope'],
        'search_location': 'questions',
        'expected_count': 1
    }
]

gaps = analyze_implementation_gaps(protocol, briefing)
```

---

## 📚 6. BOAS PRÁTICAS OPERACIONAIS

### 6.1 Workflow padrão

```
1. ANÁLISE INICIAL
   ├─ Carregar JSON
   ├─ Validar estrutura
   ├─ Entender arquitetura (nodes, edges)
   └─ Identificar node-alvo (conduct, anamnese, etc)

2. BUSCA PRÉ-MODIFICAÇÃO
   ├─ Verificar se item já existe
   ├─ Evitar duplicação
   └─ Entender padrões existentes

3. MODIFICAÇÃO
   ├─ Seguir estrutura existente
   ├─ IDs únicos e descritivos
   ├─ Condições sintaxicamente corretas
   └─ Referências e evidências

4. VALIDAÇÃO PÓS-MODIFICAÇÃO
   ├─ Verificar estrutura antes/depois
   ├─ Check duplicatas
   ├─ Validar condições
   └─ Testar casos de uso

5. DOCUMENTAÇÃO
   ├─ Update metadata
   ├─ Registrar mudanças
   └─ Timestamp

6. SALVAMENTO
   ├─ Encoding UTF-8
   ├─ Indent 2
   └─ Backup do original
```

### 6.2 Princípios fundamentais

1. **Sempre analisar antes de modificar**
   - Entender estrutura existente
   - Buscar padrões
   - Evitar duplicação

2. **Trabalhar incrementalmente**
   - Uma modificação por vez
   - Validar após cada mudança
   - Facilita debug

3. **Manter consistência**
   - IDs: padrão descritivo (`exam-bnp-dm2-rastreamento`)
   - Estrutura: seguir JSON existente
   - Nomenclatura: português clínico

4. **Validar rigorosamente**
   - Estrutura antes/depois
   - Duplicatas
   - Sintaxe de condições

5. **Documentar tudo**
   - Metadata com descrição clara
   - Comentários em código
   - Changelog separado

---

## 🎯 7. CASOS DE USO PRÁTICOS

### Caso 1: Adicionar novo exame de diretriz

```python
# 1. Analisar
conduct_node, idx = find_node_by_id(protocol, 'conduta-1754085461792')

# 2. Verificar se existe
existing = search_exams(conduct_node, ['bnp'])
if existing:
    print("⚠️ Exame já existe, não adicionar")
else:
    # 3. Adicionar
    exam = {
        "id": "exam-bnp-dm2",
        "nome": "BNP",
        "codigo": "40316130",
        "condicional": "visivel",
        "condicao": "'diabetes' in comorbidades",
        "observacao": "Rastreamento IC (ADA 2025)"
    }
    add_exam(conduct_node, exam)
    
    # 4. Atualizar protocol
    protocol['nodes'][idx] = conduct_node
    
    # 5. Validar
    validate_structure(protocol, "DEPOIS")
```

### Caso 2: Remover viés de PS de protocolo ambulatorial

```python
# 1. Analisar viés atual
ps_keywords = ['urgência', 'emergência', 'ps', 'pronto socorro']
counts, found_msgs = analyze_message_bias(conduct_node, ps_keywords)

# 2. Modificar mensagens problemáticas
messages = conduct_node['data']['condutaDataNode']['mensagem']
for msg in messages:
    if msg['id'] in found_msgs['urgência']:
        # Substituir linguagem de urgência por ambulatorial
        msg['conteudo'] = msg['conteudo'].replace('urgência', 'avaliação ambulatorial')

# 3. Validar
counts_after, _ = analyze_message_bias(conduct_node, ps_keywords)
print(f"Viés PS: {sum(counts.values())} → {sum(counts_after.values())}")
```

### Caso 3: Implementar estratificação de risco

```python
# 1. Buscar pergunta base
sincope_questions = search_questions(protocol, uid='sincope_contexto')
node, base_q = sincope_questions[0]

# 2. Adicionar perguntas de estratificação
freq_q = {
    "uid": "sincope_frequencia",
    "titulo": "<p>Frequência:</p>",
    "condicional": "visivel",
    "expressao": "sincope_presente == true",
    "select": "choice",
    "options": [...]
}
add_question(node, freq_q, insert_after_uid='sincope_contexto')

# 3. Validar fluxo condicional
# Testar que pergunta aparece quando esperado
```

---

## 📝 CONCLUSÃO

Este relatório documenta **todas as ferramentas e técnicas** utilizadas para:

✅ Analisar estrutura de protocolos JSON  
✅ Buscar e localizar elementos específicos  
✅ Modificar protocolos de forma segura  
✅ Validar implementações rigorosamente  
✅ Documentar mudanças rastreáveis  

**Próximo passo:** Incorporar essas técnicas no **sistema de memória operacional do agente** para que ele execute automaticamente esse workflow em futuras tarefas.

---

**Documento gerado:** Dezembro de 2025  
**Contexto:** Ficha Cardiologia v2.0.0  
**Status:** Template reutilizável para qualquer protocolo clínico
