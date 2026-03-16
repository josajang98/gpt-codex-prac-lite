"""ccxt를 이용해 바이낸스와 통신하는 최소 기능 모듈입니다."""

from __future__ import annotations

import ccxt


class BinanceExchange:
    """바이낸스 연결, 시세 조회, 시장가 주문 기능을 제공합니다."""

    def __init__(self, api_key: str, api_secret: str, use_testnet: bool = True) -> None:
        """ccxt 바이낸스 객체를 생성합니다.

        Args:
            api_key: 바이낸스 API 키
            api_secret: 바이낸스 시크릿 키
            use_testnet: True면 테스트넷 엔드포인트 사용
        """
        self.exchange = ccxt.binance(
            {
                "apiKey": api_key,
                "secret": api_secret,
                "enableRateLimit": True,
            }
        )

        if use_testnet:
            # 테스트넷용 URL 설정
            self.exchange.set_sandbox_mode(True)

        # 시장 정보 로드 (심볼 유효성, 최소 수량 등 내부 계산에 사용)
        self.exchange.load_markets()

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100):
        """OHLCV 데이터를 가져옵니다.

        Returns:
            [timestamp, open, high, low, close, volume] 리스트의 리스트
        """
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def fetch_ticker_price(self, symbol: str) -> float:
        """현재 가격(last)을 조회합니다."""
        ticker = self.exchange.fetch_ticker(symbol)
        return float(ticker["last"])

    def fetch_free_balance(self, asset: str = "USDT") -> float:
        """사용 가능한 잔고를 조회합니다."""
        balance = self.exchange.fetch_balance()
        return float(balance.get("free", {}).get(asset, 0.0))

    def market_buy_by_quote_usdt(self, symbol: str, quote_usdt: float):
        """USDT 금액 기준으로 시장가 매수합니다.

        바이낸스는 create_market_buy_order에서 수량(base)을 받으므로,
        현재가를 조회해 대략적인 수량으로 변환 후 주문합니다.
        """
        price = self.fetch_ticker_price(symbol)
        amount = quote_usdt / price
        amount = float(self.exchange.amount_to_precision(symbol, amount))
        return self.exchange.create_market_buy_order(symbol, amount)

    def create_market_sell_order(self, symbol: str, amount: float):
        """보유 수량(amount) 기준으로 시장가 매도합니다."""
        amount = float(self.exchange.amount_to_precision(symbol, amount))
        return self.exchange.create_market_sell_order(symbol, amount)
