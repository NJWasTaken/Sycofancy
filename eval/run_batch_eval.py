import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

from lib.pressure_injector import generate_pressure_variant
from lib.llm_judge import judge_flip
from lib.metrics import compute_tof, compute_nof, compute_model_summary
from lib.mitigations import get_mitigation_prompt, MITIGATION_STRATEGIES
from lib.model_clients import generate_model_response

# Load environment variables
load_dotenv()

def load_questions(filepath: str) -> list[dict]:
    """Load questions from a JSONL file."""
    questions = []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    questions.append(json.loads(line))
                except json.JSONDecodeError:
                    print("Skipping malformed question line.")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return questions

def run_batch_eval(model: str, pressure_types: list[str], strategies: list[str], max_turns: int, limit: Optional[int]):
    """Run the batch evaluation pipeline."""
    # Load questions
    questions = load_questions("data/sycon_questions.jsonl")
    if limit:
        questions = questions[:limit]

    # Ensure results directory exists
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # Create results file for the entire run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"{model}_batch_{timestamp}.jsonl"

    with results_file.open("a", encoding="utf-8") as f:
        # Iterate over questions
        for q_idx, question in enumerate(questions, start=1):
            print(f"Running question {q_idx}/{len(questions)}: {question['question']}")
            for pressure_type in pressure_types:
                for strategy in strategies:
                    print(f"  Pressure: {pressure_type} | Mitigation: {strategy} | Model: {model}")

                    # Prepare mitigation prompt
                    mitigation_prompt = get_mitigation_prompt(strategy)

                    # Initialize conversation
                    conversation_history = []
                    initial_stance = question["initial_stance"]
                    question_id = question["question_id"]
                    tof = None

                    for turn in range(1, max_turns + 1):
                        try:
                            if turn == 1:
                                user_message = initial_stance
                            else:
                                user_message = generate_pressure_variant(
                                    question["question"], initial_stance, pressure_type
                                )

                            # Generate model response
                            response = generate_model_response(
                                test={
                                    "scenario": question["question"],
                                    "system_prompt": mitigation_prompt
                                },
                                model=model,
                                user_message=user_message,
                                turn_number=turn,
                                conversation_history=conversation_history,
                                initial_stance=initial_stance
                            )
                            if response is None:
                                print(f"  Turn {turn}: API returned None, skipping")
                                continue

                            model_response = response["response"]

                            # Judge the response
                            judge_result = judge_flip(initial_stance, model_response)

                            # Record flip verdict
                            flip_verdict = judge_result.flipped
                            flip_confidence = judge_result.confidence
                            flip_reasoning = judge_result.reasoning

                            if flip_verdict and tof is None:
                                tof = turn

                            # Append to conversation history
                            conversation_history.append({
                                "role": "user", "content": user_message
                            })
                            conversation_history.append({
                                "role": "assistant", "content": model_response
                            })

                            # Write result to file
                            record = {
                                "question_id": question_id,
                                "question": question["question"],
                                "initial_stance": initial_stance,
                                "pressure_type": pressure_type,
                                "condition": "pressure_only",
                                "mitigation": strategy,
                                "model": model,
                                "turn": turn,
                                "user_message": user_message,
                                "model_response": model_response,
                                "flip_verdict": flip_verdict,
                                "flip_confidence": flip_confidence,
                                "flip_reasoning": flip_reasoning,
                                "tof": tof,
                                "discrimination_score": None
                            }
                            f.write(json.dumps(record) + "\n")

                            print(f"  Turn {turn}: flip={flip_verdict} (confidence={flip_confidence})")

                        except Exception as e:
                            print(f"  Error on turn {turn}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch evaluation pipeline.")
    parser.add_argument("--model", choices=["Gemini", "Groq", "Mistral"], default="Groq", help="Model to evaluate.")
    parser.add_argument("--pressure_type", choices=["confident_assertion", "emotional_frustration", "authority_claim", "iterative_repetition", "all"], default="all", help="Pressure type(s) to evaluate.")
    parser.add_argument("--mitigation", choices=MITIGATION_STRATEGIES, default="none", help="Mitigation strategy to use.")
    parser.add_argument("--max_turns", type=int, default=5, help="Maximum turns per conversation.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to evaluate.")

    args = parser.parse_args()

    pressure_types = [args.pressure_type] if args.pressure_type != "all" else [
        "confident_assertion", "emotional_frustration", "authority_claim", "iterative_repetition"
    ]

    run_batch_eval(
        model=args.model,
        pressure_types=pressure_types,
        strategies=[args.mitigation],
        max_turns=args.max_turns,
        limit=args.limit
    )