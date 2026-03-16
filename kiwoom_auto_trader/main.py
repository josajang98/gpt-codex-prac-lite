"""키움 자동매매 MVP 실행 파일.

단순 흐름(1회 실행):
1) 로그인
2) 차트 데이터 조회
3) 이동평균 계산
4) 시그널 생성
5) 포지션 확인
6) 주문 또는 PAPER 로그
7) 상태 출력 후 종료
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

import config
from kiwoom_api import KiwoomAPI
from strategy import add_moving_averages, generate_signal


# 한 번에 하나의 포지션만 보유한다고 가정
# None 또는 {"stock_code": ..., "qty": ..., "entry_price": ...}
position = None


def run_once() -> None:
    """로그인 -> 조회 -> 판단 -> (주문/로그) -> 종료를 한 번 수행합니다."""
    global position

    load_dotenv()

    if not config.ACCOUNT_NO:
        raise ValueError("KIWOOM_ACCOUNT_NO가 비어 있습니다. .env를 확인하세요.")

    app = QApplication(sys.argv)
    api = KiwoomAPI()

    # 1) 로그인
    api.login()

    # 2) 데이터 조회 (MVP에서는 일봉 조회를 우선 사용)
    if config.CHART_TYPE != "D":
        print("[WARN] MVP는 일봉(D) 조회만 구현되어 있어 D로 처리합니다.")

    df = api.request_daily_ohlcv(
        stock_code=config.STOCK_CODE,
        screen_no=config.SCREEN_NO,
        count=config.CANDLE_COUNT,
    )

    if df.empty:
        print("[ERROR] 차트 데이터를 받지 못했습니다.")
        return

    # 3) 이동평균 계산
    df = add_moving_averages(df, short_ma=config.SHORT_MA, long_ma=config.LONG_MA)

    # 4) 마지막 데이터 기준 신호
    signal = generate_signal(df)
    last = df.iloc[-1]

    # 2번 요구사항(현재가/기본 시세 조회)을 위해 현재가 1회 조회
    current_price = api.request_basic_price(config.STOCK_CODE, config.SCREEN_NO)
    if current_price == 0:
        current_price = int(last["close"])

    short_ma_val = float(last["short_ma"]) if str(last["short_ma"]) != "nan" else float("nan")
    long_ma_val = float(last["long_ma"]) if str(last["long_ma"]) != "nan" else float("nan")

    # 5) 포지션 상태 확인 + 6) 주문 또는 PAPER 로그
    if signal == "BUY" and position is None:
        if config.PAPER_MODE:
            position = {
                "stock_code": config.STOCK_CODE,
                "qty": config.ORDER_QTY,
                "entry_price": current_price,
            }
            print(
                f"[PAPER BUY] {config.STOCK_NAME}({config.STOCK_CODE}) "
                f"qty={config.ORDER_QTY}, price={current_price}"
            )
        else:
            ret = api.send_market_buy_order(
                account_no=config.ACCOUNT_NO,
                stock_code=config.STOCK_CODE,
                qty=config.ORDER_QTY,
                screen_no=config.SCREEN_NO,
            )
            print(f"[REAL BUY] SendOrder return={ret}")
            if ret == 0:
                position = {
                    "stock_code": config.STOCK_CODE,
                    "qty": config.ORDER_QTY,
                    "entry_price": current_price,
                }

    elif signal == "SELL" and position is not None:
        if config.PAPER_MODE:
            print(
                f"[PAPER SELL] {config.STOCK_NAME}({config.STOCK_CODE}) "
                f"qty={position['qty']}, price={current_price}"
            )
            position = None
        else:
            ret = api.send_market_sell_order(
                account_no=config.ACCOUNT_NO,
                stock_code=config.STOCK_CODE,
                qty=position["qty"],
                screen_no=config.SCREEN_NO,
            )
            print(f"[REAL SELL] SendOrder return={ret}")
            if ret == 0:
                position = None

    # 7) 상태 출력
    position_state = "LONG" if position is not None else "NONE"
    print(
        f"[STATUS] stock={config.STOCK_NAME}({config.STOCK_CODE}), "
        f"price={current_price}, short_ma={short_ma_val:.2f}, long_ma={long_ma_val:.2f}, "
        f"signal={signal}, position={position_state}, paper_mode={config.PAPER_MODE}"
    )

    # Qt 이벤트 루프를 길게 유지하지 않고 종료
    app.quit()


if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        print(f"[ERROR] {e}")
