# knowledge Agnet API

문서를 등록하고 검색한뒤, 검색 결과를 기반으로 답변하는 RAG 연습 프로젝트입니다.

## 예정 기능 

-문서 등록 및 조회
-문서 검색
-RAG 질문-답변
-서버 상태 확인


## 브랜치 전략

-main: 배포 가능한 코드
-develop: 기능 통합 및 테스트 ( feat에서 올려줌)
-feature/* : 개별 기능 개발


## 로컬 실행 및 문서 API 권한

저장소 루트에서 의존성을 설치한 뒤 `.env.example`을 `.env`로 복사하고 새 Django 서명 키를 저장합니다. Django는 이 프로젝트 루트의 `.env`를 자동으로 읽으며, 이미 설정된 프로세스 환경변수는 우선 적용합니다. `.env`는 Git에서 제외됩니다. 배포 환경에서는 별도로 생성한 키를 비밀 저장소에 보관하고, 여러 프로세스가 같은 키를 읽도록 구성합니다. 기존 설정에 공개됐던 개발 키는 교체합니다.

```powershell
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "from dotenv import set_key; import secrets; set_key('.env', 'DJANGO_SECRET_KEY', secrets.token_urlsafe(48))"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

브라우저에서 현재 Django 사이트의 /api-auth/login/ 으로 로그인한 뒤 /api/documents/ 를 이용합니다. 관리 화면에서 문서 조회, 추가, 변경, 삭제 권한을 사용자나 그룹에 각각 부여할 수 있습니다. 세션으로 변경 요청을 보내는 API 클라이언트는 CSRF 토큰도 전달해야 합니다.

운영 환경에서는 DJANGO_ALLOWED_HOSTS에 실제 호스트 이름을 쉼표로 구분해 설정합니다. DEBUG는 기본적으로 꺼져 있습니다. Django가 직접 HTTPS를 처리할 때는 DJANGO_SECURE_HTTPS=1로 SSL 리디렉션과 보안 쿠키를 활성화합니다. 프록시에서 HTTPS를 종료한다면 실제 구성에 맞춰 HTTPS와 보안 쿠키를 설정한 뒤 python manage.py check --deploy로 확인합니다.

프로젝트 루트의 `.env`를 준비한 뒤 python -m pytest를 실행합니다.
