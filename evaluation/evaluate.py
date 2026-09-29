import json
from pathlib import Path

def main():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    experiences = json.loads((data_dir / "synthetic_experiences.json").read_text())
    ground_truth = json.loads((data_dir / "ground_truth.json").read_text())

    payment = [x for x in experiences if x["action"] == "payment_provider_migration"]
    legacy_failures = [
        x for x in payment
        if "legacy_reconciliation" in x["conditions"] and x["status"] == "failure"
    ]
    modern_successes = [
        x for x in payment
        if "modern_billing" in x["conditions"] and x["status"] == "success"
    ]

    # Transparent descriptive metrics for the seeded benchmark.
    result = {
        "experience_count": len(experiences),
        "ground_truth_patterns": len(ground_truth["patterns"]),
        "legacy_failure_cases": len(legacy_failures),
        "modern_success_cases": len(modern_successes),
        "drift_signal": len(modern_successes) >= 2,
        "note": "These are dataset-level signals, not fabricated model accuracy scores."
    }

    report = Path(__file__).parent / "report.json"
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
