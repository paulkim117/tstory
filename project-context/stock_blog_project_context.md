# Project Context

## 1. Project Overview

- 프로젝트명: 티스토리 주식 블로그 SEO/GEO 개선 및 GitHub 백업 프로젝트
- 목적: 티스토리 기반 주식·ETF 블로그를 검색 유입 중심으로 개선하고, HTML 원고, JSON-LD Schema, 프로젝트 진행 상태, GSC 성과 로그를 GitHub에 백업한다.
- 현재 단계: 기존 성과 글 개선 완료 후 GitHub 백업 체계 구축 및 신규 콘텐츠 확장 준비

## 2. Current Status

- 진행률: 초기 SEO 개선 완료, GitHub 백업 저장소 구성 완료, 템플릿·성과 로그 파일 생성 전 단계
- 현재 핵심 작업:
  - 기존 성과 글 리라이트 및 내부 링크 보강
  - 국내 ETF 브랜드 허브 글 발행 및 내부 링크 허브화
  - 신규 글 산출 형식을 티스토리 HTML 본문 + JSON-LD Schema 기준으로 전환
  - GitHub 저장소 `paulkim117/tstory`를 백업용 단일 저장소로 사용
  - README 및 Project Context MD를 GitHub에 저장
- 마지막 업데이트 날짜: 2026-05-07

## 3. Key Decisions

- [2026-05-07] 티스토리 Open API 기반 자동 발행은 사용하지 않는다.
- [2026-05-07] GitHub는 티스토리 자동 발행 도구가 아니라 원고 버전관리 및 백업 저장소로 사용한다.
- [2026-05-07] 최종 발행은 티스토리 HTML 모드에서 사람이 확인 후 진행한다.
- [2026-05-07] 향후 원고 산출 형식은 제목, 메타 설명, 티스토리 HTML 본문, JSON-LD Schema, 태그, 내부 링크, 발행 후 체크리스트 순서로 제공한다.
- [2026-05-07] 일반 텍스트 복붙 시 문장 중간 줄바꿈, 문단 간격, 제목 서식 깨짐 문제가 발생하므로 신규 글과 리라이트 원고는 HTML 모드 붙여넣기용으로 작성한다.
- [2026-05-07] Schema는 검색 이해 보조 요소이며 순위 상승이나 리치 결과 노출을 보장하지 않는다.
- [2026-05-07] GitHub 백업 저장소는 `paulkim117/tstory`로 확정한다.
- [2026-05-07] `paulkim117/tstory` 저장소는 public 상태이므로 API Key, GSC 인증 정보, 개인 계정 토큰, 비공개 수익 데이터, 투자 계좌 정보, 고객사 비공개 자료는 저장하지 않는다.
- [2026-05-07] 백업 저장소 기본 브랜치는 `main`을 사용한다.

## 4. KPI / Metrics

- 기준 기간: 2026-05-14 이후 재측정 필요
- 핵심 지표:
  - GSC 클릭수: 측정 필요
  - GSC 노출수: 측정 필요
  - 평균 게재순위: 측정 필요
  - CTR: 측정 필요
  - 색인 상태: 측정 필요
- 변화 요약 Before vs After:
  - /95: 리라이트 및 내부 링크 반영 후 재측정 필요
  - /101: 첫 문단 수정 및 내부 링크 보강 후 재측정 필요
  - /102: 제목, 첫 문단, 내부 링크 수정 후 재측정 필요
  - /177: 국내 ETF 브랜드 허브 글 발행 후 재측정 필요

## 5. Completed Work

- /95 전체 리라이트 발행 완료
- /101 첫 문단 수정 및 내부 링크 보강 완료
- /102 제목, 첫 문단, 내부 링크 수정 완료
- /95, /101, /102 GSC 색인 요청 완료
- 국내 ETF 브랜드 허브 글 발행 완료
- 국내 ETF 브랜드 허브 글 URL 확인: `https://mystock-note.tistory.com/177`
- 국내 ETF 브랜드 허브 글 제목 확정: `국내 ETF 브랜드 총정리: KODEX, TIGER, ACE, RISE, SOL, 1Q는 무엇이 다를까?`
- 국내 ETF 브랜드 허브 글 GSC 색인 요청 완료
- /95, /101, /102에 국내 ETF 브랜드 허브 글 내부 링크 추가 완료
- 향후 원고 산출 형식을 티스토리 HTML 본문 중심으로 전환 완료
- JSON-LD Schema 블록을 기본 산출물에 포함하는 기준 설정 완료
- GitHub 계정 `paulkim117` 연결 확인 완료
- GitHub 백업 저장소 `paulkim117/tstory` 생성 및 접근 확인 완료
- `paulkim117/tstory` 저장소 권한 확인 완료: admin, maintain, pull, push, triage
- `paulkim117/tstory` 저장소 기본 브랜치 확인 완료: `main`
- GitHub 백업 저장소 README 생성 완료
- GitHub 백업 저장소 `project-context/stock_blog_project_context.md` 생성 완료

## 6. Pending Tasks

- 우선순위 높은 작업:
  - `templates/tistory-post-template.html` 생성
  - `gsc/performance-log.md` 생성
  - 다음 신규 글 작성: 연금저축펀드에서 ETF 투자할 때 KODEX, TIGER, ACE 중 무엇을 봐야 할까?
  - 신규 글 작성 시 HTML 본문과 JSON-LD Schema를 함께 생성
  - 신규 글 발행 후 GitHub `posts/`, `schemas/`에 백업
  - 2026-05-14 이후 GSC 성과 재측정
- 대기 작업:
  - 기존 성과 글 추가 리라이트 여부 판단
  - ETF 브랜드 허브 글 후속 내부 링크 구조 확장
  - GitHub 백업 파일 네이밍 규칙 확정

## 7. Issues / Risks

- 현재 문제:
  - 티스토리 일반 텍스트 복붙 시 문장 중간 줄바꿈, 문단 간격, 제목 서식 깨짐 발생 가능
  - 티스토리 Open API 종료로 공식 API 기반 자동 발행 불가
  - public GitHub 저장소이므로 민감 정보 커밋 위험 관리 필요
- 리스크 요소:
  - Schema 적용이 검색 노출 개선을 보장하지 않음
  - GSC 성과 판단 전 무분별한 콘텐츠 발행 시 방향성 검증이 어려움
  - 투자 권유로 오인될 수 있는 표현 사용 시 콘텐츠 신뢰도 및 법적 리스크 발생 가능
  - HTML 본문과 Schema 내용이 불일치하면 검색엔진 구조화 데이터 품질 문제가 발생할 수 있음

## 8. Next Actions

- `templates/tistory-post-template.html` 생성
- `gsc/performance-log.md` 생성
- 다음 신규 글 HTML 원고 작성
- 다음 신규 글 JSON-LD Schema 작성
- 발행 후 GitHub 백업 및 GSC 색인 요청
- 2026-05-14 이후 /95, /101, /102, /177 GSC 성과 재측정

## 9. Notes

- GitHub 저장소:
  - 저장소: `paulkim117/tstory`
  - URL: `https://github.com/paulkim117/tstory.git`
  - 기본 브랜치: `main`
  - 공개 여부: public
- GitHub 백업 디렉터리 기준:
  - `project-context/`: 프로젝트 진행 상태 MD 백업
  - `posts/`: 티스토리 HTML 본문 백업
  - `schemas/`: JSON-LD Schema 백업
  - `gsc/`: GSC 성과 측정 로그
  - `templates/`: 반복 사용 원고 템플릿
- 주요 콘텐츠 방향:
  - 국내 ETF 브랜드
  - 연금저축
  - IRP
  - TDF
  - 장기 자산배분
  - 상품군 비교
  - 액티브 ETF 설명형 글
- 주요 브랜드 후보:
  - KODEX
  - TIGER
  - ACE
  - RISE
  - SOL
  - 1Q
  - TIMEFOLIO
  - KoAct
  - MIDAS
- 콘텐츠 작성 유의사항:
  - 투자 권유 표현 금지
  - 고배당, 월배당, 커버드콜 상품의 원금 손실, NAV 감소, 분배금 변동 위험 명시
  - FAQPage Schema는 본문에 실제 FAQ 섹션이 있는 경우에만 사용
  - Schema 질문과 답변은 본문 내용과 일치해야 함
  - public GitHub 저장소에는 민감 정보와 인증 정보를 저장하지 않음
