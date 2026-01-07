"""Utility stubs for the test-only sentence_transformers package."""
def cos_sim(a, b):
    try:
        va = list(a)
        vb = list(b)
        if not va or not vb:
            return 0.0
        dot = sum(x * y for x, y in zip(va, vb))
        norma = sum(x * x for x in va) ** 0.5
        normb = sum(y * y for y in vb) ** 0.5
        if norma == 0 or normb == 0:
            return 0.0
        return dot / (norma * normb)
    except Exception:
        return 0.0

def is_datasets_available():
    return False
