# Core và hợp đồng chiến lược

Đọc cùng 02_DATA_AUDIT.md, 05A/05B_TESTS và 06_VALIDATION_AUDIT.md.

## File gốc: `core/models.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\models.py`

Số dòng: 153; kích thước: 5714 bytes; SHA256: `81c2b36789871376a1e39f68dc0980f1bb676be14c153fa2bee2f3f1b14df79d`.

<!-- SOURCE_BEGIN core/models.py -->
```python
"""Explicit records and units for deterministic, single-instrument simulation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, isclose
from typing import Any

import pandas as pd

from core.data_loader import metadata_blockers


def positive(value: float, name: str) -> None:
    """Require a finite positive number, excluding booleans."""
    if isinstance(value, bool) or not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive.")


@dataclass(frozen=True)
class Instrument:
    symbol: str
    tick_size: float
    pip_size: float
    contract_size: float
    quantity_unit: str
    quote_currency: str
    minimum_quantity_increment: float

    def __post_init__(self) -> None:
        for name in ("tick_size", "pip_size", "contract_size", "minimum_quantity_increment"):
            positive(getattr(self, name), name)
        if self.quantity_unit not in ("lots", "units"):
            raise ValueError("quantity_unit must be lots or units.")
        if self.quantity_unit == "units" and self.contract_size != 1:
            raise ValueError("Unit quantities require contract_size=1.")
        if not self.symbol or not self.quote_currency:
            raise ValueError("Symbol and quote currency are required.")

    @classmethod
    def from_metadata(cls, metadata: dict[str, Any]) -> Instrument:
        """Use confirmed dataset metadata, never legacy symbol guesses."""
        blockers = metadata_blockers(metadata)
        if blockers:
            raise ValueError("; ".join(blockers))
        specs = metadata["instrument_specifications"]["value"]
        return cls(metadata["symbol"]["value"], **{
            name: specs[name] for name in cls.__dataclass_fields__ if name != "symbol"
        })

    def units(self, quantity: float) -> float:
        """Convert declared quantities to underlying units; reject off-step sizes."""
        positive(quantity, "quantity")
        steps = quantity / self.minimum_quantity_increment
        if not isclose(steps, round(steps), rel_tol=0, abs_tol=1e-8):
            raise ValueError("Quantity is not a multiple of minimum_quantity_increment.")
        return quantity * self.contract_size


@dataclass(frozen=True)
class Order:
    order_id: int
    action: str
    quantity: float
    submitted_at: pd.Timestamp
    stop_loss: float | None = None
    take_profit: float | None = None
    order_type: str = "market"

    def __post_init__(self) -> None:
        if self.order_type != "market":
            raise ValueError("Only next-bar market orders are supported.")
        if self.action not in ("BUY", "SELL", "EXIT"):
            raise ValueError("Action must be BUY, SELL or EXIT.")
        positive(self.quantity, "quantity")
        if pd.isna(self.submitted_at) or str(self.submitted_at.tz) != "UTC":
            raise ValueError("Order submission requires a UTC timestamp.")
        for level in (self.stop_loss, self.take_profit):
            if level is not None:
                positive(level, "SL/TP")


@dataclass(frozen=True)
class Fill:
    order_id: int
    timestamp: pd.Timestamp
    side: int
    quantity: float
    price: float
    commission: float
    spread_cost: float
    slippage_cost: float
    reason: str
    ambiguous: bool = False
    timing: str = "open"

    def __post_init__(self) -> None:
        if isinstance(self.order_id, bool) or not isinstance(self.order_id, int) or self.order_id < 1:
            raise ValueError("Fill order_id must be a positive integer.")
        if isinstance(self.side, bool) or self.side not in (-1, 1):
            raise ValueError("Fill side must be +1 or -1.")
        positive(self.quantity, "fill quantity")
        positive(self.price, "fill price")
        for name in ("commission", "spread_cost", "slippage_cost"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative.")
        if pd.isna(self.timestamp) or str(self.timestamp.tz) != "UTC":
            raise ValueError("Fill timestamp must be timezone-aware UTC.")
        if self.timing not in ("open", "intrabar"):
            raise ValueError("Fill timing must be open or intrabar.")
        if not isinstance(self.ambiguous, bool):
            raise ValueError("Fill ambiguous must be boolean.")


@dataclass(frozen=True)
class Position:
    direction: int
    quantity: float
    entry: Fill
    stop_loss: float | None
    take_profit: float | None
    reserved_capital: float

    def __post_init__(self) -> None:
        if isinstance(self.direction, bool) or self.direction not in (-1, 1):
            raise ValueError("Position direction must be +1 or -1.")
        positive(self.quantity, "position quantity")
        positive(self.reserved_capital, "reserved_capital")
        if self.entry.side != self.direction or self.entry.quantity != self.quantity:
            raise ValueError("Position entry does not match direction or quantity.")
        for name, level in (("stop_loss", self.stop_loss), ("take_profit", self.take_profit)):
            if level is not None:
                positive(level, name)


@dataclass(frozen=True)
class Trade:
    entry: Fill
    exit: Fill
    gross_pnl: float
    net_pnl: float


@dataclass(frozen=True)
class AccountState:
    timestamp: pd.Timestamp
    balance: float
    unrealized_pnl: float
    equity: float
    reserved_capital: float
    free_capital: float
    realized_pnl: float
```
<!-- SOURCE_END core/models.py -->

## File gốc: `core/execution.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\execution.py`

Số dòng: 37; kích thước: 1401 bytes; SHA256: `fdd5262964943c0b9e817f3857b088af6b675dc0026f5dd853d10c0bcff1628e`.

<!-- SOURCE_BEGIN core/execution.py -->
```python
"""OHLC market and protective execution; prices are executable-side prices."""

from __future__ import annotations

from dataclasses import dataclass

from core.models import Position


@dataclass(frozen=True)
class ExitDecision:
    price: float
    reason: str
    ambiguous: bool = False
    timing: str = "intrabar"


def protective_exit(position: Position, bar: dict[str, float]) -> ExitDecision | None:
    """SL first on ambiguity; gap stops at open, gap TP at the target.

    Input bar must use Bid for long liquidation and Ask for short liquidation.
    Intrabar timing identifies a candle interval, not an observed event time.
    """
    direction = position.direction
    sl, tp = position.stop_loss, position.take_profit
    opening = bar["open"]
    if sl is not None and direction * (opening - sl) <= 0:
        return ExitDecision(opening, "stop_loss_gap", timing="open")
    if tp is not None and direction * (opening - tp) >= 0:
        return ExitDecision(tp, "take_profit_gap", timing="open")
    stop_hit = sl is not None and (bar["low"] <= sl if direction == 1 else bar["high"] >= sl)
    target_hit = tp is not None and (bar["high"] >= tp if direction == 1 else bar["low"] <= tp)
    if stop_hit:
        return ExitDecision(sl, "stop_loss", bool(target_hit))
    if target_hit:
        return ExitDecision(tp, "take_profit")
    return None
```
<!-- SOURCE_END core/execution.py -->

## File gốc: `core/cost_model.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\cost_model.py`

Số dòng: 57; kích thước: 2746 bytes; SHA256: `b8e12db3ae11c56f9ca9c0521e8ab24d6bda4595c4f9b24db07149f72a1178fc`.

<!-- SOURCE_BEGIN core/cost_model.py -->
```python
"""Centralized fixed spread, adverse slippage and per-side commission."""

from dataclasses import dataclass
from math import ceil, floor, isfinite

from core.models import Fill, Instrument, positive


@dataclass(frozen=True)
class CostModel:
    """Spread/slippage in price units; commission in account currency per quantity.

    Spread and slippage are embedded in fill prices, never debited again.
    Commission is per side per declared quantity unit (lot or unit).
    """

    spread: float
    slippage: float
    commission_per_quantity: float
    swap_per_day: float = 0.0

    def __post_init__(self) -> None:
        for value in (self.spread, self.slippage, self.commission_per_quantity, self.swap_per_day):
            if isinstance(value, bool) or not isfinite(value) or value < 0:
                raise ValueError("Costs must be finite and nonnegative.")
        if self.swap_per_day != 0:
            raise ValueError("Swap/rollover is not supported; use zero explicitly.")

    def side_bar(self, bar: dict[str, float], price_type: str, side: int) -> dict[str, float]:
        """Derive executable Ask (+1) or Bid (-1) from a single OHLC stream."""
        if side not in (-1, 1) or price_type not in ("Mid", "Bid", "Ask"):
            raise ValueError("Requires side +/-1 and price_type Mid/Bid/Ask.")
        source = {"Mid": 0, "Bid": -1, "Ask": 1}[price_type]
        offset = (side - source) * self.spread / 2
        result = {name: float(value) + offset for name, value in bar.items()}
        for value in result.values():
            positive(value, "executable price")
        return result

    def fill(self, *, instrument: Instrument, order_id: int, timestamp,
             side: int, quantity: float, price: float, conversion_rate: float,
             reason: str, ambiguous: bool = False, timing: str = "open") -> Fill:
        """Apply slippage with adverse tick rounding and record account-currency costs."""
        positive(conversion_rate, "conversion_rate")
        if side not in (-1, 1):
            raise ValueError("Fill side must be +/-1.")
        units = instrument.units(quantity)
        raw = price + side * self.slippage
        ticks = raw / instrument.tick_size
        rounded = (ceil(ticks - 1e-9) if side == 1 else floor(ticks + 1e-9))
        executed = rounded * instrument.tick_size
        positive(executed, "fill price")
        return Fill(order_id, timestamp, side, quantity, executed,
                    quantity * self.commission_per_quantity,
                    units * self.spread / 2 * conversion_rate,
                    units * abs(executed - price) * conversion_rate,
                    reason, ambiguous, timing)
```
<!-- SOURCE_END core/cost_model.py -->

## File gốc: `core/portfolio.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\portfolio.py`

Số dòng: 70; kích thước: 3954 bytes; SHA256: `7f5c0d55cd3b454fdf1e34101b40cbcf398de0a06d1ef1104c93860cf01c3d24`.

<!-- SOURCE_BEGIN core/portfolio.py -->
```python
"""Single-position full-notional collateral accounting, without leverage."""

from core.models import AccountState, Fill, Instrument, Order, Position, Trade, positive


class Portfolio:
    """Balance is collateral cash, not spot inventory cash; costs debit on fills."""

    def __init__(self, instrument: Instrument, initial_capital: float) -> None:
        positive(initial_capital, "initial_capital")
        self.instrument = instrument
        self.initial_capital = initial_capital
        self.balance = initial_capital
        self.position: Position | None = None
        self.trades: list[Trade] = []

    def open(self, order: Order, fill: Fill, conversion_rate: float) -> None:
        """Reserve entry notional in account currency, rejecting insufficient cash."""
        positive(conversion_rate, "conversion_rate")
        if self.position is not None:
            raise ValueError("A position is already open.")
        if order.action not in ("BUY", "SELL"):
            raise ValueError("Entry requires BUY or SELL.")
        direction = 1 if order.action == "BUY" else -1
        if fill.side != direction or fill.quantity != order.quantity:
            raise ValueError("Fill does not match entry order.")
        if fill.order_id != order.order_id or fill.timestamp < order.submitted_at:
            raise ValueError("Entry fill ID/timestamp does not match the submitted order.")
        for level, sign in ((order.stop_loss, -1), (order.take_profit, 1)):
            if level is not None and direction * (level - fill.price) * sign <= 0:
                raise ValueError("SL/TP must bracket the actual entry price.")
        reserved = self.instrument.units(fill.quantity) * fill.price * conversion_rate
        if reserved + fill.commission > self.balance:
            raise ValueError("Insufficient capital for full-notional collateral and commission.")
        self.balance -= fill.commission
        self.position = Position(direction, fill.quantity, fill, order.stop_loss,
                                 order.take_profit, reserved)

    def close(self, fill: Fill, conversion_rate: float) -> Trade:
        """Convert quote P/L at exit; never debit spread/slippage a second time."""
        positive(conversion_rate, "conversion_rate")
        position = self.position
        if position is None:
            raise ValueError("No position to close.")
        if fill.side != -position.direction or fill.quantity != position.quantity:
            raise ValueError("Closing fill must exactly offset the position.")
        if fill.timestamp < position.entry.timestamp:
            raise ValueError("Closing fill cannot precede the entry fill.")
        gross = (fill.price - position.entry.price) * position.direction
        gross *= self.instrument.units(position.quantity) * conversion_rate
        trade = Trade(position.entry, fill, gross,
                      gross - position.entry.commission - fill.commission)
        self.balance += gross - fill.commission
        self.trades.append(trade)
        self.position = None
        return trade

    def mark(self, timestamp, liquidation_price: float, conversion_rate: float) -> AccountState:
        """Mark to executable close, excluding hypothetical exit fees/slippage."""
        positive(liquidation_price, "liquidation_price")
        positive(conversion_rate, "conversion_rate")
        unrealized = reserved = 0.0
        if self.position is not None:
            p = self.position
            unrealized = ((liquidation_price - p.entry.price) * p.direction
                          * self.instrument.units(p.quantity) * conversion_rate)
            reserved = p.reserved_capital
        equity = self.balance + unrealized
        return AccountState(timestamp, self.balance, unrealized, equity, reserved,
                            equity - reserved, self.balance - self.initial_capital)
```
<!-- SOURCE_END core/portfolio.py -->

## File gốc: `core/engine.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\engine.py`

Số dòng: 229; kích thước: 12934 bytes; SHA256: `b2e35f439025d9b932dec9a8a94c00e94b3317df965c282cfe4c6335bc46880b`.

<!-- SOURCE_BEGIN core/engine.py -->
```python
"""Chronological single-instrument backtest with prefix-only strategy input."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import logging
from typing import Any

import numpy as np
import pandas as pd

from core.cost_model import CostModel
from core.data_validator import validate_data
from core.execution import protective_exit
from core.models import AccountState, Fill, Instrument, Order, Position, Trade, positive
from core.portfolio import Portfolio
from strategies.base_strategy import BaseStrategy

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BacktestResult:
    """In-memory hypothetical outputs; open positions are not force-liquidated."""

    orders: tuple[Order, ...]
    fills: tuple[Fill, ...]
    trades: tuple[Trade, ...]
    states: tuple[AccountState, ...]
    events: tuple[dict[str, Any], ...]
    open_position: Position | None
    assumptions: dict[str, Any]


class ConversionRates:
    """Historical quote-to-account rates: account currency per one quote unit.

    Use the latest published rate at or before the event. No backfilling from
    future observations. Intrabar events conservatively use the bar-open rate.
    """

    def __init__(self, quote_currency: str, account_currency: str,
                 rates: pd.Series | None) -> None:
        if not account_currency:
            raise ValueError("account_currency is required.")
        self.identity = quote_currency == account_currency
        if not self.identity and rates is None:
            raise ValueError("Historical quote-to-account conversion rates are required.")
        self.rates = None if rates is None else rates.copy(deep=True)
        if rates is not None:
            index = rates.index
            if (not isinstance(index, pd.DatetimeIndex) or str(index.tz) != "UTC"
                    or index.hasnans or not index.is_unique or not index.is_monotonic_increasing
                    or rates.empty or not pd.api.types.is_numeric_dtype(rates)
                    or not np.isfinite(rates).all() or not (rates > 0).all()):
                raise ValueError("Conversion rates must be positive, finite, ordered unique UTC observations.")

    def at(self, timestamp: pd.Timestamp) -> float:
        if self.identity:
            return 1.0
        offset = self.rates.index.searchsorted(timestamp, side="right") - 1
        if offset < 0:
            raise ValueError(f"No conversion rate available at {timestamp}.")
        return float(self.rates.iloc[offset])


class BacktestEngine:
    """Coordinate execution, costs and accounting without strategy-specific rules."""

    def __init__(self, metadata: dict[str, Any], costs: CostModel, *,
                 initial_capital: float, account_currency: str, quantity: float) -> None:
        self.metadata = deepcopy(metadata)
        self.instrument = Instrument.from_metadata(self.metadata)
        self.instrument.units(quantity)
        positive(initial_capital, "initial_capital")
        if not account_currency:
            raise ValueError("account_currency is required.")
        self.costs = costs
        self.initial_capital = initial_capital
        self.account_currency = account_currency
        self.quantity = quantity

    def run(self, data: pd.DataFrame, strategy: BaseStrategy, *,
            expected_timestamps: pd.DatetimeIndex | None = None,
            conversion_rates: pd.Series | None = None) -> BacktestResult:
        """Evaluate after close, execute on next available bar open.

        Without expected timestamps, intraday gaps warn and cross-day gaps are
        ignored. An optional schedule must come from an independent calendar.
        All input rows are checked before simulation; none are silently filled.
        Strategies receive copies of completed prefixes, never future rows.
        """
        report = validate_data(data, self.metadata, expected_timestamps=expected_timestamps)
        if report["errors"] or report["metadata_blockers"]:
            raise ValueError(f"Data is not simulation-ready: {report}")
        if not data.columns.is_unique:
            raise ValueError("Duplicate data columns are unsupported.")
        columns = ["open", "high", "low", "close"]
        if any(not pd.api.types.is_numeric_dtype(data[c]) for c in columns):
            raise ValueError("OHLC columns must have numeric dtypes.")
        frame = data.copy(deep=True)
        history_limit = strategy.signal_history_limit
        if history_limit is not None and (
            isinstance(history_limit, bool) or not isinstance(history_limit, int) or history_limit < 1
        ):
            raise ValueError("signal_history_limit must be a positive integer or None.")
        duration = pd.Timedelta(self.metadata["timeframe"]["value"])
        is_open = self.metadata["timestamp_kind"]["value"] == "open"
        openings = frame.index if is_open else frame.index - duration
        closings = frame.index + duration if is_open else frame.index
        if len(frame) > 1 and (openings[1:] < closings[:-1]).any():
            raise ValueError("Overlapping candles are unsupported.")
        rates = ConversionRates(self.instrument.quote_currency, self.account_currency, conversion_rates)
        portfolio = Portfolio(self.instrument, self.initial_capital)
        orders: list[Order] = []
        fills: list[Fill] = []
        states: list[AccountState] = []
        events: list[dict[str, Any]] = []
        pending: Order | None = None
        price_type = self.metadata["price_type"]["value"]
        LOGGER.info("Starting hypothetical simulation: %s, %d bars", self.instrument.symbol, len(frame))

        def make_fill(order_id, side, quantity, price, timestamp, rate, reason,
                      ambiguous=False, timing="open"):
            return self.costs.fill(instrument=self.instrument, order_id=order_id,
                                   timestamp=timestamp, side=side, quantity=quantity,
                                   price=price, conversion_rate=rate, reason=reason,
                                   ambiguous=ambiguous, timing=timing)

        for i in range(len(frame)):
            opening, closing = openings[i], closings[i]
            rate = rates.at(opening)
            bar = {c: float(frame.iloc[i][c]) for c in columns}
            if pending is not None:
                order, pending = pending, None
                if opening < order.submitted_at:
                    raise ValueError("Order cannot fill before submission.")
                position = portfolio.position
                rejection = None
                if order.action == "EXIT" and position is None:
                    rejection = "no_open_position"
                elif order.action != "EXIT" and position is not None:
                    rejection = "position_already_open"
                if rejection is None:
                    side = (-position.direction if order.action == "EXIT"
                            else 1 if order.action == "BUY" else -1)
                    quantity = position.quantity if order.action == "EXIT" else order.quantity
                    price = self.costs.side_bar(bar, price_type, side)["open"]
                    fill = make_fill(order.order_id, side, quantity, price, opening, rate, order.action)
                    if order.action == "EXIT":
                        portfolio.close(fill, rate)
                    else:
                        try:
                            portfolio.open(order, fill, rate)
                        except ValueError as exc:
                            rejection = str(exc)
                    if rejection is None:
                        fills.append(fill)
                events.append({"order_id": order.order_id, "timestamp": opening,
                               "status": "rejected" if rejection else "filled",
                               "reason": rejection or order.action})
            position = portfolio.position
            if position is not None:
                side = -position.direction
                executable = self.costs.side_bar(bar, price_type, side)
                decision = protective_exit(position, executable)
                if decision is not None:
                    # For intrabar events opening identifies the containing candle.
                    fill = make_fill(position.entry.order_id, side, position.quantity,
                                     decision.price, opening, rate, decision.reason,
                                     decision.ambiguous, decision.timing)
                    portfolio.close(fill, rate)
                    fills.append(fill)
                    events.append({"timestamp": opening, "status": "protective_exit",
                                   "reason": decision.reason, "ambiguous": decision.ambiguous,
                                   "timing": decision.timing, "order_id": fill.order_id})
            position = portfolio.position
            mark_side = -position.direction if position else -1
            mark = self.costs.side_bar(bar, price_type, mark_side)["close"]
            states.append(portfolio.mark(closing, mark, rates.at(closing)))
            if states[-1].equity < 0 or portfolio.balance < 0:
                events.append({"timestamp": closing, "status": "insolvent",
                               "reason": "negative_equity_or_balance_after_market_loss"})
                LOGGER.warning("Simulated account insolvency at %s", closing)
            start = 0 if history_limit is None else max(0, i + 1 - history_limit)
            prefix = frame.iloc[start:i + 1].copy(deep=True)
            row = strategy.generate_signal(prefix)
            if not isinstance(row, pd.Series) or not row.index.is_unique or "signal" not in row:
                raise ValueError("Strategy must return a signal Series including signal.")
            signal = row["signal"]
            if pd.isna(signal) or signal not in (-1, 0, 1):
                raise ValueError("signal must be -1, 0 or 1; warm-up must emit 0.")
            exit_signal = row.get("exit", False)
            if not isinstance(exit_signal, (bool, np.bool_)):
                raise ValueError("exit must be boolean.")
            if exit_signal and signal != 0:
                raise ValueError("EXIT and entry cannot be submitted together.")
            if signal != 0 or exit_signal:
                def level(name):
                    value = row.get(name)
                    return None if value is None or pd.isna(value) else float(value)
                action = "EXIT" if exit_signal else "BUY" if signal == 1 else "SELL"
                pending = Order(len(orders) + 1, action, self.quantity, closing,
                                level("sl") if not exit_signal else None,
                                level("tp") if not exit_signal else None)
                orders.append(pending)
                events.append({"order_id": pending.order_id, "timestamp": closing,
                               "status": "submitted", "reason": action})
        if pending is not None:
            events.append({"order_id": pending.order_id, "timestamp": closings[-1],
                           "status": "unfilled", "reason": "end_of_data"})
        LOGGER.info("Simulation complete: %d fills, %d closed trades", len(fills), len(portfolio.trades))
        return BacktestResult(tuple(orders), tuple(fills), tuple(portfolio.trades),
                              tuple(states), tuple(events), portfolio.position, {
                                  "hypothetical": True, "metadata": deepcopy(self.metadata),
                                  "costs": self.costs, "quantity": self.quantity,
                                  "initial_capital": self.initial_capital,
                                  "account_currency": self.account_currency,
                                  "execution": "next_available_bar_open",
                                  "ambiguity": "stop_loss_first",
                                  "collateral": "full_entry_notional_no_leverage",
                                  "conversion": "latest_published_rate; intrabar uses open rate",
                                  "warnings": report["warnings"],
                                  "gap_check_mode": report["gap_check_mode"],
                                  "intraday_gap_check_passed": report["intraday_gap_check_passed"],
                                  "full_calendar_verified": report["full_calendar_verified"],
                                  "interval_analysis": deepcopy(report["interval_analysis"]),
                                  "open_positions": "marked_to_close_not_forced_closed"})
```
<!-- SOURCE_END core/engine.py -->

## File gốc: `strategies/base_strategy.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\strategies\base_strategy.py`

Số dòng: 33; kích thước: 1769 bytes; SHA256: `f476111d945bf4d50ad9ccac81b8f03f07d822c62aa87a8994a835e24af2eaad`.

<!-- SOURCE_BEGIN strategies/base_strategy.py -->
```python
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
```
<!-- SOURCE_END strategies/base_strategy.py -->

## File gốc: `core/BACKTEST_ENGINE.md`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\BACKTEST_ENGINE.md`

Số dòng: 207; kích thước: 14292 bytes; SHA256: `48963307de96476d1010ef50a79881391177bdde159ced0a6341991f871dc672`.

<!-- SOURCE_BEGIN core/BACKTEST_ENGINE.md -->
````markdown
# Backtest engine — Giai đoạn 4

Đây là mô phỏng lịch sử giả định. API hiện trả kết quả trong bộ nhớ, chưa tích hợp
chạy cấu hình qua `run_backtest.py` hoặc xuất báo cáo nghiên cứu.

## Phạm vi và giao diện

- Một công cụ, một vị thế tối đa. Không cộng dồn, đảo chiều tự động hoặc đóng một phần.
- Lệnh `market` BUY/SELL/EXIT. Lệnh limit, stop-entry và trailing stop chưa hỗ trợ.
  `Order` từ chối loại lệnh ngoài phạm vi này.
- `BaseStrategy.generate_signals` nhận bản sao dữ liệu từ đầu mẫu đến hết nến vừa
  đóng, trả DataFrame cùng index, có `signal` bằng `1/-1/0`, tùy chọn `exit` kiểu
  boolean và `sl/tp` là mức giá tuyệt đối. Warm-up phát `0`. `0` tiếp tục giữ vị thế.
- `exit=True` là yêu cầu đóng toàn bộ vị thế. Không gửi EXIT đồng thời BUY/SELL.
- BUY/SELL khi đã có vị thế và EXIT khi không có vị thế bị từ chối, có event.
- Chiến lược phải thuần theo dữ liệu đầu vào, không tự tải dữ liệu tương lai. Các cột
  đặc trưng do người gọi cung cấp cũng phải được kiểm tra tính nhân quả. Engine
  giới hạn prefix nhưng không thể kiểm soát mã chiến lược tự truy cập nguồn ngoài.

### Cập nhật tín hiệu và kiểm tra nhân quả

Engine gọi `generate_signal(completed_data)` mỗi nến. Mặc định phương thức này
gọi `generate_signals` và giữ kiểm tra index/cột như trước, nên chiến lược cũ
không cần thay đổi. Chiến lược muốn cập nhật gia tăng có thể override
`generate_signal`, trả một Series gồm `signal` và các trường tùy chọn.

`signal_history_limit=None` vẫn truyền toàn prefix. Chiến lược gia tăng có thể
chủ động đặt một số nguyên dương (ví dụ 1) để chỉ sao chép các nến gần nhất;
chiến lược chịu trách nhiệm quản lý state, warm-up và khởi tạo lại cho mỗi run.
Không tự cắt lịch sử của chiến lược cũ và không tính tín hiệu trước trên toàn mẫu.

`core.causality.check_prefix_invariance(builder, raw_data)` tính lại đặc trưng
trên các prefix rồi so với phần tương ứng của kết quả toàn mẫu. Test phát hiện
`shift(-1)`, rolling đặt giữa và chuẩn hóa theo cực đại toàn mẫu. Đây là kiểm tra
trên mẫu cung cấp, không chứng minh tính nhân quả cho mọi dữ liệu. Phải truyền
hàm tính lại từ OHLC gốc; cắt cột đặc trưng đã tính sẵn không phát hiện được rò rỉ.

## Chu trình thời gian

1. Tại đầu nến: xử lý lệnh gửi sau nến trước, tại giá mở phía thực thi.
2. Kiểm tra SL/TP cho vị thế đang giữ, kể cả vị thế mới mở tại đầu nến này.
3. Tại cuối nến: đánh dấu P/L chưa thực hiện bằng giá đóng phía thanh lý.
4. Gọi chiến lược trên prefix đã đóng và tạo lệnh cho đầu nến kế tiếp có dữ liệu.

Timestamp nội bộ UTC; hỗ trợ nhãn nến `open` và `close`, timeframe cố định.
Thời gian đặt lệnh sau đóng nến có thể bằng thời gian mở nến kế tiếp.
Không dùng giá đóng nến tín hiệu để khớp. Không tạo nến bù. Nến chồng lấn,
sai OHLC, NaN/Infinity, timestamp trùng/không tăng và các lỗi dữ liệu bắt buộc
khác vẫn bị từ chối. Có hai chế độ kiểm tra khoảng trống:

- Mặc định `expected_timestamps=None`: không cần lịch Forex bên ngoài. Chỉ so
  hai timestamp liên tiếp thuộc **cùng ngày UTC**. Khoảng cách lớn hơn timeframe
  được ghi vào `interval_analysis.intraday_gaps`, gồm đầu/cuối khoảng quan sát,
  độ dài giây và `candidate_missing_slots`. Đây chỉ là cảnh báo, không chặn chạy.
  Mỗi cặp khác ngày UTC bị bỏ qua, kể cả cuối tuần, ngày lễ và qua nửa đêm;
  không cố xác định nguyên nhân nghỉ. Không kiểm tra thiếu nến trước/sau mẫu.
- Truyền `expected_timestamps`: đối chiếu toàn bộ với lịch độc lập đã xác nhận,
  bao gồm đầu/cuối mẫu; nến thiếu hoặc ngoài lịch là lỗi chặn như trước.

Số nến có khả năng thiếu là số điểm trên lưới `timestamp_trước + k*timeframe`
nằm hoàn toàn giữa hai đầu mút. Ví dụ timeframe H1: 10:00→14:00 có 3 điểm;
10:00→12:30 có 2 điểm và thêm cảnh báo khoảng không chia hết timeframe.
Đây là ứng viên thiếu, không khẳng định dữ liệu thực sự đã mất.

`intraday_gap_check_passed=True` nghĩa là timestamp hợp lệ, có thứ tự và không
phát hiện khoảng bất thường trong ngày theo quy ước này. Không đồng nghĩa dữ
liệu hoàn chỉnh. `full_calendar_verified` luôn False khi không truyền lịch;
chỉ True khi lịch cung cấp khớp dữ liệu và timestamp hợp lệ. Không dùng chính
`data.index` làm bằng chứng lịch hoàn chỉnh. `ready_for_research` chỉ yêu cầu
các kiểm tra bắt buộc và metadata đạt; cảnh báo vẫn lưu trong báo cáo/kết quả.

`validate_expected_timestamps` kiểm tra UTC, thứ tự, duy nhất, không rỗng và
không chồng lấn. Lịch dùng cùng quy ước nhãn `open/close` như dữ liệu, không dịch
timestamp thêm một lần. Cần dựng lịch độc lập từ nguồn/lịch phiên và ranh giới
khoảng nghiên cứu đã xác nhận, rồi đối chiếu toàn bộ, kể cả nến đầu và cuối.
Không tự suy ra lịch Forex/broker từ khoảng cách nến; dãy timestamp đơn thuần
không chứng minh được nguồn lịch. Lịch tổng hợp trong test định nghĩa trước
các thời điểm phải có và được giữ nguyên khi cố ý xóa nến.

Lệnh cuối mẫu ghi `unfilled/end_of_data`. Vị thế còn mở được giữ và định giá,
không ép đóng tại cuối mẫu. Không có giả định về thanh khoản, khối lượng khớp,
độ trễ hoặc khớp một phần: lệnh thị trường hợp lệ khớp toàn bộ tại nến kế tiếp.

Lệnh luôn chờ **nến thực tế tiếp theo**, dù cách nhiều giờ/ngày: BUY sau đóng
nến thứ Sáu có thể khớp tại giá mở nến đầu Chủ nhật/thứ Hai nếu đó là dòng dữ
liệu tiếp theo. Cảnh báo thiếu nến trong ngày cũng không tạo nến hay giá giả;
gap giá, SL/TP, chi phí và kế toán tiếp tục áp dụng trên dữ liệu thực tế.

## Giá, SL/TP và chi phí

- Metadata phải được xác nhận theo schema dữ liệu hiện có. Không suy đoán từ
  `symbols.json` cũ. Hỗ trợ một dòng OHLC đã xác định `Mid`, `Bid` hoặc `Ask`.
- Spread cố định `s` theo đơn vị giá. Từ Mid suy ra Bid=Mid-s/2, Ask=Mid+s/2;
  từ Bid suy ra Ask=Bid+s; từ Ask suy ra Bid=Ask-s.
- BUY dùng Ask, SELL dùng Bid; long thoát dùng Bid, short thoát dùng Ask.
  SL/TP kiểm tra trên OHLC phía thoát, không trên giá Mid.
- Hai SL/TP cùng chạm: SL trước, `ambiguous=True`. Nếu giá mở đã qua một mức,
  xử lý sự kiện đầu nến trước khi xét high/low của nến.
- Gap qua SL: dùng giá mở. Gap qua TP: dùng giá mục tiêu, không hưởng cải thiện
  giá qua gap. TP là trigger cho thoát thị trường bảo thủ, không phải limit đảm
  bảo giá. Slippage bất lợi và làm tròn tick có thể làm giá thoát xấu hơn TP.
- `Fill.timing=intrabar` chỉ xác định khoảng nến; `timestamp` là đầu khoảng đó,
  không phải khẳng định thời điểm chạm chính xác. Không suy diễn đường giá nội nến.
- Slippage cố định theo đơn vị giá, cộng cho BUY, trừ cho SELL, làm tròn theo
  tick về phía bất lợi. Commission tính theo mỗi phía, mỗi đơn vị quantity đã
  khai báo, bằng đồng tiền tài khoản. Mức commission phải được cấu hình rõ.
- Spread/slippage nằm trong giá khớp. Các trường cost trong Fill chỉ phục vụ
  kiểm tra, không trừ tiền lần hai. `spread_cost` là nửa spread tham chiếu Mid.
- Chưa hỗ trợ OHLC Bid/Ask đồng thời, spread biến thiên, commission theo phần
  trăm/notional, swap hoặc rollover. Swap khác 0 bị từ chối. Chạy qua đêm với
  swap=0 là giả định không tính chi phí tài trợ, không đại diện chi phí thực tế.
- SL/TP không còn bao quanh giá khớp sau gap/slippage: từ chối lệnh và ghi lý do.

## Quy cách và tài khoản

`Instrument` lấy tick, pip, contract size, quantity unit, bước khối lượng và quote
currency từ metadata đã xác nhận. `lots`: units=quantity*contract_size;
`units`: contract_size phải bằng 1. Khối lượng phải đúng bước tăng.

Đây là sổ tài khoản ký quỹ giả lập dự trữ 100% notional lúc vào, không đòn bẩy.
Không phải sổ mua/bán tài sản spot. Entry không trừ notional khỏi balance;
notional được ghi là `reserved_capital`, cố định đến khi đóng.

- P/L trước commission = direction*(exit-entry)*units*FX tại thời điểm thoát.
  Con số này đã bao gồm ảnh hưởng spread/slippage trong giá khớp.
- Commission trừ ngay mỗi lần khớp; net P/L trừ cả hai commission.
- Balance = vốn đầu + P/L đã chốt - commission đã trả (kể cả phí vị thế mở).
- Unrealized P/L dùng giá đóng phía thanh lý và FX tại cuối nến, chưa tính
  commission/slippage thoát giả định. Equity=balance+unrealized P/L.
- Free capital=equity-reserved capital; realized P/L của state=balance-vốn đầu.
- Thiếu vốn cho notional+phí mở: từ chối mà không thu phí.
- Không có margin call/stop-out. Short hoặc gap lớn có thể tạo equity/balance âm;
  engine ghi event `insolvent` và cảnh báo log, không tự xóa lỗ hoặc bù tiền.

FX là số đơn vị account currency cho một đơn vị quote currency. Cùng đồng tiền
dùng 1. Khác đồng tiền bắt buộc truyền Series tỷ giá dương, hữu hạn, index UTC
tăng và duy nhất. Index là thời điểm tỷ giá **đã được công bố và có thể sử dụng**.
Lấy giá mới nhất không muộn hơn sự kiện, không nội suy hoặc lấy dữ liệu tương lai.
Thoát intrabar dùng tỷ giá đã biết tại đầu nến do không biết thời điểm chạm.
Chưa giới hạn tuổi tỷ giá; người gọi chịu trách nhiệm về độ mới và nguồn tỷ giá.

## Ví dụ API

```python
from core.cost_model import CostModel
from core.engine import BacktestEngine

# metadata, data and strategy are supplied by the caller.
engine = BacktestEngine(
    metadata,
    CostModel(spread=0.0002, slippage=0.00001, commission_per_quantity=3.5),
    initial_capital=10000,
    account_currency="USD",
    quantity=0.01,
)
result = engine.run(data, strategy)  # Simple intraday gap checks, no calendar.
# Optional strict calendar check with an independently verified schedule:
# result = engine.run(data, strategy, expected_timestamps=confirmed_schedule)
```

Giá trị ví dụ là giả định minh họa, không phải thông số broker. Quantity phải phù
hợp metadata. `BacktestResult` lưu orders, fills, trades, states, events, vị thế
còn mở và snapshot giả định; không ghi dữ liệu hoặc ghi đè báo cáo.

## Kiểm chứng tính tay

Fixture có contract_size=10, quantity=1 lot, giá Mid mở nến vào=102 và nến
thoát=110. Spread=2, slippage=0.1 và commission=3 mỗi phía:

- BUY=102+1+0.1=103.1; EXIT=110-1-0.1=108.9.
- P/L trước commission=(108.9-103.1)*10=58; net=58-3-3=52.
- Vốn 10000 thành balance/equity 10052 sau đóng.

Bộ test còn kiểm tra long/short, gap, SL/TP cùng chạm, Bid/Ask, tỷ giá,
không khớp cuối mẫu, thiếu vốn, thời điểm khớp và tính tái lập.

`Fill` từ chối giá/quantity không dương, chi phí âm/không hữu hạn, hướng sai,
timestamp thiếu UTC và timing không hỗ trợ. Portfolio kiểm tra ID/thời gian
lệnh vào, hướng/quantity và thời gian thoát không trước lần vào.

Lưu Parquet ghi vào file tạm cùng thư mục, flush/fsync, rồi công bố bằng hard
link không ghi đè. Lỗi ghi hoặc công bố dọn file tạm và không để lại file đích
dở dang. Filesystem phải hỗ trợ hard link; nếu không, thao tác báo lỗi thay vì
hạ xuống ghi trực tiếp không an toàn. Không bảo đảm dọn file tạm nếu tiến trình
bị kill hoặc mất điện giữa lúc ghi.

### Benchmark tổng hợp sau rà soát

Chạy `benchmark_engine.py --sizes 2000 10000 --repeats 3`, đo toàn run với cùng
tín hiệu so close với SMA20. So sánh kết quả đầy đủ của hai cách cập nhật trước
khi báo tốc độ. Python 3.15.2, pandas 3.1.1, NumPy 2.5.5, Windows 10:

| Số nến | Toàn prefix, trung vị (s) | Gia tăng, trung vị (s) | Tỷ lệ |
|---|---:|---:|---:|
| 2.000 | 0,9761 | 0,5048 | 1,93 lần |
| 10.000 | 5,4972 | 2,5152 | 2,19 lần |

Đây là số đo dữ liệu tổng hợp, không phải backtest lịch sử dài hạn hoặc bảo đảm
tốc độ của chiến lược khác. Hai đường dùng chung engine sau rà soát; đường
toàn prefix giữ cách tính tín hiệu trước đây, không phải benchmark binary cũ.
API không tự tối ưu chiến lược cũ; muốn hưởng lợi cần triển khai state gia tăng.

Chạy bằng PowerShell tại thư mục dự án:

```powershell
& 'c:/Users/Admin/Documents/quant_backtest_system/.venv/Scripts/python.exe' -m pytest -q
```
````
<!-- SOURCE_END core/BACKTEST_ENGINE.md -->

## File gốc: `core/__init__.py`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\core\__init__.py`

Số dòng: 0; kích thước: 0 bytes; SHA256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

<!-- SOURCE_BEGIN core/__init__.py -->
```python
```
<!-- SOURCE_END core/__init__.py -->
