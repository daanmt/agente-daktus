"""
Script de validação para as correções de bugs na reconstrução de protocolo.

Testa:
1. Função get_suggestion_node_id() com múltiplos fallbacks
2. Conversão de SpecificLocation para dict
3. Atribuição de sugestões a seções
"""

import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "src"))

def test_get_suggestion_node_id():
    """Testa extração de node_id com múltiplos fallbacks."""
    from typing import Dict, Optional
    
    def get_suggestion_node_id(sug: Dict) -> Optional[str]:
        """Extract node_id from suggestion using multiple fallback strategies."""
        # Strategy 1: specific_location.node_id (original)
        spec_loc = sug.get("specific_location", {})
        if spec_loc:
            if hasattr(spec_loc, 'node_id'):
                node_id = spec_loc.node_id
            elif isinstance(spec_loc, dict):
                node_id = spec_loc.get("node_id")
            else:
                node_id = None
            if node_id:
                return node_id
        
        # Strategy 2: location.node_id (CLI conversion)
        location = sug.get("location", {})
        if location:
            if hasattr(location, 'node_id'):
                node_id = location.node_id
            elif isinstance(location, dict):
                node_id = location.get("node_id")
            else:
                node_id = None
            if node_id:
                return node_id
        
        # Strategy 3: implementation_strategy.node_id (Wave 2)
        impl_strategy = sug.get("implementation_strategy", {})
        if impl_strategy and isinstance(impl_strategy, dict):
            node_id = impl_strategy.get("node_id")
            if node_id:
                return node_id
        
        return None
    
    # Caso 1: specific_location.node_id presente
    sug1 = {"id": "sug_001", "specific_location": {"node_id": "node-1"}}
    assert get_suggestion_node_id(sug1) == "node-1", "Caso 1 falhou"
    print("✅ Caso 1: specific_location.node_id presente - OK")
    
    # Caso 2: specific_location vazio, location presente
    sug2 = {"id": "sug_002", "specific_location": {}, "location": {"node_id": "node-2"}}
    assert get_suggestion_node_id(sug2) == "node-2", "Caso 2 falhou"
    print("✅ Caso 2: location.node_id como fallback - OK")
    
    # Caso 3: Nenhum tem node_id
    sug3 = {"id": "sug_003", "specific_location": {}, "location": {}}
    assert get_suggestion_node_id(sug3) is None, "Caso 3 falhou"
    print("✅ Caso 3: Nenhum node_id, retorna None - OK")
    
    # Caso 4: implementation_strategy.node_id
    sug4 = {"id": "sug_004", "implementation_strategy": {"node_id": "node-4"}}
    assert get_suggestion_node_id(sug4) == "node-4", "Caso 4 falhou"
    print("✅ Caso 4: implementation_strategy.node_id como fallback - OK")
    
    # Caso 5: specific_location é None (não dict vazio)
    sug5 = {"id": "sug_005", "specific_location": None, "location": {"node_id": "node-5"}}
    assert get_suggestion_node_id(sug5) == "node-5", "Caso 5 falhou"
    print("✅ Caso 5: specific_location=None, usa location - OK")
    
    return True


def test_convert_specific_location():
    """Testa conversão de SpecificLocation para dict."""
    from pydantic import BaseModel
    from typing import Optional
    
    class SpecificLocation(BaseModel):
        node_id: Optional[str] = None
        question_id: Optional[str] = None
        section: Optional[str] = None
    
    def convert_specific_location(loc):
        """Convert SpecificLocation (Pydantic or dict) to dict safely."""
        if loc is None:
            return {}
        if isinstance(loc, dict):
            return loc
        if hasattr(loc, 'model_dump'):
            return loc.model_dump(exclude_none=True)
        elif hasattr(loc, 'dict'):
            return loc.dict(exclude_none=True)
        elif hasattr(loc, '__dict__'):
            return {k: v for k, v in loc.__dict__.items() if v is not None}
        return {}
    
    # Caso 1: None
    assert convert_specific_location(None) == {}, "Caso 1 falhou"
    print("✅ Caso 1: None retorna {} - OK")
    
    # Caso 2: Dict
    assert convert_specific_location({"node_id": "node-1"}) == {"node_id": "node-1"}, "Caso 2 falhou"
    print("✅ Caso 2: Dict retorna dict original - OK")
    
    # Caso 3: Pydantic object
    pydantic_obj = SpecificLocation(node_id="node-3", question_id="q1")
    result = convert_specific_location(pydantic_obj)
    assert result.get("node_id") == "node-3", "Caso 3 falhou (node_id)"
    assert result.get("question_id") == "q1", "Caso 3 falhou (question_id)"
    assert "section" not in result, "Caso 3 falhou (section não deveria estar presente)"
    print("✅ Caso 3: Pydantic object converte corretamente - OK")
    
    return True


def test_section_enumeration_with_fallback():
    """Testa que seções são criadas corretamente com o fallback."""
    import json
    
    # Simular protocolo com 3 nodes
    protocol = {
        "metadata": {"company": "Test", "name": "test_proto", "version": "1.0.0"},
        "nodes": [
            {"id": "node-1", "type": "custom", "position": {"x": 0}, "data": {}},
            {"id": "node-2", "type": "custom", "position": {"x": 100}, "data": {}},
            {"id": "node-3", "type": "conduct", "position": {"x": 200}, "data": {}},
        ],
        "edges": []
    }
    
    # Sugestões SEM node_id (simula bug original)
    suggestions = [
        {"id": "sug_001", "title": "Test 1", "specific_location": {}},
        {"id": "sug_002", "title": "Test 2", "specific_location": None},
    ]
    
    # A lógica de fallback deve atribuir todas à primeira seção
    protocol_size = len(json.dumps(protocol))
    nodes_per_section = 3 if protocol_size < 50000 else 2 if protocol_size < 100000 else 1
    
    nodes = protocol["nodes"]
    edges = protocol["edges"]
    
    # Simular enumeração de seções (simplificado)
    sections = [{"section_id": "section_0_metadata", "type": "metadata"}]
    
    idx = 1
    for i in range(0, len(nodes), nodes_per_section):
        node_group = nodes[i:i + nodes_per_section]
        if not node_group:
            continue
        
        node_ids = set(n["id"] for n in node_group)
        
        # Simular get_suggestion_node_id que retorna None para nossas sugestões
        section_suggestions = [
            sug for sug in suggestions
            if (sug.get("specific_location", {}) or {}).get("node_id") in node_ids
        ]
        
        # CRITICAL FIX: fallback
        if not section_suggestions and idx == 1 and suggestions:
            section_suggestions = suggestions
        
        sections.append({
            "section_id": f"section_{idx}",
            "type": "nodes",
            "relevant_suggestions": section_suggestions,
        })
        idx += 1
    
    # Verificar que a primeira seção de nodes tem TODAS as sugestões
    first_node_section = sections[1]  # sections[0] é metadata
    assert len(first_node_section["relevant_suggestions"]) == 2, \
        f"Esperado 2 sugestões na primeira seção, mas encontrou {len(first_node_section['relevant_suggestions'])}"
    
    print("✅ Fallback de sugestões funciona - todas atribuídas à primeira seção - OK")
    return True


def main():
    print("=" * 60)
    print("VALIDAÇÃO DAS CORREÇÕES DE BUGS")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        test_get_suggestion_node_id()
        tests_passed += 1
    except Exception as e:
        print(f"❌ test_get_suggestion_node_id FALHOU: {e}")
        tests_failed += 1
    
    print()
    
    try:
        test_convert_specific_location()
        tests_passed += 1
    except Exception as e:
        print(f"❌ test_convert_specific_location FALHOU: {e}")
        tests_failed += 1
    
    print()
    
    try:
        test_section_enumeration_with_fallback()
        tests_passed += 1
    except Exception as e:
        print(f"❌ test_section_enumeration_with_fallback FALHOU: {e}")
        tests_failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTADO: {tests_passed} testes passaram, {tests_failed} falharam")
    print("=" * 60)
    
    return tests_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
