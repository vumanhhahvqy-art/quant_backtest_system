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