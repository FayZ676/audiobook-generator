def test_precision_recall(computed: set[tuple[str]], expected: set[tuple[str]]):
    true_positives = computed.intersection(expected)
    # Calculate precision: TP / (TP + FP)
    precision = len(true_positives) / len(computed) if computed else 0.0
    # Calculate recall: TP / (TP + FN)
    recall = len(true_positives) / len(expected) if expected else 0.0
    return precision, recall
