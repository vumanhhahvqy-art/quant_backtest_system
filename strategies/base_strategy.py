"""Khung chuẩn (Base Class) cho mọi chiến lược giao dịch trong hệ thống."""
import pandas as pd

class BaseStrategy:
    def __init__(self, params: dict = None):
        self.params = params or {}

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nhận vào DataFrame OHLCV chuẩn hóa.
        Trả về DataFrame có thêm cột 'signal' (1: Buy, -1: Sell, 0: Hold)
        kèm 'sl' (Stop Loss) và 'tp' (Take Profit) nếu có.
        """
        raise NotImplementedError("Chiến lược con bắt buộc phải định nghĩa hàm generate_signals()")
