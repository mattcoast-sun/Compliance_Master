"""
Quality Rules for ISO Document Validation
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


class QualityRule:
    """Base class for quality rules"""
    
    def __init__(self, rule_id: str, name: str, description: str, severity: str = "error"):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.severity = severity  # "error", "warning", "info"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity
        }


# Define quality rules
QUALITY_RULES = [
    # Completeness Rules
    QualityRule(
        rule_id="QR001",
        name="Required Fields Present",
        description="All required fields (document_title, document_number, revision_number, effective_date, department, author, purpose, scope) must be present and not empty or 'Not found'.",
        severity="error"
    ),
    QualityRule(
        rule_id="QR002",
        name="Document Structure Complete",
        description="Generated template must include all required sections: header, purpose, scope, definitions, procedures/records, responsibilities, related documents, and revision history.",
        severity="error"
    ),
    
    # Data Quality Rules
    QualityRule(
        rule_id="QR003",
        name="Department Field Validation",
        description="Department field must contain a valid department name, not 'Not found', 'N/A', or be empty.",
        severity="error"
    ),
    QualityRule(
        rule_id="QR004",
        name="Date Validity Check",
        description="Effective date must be a valid date and not older than 2 years from today.",
        severity="warning"
    ),
    QualityRule(
        rule_id="QR005",
        name="Document Number Format",
        description="Document number should follow a standard format (e.g., XXX-### or similar alphanumeric pattern).",
        severity="warning"
    ),
    QualityRule(
        rule_id="QR006",
        name="Revision Number Format",
        description="Revision number should be in a standard format (e.g., 1.0, 2.1, Rev A, etc.).",
        severity="info"
    ),
    QualityRule(
        rule_id="QR007",
        name="Author Field Populated",
        description="Author field must contain a person's name, not 'Not found' or generic text.",
        severity="error"
    ),
    
    # Content Quality Rules
    QualityRule(
        rule_id="QR008",
        name="Purpose Statement Quality",
        description="Purpose statement must be clear, concise, and at least 20 characters long.",
        severity="warning"
    ),
    QualityRule(
        rule_id="QR009",
        name="Scope Statement Quality",
        description="Scope statement must be specific and at least 20 characters long.",
        severity="warning"
    ),
    QualityRule(
        rule_id="QR010",
        name="Template Length Check",
        description="Generated template must be at least 500 characters long to ensure adequate detail.",
        severity="error"
    ),
    
    # ISO Compliance Rules
    QualityRule(
        rule_id="QR011",
        name="ISO Standard Referenced",
        description="Template must explicitly reference the ISO standard it complies with.",
        severity="error"
    ),
    QualityRule(
        rule_id="QR012",
        name="Traceability Present",
        description="Template should include document control information (version, date, approval).",
        severity="warning"
    ),
    QualityRule(
        rule_id="QR013",
        name="Professional Language",
        description="Template must use professional, formal language appropriate for ISO documentation.",
        severity="info"
    ),
    
    # Consistency Rules
    QualityRule(
        rule_id="QR014",
        name="Field Consistency",
        description="Extracted fields must be consistently used throughout the generated template.",
        severity="warning"
    ),
    QualityRule(
        rule_id="QR015",
        name="No Placeholder Text",
        description="Template must not contain placeholder text like '[INSERT TEXT]', 'TBD', or similar.",
        severity="error"
    ),
]


def get_all_rules() -> List[Dict[str, str]]:
    """Get all quality rules as dictionaries"""
    return [rule.to_dict() for rule in QUALITY_RULES]


def get_rules_by_severity(severity: str) -> List[Dict[str, str]]:
    """Get quality rules filtered by severity"""
    return [rule.to_dict() for rule in QUALITY_RULES if rule.severity == severity]


def get_critical_rules() -> List[Dict[str, str]]:
    """Get only critical (error severity) rules"""
    return get_rules_by_severity("error")


def format_rules_for_prompt() -> str:
    """Format quality rules for LLM prompt"""
    rules_text = []
    for rule in QUALITY_RULES:
        rules_text.append(
            f"[{rule.rule_id}] {rule.name} ({rule.severity.upper()})\n"
            f"   {rule.description}"
        )
    return "\n\n".join(rules_text)

