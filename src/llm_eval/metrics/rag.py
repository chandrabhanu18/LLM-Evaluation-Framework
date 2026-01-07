from typing import Any, Dict, List
from .base import Metric

import re


def _tokenize_text(s: str) -> List[str]:
    return re.findall(r"\w+", s.lower())


class FaithfulnessMetric(Metric):
    def __init__(self, name: str = "faithfulness"):
        super().__init__(name)

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        ans_tokens = set(_tokenize_text(answer))
        ctx_tokens = set()
        if isinstance(contexts, list):
            for c in contexts:
                ctx_tokens.update(_tokenize_text(c))
        else:
            ctx_tokens.update(_tokenize_text(str(contexts)))
        if not ans_tokens:
            return {"score": 0.0}
        overlap = len(ans_tokens & ctx_tokens) / len(ans_tokens)
        return {"score": float(overlap)}


class ContextRelevancyMetric(Metric):
    _model = None

    def __init__(self, name: str = "context_relevancy", model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(name)
        if not ContextRelevancyMetric._model:
            try:
                from sentence_transformers import SentenceTransformer
                ContextRelevancyMetric._model = SentenceTransformer(model_name)
            except Exception:
                ContextRelevancyMetric._model = None
        self.model = ContextRelevancyMetric._model

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        if not self.model:
            # fallback simple heuristic
            best = 0.0
            if isinstance(contexts, list):
                for c in contexts:
                    if query in c or any(tok in c for tok in query.split()):
                        best = 1.0
            else:
                if query in str(contexts):
                    best = 1.0
            return {"score": float(best)}

        q_emb = self.model.encode(query, convert_to_tensor=True)
        best = 0.0
        if isinstance(contexts, list):
            for c in contexts:
                c_emb = self.model.encode(c, convert_to_tensor=True)
                try:
                    from sentence_transformers import util as _util
                except Exception:
                    try:
                        import sentence_transformers.util as _util
                    except Exception:
                        _util = None
                sim = _util.cos_sim(q_emb, c_emb).item() if _util is not None else 0.0
                if sim > best:
                    best = sim
        else:
            c_emb = self.model.encode(str(contexts), convert_to_tensor=True)
            try:
                from sentence_transformers import util as _util
            except Exception:
                try:
                    import sentence_transformers.util as _util
                except Exception:
                    _util = None
            best = _util.cos_sim(q_emb, c_emb).item() if _util is not None else 0.0
        normal = (best + 1.0) / 2.0
        return {"score": float(normal)}


class AnswerRelevancyMetric(Metric):
    _model = None

    def __init__(self, name: str = "answer_relevancy", model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(name)
        if not AnswerRelevancyMetric._model:
            try:
                from sentence_transformers import SentenceTransformer
                AnswerRelevancyMetric._model = SentenceTransformer(model_name)
            except Exception:
                AnswerRelevancyMetric._model = None
        self.model = AnswerRelevancyMetric._model

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        if not self.model:
            # fallback simple overlap
            qset = set(query.split())
            aset = set(answer.split())
            sim = len(qset & aset) / max(1, len(qset))
            return {"score": float(sim)}
        q_emb = self.model.encode(query, convert_to_tensor=True)
        a_emb = self.model.encode(answer, convert_to_tensor=True)
        # try to use util.cos_sim if available
        try:
            from sentence_transformers import util as _util
            sim = _util.cos_sim(q_emb, a_emb).item()
        except Exception:
            sim = 0.0
        normal = (sim + 1.0) / 2.0
        return {"score": float(normal)}
