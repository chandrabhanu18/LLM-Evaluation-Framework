import json
from typing import Dict, Any, Iterable


def load_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


class _DataFrameWrapper:
    """Wrapper to provide consistent interface for both pandas and lite DataFrames"""
    def __init__(self, df):
        self._df = df
        self.iloc = df.iloc if hasattr(df, 'iloc') else None
        self.columns = df.columns if hasattr(df, 'columns') else None

    @property
    def shape(self):
        return self._df.shape

    def iterrows(self):
        """Iterate over rows, yielding (index, row_dict) tuples"""
        for idx, row in self._df.iterrows():
            # Convert pandas Series to dict if needed
            if hasattr(row, 'to_dict'):
                yield idx, row.to_dict()
            else:
                yield idx, row

    def __getitem__(self, key):
        """Support integer indexing to return row as dict, and column access"""
        if isinstance(key, int):
            # Return row as dictionary
            row = self._df.iloc[key] if hasattr(self._df, 'iloc') else self._df._rows[key]
            if hasattr(row, 'to_dict'):
                return row.to_dict()
            return dict(row) if hasattr(row, '__iter__') else row
        # Column access - return as list
        col = self._df[key]
        return col.tolist() if hasattr(col, 'tolist') else list(col)


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
                # support integer indexing to return row dict
                if isinstance(key, int):
                    # Return row as a dict-like object
                    row = self._rows[key]
                    # If it's already a dict, return it; otherwise make it dict-like
                    if isinstance(row, dict):
                        return row
                    # Handle tuple or other sequence types
                    return dict(enumerate(row)) if hasattr(row, '__iter__') else row
                # support column access by name
                return [row.get(key) if isinstance(row, dict) else row[key] if hasattr(row, '__getitem__') else None 
                        for row in self._rows]

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
    
    # Wrap the pandas DataFrame to provide consistent interface
    return _DataFrameWrapper(df)
