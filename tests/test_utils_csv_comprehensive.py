"""Comprehensive CSV loading tests to increase coverage."""
import pytest
from pathlib import Path
import csv
from llm_eval.utils import load_dataset


def test_load_csv_basic(tmp_path):
    """Test basic CSV loading."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        "query,expected_answer,retrieved_contexts\n"
        "What is AI?,Artificial Intelligence,\"Context about AI\"\n"
        "What is ML?,Machine Learning,\"Context about ML\"\n",
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2
    assert df[0]["query"] == "What is AI?"
    assert df[1]["expected_answer"] == "Machine Learning"


def test_load_csv_with_list_contexts(tmp_path):
    """Test CSV with list-style contexts."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        'Q1,A1,"[\'ctx1\', \'ctx2\']"\n'
        'Q2,A2,"[\'ctx3\']"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2
    # Contexts field exists
    assert "retrieved_contexts" in df[0]


def test_load_csv_quoted_fields(tmp_path):
    """Test CSV with quoted fields containing commas."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        '"What is AI, ML?","AI, ML explanation","Context with, commas"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1
    assert "," in df[0]["query"]
    assert "," in df[0]["expected_answer"]


def test_load_csv_empty_contexts(tmp_path):
    """Test CSV with empty contexts field."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        'Q1,A1,""\n'
        'Q2,A2,"[]"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2


def test_load_csv_multiline_fields(tmp_path):
    """Test CSV with multiline fields."""
    csv_file = tmp_path / "data.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['query', 'expected_answer', 'retrieved_contexts'])
        writer.writerow(['What is AI?', 'AI is\nArtificial\nIntelligence', 'Context here'])
    
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1
    assert '\n' in df[0]['expected_answer']


def test_load_csv_unicode(tmp_path):
    """Test CSV with Unicode characters."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        '¿Qué es IA?,Inteligencia Artificial,Contexto en español\n'
        '什么是人工智能?,人工智能,中文语境\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2
    assert '¿' in df[0]["query"]
    assert '什么' in df[1]["query"]


def test_load_csv_special_characters(tmp_path):
    """Test CSV with special characters."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        '"Q with ""quotes""",A with \'quotes\',"Ctx with; semicolons"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1


def test_load_csv_extra_columns(tmp_path):
    """Test CSV with extra columns (should be ignored)."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts,extra_col1,extra_col2\n'
        'Q1,A1,C1,Extra1,Extra2\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1
    assert "query" in df[0]
    assert "expected_answer" in df[0]
    assert "retrieved_contexts" in df[0]


def test_load_csv_windows_line_endings(tmp_path):
    """Test CSV with Windows line endings."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\r\n'
        'Q1,A1,C1\r\n'
        'Q2,A2,C2\r\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2


def test_load_csv_tabs_in_data(tmp_path):
    """Test CSV with tabs in data."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        'Q\twith\ttabs,A\twith\ttabs,C\twith\ttabs\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1
    assert '\t' in df[0]['query']


def test_load_csv_bom(tmp_path):
    """Test CSV with BOM (Byte Order Mark)."""
    csv_file = tmp_path / "data.csv"
    with open(csv_file, 'w', encoding='utf-8-sig') as f:
        f.write('query,expected_answer,retrieved_contexts\n')
        f.write('Q1,A1,C1\n')
    
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1


def test_load_csv_various_formats(tmp_path):
    """Test CSV with various data formats."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        '123,456,789\n'
        'True,False,None\n'
        '1.5,2.7,3.9\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 3


def test_load_csv_large_dataset(tmp_path):
    """Test CSV with many rows."""
    csv_file = tmp_path / "data.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write('query,expected_answer,retrieved_contexts\n')
        for i in range(100):
            f.write(f'Query{i},Answer{i},Context{i}\n')
    
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 100


def test_load_csv_long_text(tmp_path):
    """Test CSV with very long text fields."""
    csv_file = tmp_path / "data.csv"
    long_text = "X" * 10000
    csv_file.write_text(
        f'query,expected_answer,retrieved_contexts\n'
        f'"{long_text}","{long_text}","{long_text}"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1
    assert len(df[0]['query']) == 10000


def test_load_csv_numeric_strings(tmp_path):
    """Test CSV with numeric-looking strings."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        '"001","002","003"\n'
        '"1.0","2.0","3.0"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2


def test_load_csv_mixed_quotes(tmp_path):
    """Test CSV with mixed quote styles."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        '"Q1","A1","C1"\n'
        'Q2,A2,C2\n'
        '"Q3",A3,"C3"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 3


def test_load_csv_trailing_whitespace(tmp_path):
    """Test CSV with trailing whitespace."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        'Q1  ,  A1,C1  \n'
        '  Q2,A2  ,  C2\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 2


def test_load_csv_json_in_contexts(tmp_path):
    """Test CSV with JSON-like strings in contexts."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        'query,expected_answer,retrieved_contexts\n'
        'Q1,A1,"{""key"": ""value""}"\n',
        encoding="utf-8"
    )
    df = load_dataset(str(csv_file))
    assert df.shape[0] == 1
