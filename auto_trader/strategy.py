"""볼린저 밴드 계산과 매매 신호를 담당하는 단순 전략 모듈입니다."""

from __future__ import annotations

import pandas as pd


def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_multiplier: float = 2.0,
) -> pd.DataFrame:
    """종가(close) 기준으로 볼린저 밴드를 계산합니다.

    Args:
        df: OHLCV 데이터프레임 (close 컬럼 필수)
        period: 이동평균 기간
        std_multiplier: 표준편차 배수

    Returns:
        middle_band, upper_band, lower_band 컬럼이 추가된 데이터프레임
    """
    result = df.copy()
    result["middle_band"] = result["close"].rolling(window=period).mean()
    std = result["close"].rolling(window=period).std()
    result["upper_band"] = result["middle_band"] + (std_multiplier * std)
    result["lower_band"] = result["middle_band"] - (std_multiplier * std)
    return result


def generate_signal(df: pd.DataFrame) -> str:
    """마지막 캔들 기준으로 BUY/SELL/HOLD 신호를 생성합니다.

    규칙:
    - close < lower_band => BUY
    - close > upper_band => SELL
    - 그 외 => HOLD
    """
    last = df.iloc[-1]

    # 밴드 계산 초기 구간(NaN)에서는 매매하지 않습니다.
    if pd.isna(last["upper_band"]) or pd.isna(last["lower_band"]):
        return "HOLD"

    if last["close"] < last["lower_band"]:
        return "BUY"
    if last["close"] > last["upper_band"]:
        return "SELL"
    return "HOLD"
