import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, cohen_kappa_score
from sklearn.utils import resample

def rule_baseline(df):
    return ((df['perpendicular_distance_m'] <= 20.0) & 
            ((df['normalized_name_similarity'] > 0.85) | (df['route_reference_match'] == 1.0))).astype(int)

def distance_baseline(df):
    return (df['perpendicular_distance_m'] <= 15.0).astype(int)

def bootstrap_metrics(y_true, y_pred, n_iterations=1000, seed=42):
    np.random.seed(seed)
    n_size = len(y_true)
    precisions, recalls, f1s = [], [], []
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    for i in range(n_iterations):
        indices = resample(range(n_size))
        yt = y_true[indices]
        yp = y_pred[indices]
        precisions.append(precision_score(yt, yp, zero_division=0))
        recalls.append(recall_score(yt, yp, zero_division=0))
        f1s.append(f1_score(yt, yp, zero_division=0))
        
    return {
        "precision_ci": (np.percentile(precisions, 2.5), np.percentile(precisions, 97.5)),
        "recall_ci": (np.percentile(recalls, 2.5), np.percentile(recalls, 97.5)),
        "f1_ci": (np.percentile(f1s, 2.5), np.percentile(f1s, 97.5))
    }

def run():
    df = pd.read_csv("eval/conflation/labeled_pairs.csv")
    
    # Inter-reviewer agreement
    rev_df = df[df['reviewer_2'].notna() & (df['reviewer_2'] != '')]
    if len(rev_df) > 0:
        kappa = cohen_kappa_score(rev_df['reviewer_1'], rev_df['reviewer_2'])
        raw_agree = (rev_df['reviewer_1'] == rev_df['reviewer_2']).mean()
    else:
        kappa, raw_agree = 0, 0

    df_clean = df[df['label'].isin(["MATCH", "NON_MATCH"])].copy()
    df_clean['target'] = (df_clean['label'] == 'MATCH').astype(int)
    
    train_c = df_clean[df_clean['geography'] == 'TRAIN']
    val_c = df_clean[df_clean['geography'] == 'VAL']
    test_c = df_clean[df_clean['geography'] == 'TEST']
    
    features = ["perpendicular_distance_m", "normalized_name_similarity", "route_reference_match", "orientation_difference"]
    
    X_train, y_train = train_c[features], train_c['target']
    X_val, y_val = val_c[features], val_c['target']
    X_test, y_test = test_c[features], test_c['target']
    
    lr = LogisticRegression(class_weight='balanced', random_state=42)
    lr.fit(X_train, y_train)
    
    coeffs = dict(zip(features, lr.coef_[0]))
    
    val_res = {
        "dist_f1": f1_score(y_val, distance_baseline(val_c)),
        "rule_f1": f1_score(y_val, rule_baseline(val_c)),
        "lr_f1": f1_score(y_val, lr.predict(X_val))
    }
    
    test_dist = distance_baseline(test_c)
    test_rule = rule_baseline(test_c)
    test_lr_probs = lr.predict_proba(X_test)[:, 1]
    
    test_lr_preds = []
    ambiguity_correct = 0
    for p in test_lr_probs:
        if p < 0.4: test_lr_preds.append(0)
        elif 0.4 <= p <= 0.6: 
            test_lr_preds.append(0)
            ambiguity_correct += 1
        else: test_lr_preds.append(1)
        
    ci = bootstrap_metrics(y_test, test_lr_preds)
    
    test_res = {
        "dist": {
            "p": precision_score(y_test, test_dist),
            "r": recall_score(y_test, test_dist),
            "f1": f1_score(y_test, test_dist)
        },
        "rule": {
            "p": precision_score(y_test, test_rule),
            "r": recall_score(y_test, test_rule),
            "f1": f1_score(y_test, test_rule)
        },
        "lr": {
            "p": precision_score(y_test, test_lr_preds),
            "r": recall_score(y_test, test_lr_preds),
            "f1": f1_score(y_test, test_lr_preds),
            "ci_f1": ci['f1_ci']
        }
    }
    
    out = {
        "kappa": kappa,
        "raw_agree": raw_agree,
        "coeffs": coeffs,
        "val": val_res,
        "test": test_res,
        "ambiguity_correct": ambiguity_correct
    }
    
    with open("eval/conflation/phase45_results.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == '__main__':
    run()
