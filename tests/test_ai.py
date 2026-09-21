from services.ai_service import local_text_summary

def test_local_summary():
    result = local_text_summary("I feel stressed and worried.")
    assert "stress" in result.lower() or "worried" in result.lower()
