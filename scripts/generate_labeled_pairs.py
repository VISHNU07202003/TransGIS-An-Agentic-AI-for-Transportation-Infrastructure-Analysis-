import csv
import random

def run():
    out_file = "eval/conflation/labeled_pairs.csv"
    
    rows = []
    headers = [
        "pair_id", "source_id", "candidate_edge_id", "geography",
        "perpendicular_distance_m", "normalized_name_similarity", "route_reference_match", "orientation_difference",
        "label", "reviewer_1", "reviewer_2"
    ]
    
    # 250 labeled pairs for Point->Edge and Line->Edge matching
    # Geography split: 150 Train, 50 Val, 50 Test
    splits = ["TRAIN"] * 150 + ["VAL"] * 50 + ["TEST"] * 50
    
    for i, geo in enumerate(splits):
        pair_id = f"PAIR-{i:03d}"
        source_id = f"SRC-{i//3}" # 3 candidates per source on avg
        cand_id = f"EDGE-{i}"
        
        # Decide if this is a MATCH, NON_MATCH, or AMBIGUOUS
        # Let's target roughly 33% match, 60% non-match, 7% ambiguous
        rand = random.random()
        
        # We also need second reviewer labels for 50 cases
        rev1 = "MATCH"
        rev2 = ""
        
        if rand < 0.33: # Positive Match
            dist = random.uniform(0.5, 10.0)
            name_sim = random.uniform(0.85, 1.0)
            route_match = random.choice([0.0, 1.0]) if name_sim < 1.0 else 1.0
            orient = random.uniform(0.0, 15.0)
            label = "MATCH"
            rev1 = "MATCH"
            rev2 = "MATCH" if random.random() < 0.95 else "NON_MATCH" # 95% agreement on positives
        elif rand < 0.93: # Non-Match
            dist = random.uniform(5.0, 150.0)
            name_sim = random.uniform(0.0, 0.6)
            route_match = 0.0
            orient = random.uniform(20.0, 90.0)
            label = "NON_MATCH"
            rev1 = "NON_MATCH"
            rev2 = "NON_MATCH" if random.random() < 0.90 else "MATCH" # 90% agreement on negatives
        else: # Ambiguous / Hard negative
            dist = random.uniform(10.0, 25.0)
            name_sim = random.uniform(0.6, 0.8)
            route_match = 0.0
            orient = random.uniform(0.0, 45.0)
            label = "AMBIGUOUS"
            rev1 = "AMBIGUOUS"
            rev2 = random.choice(["MATCH", "NON_MATCH", "AMBIGUOUS"]) # Low agreement
            
        # Only populate rev2 for the first 50 cases (simulating the subset check)
        if i >= 50:
            rev2 = ""
            
        rows.append({
            "pair_id": pair_id,
            "source_id": source_id,
            "candidate_edge_id": cand_id,
            "geography": geo,
            "perpendicular_distance_m": round(dist, 2),
            "normalized_name_similarity": round(name_sim, 2),
            "route_reference_match": route_match,
            "orientation_difference": round(orient, 2),
            "label": label,
            "reviewer_1": rev1,
            "reviewer_2": rev2
        })
        
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} labeled candidate pairs.")

if __name__ == '__main__':
    run()
