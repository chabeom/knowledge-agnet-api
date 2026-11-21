import pytest
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APIClient

from documents.models import Document

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client(django_user_model):
    user = django_user_model.objects.create_user(username="document-editor")
    user.user_permissions.set(
        Permission.objects.filter(content_type__app_label="documents", content_type__model="document")
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


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


@pytest.mark.parametrize("list_path,detail_path", [("/api/documents/", "/api/documents/{id}/"), ("/", "/{id}/")])
@pytest.mark.parametrize("authenticated", [False, True])
def test_document_routes_deny_users_without_permissions(
    django_user_model, document, list_path, detail_path, authenticated
):
    client = APIClient()
    if authenticated:
        client.force_authenticate(user=django_user_model.objects.create_user(username="unprivileged"))

    detail_url = detail_path.format(id=document.id)
    payload = {"title": "unauthorized change", "content": "blocked"}
    assert client.get(list_path).status_code == status.HTTP_403_FORBIDDEN
    assert client.post(list_path, payload, format="json").status_code == status.HTTP_403_FORBIDDEN
    assert client.get(detail_url).status_code == status.HTTP_403_FORBIDDEN
    assert client.put(detail_url, payload, format="json").status_code == status.HTTP_403_FORBIDDEN
    assert client.patch(detail_url, payload, format="json").status_code == status.HTTP_403_FORBIDDEN
    assert client.delete(detail_url).status_code == status.HTTP_403_FORBIDDEN
    document.refresh_from_db()
    assert document.title == "Git 브랜치 전략"
    assert Document.objects.count() == 1


def test_view_permission_does_not_grant_write_access(django_user_model, document):
    user = django_user_model.objects.create_user(username="document-reader")
    user.user_permissions.add(
        Permission.objects.get(content_type__app_label="documents", codename="view_document")
    )
    client = APIClient()
    client.force_authenticate(user=user)

    detail_url = f"/api/documents/{document.id}/"
    assert client.get("/api/documents/").status_code == status.HTTP_200_OK
    assert client.get(detail_url).status_code == status.HTTP_200_OK
    assert client.delete(detail_url).status_code == status.HTTP_403_FORBIDDEN
    assert Document.objects.count() == 1
