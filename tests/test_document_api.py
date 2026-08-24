import pytest
from rest_framework import status
from rest_framework.test import APIClient

from documents.models import Document

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def document():
    return Document.objects.create(
        title="Git 브랜치 전략",
        content="기능 브랜치는 develop에서 생성합니다.",
        source="개발 가이드",
    )


def test_create_document(api_client):
    response = api_client.post(
        "/api/documents/",
        {
            "title": "Django 사용법",
            "content": "Django 프로젝트 실행 방법입니다.",
            "source": "교육 자료",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.count() == 1


def test_create_document_without_title_returns_400(api_client):
    response = api_client.post(
        "/api/documents/",
        {
            "content": "제목이 없는 문서입니다.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_documents(api_client, document):
    response = api_client.get("/api/documents/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == document.title


def test_retrieve_document(api_client, document):
    response = api_client.get(f"/api/documents/{document.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == document.id


def test_update_document(api_client, document):
    response = api_client.patch(
        f"/api/documents/{document.id}/",
        {"title": "수정된 문서 제목"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    document.refresh_from_db()

    assert document.title == "수정된 문서 제목"


def test_delete_document(api_client, document):
    response = api_client.delete(f"/api/documents/{document.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Document.objects.count() == 0
