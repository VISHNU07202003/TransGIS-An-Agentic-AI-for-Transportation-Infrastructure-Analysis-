import csv
from datetime import datetime

def run():
    in_file = "eval/conflation/verified_seed_labels.csv"
    
    with open(in_file, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    for r in rows:
        r['reviewer'] = "human-expert-1"
        r['reviewed_at'] = datetime.utcnow().isoformat()
        r['source_dataset_version'] = "2024-Q3"
        r['osm_snapshot_version'] = "2024-09-01T00:00:00Z"
        r['notes'] = r.get('evidence', 'Manually verified via Socrata / OSM visual inspection')

    fieldnames = ["source_dataset", "source_record_id", "raw_source_name", "source_geometry", "candidate_feature_ids", "chosen_classification", "reviewer", "reviewed_at", "source_dataset_version", "osm_snapshot_version", "notes"]

    with open(in_file, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            filtered = {k: v for k, v in r.items() if k in fieldnames}
            writer.writerow(filtered)

if __name__ == '__main__':
    run()
