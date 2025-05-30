import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple, Union

class MT5Connector:
    def __init__(self, config: dict):
        """Initialize MT5 connector with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_mt5()
        self.connected = False

    def _initialize_mt5(self) -> bool:
        """Initialize connection to MetaTrader 5"""
        try:
            if not mt5.initialize():
                raise Exception("MT5 initialization failed")
            
            # Login to MT5
            login_result = mt5.login(
                login=self.config['mt5']['login'],
                password=self.config['mt5']['password'],
                server=self.config['mt5']['server']
            )

            if not login_result:
                raise Exception(f"MT5 login failed. Error: {mt5.last_error()}")

            # Verify account type (reject demo accounts)
            account_info = mt5.account_info()
            if account_info.trade_mode != 0:  # 0 is real account
                raise Exception("Demo accounts are not allowed")

            self.connected = True
            self.logger.info("Successfully connected to MT5")
            return True

        except Exception as e:
            self.logger.error(f"MT5 initialization error: {str(e)}")
            return False

    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            account_info = mt5.account_info()
            return {
                'balance': account_info.balance,
                'equity': account_info.equity,
                'profit': account_info.profit,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'leverage': account_info.leverage,
                'currency': account_info.currency
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return {}

    def get_candles(self, symbol: str, timeframe: str, count: int = 1000) -> pd.DataFrame:
        """Fetch OHLCV candles from MT5"""
        try:
            # Convert timeframe string to MT5 timeframe constant
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            tf = timeframe_map.get(timeframe)
            if tf is None:
                raise ValueError(f"Invalid timeframe: {timeframe}")

            # Get candles from MT5
            candles = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            
            if candles is None:
                raise Exception(f"Failed to get candles for {symbol}")

            # Convert to DataFrame
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return df

        except Exception as e:
            self.logger.error(f"Error fetching candles: {str(e)}")
            return pd.DataFrame()

    def place_order(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = ""
    ) -> Dict:
        """Place a trading order"""
        try:
            order_types = {
                'BUY': mt5.ORDER_TYPE_BUY,
                'SELL': mt5.ORDER_TYPE_SELL,
                'BUY_LIMIT': mt5.ORDER_TYPE_BUY_LIMIT,
                'SELL_LIMIT': mt5.ORDER_TYPE_SELL_LIMIT,
                'BUY_STOP': mt5.ORDER_TYPE_BUY_STOP,
                'SELL_STOP': mt5.ORDER_TYPE_SELL_STOP
            }

            if order_type not in order_types:
                raise ValueError(f"Invalid order type: {order_type}")

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_types[order_type],
                "comment": comment,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Add optional parameters
            if price is not None:
                request["price"] = price
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp

            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"Order failed: {result.comment}")

            return {
                'ticket': result.order,
                'volume': result.volume,
                'price': result.price,
                'comment': result.comment
            }

        except Exception as e:
            self.logger.error(f"Error placing order: {str(e)}")
            return {}

    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            positions = mt5.positions_get()
            
            if positions is None:
                return []

            return [{
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'volume': pos.volume,
                'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                'price_open': pos.price_open,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'comment': pos.comment
            } for pos in positions]

        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return []

    def close_position(self, ticket: int) -> bool:
        """Close a specific position by ticket"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                raise Exception(f"Position {ticket} not found")

            pos = position[0]
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": ticket,
                "comment": "Position closed by AI",
                "type_filling": mt5.ORDER_FILLING_IOC
            }

            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"Close failed: {result.comment}")

            return True

        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            return False

    def get_symbol_info(self, symbol: str) -> Dict:
        """Get symbol information"""
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                raise Exception(f"Symbol {symbol} not found")

            return {
                'symbol': info.name,
                'bid': info.bid,
                'ask': info.ask,
                'spread': info.spread,
                'digits': info.digits,
                'min_lot': info.volume_min,
                'max_lot': info.volume_max,
                'lot_step': info.volume_step,
                'point': info.point
            }

        except Exception as e:
            self.logger.error(f"Error getting symbol info: {str(e)}")
            return {}

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.connected:
            mt5.shutdown()
