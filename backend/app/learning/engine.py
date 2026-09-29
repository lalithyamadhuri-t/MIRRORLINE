from datetime import datetime
from uuid import uuid4
from collections import defaultdict
from ..models.schemas import Belief, Experience, BeliefValidation
from ..hindsight.memory_service import MemoryService

class LearningEngine:
    def __init__(self, memory: MemoryService):
        self.memory = memory
        self.beliefs: dict[str, Belief] = {}
        self.history: list[dict] = []

    def _is_payment_migration(self, e: dict) -> bool:
        return "payment" in e.get("action", "").lower() and "migration" in e.get("action", "").lower()

    def discover(self) -> list[Belief]:
        experiences = self.memory.memories
        payment = [e for e in experiences if self._is_payment_migration(e)]
        if payment:
            legacy = [e for e in payment if any("legacy" in c.lower() for c in e.get("conditions", []))]
            if legacy:
                failures = sum(e.get("status") == "failure" for e in legacy)
                successes = sum(e.get("status") == "success" for e in legacy)
                total = failures + successes
                strength = round((failures + 1) / (total + 2), 2)
                statement = "Payment migration with legacy reconciliation infrastructure is associated with elevated reconciliation risk."
                self._upsert("BELIEF-001", statement, strength, failures, successes, [e["experience_id"] for e in legacy])
        return list(self.beliefs.values())

    def _upsert(self, belief_id, statement, strength, support_count, contradiction_count, evidence_ids):
        now = datetime.utcnow()
        old = self.beliefs.get(belief_id)
        version = old.version if old else 1
        if old and old.statement != statement:
            version += 1
        self.beliefs[belief_id] = Belief(
            belief_id=belief_id,
            statement=statement,
            strength=max(0, min(1, strength)),
            status=self._status(strength, support_count, contradiction_count),
            support_count=support_count,
            contradiction_count=contradiction_count,
            created_at=old.created_at if old else now,
            updated_at=now,
            version=version,
            evidence_ids=evidence_ids,
        )

    @staticmethod
    def _status(strength, support, contradiction):
        if contradiction >= max(2, support):
            return "CHALLENGED"
        if support >= 5 and strength >= .75:
            return "ESTABLISHED"
        if contradiction > 0 and support > contradiction:
            return "CONTEXT_DEPENDENT"
        if support >= 2:
            return "SUPPORTED"
        return "EMERGING"

    def validate(self, belief_id: str) -> BeliefValidation:
        belief = self.beliefs[belief_id]
        memories = self.memory.memories
        relevant = [e for e in memories if self._is_payment_migration(e)]
        legacy = [e for e in relevant if any("legacy" in c.lower() for c in e.get("conditions", []))]
        modern = [e for e in relevant if any("modern" in c.lower() for c in e.get("conditions", []))]
        supporting = [e for e in legacy if e.get("status") == "failure"]
        contradictory = [e for e in modern if e.get("status") == "success"]
        drift = len(contradictory) >= 2

        revised = None
        status = belief.status
        explanation = "The historical evidence remains consistent with the current belief."
        if drift:
            revised = "Payment migration is associated with elevated reconciliation risk primarily when legacy reconciliation infrastructure is present."
            status = "CONTEXT_DEPENDENT"
            explanation = (
                f"{len(contradictory)} recent successful migrations occurred under modernized "
                "conditions, while failures remain concentrated in legacy infrastructure. "
                "The evidence supports a contextual refinement rather than deleting the historical lesson."
            )
        return BeliefValidation(
            belief_id=belief_id,
            original_statement=belief.statement,
            status=status,
            strength=belief.strength,
            support_count=len(supporting),
            contradiction_count=len(contradictory),
            supporting_evidence=[Experience(**e) for e in supporting],
            contradictory_evidence=[Experience(**e) for e in contradictory],
            context_change="Legacy reconciliation infrastructure vs modernized billing/reconciliation infrastructure.",
            revised_statement=revised,
            explanation=explanation,
        )

    def revise(self, belief_id: str) -> Belief:
        validation = self.validate(belief_id)
        if not validation.revised_statement:
            return self.beliefs[belief_id]
        old = self.beliefs[belief_id]
        new_version = old.version + 1
        now = datetime.utcnow()
        revised = old.model_copy(update={
            "statement": validation.revised_statement,
            "status": "CONTEXT_DEPENDENT",
            "contradiction_count": validation.contradiction_count,
            "version": new_version,
            "updated_at": now,
            "strength": round(max(.55, old.strength - .08), 2),
        })
        self.beliefs[belief_id] = revised
        self.history.append({
            "type": "BELIEF_REVISION",
            "belief_id": belief_id,
            "from_version": old.version,
            "to_version": new_version,
            "timestamp": now.isoformat(),
            "reason": validation.explanation,
        })
        return revised

    def scenario(self, text: str):
        relevant = self.memory.recall(text, 50)
        beliefs = list(self.beliefs.values())
        if not relevant:
            return {
                "scenario": text,
                "relevant_beliefs": [],
                "evidence_count": 0,
                "analysis": "Insufficient historical evidence.",
                "evidence_basis": [],
                "uncertainty": "high",
            }
        analyses = []
        for b in beliefs:
            if "payment" in text.lower() and "payment" in b.statement.lower():
                analyses.append(b)
        evidence = [m["experience_id"] for m in relevant]
        return {
            "scenario": text,
            "relevant_beliefs": analyses,
            "evidence_count": len(relevant),
            "analysis": (
                "Historical evidence suggests elevated reconciliation risk when the "
                "scenario resembles legacy-infrastructure migration cases. Recent modernized "
                "migrations reduce the applicability of the older generalization."
            ),
            "evidence_basis": evidence,
            "uncertainty": "medium",
        }

    def reset(self):
        self.beliefs.clear()
        self.history.clear()
        self.memory.clear()
