# Kiwoom Auto Trader (MVP)

> ⚠️ **중요 경고**
>
> 이 프로젝트는 **학습/테스트용 최소 예제(MVP)** 입니다.  
> 실제 투자 손실이 발생할 수 있으며, 수익을 보장하지 않습니다.  
> 모든 투자 책임은 사용자 본인에게 있습니다.

## 1) 프로젝트 소개

키움 OpenAPI+로 동작하는 아주 단순한 자동매매 예제입니다.

포함 기능(최소 범위):
- 키움 API 로그인
- 종목 일봉 데이터 조회(TR)
- 종목 현재가/기본 시세 조회(TR)
- 이동평균(5/20) 전략 신호 생성
- 시장가 매수/매도 주문
- PAPER_MODE 지원

제외 기능:
- 백테스트, DB, 웹 대시보드, 멀티전략, 멀티계좌, 알림/리포트 등

---

## 2) 실행 환경 (중요)

- **Windows 환경 기준**
- **키움 OpenAPI+ 설치 필요**
- OpenAPI ActiveX 사용 가능 환경 필요
- 보통 **32비트 Python** 권장이 많습니다 (환경에 따라 상이)
- 키움 HTS/OpenAPI 실행 권한 이슈가 있으면 관리자 권한 실행을 고려하세요

---

## 3) 설치 방법

```bash
cd kiwoom_auto_trader
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4) 가상환경 생성 방법

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 5) requirements 설치 방법

```bash
pip install -r requirements.txt
```

---

## 6) .env 설정 방법

1. `.env.example`을 복사해서 `.env` 생성
2. 계좌번호 입력

```bash
copy .env.example .env
```

`.env` 예시:

```env
KIWOOM_ACCOUNT_NO=1234567890
```

> 주의: ID/비밀번호/공인인증서 비밀번호 등 민감정보 자동입력은 이 예제에서 구현하지 않습니다.

---

## 7) 실행 방법

```bash
python main.py
```

현재 MVP는 복잡도를 낮추기 위해 **1회 실행(조회→판단→주문/로그→종료)** 구조입니다.

---

## 8) PAPER_MODE 설명

`config.py`에서 설정합니다.

- `PAPER_MODE = True` : 실제 주문 없이 콘솔 로그만 출력
- `PAPER_MODE = False` : 실제 `SendOrder` 호출

처음에는 반드시 `PAPER_MODE=True`로 테스트하세요.

---

## 9) 실제 주문 전 주의사항

1. 계좌번호(`KIWOOM_ACCOUNT_NO`)가 올바른지 확인
2. 주문 종목코드(`STOCK_CODE`)가 맞는지 확인
3. 주문 수량(`ORDER_QTY`)을 작은 값으로 테스트
4. 장중/장마감 여부에 따라 주문 체결이 다를 수 있음
5. OpenAPI/HTS 상태 불안정 시 오류 가능

---

## 10) 키움 API 사용 시 유의사항

- TR 요청 횟수 제한이 있습니다.
- ActiveX/QAxWidget 특성상 일반적인 리눅스 서버 환경과 다릅니다.
- 로그인은 키움 기본 로그인 창 흐름을 따릅니다.
- 실거래 전 모의환경/소액으로 충분히 검증하세요.

---

## 11) 반복 실행으로 확장하는 방법

현재는 초보자 이해를 위해 1회 실행 구조입니다.  
반복 실행이 필요하면 아래처럼 확장할 수 있습니다.

- 방법 A: 작업 스케줄러(Windows Task Scheduler)로 1~5분 간격 실행
- 방법 B: `main.py`에서 `while True` + `time.sleep()` 추가
- 방법 C: 장중 시간대에만 반복하도록 조건 추가

복잡한 이벤트 엔진 없이도 위 방식으로 간단히 확장 가능합니다.
