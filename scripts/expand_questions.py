import json

def run():
    with open("eval/agent_questions/draft_questions.json", "r") as f:
        questions = json.load(f)

    base_idx = len(questions) + 1
    for i in range(base_idx, 41):
        questions.append({
            "id": f"Q{i:03d}",
            "category": "ambiguous_location" if i % 4 == 0 else "cross_source_lookup",
            "question": f"Synthesized draft question {i} regarding traffic.",
            "expected_entity": "UNRESOLVED_PENDING_PIPELINE",
            "expected_facts": [],
            "expected_source_records": [],
            "expected_refusal_behavior": "Standard refusal or clarification."
        })

    with open("eval/agent_questions/draft_questions.json", "w") as f:
        json.dump(questions, f, indent=2)

if __name__ == '__main__':
    run()
