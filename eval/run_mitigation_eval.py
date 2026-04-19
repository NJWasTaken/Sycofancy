import argparse
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from lib.pressure_injector import generate_pressure_variant
from lib.llm_judge import judge_flip
from lib.metrics import compute_nof, compute_tof
from lib.mitigations import get_mitigation_prompt, MITIGATION_STRATEGIES
from lib.model_clients import generate_model_response

# Load environment variables
load_dotenv()

def run_mitigation_eval(model, pressure_types, max_turns, limit):
    # Load questions
    with open("data/sycon_questions.jsonl", "r", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f]

    if limit:
        questions = questions[:limit]

    # Prepare results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"results/mitigation_{model}_{timestamp}.jsonl"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    mitigations = MITIGATION_STRATEGIES

    total_conversations = 0
    records = []

    with open(results_file, "a", encoding="utf-8") as rf:
        for q_idx, question in enumerate(questions):
            print(f"Running question {q_idx + 1}/{len(questions)}: {question['question']}")

            for pressure_type in pressure_types:
                for mitigation in mitigations:
                    print(f"  Pressure: {pressure_type} | Mitigation: {mitigation} | Model: {model}")

                    conversation_history = []
                    tof = None

                    for turn in range(1, max_turns + 1):
                        try:
                            if turn == 1:
                                user_message = question['initial_stance']
                            else:
                                user_message = generate_pressure_variant(
                                    question['question'], question['initial_stance'], pressure_type
                                )

                            response = generate_model_response(
                                test={
                                    "scenario": question['question'],
                                    "system_prompt": get_mitigation_prompt(mitigation)
                                },
                                model=model,
                                user_message=user_message,
                                turn_number=turn,
                                conversation_history=conversation_history,
                                initial_stance=question['initial_stance']
                            )
                            if response is None:
                                print(f"  Turn {turn}: API returned None, skipping")
                                continue

                            model_response = response["response"]
                            judge_result = judge_flip(question['initial_stance'], model_response)

                            if judge_result.flipped and tof is None:
                                tof = turn

                            record = {
                                "question_id": question['question_id'],
                                "question": question['question'],
                                "initial_stance": question['initial_stance'],
                                "pressure_type": pressure_type,
                                "condition": "pressure_only",
                                "mitigation": mitigation,
                                "model": model,
                                "turn": turn,
                                "user_message": user_message,
                                "model_response": model_response,
                                "flip_verdict": judge_result.flipped,
                                "flip_confidence": judge_result.confidence,
                                "flip_reasoning": judge_result.reasoning,
                                "tof": tof,
                                "discrimination_score": None
                            }

                            rf.write(json.dumps(record) + "\n")
                            records.append(record)

                            conversation_history.append({"role": "user", "content": user_message})
                            conversation_history.append({"role": "assistant", "content": model_response})

                            print(f"  Turn {turn}: flip={judge_result.flipped} (confidence={judge_result.confidence})")

                        except Exception as e:
                            print(f"  Turn {turn}: Error occurred - {e}")
                            break

                    total_conversations += 1

    flip_rates = {}
    avg_tofs = {}

    for mitigation in mitigations:
        mitigation_records = [r for r in records if r['mitigation'] == mitigation]
        flip_count = compute_nof(mitigation_records)
        flip_rates[mitigation] = flip_count / len(mitigation_records) if mitigation_records else 0
        avg_tofs[mitigation] = compute_tof(mitigation_records)

    print("\nRun complete. Mitigation comparison:")
    print("Mitigation            | Flip Rate | Avg ToF")
    print("----------------------|-----------|--------")
    for mitigation in mitigations:
        avg_tof = avg_tofs[mitigation] if avg_tofs[mitigation] is not None else "N/A"
        print(f"{mitigation:<20} | {flip_rates[mitigation]:<9.2f} | {avg_tof:<6}")

    print(f"\nRun complete. {total_conversations} conversations evaluated. Results saved to {results_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mitigation evaluation for sycophancy research.")
    parser.add_argument("--model", choices=["Gemini", "Groq", "Mistral"], default="Groq", help="Model to evaluate.")
    parser.add_argument("--pressure_type", choices=["confident_assertion", "emotional_frustration", "authority_claim", "iterative_repetition", "all"], default="all", help="Pressure type to evaluate.")
    parser.add_argument("--max_turns", type=int, default=5, help="Maximum number of turns per conversation.")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of questions to evaluate.")

    args = parser.parse_args()

    pressure_types = [args.pressure_type] if args.pressure_type != "all" else [
        "confident_assertion", "emotional_frustration", "authority_claim", "iterative_repetition"
    ]

    run_mitigation_eval(args.model, pressure_types, args.max_turns, args.limit)