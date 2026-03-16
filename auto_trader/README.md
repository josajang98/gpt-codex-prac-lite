# Simple Auto Trader (MVP)

> ⚠️ **중요 경고**
>
> 이 프로젝트는 **학습/테스트용 MVP**입니다.  
> 실제 투자 환경에서는 슬리피지, 수수료, 네트워크 지연, API 제한, 급격한 변동성 등으로 인해 손실이 발생할 수 있습니다.  
> **실제 수익을 보장하지 않으며, 모든 투자 책임은 사용자 본인에게 있습니다.**

## 1) 프로젝트 소개

이 저장소는 아래 최소 기능만 포함한 초간단 코인 자동매매 예제입니다.

- 거래소 연결 (ccxt + Binance)
- 캔들 조회 (OHLCV)
- Bollinger Band 계산
- BUY / SELL / HOLD 신호 생성
- 시장가 주문 (PAPER_MODE 지원)

제외한 기능(이번 버전 미포함):
- 백테스트, DB 저장, 웹서버, 멀티전략, 알림 시스템, 리포트 시스템 등

---

## 2) 설치 방법

```bash
cd auto_trader
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## 3) 가상환경 생성 방법

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
```

---

## 4) requirements 설치 방법

```bash
pip install -r requirements.txt
```

---

## 5) .env 설정 방법

1. `.env.example` 파일을 복사해서 `.env` 파일 생성
2. API 키 입력

```bash
cp .env.example .env
```

`.env` 예시:

```env
BINANCE_API_KEY=여기에_API_KEY
BINANCE_SECRET=여기에_SECRET
```

---

## 6) 실행 방법

```bash
python main.py
```

실행하면 60초 간격으로 아래를 반복합니다.
1. OHLCV 조회
2. 볼린저 밴드 계산
3. 시그널 생성
4. 포지션 상태 확인
5. 주문 또는 PAPER 로그
6. 상태 출력

---

## 7) PAPER_MODE 설명

`config.py`의 `PAPER_MODE` 값으로 제어합니다.

- `PAPER_MODE = True`: 실제 주문 없이 콘솔 로그만 출력 (권장)
- `PAPER_MODE = False`: 실제 주문 API 호출

처음에는 반드시 `PAPER_MODE = True`로 충분히 테스트하세요.

---

## 8) 실제 주문 전 주의사항

실제 주문(`PAPER_MODE=False`) 전에 아래를 꼭 확인하세요.

1. API 키 권한(주문 가능 여부)
2. 테스트넷/실서버 설정(`USE_TESTNET`)
3. 주문 심볼이 올바른지 (`SYMBOL`)
4. 주문 금액(`ORDER_SIZE_USDT`)이 적절한지
5. 최소 주문 수량/정밀도 규칙 충족 여부
6. 네트워크/거래소 장애 가능성

초보자는 테스트넷 + PAPER_MODE로 충분히 검증한 뒤 매우 작은 금액으로만 실험하세요.
