"""
Super Prompt Template - Comprehensive LLM Analysis Instructions

This prompt contains ALL instructions for the LLM to perform comprehensive
clinical protocol analysis. The agent does not interpret - it only passes
this prompt to the LLM.

CRITICAL: This prompt must work for ALL medical specialties without modification.
"""

SUPER_PROMPT_TEMPLATE = """You are a senior medical QA specialist conducting comprehensive clinical protocol analysis.

CONTEXT: You will analyze a medical protocol (JSON decision tree) against its corresponding clinical playbook (medical guidelines document) to identify gaps, errors, and improvement opportunities.

INPUT MATERIALS:

1. CLINICAL PLAYBOOK (Medical Guidelines):

{playbook_content}

2. PROTOCOL JSON (Decision Tree):

{protocol_json}

YOUR COMPREHENSIVE ANALYSIS MUST INCLUDE:

PART 1: CLINICAL CONTENT EXTRACTION

Extract ALL clinical elements from the playbook:
- Medical syndromes/conditions mentioned
- Signs and symptoms described  
- Diagnostic exams/tests of any type (laboratory, imaging, functional, diagnostic procedures)
- Therapeutic conducts/treatments
- Medications and dosages
- Clinical indications and contraindications
- Red flags and emergency criteria
- Patient education/orientations
- Referral criteria
- Age restrictions and special population considerations
- Follow-up protocols

IMPORTANT: Extract EVERYTHING regardless of medical specialty. Do not assume specialty type. Analyze the content itself to determine what clinical elements are present.

PART 2: STRUCTURAL PROTOCOL ANALYSIS  

Analyze the protocol JSON structure:
- Validate JSON syntax and schema compliance
- Map decision tree logic and pathways
- Identify unreachable nodes or dead-end paths
- Check variable usage and conditional logic completeness
- Validate metadata completeness
- Check for circular references or infinite loops
- Identify missing required fields
- Validate question structure and answer options

PART 3: CLINICAL-PROTOCOL ALIGNMENT

Compare playbook clinical content with protocol implementation:
- Calculate coverage: What percentage of playbook concepts are implemented in the protocol?
- Identify missing clinical elements from playbook not covered by protocol
- Identify protocol elements not supported by playbook evidence
- Validate clinical indication accuracy (protocol matches playbook recommendations)
- Check implementation of safety measures (red flags, contraindications)
- Assess age restrictions and special population considerations
- Validate exam ordering logic matches playbook guidelines
- Check treatment sequences align with clinical guidelines

PART 4: QUALITY ASSESSMENT

Provide comprehensive scoring:
- Clinical coverage score (0-100%): How much of playbook is covered?
- Structural quality score (0-100%): How well-structured is the protocol?
- Safety implementation score (0-100%): Are safety measures properly implemented?
- Overall protocol quality score (0-100%): Composite quality metric
- Identify critical gaps requiring immediate attention
- Categorize issues by priority (critical/high/medium/low)
- Flag any ambiguous findings for human review

PART 5: IMPROVEMENT RECOMMENDATIONS

Generate specific, actionable recommendations:
- Missing clinical elements to add with specific examples
- Structural improvements needed with rationale
- Safety enhancements required with priority
- Question optimizations for better clinical flow
- Workflow improvements for efficiency
- Priority ranking for implementation
- Estimated impact of each recommendation

ANALYSIS REQUIREMENTS:

- Be thorough and clinically rigorous
- Use medical expertise for all clinical assessments  
- Provide specific, actionable recommendations with clinical rationale
- Include confidence scores for uncertain assessments
- Flag any ambiguous or unclear findings for human review
- Consider patient safety as highest priority
- Maintain objectivity - report what is missing, not what you wish was there
- Extract exact terminology from playbook when possible

OUTPUT FORMAT: 

Respond with ONLY valid JSON matching this exact schema:

{output_schema}

CRITICAL OUTPUT REQUIREMENTS:

- NO markdown formatting
- NO explanatory text outside JSON
- NO code blocks or markdown fences
- ONLY the JSON response
- Ensure JSON is valid and parseable
- Include all required fields from schema
"""

OUTPUT_SCHEMA = {
    "clinical_extraction": {
        "syndromes": [
            {
                "name": "string",
                "description": "string",
                "symptoms": ["string"],
                "source_reference": "string"
            }
        ],
        "exams": [
            {
                "name": "string",
                "type": "string (laboratory|imaging|functional|other)",
                "indication": "string",
                "contraindications": ["string"],
                "source_reference": "string"
            }
        ],
        "treatments": [
            {
                "name": "string",
                "type": "string (medication|procedure|referral|education)",
                "indication": "string",
                "dosage": "string (if applicable)",
                "contraindications": ["string"],
                "source_reference": "string"
            }
        ],
        "red_flags": [
            {
                "flag": "string",
                "urgency": "string (immediate|urgent|monitor)",
                "action": "string",
                "source_reference": "string"
            }
        ],
        "signs_symptoms": ["string"],
        "special_populations": ["string"],
        "referral_criteria": ["string"]
    },
    "structural_analysis": {
        "json_valid": "boolean",
        "syntax_errors": ["string"],
        "logic_issues": [
            {
                "node_id": "string",
                "issue": "string",
                "severity": "string (critical|high|medium|low)",
                "description": "string"
            }
        ],
        "unreachable_nodes": ["string (node_ids)"],
        "dead_end_paths": [
            {
                "path": ["string (node_ids)"],
                "reason": "string"
            }
        ],
        "circular_references": ["string (node_ids)"],
        "missing_required_fields": ["string"]
    },
    "recommendations": [
        {
            "priority": "string (critical|high|medium|low)",
            "category": "string (structural|clinical|safety|workflow)",
            "description": "string",
            "impact": "string",
            "estimated_effort": "string (low|medium|high)"
        }
    ],
    "quality_scores": {
        "clinical_coverage": "number (0-100)",
        "structural_quality": "number (0-100)",
        "safety_implementation": "number (0-100)",
        "overall_quality": "number (0-100)"
    },
    "metadata": {
        "analysis_timestamp": "string (ISO 8601)",
        "model_used": "string",
        "playbook_size_bytes": "number",
        "protocol_nodes_count": "number",
        "confidence_scores": {
            "extraction_confidence": "number (0-1)",
            "alignment_confidence": "number (0-1)",
            "recommendations_confidence": "number (0-1)"
        }
    }
}

# Convert schema to JSON string for prompt inclusion (simplified for LLM)
OUTPUT_SCHEMA_JSON = """{
    "clinical_extraction": {
        "syndromes": [
            {
                "name": "string",
                "description": "string",
                "symptoms": ["string"]
            }
        ],
        "exams": [
            {
                "name": "string",
                "type": "string",
                "indication": "string",
                "normalized_name": "string"
            }
        ],
        "treatments": [
            {
                "name": "string",
                "type": "string",
                "indication": "string"
            }
        ],
        "red_flags": [
            {
                "flag": "string",
                "urgency": "string",
                "action": "string"
            }
        ],
        "signs_symptoms": ["string"]
    },
    "structural_analysis": {
        "json_valid": true,
        "logic_issues": [
            {
                "node_id": "string",
                "issue": "string",
                "severity": "string"
            }
        ],
        "unreachable_nodes": ["string"],
        "dead_end_paths": [
            {
                "path": ["string"],
                "reason": "string"
            }
        ]
    },
    "recommendations": [
        {
            "priority": "string",
            "category": "string",
            "description": "string",
            "impact": "string"
        }
    ],
    "quality_scores": {
        "clinical_coverage": 0.0,
        "structural_quality": 0.0,
        "safety_implementation": 0.0,
        "overall_quality": 0.0
    },
    "metadata": {
        "analysis_timestamp": "string",
        "model_used": "string",
        "confidence_scores": {}
    }
}"""

