from app.text_utils import normalize_document, split_document
from qdrant_client import QdrantClient, models


COLLECTION_NAME = "intern_study"
MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

DOCUMENTS = [
    "기능 브랜치는 최신 develop 브랜치에서 생성합니다.",
    "개발이 끝나면 feature 브랜치를 원격 저장소에 push합니다.",
    "Pull Request를 생성하여 feature 브랜치를 develop에 병합합니다.",
    "Django의 migrate 명령은 마이그레이션을 데이터베이스에 적용합니다.",
]

QUESTIONS = [
    "feature 브랜치는 어디에 병합하나요?",
    #"기능 작업을 팀 코드에 합치려면 어떻게 해야 하나요?",
    #"회사 점심시간은 몇 시인가요?",
]


def create_chunks_and_payloads() -> tuple[list[str], list[dict]]:
    """문서를 정리하고 청크와 메타데이터를 생성한다."""

    chunks = []
    payloads = []

    for document_id, document in enumerate(DOCUMENTS, start=1):
        cleaned_document = normalize_document(document)

        document_chunks = split_document(
            cleaned_document,
            chunk_size=100,
        )

        for chunk_index, chunk in enumerate(document_chunks):
            chunks.append(chunk)

            payloads.append(
                {
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "source": "개발 가이드",
                }
            )

    return chunks, payloads


def create_vector_database(
    chunks: list[str],
    payloads: list[dict],
) -> QdrantClient:
    """청크를 임베딩으로 변환해서 Qdrant에 저장한다."""

    client = QdrantClient(":memory:")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=client.get_embedding_size(MODEL_NAME),
            distance=models.Distance.COSINE,
        ),
    )

    client.upload_collection(
        collection_name=COLLECTION_NAME,
        vectors=[
            models.Document(
                text=chunk,
                model=MODEL_NAME,
            )
            for chunk in chunks
        ],
        payload=payloads,
        ids=list(range(1, len(chunks) + 1)),
    )

    return client


def search_documents(
    client: QdrantClient,
    question: str,
) -> list:
    """질문과 의미가 비슷한 청크를 검색한다."""

    return client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.Document(
            text=question,
            model=MODEL_NAME,
        ),
        limit=2,
    ).points


def create_prompt(question: str, results: list) -> str:
    """검색 결과를 이용해 LLM에 전달할 프롬프트를 만든다."""

    context = "\n".join(
        (
            f"- {result.payload['text']} "
            f"(출처: {result.payload['source']})"
        )
        for result in results
    )

    return f"""
아래 근거만 사용해서 질문에 답하세요.
근거에 답이 없다면 모른다고 답하세요.

[근거]
{context}

[질문]
{question}
""".strip()


def print_results(question: str, results: list) -> None:
    """질문과 검색 결과를 화면에 출력한다."""

    print("\n" + "=" * 60)
    print(f"[질문] {question}")
    print("=" * 60)

    for rank, result in enumerate(results, start=1):
        payload = result.payload

        print(f"{rank}위")
        print(f"유사도 점수: {result.score:.4f}")
        print(f"문서 ID: {payload['document_id']}")
        print(f"청크 번호: {payload['chunk_index']}")
        print(f"내용: {payload['text']}")
        print(f"출처: {payload['source']}")
        print()


def main() -> None:
    """RAG 검색 실습을 실행한다."""

    chunks, payloads = create_chunks_and_payloads()

    print(f"생성된 청크 수: {len(chunks)}")

    client = create_vector_database(
        chunks=chunks,
        payloads=payloads,
    )

    for question in QUESTIONS:
        results = search_documents(
            client=client,
            question=question,
        )

        print_results(
            question=question,
            results=results,
        )

        prompt = create_prompt(
            question=question,
            results=results,
        )

        print("[LLM에 전달할 프롬프트]")
        print(prompt)


if __name__ == "__main__":
    main()