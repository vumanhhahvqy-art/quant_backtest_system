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