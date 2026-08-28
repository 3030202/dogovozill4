"""Modular Russian legal clauses package."""

from core.templates.clauses.preamble import build_preamble_clauses, get_party_role_names
from core.templates.clauses.subject import build_subject_clauses
from core.templates.clauses.payment import build_payment_clauses
from core.templates.clauses.delivery_acceptance import build_delivery_acceptance_clauses
from core.templates.clauses.liability import build_liability_clauses
from core.templates.clauses.force_majeure import build_force_majeure_clauses
from core.templates.clauses.confidentiality import build_confidentiality_clauses
from core.templates.clauses.dispute_resolution import build_dispute_resolution_clauses
from core.templates.clauses.term_termination import build_term_termination_clauses
from core.templates.clauses.signatures import build_signatures_block

__all__ = [
    "build_preamble_clauses",
    "get_party_role_names",
    "build_subject_clauses",
    "build_payment_clauses",
    "build_delivery_acceptance_clauses",
    "build_liability_clauses",
    "build_force_majeure_clauses",
    "build_confidentiality_clauses",
    "build_dispute_resolution_clauses",
    "build_term_termination_clauses",
    "build_signatures_block",
]
