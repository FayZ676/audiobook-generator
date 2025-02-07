from sklearn.metrics import precision_score, recall_score


# Normalize names for consistency
def _normalize_names(names):
    return [name.lower().strip() for name in names]


# Test extracted results against True Positives list for precision and recall
def test_precision_recall(predicted, true_positives):
    predicted = _normalize_names(predicted)
    true_positives = _normalize_names(true_positives)
    all_names = list(set(true_positives + predicted))
    y_true = [1 if name in predicted else 0 for name in all_names]
    y_pred = [1 if name in true_positives else 0 for name in all_names]

    precision = precision_score(y_true, y_pred, zero_division=1)
    recall = recall_score(y_true, y_pred, zero_division=1)
    return precision, recall
