"""키움 OpenAPI+ 최소 연동 모듈.

주의:
- Windows + 키움 OpenAPI+ 설치 환경에서 동작합니다.
- PyQt5의 QAxWidget(ActiveX) 기반으로 가장 단순하게 구성했습니다.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop


class KiwoomAPI(QAxWidget):
    """키움 OpenAPI+를 직접 호출하는 최소 클래스."""

    def __init__(self) -> None:
        super().__init__()

        # 키움 OpenAPI+ ActiveX 컨트롤 연결
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        # 로그인/조회 동기화용 이벤트 루프
        self.login_loop: QEventLoop | None = None
        self.tr_loop: QEventLoop | None = None

        # 최근 TR 결과를 담아둘 변수
        self._latest_rows: list[dict[str, Any]] = []

        # 이벤트 핸들러 연결
        self.OnEventConnect.connect(self._on_event_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)

    def login(self) -> None:
        """로그인 창을 띄우고 로그인 완료까지 대기합니다."""
        self.dynamicCall("CommConnect()")
        self.login_loop = QEventLoop()
        self.login_loop.exec_()

    def _on_event_connect(self, err_code: int) -> None:
        """로그인 완료 이벤트 콜백.

        err_code:
        - 0: 성공
        - 그 외: 실패
        """
        if err_code == 0:
            print("[INFO] 키움 로그인 성공")
        else:
            print(f"[ERROR] 키움 로그인 실패 (err_code={err_code})")

        if self.login_loop is not None:
            self.login_loop.exit()

    def request_daily_ohlcv(self, stock_code: str, screen_no: str, count: int = 60) -> pd.DataFrame:
        """일봉 데이터를 조회해 DataFrame으로 반환합니다.

        TR: opt10081 (주식일봉차트조회)
        """
        self._latest_rows = []

        # 입력값 세팅
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "")
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        # TR 요청
        self.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "opt10081_req",
            "opt10081",
            0,
            screen_no,
        )

        # 응답 대기
        self.tr_loop = QEventLoop()
        self.tr_loop.exec_()

        df = pd.DataFrame(self._latest_rows)
        if df.empty:
            return df

        # 최근 count개만 사용
        df = df.head(count).copy()

        # 문자열 숫자를 숫자형으로 변환
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 과거->현재 순으로 정렬
        df = df.iloc[::-1].reset_index(drop=True)
        return df

    def request_basic_price(self, stock_code: str, screen_no: str) -> int:
        """현재가 1개만 간단 조회합니다.

        TR: opt10001 (주식기본정보요청)
        """
        self._latest_rows = []

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        self.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "opt10001_req",
            "opt10001",
            0,
            screen_no,
        )

        self.tr_loop = QEventLoop()
        self.tr_loop.exec_()

        if not self._latest_rows:
            return 0

        return int(self._latest_rows[0].get("current_price", 0))

    def _on_receive_tr_data(
        self,
        screen_no: str,
        rqname: str,
        trcode: str,
        record_name: str,
        prev_next: str,
        data_len: int,
        err_code: str,
        msg1: str,
        msg2: str,
    ) -> None:
        """TR 수신 이벤트 콜백.

        요청명(rqname)별로 필요한 최소 데이터만 파싱합니다.
        """
        if rqname == "opt10081_req":
            repeat_cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)

            rows: list[dict[str, Any]] = []
            for i in range(repeat_cnt):
                date = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", trcode, rqname, i, "일자"
                ).strip()
                open_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", trcode, rqname, i, "시가"
                ).strip()
                high_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", trcode, rqname, i, "고가"
                ).strip()
                low_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", trcode, rqname, i, "저가"
                ).strip()
                close_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가"
                ).strip()
                volume = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", trcode, rqname, i, "거래량"
                ).strip()

                rows.append(
                    {
                        "date": date,
                        "open": open_price.replace("+", "").replace("-", ""),
                        "high": high_price.replace("+", "").replace("-", ""),
                        "low": low_price.replace("+", "").replace("-", ""),
                        "close": close_price.replace("+", "").replace("-", ""),
                        "volume": volume.replace("+", "").replace("-", ""),
                    }
                )

            self._latest_rows = rows

        elif rqname == "opt10001_req":
            current_price = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "현재가"
            ).strip()
            self._latest_rows = [{"current_price": abs(int(current_price or 0))}]

        if self.tr_loop is not None:
            self.tr_loop.exit()

    def send_market_buy_order(
        self,
        account_no: str,
        stock_code: str,
        qty: int,
        screen_no: str,
    ) -> int:
        """시장가 매수 주문.

        SendOrder 파라미터:
        [RQName, ScreenNo, AccNo, OrderType, Code, Qty, Price, HogaGb, OrgOrderNo]
        - OrderType: 1(신규매수)
        - HogaGb: "03"(시장가)
        """
        return int(
            self.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                "market_buy",
                screen_no,
                account_no,
                1,
                stock_code,
                qty,
                0,
                "03",
                "",
            )
        )

    def send_market_sell_order(
        self,
        account_no: str,
        stock_code: str,
        qty: int,
        screen_no: str,
    ) -> int:
        """시장가 매도 주문.

        - OrderType: 2(신규매도)
        - HogaGb: "03"(시장가)
        """
        return int(
            self.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                "market_sell",
                screen_no,
                account_no,
                2,
                stock_code,
                qty,
                0,
                "03",
                "",
            )
        )
