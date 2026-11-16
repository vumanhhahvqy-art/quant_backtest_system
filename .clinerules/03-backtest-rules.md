
# BACKTEST INTEGRITY RULES — FOREX RESEARCH

## 1. Fundamental Principle

Backtest correctness is more important than
historical profitability.

Never modify simulation assumptions merely to
improve reported performance.

Every simulated trade must be explainable using
information available at the time of the decision.

## 2. Historical Data Integrity

Treat raw datasets as immutable.

Never:
- Overwrite raw market data.
- Invent missing candles.
- Silently remove unfavorable market periods.
- Mix incompatible price sources without documenting it.
- Assume all datasets use the same timezone.

Validate:
- Required columns.
- Timestamp format.
- Timestamp uniqueness.
- Chronological order.
- Price numeric types.
- OHLC consistency.
- Missing observations.
- Unexpected gaps.
- Source metadata.

A valid OHLC candle must satisfy:

High >= max(Open, Close)
Low <= min(Open, Close)
High >= Low

Prices must also satisfy applicable positivity
and finiteness requirements.

Do not assume every calendar gap is an error.
Forex markets have weekends and trading holidays.

Report gaps using the expected trading calendar.

## 3. Time Handling

Use timezone-aware UTC timestamps internally.

Document the source timezone.

Convert session times explicitly.

Handle daylight saving time when local
market-session definitions require it.

Never assume broker server time equals UTC.

Specify whether each candle timestamp represents
the candle opening or candle closing time.

## 4. Look-Ahead Bias Prevention

Historical decisions must never use future data.

Prohibited patterns include:
- Using future candles to generate earlier signals.
- Using centered rolling indicators for live-time signals.
- Using future-confirmed swing points immediately.
- Fitting scalers on the complete dataset before splitting.
- Selecting parameters using the final test dataset.
- Accessing the current candle's final High or Low
  before that candle is complete.

If a signal is generated after candle close,
execute it according to the configured order timing.

Default research convention:
- Evaluate signals after a candle closes.
- Submit eligible market orders for the next candle.
- Apply the selected execution price and cost model.

Do not assume signal-close fills unless a separate
validated execution model explicitly supports them.

## 5. Indicator Timing

Every indicator must specify:
- Required input columns.
- Parameter definitions.
- Warm-up requirements.
- NaN handling.
- Signal availability time.

Indicators must preserve timestamp alignment.

Future-confirmed events must become available
only after their confirmation conditions are met.

Example:
A swing high requiring two later candles
cannot be known at the swing candle itself.

## 6. Forex Price Representation

Support explicit price representations such as:
- Mid
- Bid
- Ask

Never assume an OHLC dataset represents Bid,
Ask, or Mid unless verified through metadata.

If only one price series is available,
spread simulation assumptions must be documented.

For explicit Bid/Ask data:
- Long entries normally execute at Ask.
- Long exits normally execute at Bid.
- Short entries normally execute at Bid.
- Short exits normally execute at Ask.

Use the executable price side for order triggering
and filling according to the selected order model.

Do not subtract spread again when it is already
represented by execution on separate Bid/Ask prices.

## 7. Pip, Tick, and Symbol Specifications

Do not hardcode a universal pip size.

Obtain symbol specifications from metadata.

Specifications may include:
- Tick size.
- Pip size.
- Contract size.
- Quantity unit.
- Lot size.
- Quote currency.
- Account currency.
- Minimum quantity increment.

Do not assume JPY pairs, non-JPY pairs, and gold
share identical pip or contract conventions.

Use consistent units throughout calculations.

## 8. Transaction Costs

Explicitly model supported transaction costs:

- Spread.
- Commission.
- Slippage.
- Swap or overnight financing.

Each cost must:
- Have clearly defined units.
- Have a documented calculation method.
- Be applied at the correct event.
- Be recorded in the trade log when applicable.

Distinguish costs per order, per side,
per round trip, per lot, and per notional value.

Do not double-count costs.

When cost information is unavailable,
label the assumptions as hypothetical.

## 9. Order Execution

Define the supported order types explicitly.

Do not treat all orders as market orders.

For every supported order type, document:
- Submission timing.
- Trigger conditions.
- Fill conditions.
- Price selection.
- Cost treatment.
- Cancellation behavior.

An order cannot be filled before it exists.

Do not assume the exact requested price is
always executable.

Execution models must be deterministic unless
stochastic behavior is explicitly configured.

## 10. Stop-Loss and Take-Profit

SL and TP must follow explicit execution rules.

If both SL and TP are touched within the same
OHLC candle and the true sequence is unknown:

- Never automatically choose the profitable outcome.
- Use an explicitly selected conservative model,
  an ambiguity flag, or finer-granularity data.
- Record which policy was applied.

Do not claim that OHLC data reveals the exact
intrabar sequence.

Price gaps must be handled according to the
configured execution assumptions.

## 11. Position and Portfolio Accounting

Clearly distinguish:
- Cash balance.
- Unrealized PnL.
- Realized PnL.
- Equity.
- Margin requirements.
- Free margin when modeled.

Position quantities must have explicit units.

Calculate PnL consistently using:
- Trade direction.
- Entry price.
- Exit price.
- Position size.
- Contract specifications.
- Currency conversion.
- Applicable transaction costs.

Never assume all trading instruments generate
PnL directly in the account currency.

Do not silently permit unsupported leverage,
negative cash, or invalid positions.

## 12. Multi-Timeframe Research

When combining timeframes:

- Use only completed higher-timeframe candles.
- Align lower-timeframe observations chronologically.
- Prevent higher-timeframe future leakage.
- Avoid using incomplete higher-timeframe values
  as if they were final.

Never use a completed H1 candle during an M5
decision that occurred before that H1 candle closed.

## 13. Backtest Metrics

Calculate metrics using documented definitions.

Recommended metrics:
- Net PnL.
- Total return.
- Number of trades.
- Win rate.
- Profit factor.
- Average trade PnL.
- Maximum drawdown.
- Expectancy.
- Sharpe ratio.
- Sortino ratio.
- Recovery factor.

Document:
- Whether returns are gross or net of costs.
- Whether drawdown is measured on equity or balance.
- Sampling frequency.
- Annualization assumptions.
- Risk-free rate assumptions.
- Treatment of open positions.

Handle zero denominators and undefined metrics
without producing misleading values.

Do not automatically replace undefined metrics
with zero.

## 14. Research Validation

Separate:
- In-sample development data.
- Validation data.
- Final out-of-sample test data.

Use chronological splits.

Never randomly shuffle time-series observations
for ordinary backtest evaluation.

The final test period must not influence
parameter selection.

Walk-forward evaluation should refit or reselect
parameters using only information available
before each evaluation window.

Clearly distinguish exploratory results from
untouched out-of-sample results.

## 15. Overfitting Prevention

Do not select strategies based exclusively
on maximum historical return.

Evaluate:
- Parameter sensitivity.
- Transaction cost sensitivity.
- Performance across time periods.
- Performance across market conditions.
- Out-of-sample stability.
- Sample size and trade count.

Report signs of overfitting.

Do not imply that robust historical performance
guarantees future results.

## 16. Reproducibility

Each research run should record:

- Dataset identity.
- Data checksum when available.
- Source and timezone.
- Date range.
- Instrument specifications.
- Strategy name and version.
- Strategy parameters.
- Execution assumptions.
- Cost assumptions.
- Initial simulated capital.
- Account currency.
- Software version.
- Random seed when relevant.

The same deterministic inputs should reproduce
the same outputs.

## 17. Mandatory Integrity Tests

Add or maintain automated tests for:

1. Indicator timestamp alignment.
2. No future-data access.
3. Signal-to-execution timing.
4. Bid/Ask execution conventions.
5. Spread and commission accounting.
6. Stop-loss and take-profit ambiguity.
7. Position PnL calculations.
8. Multi-timeframe synchronization.
9. Missing or duplicate candle detection.
10. Deterministic result reproduction.

When a feature cannot be modeled reliably,
report the limitation rather than inventing
a plausible-looking implementation.

## 18. Research Safety

The system is limited to historical simulation.

Do not implement live broker connections,
real-money order submission, or automatic
execution of trading decisions.

Research outputs are hypothetical and must
be labeled accordingly.
