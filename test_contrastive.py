from lib.contrastive_pairs import load_pairs, get_pair_by_id, validate_pair, pairs_to_eval_records

pairs = load_pairs()
print(f"Loaded {len(pairs)} pairs")

pair = get_pair_by_id("cp_001", pairs)
print(f"Got pair: {pair['question'] if pair else 'NOT FOUND'}")

records = pairs_to_eval_records(pairs[:2], model="Groq", pressure_type="confident_assertion")
print(f"Generated {len(records)} eval records (should be 4)")
print(f"Conditions: {[r['condition'] for r in records]}")