"""이동평균 계산 + 매매 시그널 생성 모듈."""

from __future__ import annotations

import pandas as pd


def add_moving_averages(df: pd.DataFrame, short_ma: int = 5, long_ma: int = 20) -> pd.DataFrame:
    """종가(close) 기준 단기/장기 이동평균 컬럼을 추가합니다."""
    result = df.copy()
    result["short_ma"] = result["close"].rolling(window=short_ma).mean()
    result["long_ma"] = result["close"].rolling(window=long_ma).mean()
    return result


def generate_signal(df: pd.DataFrame) -> str:
    """골든크로스/데드크로스 기준으로 BUY/SELL/HOLD를 반환합니다.

    조건:
    - 직전: short <= long, 현재: short > long => BUY
    - 직전: short >= long, 현재: short < long => SELL
    - 그 외 => HOLD
    """
    if len(df) < 2:
        return "HOLD"

    prev_row = df.iloc[-2]
    curr_row = df.iloc[-1]

    # 이동평균 초기 구간(NaN)에서는 신호를 만들지 않습니다.
    if pd.isna(prev_row["short_ma"]) or pd.isna(prev_row["long_ma"]):
        return "HOLD"
    if pd.isna(curr_row["short_ma"]) or pd.isna(curr_row["long_ma"]):
        return "HOLD"

    if prev_row["short_ma"] <= prev_row["long_ma"] and curr_row["short_ma"] > curr_row["long_ma"]:
        return "BUY"

    if prev_row["short_ma"] >= prev_row["long_ma"] and curr_row["short_ma"] < curr_row["long_ma"]:
        return "SELL"

    return "HOLD"
