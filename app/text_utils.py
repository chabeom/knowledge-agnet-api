import logging

logger = logging.getLogger(__name__)


def normalize_document(text: str) -> str:
    """문서의 불필요한 공백을 정리한다."""
    if not isinstance(text, str):
        raise TypeError("text는 문자열이여야 합니다.")
    return " ".join(text.split())


def split_document(text: str, chunk_size: int) -> list[str]:
    """문서를 지정한 글자 수 단위로 나눈다."""
    if not isinstance(text, str):
        raise TypeError("text는 문자열이여야 합니다.")

    if not isinstance(chunk_size, int):
        raise TypeError("chunk_size는 정수여야 합니다.")

    if chunk_size <= 0:
        raise ValueError("chunk_size는 1이상이여야 합니다.")

    if text == "":
        return []

    chunks = [
        text[index : index + chunk_size] for index in range(0, len(text), chunk_size)
    ]

    logger.debug("문서를 %d개 조각으로 분리했습니다.", len(chunks))

    return chunks


def validate_query(query: str) -> None:
    """검색어가 사용 가능한 값인지 검사한다."""

    if not isinstance(query, str):
        raise TypeError("query는 문자열이여야 합니다.")

    cleaned_query = query.strip()

    if cleaned_query == "":
        raise ValueError("검색어를 입력해야 합니다.")

    if len(cleaned_query) > 200:
        raise ValueError("검색어는 200자를 초과할 수 없습니다.")
