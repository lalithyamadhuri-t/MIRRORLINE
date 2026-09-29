import json
import random
from pathlib import Path

random.seed(20260929)

domains = [
    "payments", "billing", "orders", "refunds", "subscriptions",
    "identity", "authentication", "support", "fraud", "analytics",
    "inventory", "fulfillment", "warehouse", "crm", "notifications",
    "pricing", "vendor_management"
]

records = []
rid = 1

def add(action, conditions, outcome, status, domain="payments"):
    global rid
    records.append({
        "experience_id": f"EXP-{rid:04d}",
        "timestamp": f"2026-{(rid % 12)+1:02d}-{(rid % 27)+1:02d}T10:00:00Z",
        "domain": domain,
        "action": action,
        "conditions": conditions,
        "entities": [domain],
        "expected_outcome": "successful operation",
        "actual_outcome": outcome,
        "intervention": None,
        "impact": random.choice(["low", "medium", "high"]),
        "status": status,
        "source": "synthetic_dataset"
    })
    rid += 1

# Purposeful payment migration pattern used by the demo.
for i in range(55):
    if i < 35:
        add("payment_provider_migration", ["legacy_reconciliation", "high_volume"],
            "reconciliation failure", "failure")
    elif i < 43:
        add("payment_provider_migration", ["legacy_reconciliation", "staged_rollout"],
            "successful migration", "success")
    else:
        add("payment_provider_migration", ["modern_billing", "staged_rollout"],
            "successful migration", "success")

actions = [
    ("order_service_deployment", "order failure"),
    ("refund_workflow_change", "refund success"),
    ("subscription_plan_migration", "subscription success"),
    ("identity_provider_rotation", "authentication interruption"),
    ("inventory_recount", "inventory discrepancy"),
    ("notification_provider_change", "delivery delay"),
]

for i in range(245):
    action, outcome = random.choice(actions)
    status = "failure" if "failure" in outcome or "interruption" in outcome or "discrepancy" in outcome or "delay" in outcome else "success"
    add(action, [random.choice(["high_volume", "staged_rollout", "automated_validation", "legacy_stack", "modern_stack"])],
        outcome, status, random.choice(domains))

ground_truth = {
    "patterns": [
        {
            "pattern_id": "PAYMENT-LEGACY-RECON",
            "action": "payment_provider_migration",
            "conditions": ["legacy_reconciliation"],
            "outcome": "reconciliation failure",
            "valid_context": "legacy infrastructure",
            "expected_behavior": "context-dependent after modern successes"
        }
    ]
}

out = Path(__file__).parent
(out/"synthetic_experiences.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
(out/"ground_truth.json").write_text(json.dumps(ground_truth, indent=2), encoding="utf-8")
print(f"Generated {len(records)} experiences.")
