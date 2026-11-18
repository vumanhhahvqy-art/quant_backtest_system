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
