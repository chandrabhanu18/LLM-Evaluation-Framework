from typing import Dict, Any
from .base import Metric



class BleuMetric(Metric):
    def __init__(self, name: str = "bleu", ngram: int = 4):
        super().__init__(name)
        self.ngram = ngram

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        try:
            import sacrebleu
            score = sacrebleu.sentence_bleu(answer, [expected]).score
            return {"score": float(score / 100.0)}
        except Exception:
            return {"score": 0.0}


class RougeLMetric(Metric):
    def __init__(self, name: str = "rouge_l"):
        super().__init__(name)
        try:
            from rouge_score import rouge_scorer
            self.scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
        except Exception:
            self.scorer = None

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        if not self.scorer:
            # fallback simple ratio
            if not expected or not answer:
                return {"score": 0.0}
            set_ref = set(expected.split())
            set_ans = set(answer.split())
            overlap = len(set_ref & set_ans) / max(1, len(set_ref))
            return {"score": float(overlap)}
        res = self.scorer.score(expected, answer)
        return {"score": float(res["rougeL"].fmeasure)}


class BertSimMetric(Metric):
    _model = None

    def __init__(self, name: str = "bertscore", model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(name)
        if not BertSimMetric._model:
            try:
                from sentence_transformers import SentenceTransformer
                BertSimMetric._model = SentenceTransformer(model_name)
            except Exception:
                BertSimMetric._model = None
        self.model = BertSimMetric._model

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        if not self.model:
            return {"score": 0.5}
        # Try to use sentence_transformers util.cos_sim if available,
        # otherwise fall back to a lightweight cosine implementation.
        try:
            from sentence_transformers import util as _util
        except Exception:
            try:
                import sentence_transformers.util as _util
            except Exception:
                _util = None

        try:
            emb_ref = self.model.encode(expected, convert_to_tensor=True)
            emb_ans = self.model.encode(answer, convert_to_tensor=True)
            
            # Convert to float32 to ensure compatibility with cos_sim
            if hasattr(emb_ref, 'float'):
                emb_ref = emb_ref.float()
            if hasattr(emb_ans, 'float'):
                emb_ans = emb_ans.float()
            
            # Ensure tensors are properly shaped (add batch dimension if needed)
            if hasattr(emb_ref, 'dim') and emb_ref.dim() == 1:
                emb_ref = emb_ref.unsqueeze(0)
            if hasattr(emb_ans, 'dim') and emb_ans.dim() == 1:
                emb_ans = emb_ans.unsqueeze(0)
            
            if _util is not None:
                score = _util.cos_sim(emb_ref, emb_ans).item()
            else:
                # emb_* may be nested lists; flatten to simple lists
                def _flatten(v):
                    try:
                        return [float(x) for x in v]
                    except Exception:
                        return [0.0]

                a = _flatten(emb_ref[0] if isinstance(emb_ref, (list, tuple)) and emb_ref else emb_ref)
                b = _flatten(emb_ans[0] if isinstance(emb_ans, (list, tuple)) and emb_ans else emb_ans)
                dot = sum(x * y for x, y in zip(a, b))
                norma = sum(x * x for x in a) ** 0.5
                normb = sum(y * y for y in b) ** 0.5
                score = dot / (norma * normb) if norma and normb else 0.0
            normal = (score + 1.0) / 2.0
            return {"score": float(normal)}
        except Exception:
            # Fallback if anything goes wrong
            return {"score": 0.5}
