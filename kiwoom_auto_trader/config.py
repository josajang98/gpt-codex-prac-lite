"""키움 자동매매 MVP 설정 파일.

초보자가 값을 바로 바꿔보며 테스트할 수 있도록
모든 핵심 설정을 한곳에 모았습니다.
"""

import os

# .env에서 계좌번호를 읽어옵니다. (예: 1234567890)
ACCOUNT_NO = os.getenv("KIWOOM_ACCOUNT_NO", "")

# 매매 대상 종목 (예시: 삼성전자)
STOCK_CODE = "005930"
STOCK_NAME = "삼성전자"

# 주문 수량 (고정 수량)
ORDER_QTY = 1

# 이동평균 전략 파라미터
SHORT_MA = 5
LONG_MA = 20

# True면 실제 주문 없이 로그만 출력
PAPER_MODE = True

# 키움 화면번호 (TR/주문 호출에 필요)
SCREEN_NO = "1000"

# 조회 기준: "D"(일봉) 또는 "m"(분봉)
CHART_TYPE = "D"

# 조회할 캔들 개수
CANDLE_COUNT = 60

# 분봉 사용 시 분 단위 (예: 1, 3, 5)
MINUTE_TICK = 1
