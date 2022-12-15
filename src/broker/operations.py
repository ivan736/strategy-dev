import json
import os
from typing import List

import pandas as pd
import shioaji as sj
from dotenv import load_dotenv
from shioaji.constant import (
    ACTION_BUY,
    ACTION_SELL,
    FUTURES_OCTYPE_AUTO,
    FUTURES_PRICE_TYPE_MKP,
    ORDER_TYPE_IOC,
    OrderState,
)
from shioaji.data import Snapshot
from shioaji.position import FuturePosition

from src.logging_system import TradeBotLogger
from src.message.telegram_bot import send_message

load_dotenv()


class BrokerOperation:
    def __init__(self) -> None:
        self.api = sj.Shioaji()
        USER = os.environ["SHIOAJI_USER"]
        PASSWORD = os.environ["SHIOAJI_PASSWORD"]
        self.accounts = self.api.login(USER, PASSWORD)
        self.api.set_order_callback(self.order_callback)
        self.contract = self.api.Contracts.Futures.MXF[os.environ["TRADE_MONTH"]]

        if os.environ["CA_PATH"]:
            self.api.activate_ca(
                ca_path=os.environ["CA_PATH"],
                person_id=os.environ["SHIOAJI_USER"],
                ca_passwd=os.environ["CA_PASSWD"],
            )

    def get_positions(self) -> str:
        def parse_position(position: FuturePosition):
            return (
                f"持倉: {position.direction}\n"
                f"數量: {position.quantity}\n"
                f"成本: {position.price}\n"
                f"現價: {position.last_price}\n"
                f"損益: {position.pnl}\n"
            )

        self.api.update_status()
        ps: List[FuturePosition] = self.api.list_positions(self.api.futopt_account)
        return (
            "\n === \n".join([parse_position(_) for _ in ps]) if ps else "No Positions"
        )

    def get_current_price(self) -> str:
        snapshot: List[Snapshot] = self.api.snapshots([self.contract])
        df = pd.DataFrame.from_dict([_.dict() for _ in snapshot])
        df.ts = pd.to_datetime(df.ts)
        row = df[["code", "close", "ts"]].iloc[0]

        return (
            f"Close: {row.close}\n"
            f'Time: {row.ts.time().strftime("%H:%M:%S")}\n'
            f"Code: {row.code}"
        )

    def buy(self, position: int = 1, octype=FUTURES_OCTYPE_AUTO) -> str:
        TradeBotLogger.bot(f"Buying {position}")
        order = self.create_mkp_order(ACTION_BUY, position, octype)
        trade = self.api.place_order(self.contract, order)

    def sell(self, position: int = 1, octype=FUTURES_OCTYPE_AUTO):
        TradeBotLogger.bot(f"Selling {position}")
        order = self.create_mkp_order(ACTION_SELL, position, octype)
        trade = self.api.place_order(self.contract, order)

    def create_mkp_order(self, action: str, quantity=1, octype=FUTURES_OCTYPE_AUTO):
        order = self.api.Order(
            action=action,
            price=15369,
            quantity=quantity,
            price_type=FUTURES_PRICE_TYPE_MKP,  # {LMT, MKT, MKP} (限價、市價、範圍市價)
            order_type=ORDER_TYPE_IOC,
            octype=octype,  # {Auto, New, Cover, DayTrade} (自動、新倉、平倉、當沖)
            account=self.api.futopt_account,
        )
        return order

    def order_callback(self, stat, msg):
        if stat is OrderState.FOrder:
            print(f"FOrder type: {type(msg)}")
            print(f"FOrder content: {msg}")

        if stat is OrderState.FDeal:
            print(f"FDeal type: {type(msg)}")
            print(f"FDeal content: {msg}")

            info = (
                f"=== 成交通知 ===\n"
                f"商品: {msg['code']}\n"
                f"成交價: {msg['price']}\n"
                f"方向: {msg['action']}\n"
                f"發行月份: {msg['delivery_month']}\n"
                f"數量: {msg['quantity']}\n"
                f"trade_id: {msg['trade_id']}\n"
                f"ordno: {msg['ordno']}"
            )
            TradeBotLogger.trade(info)
            TradeBotLogger.console(info)

            send_message(info, new_loop=True)
