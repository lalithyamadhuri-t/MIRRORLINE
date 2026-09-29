from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

ExperienceStatus = Literal["failure", "success", "near_miss", "intervention"]

class ExperienceCreate(BaseModel):
    action: str = Field(min_length=2)
    conditions: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    expected_outcome: Optional[str] = None
    actual_outcome: str = Field(min_length=2)
    intervention: Optional[str] = None
    impact: str = "medium"
    status: ExperienceStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "user"

class Experience(ExperienceCreate):
    experience_id: str

class Belief(BaseModel):
    belief_id: str
    statement: str
    strength: float
    status: str
    support_count: int
    contradiction_count: int
    created_at: datetime
    updated_at: datetime
    version: int = 1
    evidence_ids: list[str] = Field(default_factory=list)

class BeliefValidation(BaseModel):
    belief_id: str
    original_statement: str
    status: str
    strength: float
    support_count: int
    contradiction_count: int
    supporting_evidence: list[Experience]
    contradictory_evidence: list[Experience]
    context_change: str
    revised_statement: Optional[str] = None
    explanation: str

class ScenarioRequest(BaseModel):
    scenario: str = Field(min_length=3)

class ScenarioResponse(BaseModel):
    scenario: str
    relevant_beliefs: list[Belief]
    evidence_count: int
    analysis: str
    evidence_basis: list[str]
    uncertainty: str
