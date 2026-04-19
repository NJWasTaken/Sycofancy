import json
from typing import Optional, Tuple

def load_pairs(filepath: str = "data/contrastive_pairs.jsonl") -> list[dict]:
    """
    Load and validate contrastive pairs from a JSONL file.

    Args:
        filepath (str): Path to the JSONL file.

    Returns:
        list[dict]: List of valid contrastive pairs.
    """
    pairs = []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    pair = json.loads(line)
                    is_valid, missing_fields = validate_pair(pair)
                    if is_valid:
                        pairs.append(pair)
                    else:
                        print(f"Skipping invalid pair: missing fields {missing_fields}")
                except json.JSONDecodeError:
                    print("Skipping malformed line: not valid JSON")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return pairs

def get_pair_by_id(pair_id: str, pairs: list[dict]) -> Optional[dict]:
    """
    Get a contrastive pair by its ID.

    Args:
        pair_id (str): The ID of the pair to retrieve.
        pairs (list[dict]): List of contrastive pairs.

    Returns:
        dict | None: The matching pair, or None if not found.
    """
    for pair in pairs:
        if pair.get("pair_id") == pair_id:
            return pair
    return None

def validate_pair(pair: dict) -> Tuple[bool, list[str]]:
    """
    Validate a single contrastive pair.

    Args:
        pair (dict): The pair to validate.

    Returns:
        tuple[bool, list[str]]: (True, []) if valid, (False, [missing fields]) if invalid.
    """
    required_fields = ["pair_id", "question", "initial_stance", "pressure_pushback", "evidence_pushback"]
    missing_fields = [field for field in required_fields if field not in pair]
    if missing_fields:
        return False, missing_fields
    return True, []

def pairs_to_eval_records(
    pairs: list[dict], 
    model: str,
    pressure_type: str
) -> list[dict]:
    """
    Convert contrastive pairs into eval record format.

    Args:
        pairs (list[dict]): List of contrastive pairs.
        model (str): The model being evaluated.
        pressure_type (str): The type of pressure applied.

    Returns:
        list[dict]: List of eval records (2 per pair).
    """
    eval_records = []
    for pair in pairs:
        eval_records.append({
            "question_id": pair["pair_id"],
            "question": pair["question"],
            "initial_stance": pair["initial_stance"],
            "pressure_type": pressure_type,
            "condition": "pressure_only",
            "mitigation": "none",
            "model": model,
            "turn": 1,
            "user_message": pair["pressure_pushback"],
            "model_response": "",
            "flip_verdict": None,
            "flip_confidence": None,
            "flip_reasoning": "",
            "tof": None,
            "discrimination_score": None
        })
        eval_records.append({
            "question_id": pair["pair_id"],
            "question": pair["question"],
            "initial_stance": pair["initial_stance"],
            "pressure_type": pressure_type,
            "condition": "with_evidence",
            "mitigation": "none",
            "model": model,
            "turn": 1,
            "user_message": pair["evidence_pushback"],
            "model_response": "",
            "flip_verdict": None,
            "flip_confidence": None,
            "flip_reasoning": "",
            "tof": None,
            "discrimination_score": None
        })
    return eval_records