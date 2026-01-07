import json
from typing import Dict, Any, Iterable


def load_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_dataset(path: str) -> Any:
    # import pandas lazily to avoid forcing heavy runtime deps during tests
    try:
        import pandas as pd
    except Exception:
        # If pandas isn't available, provide a lightweight DataFrame-like
        # fallback for both JSONL and CSV so tests and evaluator can run.
        import csv

        class _LiteDF:
            def __init__(self, rows):
                self._rows = rows
                class _Iloc:
                    def __init__(self, rows):
                        self._rows = rows

                    def __getitem__(self, idx):
                        return self._rows[idx]

                self.iloc = _Iloc(self._rows)

            @property
            def shape(self):
                return (len(self._rows), len(self._rows[0]) if self._rows else 0)

            def iterrows(self):
                for i, r in enumerate(self._rows):
                    yield i, r

            def __getitem__(self, key):
                # support row["query"] when row is a dict
                return self._rows[key]

        if path.endswith(".jsonl"):
            rows = list(load_jsonl(path))
            keys = set(rows[0].keys()) if rows else set()
            required = {"query", "expected_answer", "retrieved_contexts"}
            missing = required - keys
            if missing:
                raise ValueError(f"Dataset missing required fields: {missing}")
            return _LiteDF(rows)
        if path.endswith(".csv"):
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [r for r in reader]
            keys = set(rows[0].keys()) if rows else set()
            required = {"query", "expected_answer", "retrieved_contexts"}
            missing = required - keys
            if missing:
                raise ValueError(f"Dataset missing required fields: {missing}")
            return _LiteDF(rows)
        raise ValueError("Unsupported dataset format. Use .jsonl or .csv")

    if path.endswith(".jsonl"):
        rows = list(load_jsonl(path))
        df = pd.DataFrame(rows)
    elif path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        raise ValueError("Unsupported dataset format. Use .jsonl or .csv")

    required = {"query", "expected_answer", "retrieved_contexts"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required fields: {missing}")
    return df
