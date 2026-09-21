from services.distress_service import calculate_distress

def test_distress_result():
    score, risk = calculate_distress(4, 8, 4, 5, 7)
    assert 0 <= score <= 100
    assert risk in {"Low Concern", "Needs Attention", "Human Review"}
