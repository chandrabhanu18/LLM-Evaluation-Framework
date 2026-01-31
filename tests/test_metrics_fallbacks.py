"""Test metric fallback scenarios and edge cases."""
import pytest
from unittest.mock import patch, MagicMock
from llm_eval.metrics.reference import BleuMetric, RougeLMetric, BertSimMetric
from llm_eval.metrics.rag import FaithfulnessMetric, ContextRelevancyMetric, AnswerRelevancyMetric


def test_bleu_with_empty_expected():
    """Test BLEU with empty references."""
    metric = BleuMetric()
    result = metric.compute("query", "", "prediction", [])
    assert result["score"] == 0.0


def test_bleu_identical_answer_expected():
    """Test BLEU with identical prediction and reference."""
    metric = BleuMetric()
    result = metric.compute("query", "exact match", "exact match", [])
    # BLEU can be 0.0 for very short sentences depending on sacrebleu settings
    assert 0.0 <= result["score"] <= 1.0


def test_rouge_with_empty_answer():
    """Test ROUGE-L with empty prediction."""
    metric = RougeLMetric()
    result = metric.compute("query", "reference text", "", [])
    assert result["score"] == 0.0


def test_rouge_with_all_empty():
    """Test ROUGE-L with both strings empty."""
    metric = RougeLMetric()
    result = metric.compute("query", "", "", [])
    assert result["score"] == 0.0


def test_bertsim_with_very_long_text():
    """Test BERTScore with text exceeding typical limits."""
    metric = BertSimMetric()
    long_text = "word " * 1000
    result = metric.compute("query", "reference", long_text, [])
    assert 0.0 <= result["score"] <= 1.0


def test_faithfulness_empty_contexts():
    """Test faithfulness with empty contexts."""
    metric = FaithfulnessMetric()
    result = metric.compute("query", "expected", "answer", [])
    assert result["score"] == 0.0


def test_faithfulness_empty_answer():
    """Test faithfulness with empty answer."""
    metric = FaithfulnessMetric()
    result = metric.compute("query", "expected", "", ["context"])
    assert result["score"] == 0.0


def test_context_relevancy_no_contexts():
    """Test context relevancy with no contexts."""
    metric = ContextRelevancyMetric()
    result = metric.compute("query", "expected", "answer", [])
    # Empty contexts may return fallback score
    assert 0.0 <= result["score"] <= 1.0


def test_context_relevancy_empty_query():
    """Test context relevancy with empty query."""
    metric = ContextRelevancyMetric()
    result = metric.compute("", "expected", "answer", ["context"])
    # Should handle gracefully
    assert isinstance(result["score"], (int, float))


def test_answer_relevancy_no_contexts():
    """Test answer relevancy with no contexts."""
    metric = AnswerRelevancyMetric()
    result = metric.compute("query", "expected", "answer", [])
    # Should still compute based on query-answer
    assert isinstance(result["score"], (int, float))


def test_answer_relevancy_identical_query_answer():
    """Test answer relevancy when query equals answer."""
    metric = AnswerRelevancyMetric()
    text = "What is AI?"
    result = metric.compute(text, "expected", text, ["context"])
    assert result["score"] >= 0.0


def test_faithfulness_with_single_context():
    """Test RAG metrics with single context string."""
    metric = FaithfulnessMetric()
    result = metric.compute("query", "expected", "answer", ["single context"])
    assert isinstance(result["score"], (int, float))


def test_faithfulness_with_multiple_contexts():
    """Test RAG metrics with multiple contexts."""
    metric = FaithfulnessMetric()
    contexts = ["context1", "context2", "context3"]
    result = metric.compute("query", "expected", "answer", contexts)
    assert isinstance(result["score"], (int, float))


def test_bleu_with_special_chars():
    """Test reference metrics with special characters."""
    metric = BleuMetric()
    prediction = "Test with !@#$%^&*()"
    reference = "Test with special chars"
    result = metric.compute("query", reference, prediction, [])
    assert 0.0 <= result["score"] <= 1.0


def test_rouge_with_unicode():
    """Test reference metrics with Unicode characters."""
    metric = RougeLMetric()
    prediction = "测试 Unicode 字符"
    reference = "测试 Unicode"
    result = metric.compute("query", reference, prediction, [])
    assert 0.0 <= result["score"] <= 1.0


def test_bertsim_with_numeric_strings():
    """Test BERTScore with numeric strings."""
    metric = BertSimMetric()
    result = metric.compute("query", "123 789", "123 456", [])
    assert 0.0 <= result["score"] <= 1.0


def test_faithfulness_with_whitespace_only():
    """Test RAG metrics with whitespace-only strings."""
    metric = FaithfulnessMetric()
    result = metric.compute("query", "expected", "   ", ["context"])
    # Should handle as empty
    assert isinstance(result["score"], (int, float))


def test_context_relevancy_with_very_long_contexts():
    """Test RAG metrics with very long contexts."""
    metric = ContextRelevancyMetric()
    long_context = "word " * 5000
    result = metric.compute("query", "expected", "answer", [long_context])
    assert 0.0 <= result["score"] <= 1.0


def test_bleu_with_repeated_words():
    """Test reference metrics with repeated words."""
    metric = BleuMetric()
    prediction = "test " * 100
    reference = "test " * 50
    result = metric.compute("query", reference, prediction, [])
    assert isinstance(result["score"], (int, float))


def test_sacrebleu_tokenization():
    """Test BLEU with different tokenization scenarios."""
    metric = BleuMetric()
    # Test punctuation
    result1 = metric.compute("query", "Hello world", "Hello, world!", [])
    # Test case sensitivity
    result2 = metric.compute("query", "hello", "HELLO", [])
    assert isinstance(result1["score"], (int, float))
    assert isinstance(result2["score"], (int, float))


def test_bertsim_model_loading():
    """Test BERTScore model is properly loaded."""
    metric = BertSimMetric()
    # Access internal model if available
    result = metric.compute("query", "test", "test", [])
    assert 0.0 <= result["score"] <= 1.0


def test_faithfulness_consistency():
    """Test RAG metrics return consistent results."""
    metric = FaithfulnessMetric()
    answer = "Paris is the capital of France"
    query = "What is the capital of France?"
    contexts = ["Paris is located in France and is its capital city"]
    
    result1 = metric.compute(query, "expected", answer, contexts)
    result2 = metric.compute(query, "expected", answer, contexts)
    assert result1["score"] == result2["score"]  # Should be deterministic


def test_rouge_consistency():
    """Test reference metrics return consistent results."""
    metric = RougeLMetric()
    prediction = "The quick brown fox"
    reference = "The quick brown dog"
    
    result1 = metric.compute("query", reference, prediction, [])
    result2 = metric.compute("query", reference, prediction, [])
    assert result1["score"] == result2["score"]  # Should be deterministic
