"""초간단 자동매매 프로그램 실행 파일입니다.

흐름:
1) OHLCV 조회
2) 볼린저밴드 계산
3) BUY/SELL/HOLD 신호 생성
4) 포지션 상태 확인
5) 조건 충족 시 주문(또는 PAPER 로그)
6) 현재 상태 콘솔 출력
7) 대기 후 반복
"""

from __future__ import annotations

import time

import pandas as pd
from dotenv import load_dotenv

import config
from exchange import BinanceExchange
from strategy import calculate_bollinger_bands, generate_signal


# 간단한 포지션 상태 (한 번에 하나의 포지션만 보유)
# None 또는 {"symbol": ..., "amount": ..., "entry_price": ...}
position = None


def build_dataframe(ohlcv: list[list[float]]) -> pd.DataFrame:
    """ccxt OHLCV 결과를 pandas DataFrame으로 변환합니다."""
    df = pd.DataFrame(
        ohlcv,
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def run() -> None:
    """메인 루프를 실행합니다."""
    global position

    # .env 로드
    load_dotenv()

    # 거래소 연결
    exchange = BinanceExchange(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        use_testnet=config.USE_TESTNET,
    )

    print("=== Simple Auto Trader Started ===")
    print(f"SYMBOL={config.SYMBOL}, TIMEFRAME={config.TIMEFRAME}")
    print(f"PAPER_MODE={config.PAPER_MODE}, TESTNET={config.USE_TESTNET}")

    while True:
        try:
            # 1) 최신 OHLCV 조회
            ohlcv = exchange.fetch_ohlcv(
                symbol=config.SYMBOL,
                timeframe=config.TIMEFRAME,
                limit=config.CANDLE_LIMIT,
            )
            df = build_dataframe(ohlcv)

            # 2) 볼린저밴드 계산
            df = calculate_bollinger_bands(
                df,
                period=config.BOLLINGER_PERIOD,
                std_multiplier=config.BOLLINGER_STD,
            )

            # 3) 마지막 캔들 기준 신호
            signal = generate_signal(df)
            last = df.iloc[-1]
            close_price = float(last["close"])
            upper_band = float(last["upper_band"]) if pd.notna(last["upper_band"]) else float("nan")
            lower_band = float(last["lower_band"]) if pd.notna(last["lower_band"]) else float("nan")

            # 4) 포지션 상태 확인 및 5) 주문/로그
            if signal == "BUY" and position is None:
                if config.PAPER_MODE:
                    # PAPER 모드: 가짜 체결 처리
                    buy_amount = config.ORDER_SIZE_USDT / close_price
                    position = {
                        "symbol": config.SYMBOL,
                        "amount": buy_amount,
                        "entry_price": close_price,
                    }
                    print(f"[PAPER BUY] {config.SYMBOL} amount={buy_amount:.6f}, price={close_price:.2f}")
                else:
                    order = exchange.market_buy_by_quote_usdt(config.SYMBOL, config.ORDER_SIZE_USDT)
                    filled_amount = float(order.get("filled") or order.get("amount") or 0)
                    avg_price = float(order.get("average") or close_price)
                    position = {
                        "symbol": config.SYMBOL,
                        "amount": filled_amount,
                        "entry_price": avg_price,
                    }
                    print(f"[REAL BUY] order_id={order.get('id')}, amount={filled_amount}, price={avg_price}")

            elif signal == "SELL" and position is not None:
                if config.PAPER_MODE:
                    print(
                        f"[PAPER SELL] {config.SYMBOL} amount={position['amount']:.6f}, price={close_price:.2f}"
                    )
                    position = None
                else:
                    order = exchange.create_market_sell_order(config.SYMBOL, position["amount"])
                    print(f"[REAL SELL] order_id={order.get('id')}, amount={position['amount']}")
                    position = None

            # HOLD이거나 포지션 조건 불일치일 때는 아무것도 안 함

            # 6) 상태 출력
            position_state = "LONG" if position is not None else "NONE"
            print(
                f"[STATUS] price={close_price:.2f}, "
                f"upper={upper_band:.2f}, lower={lower_band:.2f}, "
                f"signal={signal}, position={position_state}"
            )

        except Exception as e:
            # 학습용 MVP에서는 단순 출력 후 루프 유지
            print(f"[ERROR] {e}")

        # 7) 대기 후 반복
        time.sleep(config.POLL_INTERVAL)


if __name__ == "__main__":
    run()
