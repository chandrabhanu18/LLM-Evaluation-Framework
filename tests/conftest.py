import pytest
import types
import sys


class DummySTModel:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, s, convert_to_tensor=False):
        if isinstance(s, (list, tuple)):
            s = " ".join(map(str, s))
        import pytest
        import types
        import sys
        from importlib import import_module

        # Ensure test stubs are available during import/collection phase so any
        # module-level imports of `sentence_transformers` resolve to our lightweight
        # test stubs instead of the heavy site-package.
        try:
            st_top = import_module("tests._stubs.sentence_transformers")
            sys.modules.setdefault("sentence_transformers", st_top)
            try:
                util_top = import_module("tests._stubs.sentence_transformers.util")
                sys.modules.setdefault("sentence_transformers.util", util_top)
            except Exception:
                pass
        except Exception:
            pass


        # Simplified test fixture: use the test-only stubs in `tests/_stubs`.
        @pytest.fixture(autouse=True)
        def patch_sentence_transformer(monkeypatch):
            # monkeypatch the SentenceTransformer class from our test stub
            try:
                st = import_module("tests._stubs.sentence_transformers")
            except Exception:
                st = None

            if st is not None:
                # Ensure imports of `sentence_transformers` resolve to our test stub modules
                sys.modules.setdefault("sentence_transformers", st)
                try:
                    util = import_module("tests._stubs.sentence_transformers.util")
                    sys.modules.setdefault("sentence_transformers.util", util)
                except Exception:
                    pass

            # Provide light-weight fakes for sacrebleu and rouge_score used in tests
            fake_sacre = types.SimpleNamespace()
            fake_sacre.sentence_bleu = lambda hyp, refs: types.SimpleNamespace(score=100.0)
            monkeypatch.setitem(__import__("sys").modules, "sacrebleu", fake_sacre)

            class FakeRouge:
                def __init__(self, *args, **kwargs):
                    pass

                def score(self, ref, hyp):
                    return {"rougeL": types.SimpleNamespace(fmeasure=1.0)}

            monkeypatch.setitem(__import__("sys").modules, "rouge_score", types.SimpleNamespace(rouge_scorer=types.SimpleNamespace(RougeScorer=FakeRouge)))
            yield

