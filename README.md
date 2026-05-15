# tstory

티스토리 주식 블로그 운영 및 백업용 저장소입니다.

## 목적

이 저장소는 티스토리 블로그 원고, HTML 본문, JSON-LD Schema, 프로젝트 진행 상태, GSC 성과 측정 로그를 백업하고 버전관리하기 위한 공간입니다.

## 운영 원칙

- 티스토리 자동 발행 저장소가 아니라 백업 및 원고 관리 저장소로 사용합니다.
- 최종 발행은 티스토리 HTML 모드에서 사람이 확인 후 진행합니다.
- 티스토리 Open API 종료로 인해 공식 API 기반 자동 발행은 사용하지 않습니다.
- GitHub Actions는 원고 생성, 백업, RSS 수집, README 업데이트 등 보조 자동화에만 사용합니다.
- API Key, GSC 인증 정보, 개인 계정 토큰, 민감한 수익 데이터, 투자 계좌 정보는 저장하지 않습니다.

## 디렉터리 구조

```text
project-context/
  stock_blog_project_context.md
posts/
  2026/
    05/
schemas/
  2026/
    05/
gsc/
  performance-log.md
templates/
  tistory-post-template.html
```

## 디렉터리 역할

| 디렉터리 | 용도 |
|---|---|
| project-context/ | 프로젝트 진행 상태 MD 백업 |
| posts/ | 티스토리 HTML 본문 백업 |
| schemas/ | JSON-LD Schema 백업 |
| gsc/ | GSC 성과 측정 로그 |
| templates/ | 반복 사용 원고 템플릿 |

## 기본 원고 산출 형식

향후 원고는 다음 순서로 관리합니다.

1. 제목
2. 메타 설명
3. 티스토리 HTML 본문
4. JSON-LD Schema
5. 태그
6. 내부 링크
7. 발행 후 체크리스트

## 주의사항

이 저장소는 public 저장소입니다. 민감 정보, 인증 정보, 계좌 정보, 고객사 비공개 자료는 커밋하지 않습니다.

## 자동 백업

이 저장소는 GitHub Actions를 통해 티스토리 공개 글을 주기적으로 백업합니다.

### 백업 대상

- 티스토리 숫자형 공개 글 URL
- 예: `https://mystock-note.tistory.com/178`

### 백업 파일

- `posts/YYYY/MM/{post_id}.html`: 티스토리 본문 HTML
- `schemas/YYYY/MM/{post_id}.schema.json`: JSON-LD Schema
- `metadata/YYYY/MM/{post_id}.metadata.json`: 제목, 설명, canonical, hash 등 메타데이터
- `logs/latest-backup-report.md`: 최신 실행 리포트

### 제외 대상

카테고리, 태그, 검색, 방명록, 관리자 페이지, 모바일 중복 URL은 백업하지 않습니다.

### 실행 방법

로컬에서 다음 명령으로 공개 글 백업을 실행할 수 있습니다.

```bash
python -m pip install -r requirements.txt
python scripts/backup_tistory.py
```

GitHub Actions는 매일 1회 자동 실행되며, Actions 탭에서 수동으로도 실행할 수 있습니다. 변경된 백업 파일이 있을 때만 `Backup Tistory posts - YYYY-MM-DD` 형식의 커밋을 생성합니다.


### 의존성

현재 백업 스크립트는 Python 표준 라이브러리만 사용합니다.  
Codex 또는 제한된 실행 환경에서 PyPI 접근이 차단되어도 문법 검증과 기본 실행이 가능하도록 설계했습니다.

### 주의사항

이 저장소는 public 저장소이므로 민감 정보는 저장하지 않습니다.
