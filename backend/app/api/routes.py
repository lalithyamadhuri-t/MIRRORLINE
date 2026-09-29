from fastapi import APIRouter, HTTPException
from ..models.schemas import ExperienceCreate, Experience, ScenarioRequest
from ..hindsight.memory_service import MemoryService
from ..learning.engine import LearningEngine
from ..hindsight.hindsight_adapter import HindsightAdapter

router = APIRouter(prefix="/api")

memory = MemoryService()
engine = LearningEngine(memory)
hindsight_adapter = HindsightAdapter()

def serialize_experience(data):
    return Experience(**data)


@router.get("/hindsight/status")
def hindsight_status():
    return hindsight_adapter.status()

@router.get("/dashboard")
def dashboard():
    beliefs = list(engine.beliefs.values())
    return {
        "experiences": len(memory.memories),
        "beliefs": len(beliefs),
        "drifting": sum(b.status == "CONTEXT_DEPENDENT" for b in beliefs),
        "challenged": sum(b.status == "CHALLENGED" for b in beliefs),
        "supported": sum(b.status in {"SUPPORTED", "ESTABLISHED"} for b in beliefs),
        "memory_events": len(memory.memories),
        "learning_events": len(engine.history),
    }

@router.post("/experiences", response_model=Experience)
def create_experience(payload: ExperienceCreate):
    eid = f"EXP-{len(memory.memories)+1:03d}"
    data = payload.model_dump()
    data["experience_id"] = eid
    memory.retain(data)
    return Experience(**data)

@router.get("/experiences", response_model=list[Experience])
def get_experiences():
    return [Experience(**e) for e in memory.memories]

@router.post("/learn/discover")
def discover():
    return {"beliefs": engine.discover()}

@router.get("/beliefs")
def beliefs():
    return list(engine.beliefs.values())

@router.get("/beliefs/{belief_id}")
def get_belief(belief_id: str):
    if belief_id not in engine.beliefs:
        raise HTTPException(404, "Belief not found")
    return engine.beliefs[belief_id]

@router.post("/beliefs/{belief_id}/validate")
def validate_belief(belief_id: str):
    if belief_id not in engine.beliefs:
        raise HTTPException(404, "Belief not found")
    return engine.validate(belief_id)

@router.post("/beliefs/{belief_id}/revise")
def revise_belief(belief_id: str):
    if belief_id not in engine.beliefs:
        raise HTTPException(404, "Belief not found")
    return engine.revise(belief_id)

@router.get("/drift")
def drift():
    results = []
    for belief in engine.beliefs.values():
        validation = engine.validate(belief.belief_id)
        if validation.revised_statement:
            results.append({
                "belief_id": belief.belief_id,
                "status": "DRIFT_DETECTED",
                "contradictions": validation.contradiction_count,
                "context_change": validation.context_change,
            })
    return results

@router.post("/analyze")
def analyze(payload: ScenarioRequest):
    return engine.scenario(payload.scenario)

@router.get("/learning-history")
def learning_history():
    return engine.history

@router.get("/evaluation")
def evaluation():
    return {
        "note": "Prototype evaluation endpoint. Add generated ground truth and measured metrics before final submission.",
        "metrics": {},
    }

@router.post("/demo/reset")
def demo_reset():
    engine.reset()
    return {"status": "reset"}

@router.post("/demo/run")
def demo_run():
    engine.reset()
    demo = [
        ("payment_provider_migration", ["legacy_reconciliation", "high_transaction_volume"], "reconciliation failure", "failure"),
        ("payment_provider_migration", ["legacy_billing", "weekend_deployment"], "refund failure", "failure"),
        ("payment_provider_migration", ["legacy_infrastructure"], "reconciliation failure", "failure"),
        ("payment_provider_migration", ["legacy_reconciliation"], "reconciliation failure", "failure"),
        ("payment_provider_migration", ["staged_rollout", "legacy_reconciliation"], "successful migration", "success"),
        ("payment_provider_migration", ["modern_billing", "staged_rollout"], "successful migration", "success"),
        ("payment_provider_migration", ["modern_billing"], "successful migration", "success"),
        ("payment_provider_migration", ["modern_billing", "staged_rollout"], "successful migration", "success"),
    ]
    for action, conditions, outcome, status in demo:
        create_experience(ExperienceCreate(
            action=action,
            conditions=conditions,
            entities=["Payments", "Billing", "Reconciliation"],
            expected_outcome="successful migration",
            actual_outcome=outcome,
            status=status,
            impact="high",
            source="demo",
        ))
    engine.discover()
    initial = engine.beliefs.get("BELIEF-001")
    validation = engine.validate("BELIEF-001")
    revised = engine.revise("BELIEF-001")
    return {
        "initial_belief": initial.model_copy(update={"version": 1}) if initial else None,
        "validation": validation,
        "revised_belief": revised,
        "hindsight": {
            "retain": len(memory.memories),
            "recall": len(memory.recall("payment migration", 50)),
            "reflect": memory.reflect(memory.memories),
        },
    }
