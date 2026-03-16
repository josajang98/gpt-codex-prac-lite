"""프로그램 전체 설정을 모아두는 파일입니다.
초보자도 한 눈에 이해할 수 있도록 단순한 상수 형태로 관리합니다.
"""

import os

# 거래할 심볼 (바이낸스 선물/현물 형식과 맞아야 합니다)
SYMBOL = "BTC/USDT"

# 캔들 주기 (예: 1m, 5m, 1h)
TIMEFRAME = "1m"

# 불러올 캔들 개수 (볼린저밴드 계산에 period보다 충분히 크게 권장)
CANDLE_LIMIT = 100

# 볼린저밴드 설정
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# 주문 금액 (USDT 고정 금액)
ORDER_SIZE_USDT = 50

# 루프 간격(초)
POLL_INTERVAL = 60

# True면 실제 주문 없이 로그만 출력 (학습/테스트용)
PAPER_MODE = True

# True면 바이낸스 테스트넷 사용
USE_TESTNET = True

# 바이낸스 API 키/시크릿 (.env 파일에서 주입)
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET", "")
