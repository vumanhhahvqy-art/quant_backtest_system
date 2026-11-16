
# ARCHITECTURE RULES — QUANT BACKTEST SYSTEM

## 1. Architectural Philosophy

Use a modular architecture with clear separation of
responsibilities.

Each module should have one primary responsibility.

Strategies must be independent of the backtest engine,
transaction cost calculations, and report generation.

Indicators must be reusable across all strategies.

Avoid circular dependencies.

## 2. Expected Project Structure

quant_backtest_system/
    .clinerules/
    configs/
    data/
        raw/
        processed/
        metadata/
    core/
        __init__.py
        data_loader.py
        data_validator.py
        engine.py
        execution.py
        cost_model.py
        portfolio.py
        metrics.py
    indicators/
        __init__.py
        trend.py
        momentum.py
        volatility.py
        price_action.py
    strategies/
        __init__.py
        base_strategy.py
        trend_following.py
        mean_reversion.py
    validation/
        __init__.py
        walk_forward.py
        sensitivity.py
    tests/
    notebooks/
    reports/
        runs/
    run_backtest.py
    pyproject.toml
    README.md

This structure is the target architecture.

Do not create every missing module automatically.
Implement modules incrementally when needed.

## 3. Data Layer

### core/data_loader.py

Responsibilities:
- Read supported historical data files.
- Support CSV and optionally Parquet.
- Parse timestamps and numeric columns.
- Return data in a consistent internal format.

Do not calculate indicators here.
Do not modify source files.

### core/data_validator.py

Responsibilities:
- Validate required columns.
- Validate timestamp ordering.
- Detect duplicate timestamps.
- Detect missing and invalid numeric values.
- Detect impossible OHLC relationships.
- Detect unexpected time gaps.
- Produce a data quality report.

Do not silently fill missing candles.

### data/

raw/
- Original, immutable datasets.

processed/
- Cleaned or normalized derived datasets.

metadata/
- Data source information.
- Symbol specifications.
- Timezone information.
- Dataset version and transformation history.

## 4. Indicator Layer

Location: indicators/

### trend.py

Examples:
- SMA
- EMA
- MACD
- SuperTrend

### momentum.py

Examples:
- RSI
- Stochastic
- CCI

### volatility.py

Examples:
- ATR
- Bollinger Bands

### price_action.py

Examples:
- Candlestick patterns
- Swing highs and lows
- Market structure features

Indicator rules:

- Implement each indicator in one canonical location.
- Keep indicators independent from individual strategies.
- Use explicit parameters.
- Specify calculation conventions.
- Return consistently indexed results.
- Preserve input alignment.
- Document warm-up requirements.
- Avoid look-ahead bias.
- Never overwrite source price columns unexpectedly.

Strategies must import shared indicator functions.

Do not reimplement EMA, RSI, ATR, or other shared
indicators inside strategy files.

## 5. Strategy Layer

Location: strategies/

### base_strategy.py

Define the common strategy interface.

A strategy should be able to:

- Receive validated market data.
- Receive a parameter configuration.
- Calculate or request required indicators.
- Generate time-aligned signals.
- Expose signal-related metadata.

Use a clear signal convention.

Recommended directional convention:
- 1 = long signal
- 0 = no new directional signal
- -1 = short signal

Do not interpret 0 as automatic position closure.

Position exits must be explicitly represented through
the strategy interface or separate exit instructions.

### Individual strategies

Examples:
- trend_following.py
- mean_reversion.py

Each strategy should contain:
- Strategy-specific parameters.
- Entry conditions.
- Exit conditions.
- Required indicator references.
- Optional signal explanations.

Strategies must NOT:
- Modify account balances.
- Independently calculate transaction fees.
- Directly simulate order fills.
- Write reports.
- Load files from arbitrary disk paths.
- Use future market observations.

## 6. Backtest Engine

### core/engine.py

Responsibilities:
- Coordinate the simulation lifecycle.
- Process events chronologically.
- Provide only currently available information.
- Evaluate strategy signals.
- Submit simulated order requests.
- Coordinate execution and portfolio updates.
- Record simulation events.

The engine must not contain strategy-specific
entry and exit conditions.

## 7. Execution Layer

### core/execution.py

Responsibilities:
- Simulate order fills.
- Apply order timing rules.
- Handle market orders and supported order types.
- Evaluate stop-loss and take-profit instructions.
- Apply explicit same-bar ambiguity rules.
- Record executed prices and quantities.

Order types must be implemented and tested separately.

Never silently assume that an order was filled
at the signal candle's closing price.

## 8. Transaction Cost Layer

### core/cost_model.py

Responsibilities:
- Spread treatment.
- Commission calculations.
- Slippage assumptions.
- Swap or overnight costs when supported.

Costs must be calculated in one centralized location.

Prevent duplicate charging of the same cost.

## 9. Portfolio Layer

### core/portfolio.py

Responsibilities:
- Track simulated cash and equity.
- Track open positions.
- Track realized and unrealized PnL.
- Track margin requirements when modeled.
- Track position sizes.
- Track account currency conversions.

Never allow strategy modules to modify portfolio
state directly.

## 10. Metrics Layer

### core/metrics.py

Responsibilities:
- Calculate performance statistics.
- Calculate drawdown statistics.
- Calculate risk-adjusted metrics.
- Analyze completed trades.
- Provide consistently defined results.

Metrics should operate on recorded outputs rather
than rerunning strategy logic.

## 11. Validation Layer

### validation/walk_forward.py

Perform chronological train/validation/test
procedures and walk-forward evaluations.

### validation/sensitivity.py

Measure how strategy outcomes change when
parameters or simulation assumptions vary.

Do not mix evaluation and optimization results.

## 12. Configuration Layer

Location: configs/

Use human-readable configuration files,
preferably YAML.

Configurations should define:
- Dataset reference.
- Symbol.
- Timeframe.
- Date range.
- Strategy name.
- Strategy parameters.
- Initial simulated capital.
- Account currency.
- Transaction cost assumptions.
- Execution assumptions.
- Random seed when applicable.

Do not hardcode experimental parameters across modules.

Validate configurations before running backtests.

## 13. Reports

Location: reports/runs/

Each run should have a unique identifier.

Store, where available:
- Configuration snapshot.
- Dataset reference and checksum.
- Strategy parameters.
- Software or Git revision.
- Metrics.
- Simulated trade log.
- Equity curve.
- Warnings and assumptions.

Never overwrite an earlier run by default.

## 14. Main Entry Point

### run_backtest.py

Responsibilities:
- Parse the selected configuration.
- Validate the configuration.
- Initialize required modules.
- Start the backtest.
- Save results.
- Display a concise run summary.

Keep complex business logic out of this file.

## 15. Dependency Direction

Preferred dependency flow:

Data -> Indicators -> Strategies -> Engine
                                  |
                             Execution
                                  |
                              Portfolio
                                  |
                               Metrics

Configs control initialization.

The engine coordinates components.

Validation consumes or coordinates completed
research runs without changing core calculations.

Avoid circular imports and hidden global state.

## 16. Future Extensibility

Design interfaces to allow future support for:
- Additional currency pairs.
- Gold and other market datasets.
- Multiple timeframes.
- Alternative execution models.
- Additional cost models.
- Portfolio-level research.

Do not implement speculative features prematurely.
