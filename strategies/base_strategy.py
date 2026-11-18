"""Khung chuẩn (Base Class) cho mọi chiến lược giao dịch trong hệ thống."""
import pandas as pd

class BaseStrategy:
    # None preserves full-prefix behavior; incremental strategies may opt into
    # bounded trailing history and maintain their own state between candles.
    signal_history_limit: int | None = None

    def __init__(self, params: dict = None):
        self.params = params or {}

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return aligned signals from normalized, completed OHLCV candles.

        'signal' uses 1=BUY, -1=SELL, 0=HOLD; optional 'sl'/'tp' are price levels.
        Optional boolean 'exit' closes a position explicitly; 0 never closes it.
        The engine calls this method with completed historical prefixes only.
        """
        raise NotImplementedError("Chiến lược con bắt buộc phải định nghĩa hàm generate_signals()")

    def generate_signal(self, completed_data: pd.DataFrame) -> pd.Series:
        """Return the latest signal; subclasses may implement incremental updates.

        The default keeps backward compatibility with strategies that implement
        only ``generate_signals``. An incremental implementation can update its
        own indicator state and return one row without rebuilding the prefix.
        """
        signals = self.generate_signals(completed_data)
        if (not isinstance(signals, pd.DataFrame) or signals.empty
                or not signals.index.equals(completed_data.index)
                or not signals.columns.is_unique or "signal" not in signals):
            raise ValueError("Strategy must return aligned unique columns including signal.")
        return signals.iloc[-1].copy()
