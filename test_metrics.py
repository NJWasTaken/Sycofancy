from lib.metrics import compute_tof, compute_nof, compute_discrimination_score, compute_model_summary

# Dummy records simulating a 5-turn conversation where model flips on turn 3
conversation = [
    {"question_id": "q1", "pressure_type": "confident_assertion", "model": "Groq", "turn": 1, "flip_verdict": False, "flip_confidence": 0.1},
    {"question_id": "q1", "pressure_type": "confident_assertion", "model": "Groq", "turn": 2, "flip_verdict": False, "flip_confidence": 0.2},
    {"question_id": "q1", "pressure_type": "confident_assertion", "model": "Groq", "turn": 3, "flip_verdict": True,  "flip_confidence": 0.9},
    {"question_id": "q1", "pressure_type": "confident_assertion", "model": "Groq", "turn": 4, "flip_verdict": True,  "flip_confidence": 0.8},
    {"question_id": "q1", "pressure_type": "confident_assertion", "model": "Groq", "turn": 5, "flip_verdict": False, "flip_confidence": 0.1},
]

print("ToF (should be 3):", compute_tof(conversation))
print("NoF (should be 2):", compute_nof(conversation))

# Discrimination score test
pressure_records = [
    {"flip_verdict": True},
    {"flip_verdict": True},
    {"flip_verdict": False},
]  # resists 1/3 of the time = 0.33

evidence_records = [
    {"flip_verdict": False},
    {"flip_verdict": False},
    {"flip_verdict": True},
]  # resists 2/3 of the time = 0.67

# Score = 0.33 - 0.67 = -0.33 (model is stubborn even on evidence)
print("Discrimination score (should be -0.33):", round(compute_discrimination_score(pressure_records, evidence_records), 2))

# Model summary test
summary = compute_model_summary(conversation)
print("Model:", summary["model"])
print("Total conversations:", summary["total_conversations"])
print("Overall flip rate (should be 0.4):", summary["overall_flip_rate"])
print("Avg ToF (should be 3.0):", summary["avg_tof"])
print("Total NoF (should be 2):", summary["total_nof"])
print("Per pressure type:", summary["per_pressure_type"])