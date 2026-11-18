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