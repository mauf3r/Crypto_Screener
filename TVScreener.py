import requests
import threading
import time
import pandas as pd
from Settings import *

class TVScreener():
    def __init__(self, symbols, interval=3600, out_file = None):
        
        self.screener_df = pd.DataFrame()
        self.lock = threading.Lock()
        threading.Thread(target=self.__start_screener, args=(symbols, interval, out_file)).start()
        while self.get_screener().empty:
            time.sleep(1)
            logger.info(f"screener_df is empty")


    def get_screener(self):
        with self.lock:
            return self.screener_df


    def __start_screener(self, symbols, interval, out_file):
        url = "https://scanner.tradingview.com/crypto/scan"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15'
        }
        payload = self.__create_payload(symbols)
        response = requests.post(url, headers=headers, json=payload)
        while True:
            if response.status_code == 200:
                data = [[d["s"]] + d["d"] for d in response.json()['data']]
                cols= ["Symbol"] + payload['columns']
                with self.lock:
                    self.screener_df = pd.DataFrame(data,columns=cols)
                    self.screener_df['MySignal'] = self.screener_df['Volatility.D'] * self.screener_df['Volatility.D'] * self.screener_df['Recommend.All|60'] * self.screener_df['Recommend.All'] * self.screener_df['Recommend.All']
                    positive_condition = (self.screener_df['Volatility.D'] > 10) & (self.screener_df['Recommend.All|60'] > 0) & (self.screener_df['Recommend.All'] > 0)
                    self.screener_df.loc[positive_condition, 'MySignal'] = self.screener_df['MySignal']
                    self.screener_df.loc[~positive_condition, 'MySignal'] = 0.0
                    self.screener_df = self.screener_df.sort_values(by='MySignal', ascending=False)
                logger.debug(f"recieved {len(self.screener_df)} lines of data")
            elif self.screener_df.empty:
                logger.error(f"screener_df is empty!")
            else:
                logger.error(f"sreener query did not return status 200: {response.text}")
            
            if out_file:
                self.screener_df.to_csv(out_file, index=False)

            time.sleep(interval)


    def __create_payload(self, symbols):
        symbols_with_exchange = ["BINANCE:" + symbol for symbol in symbols]
        filter_condition = [
                {"left": "exchange", "operation": "equal", "right": "BINANCE"},
                # {"left": "average_volume_10d_calc", "operation": "egreater", "right": 1000000},
                {"left": "active_symbol", "operation": "equal", "right": True},
                {"left": "currency", "operation": "equal", "right": "USDT"}
            ]
        columns = [
                "name", "close", "Volatility.D", "Volatility.W",
                "24h_vol_change|5", "Recommend.Other",  "Recommend.All|15",  "Recommend.All|60",  "Recommend.All",
                "change|1", "change|5", "change|15", "change|240", "change|60", "change", "change|1W", "change|1M",
                "BB.lower", "BB.upper", "BBPower", "Rec.BBPower", "MACD.macd", "MACD.signal",
                "SMA5", "SMA10", "SMA20",
                "SMA30", "SMA50", "SMA100", "SMA200",
                "pricescale", "minmov", "fractional", "minmove2"
            ]
        payload = {
            "filter": filter_condition,
            "options": {"lang": "en"},
            "filter2": {
                "operator": "and",
                "operands": [
                    {
                        "operation": {
                            "operator": "or",
                            "operands": [
                                {
                                    "expression": {"left": "type", "operation": "in_range", "right": ["spot"]}
                                }
                            ]
                        }
                    }
                ]
            },
            "markets": ["crypto"],
            "symbols": {
                "query": {"types": []},
                "tickers": symbols_with_exchange
            },
            "columns": columns,
            "sort": {"sortBy": "Volatility.D", "sortOrder": "desc"},
            "price_conversion": {"to_symbol": False},
            "range": [0, 150]
        }

        return payload