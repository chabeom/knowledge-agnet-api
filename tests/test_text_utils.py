import pytest

from app.text_utils import (
    normalize_document,
    split_document,
    validate_query,
)


def test_normalize_document_removes_extra_spaces():
    result = normalize_document("  Hello   World  ")

    assert result == "Hello World"


def test_normalize_document_supports_korean():
    result = normalize_document("  안녕하세요   Python  ")

    assert result == "안녕하세요 Python"


def test_normalize_document_rejects_non_string():
    with pytest.raises(TypeError):
        normalize_document(123)


def test_split_document_returns_chunks():
    result = split_document("abcdefghij", 4)

    assert result == ["abcd", "efgh", "ij"]


def test_split_document_returns_empty_list():
    result = split_document("", 4)

    assert result == []


def test_split_document_rejects_zero_size():
    with pytest.raises(ValueError):
        split_document("abcdef", 0)


def test_split_document_rejects_non_integer_size():
    with pytest.raises(TypeError):
        split_document("abcdef", "4")


def test_validate_query_accepts_normal_query():
    result = validate_query("Python 가상환경")

    assert result is None


def test_validate_query_rejects_empty_query():
    with pytest.raises(ValueError):
        validate_query("")


def test_validate_query_rejects_blank_query():
    with pytest.raises(ValueError):
        validate_query("   ")


def test_validate_query_rejects_long_query():
    with pytest.raises(ValueError):
        validate_query("a" * 201)


def test_validate_query_rejects_non_string():
    with pytest.raises(TypeError):
        validate_query(123)