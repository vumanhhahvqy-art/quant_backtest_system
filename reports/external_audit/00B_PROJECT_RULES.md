# Toàn bộ quy tắc dự án gốc

Đọc cùng chính sách gap trong 00_PROJECT_OVERVIEW.md.

## File gốc: `.clinerules/01-project.md`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\.clinerules\01-project.md`

Số dòng: 148; kích thước: 4394 bytes; SHA256: `bab5fd7c934dbafc9b5fdd01ca99decb1dee343bfb80d2adf5bfbaeeac7df7ff`.

<!-- SOURCE_BEGIN .clinerules/01-project.md -->
```markdown

# PROJECT RULES — QUANT BACKTEST SYSTEM

## 1. Project Identity

Project name: Quant Backtest System

Language: Python 3.11+

Development environment:
- Visual Studio Code
- Cline AI coding assistant
- Gemini and OpenAI models through a compatible API provider

Project purpose:
Build a modular, reproducible, and scientifically reliable
research backtesting system for historical Forex market data.

The system is for historical strategy research, simulation,
comparison, and statistical evaluation.

It is NOT a live trading execution system.

## 2. Main Objectives

The system must support:

1. Importing and validating historical Forex datasets.
2. Reusing technical indicators across different strategies.
3. Defining independent trading strategies.
4. Simulating historical orders with explicit assumptions.
5. Modeling transaction costs.
6. Calculating performance and risk metrics.
7. Comparing strategies and parameter configurations.
8. Evaluating robustness on out-of-sample data.
9. Generating reproducible research reports.

## 3. Core Principles

Priority order:

1. Data integrity and correctness.
2. Prevention of look-ahead bias.
3. Realistic and transparent simulation assumptions.
4. Reproducibility.
5. Modularity and maintainability.
6. Computational efficiency.
7. Extensibility.

Never sacrifice correctness for performance or convenience.

A strategy showing high historical profitability does not
prove that it will be profitable in the future.

## 4. Communication Language

The user communicates in Vietnamese.

Rules:

- Always communicate with the user in Vietnamese.
- Explain plans, decisions, errors, and results in Vietnamese.
- Use English for Python identifiers, filenames, and APIs.
- Write code comments and docstrings in clear English.
- Explain complicated technical terms in Vietnamese.
- Keep explanations understandable to a user who may not
  be an experienced software developer.
- When appropriate, explain where to find or edit files
  in Visual Studio Code.

## 5. Task Execution Workflow

For each user request:

1. Identify the specific objective.
2. Inspect the relevant existing files.
3. Reuse existing modules whenever possible.
4. Briefly explain the proposed implementation in Vietnamese.
5. Identify which files need modification.
6. Implement only the requested functionality.
7. Run relevant available tests.
8. Report the outcome in Vietnamese.

For substantial architectural changes, present the proposed
change and request approval before implementation.

For small, clearly scoped tasks, proceed directly.

Do not unnecessarily ask questions when the existing project
already provides sufficient information.

## 6. Scope Control

Do not:

- Rewrite unrelated modules.
- Rename existing files without a clear reason.
- Replace working implementations unnecessarily.
- Introduce large dependencies without justification.
- Create duplicate implementations of existing indicators.
- Change strategy rules without informing the user.
- Silently change default parameters.
- Delete historical data or previous research results.
- Add live trading, broker access, or order submission.

Keep each task focused on one clear objective.

## 7. Decision Making

When multiple implementations are possible:

1. Prefer the simplest reliable solution.
2. Explain meaningful trade-offs.
3. Follow existing project conventions.
4. Choose well-established scientific and software methods.
5. Make assumptions explicit.

Never fabricate:
- Test results.
- Backtest results.
- Data sources.
- Performance statistics.
- Successful execution claims.

## 8. Research Integrity

Always distinguish:

- Historical observations.
- Simulation assumptions.
- In-sample optimization results.
- Out-of-sample evaluation results.
- Unverified hypotheses.

Do not claim that a strategy has a proven edge solely
because it performs well on historical data.

## 9. Final Response Format

After completing a coding task, report in Vietnamese:

1. What was implemented.
2. Which files were created or modified.
3. What tests were executed and their outcomes.
4. Any remaining limitations or assumptions.
5. The next recommended development step, if relevant.

Be concise but sufficiently detailed for verification.
```
<!-- SOURCE_END .clinerules/01-project.md -->

## File gốc: `.clinerules/02-architecture.md`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\.clinerules\02-architecture.md`

Số dòng: 379; kích thước: 8448 bytes; SHA256: `661c1dabf0208252c754728ea662a541453c4eda95ca3e1951aeabb2545ef5e8`.

<!-- SOURCE_BEGIN .clinerules/02-architecture.md -->
```markdown

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
```
<!-- SOURCE_END .clinerules/02-architecture.md -->

## File gốc: `.clinerules/03-backtest-rules.md`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\.clinerules\03-backtest-rules.md`

Số dòng: 378; kích thước: 9474 bytes; SHA256: `05b47622a0f36bf43e937e53c1cadbd5d8c69e7f8fd3441e32e7fe3adff050b0`.

<!-- SOURCE_BEGIN .clinerules/03-backtest-rules.md -->
```markdown

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
```
<!-- SOURCE_END .clinerules/03-backtest-rules.md -->

## File gốc: `.clinerules/04-coding-standards.md`

Đường dẫn tuyệt đối: `C:\Users\Admin\Documents\quant_backtest_system\.clinerules\04-coding-standards.md`

Số dòng: 354; kích thước: 8057 bytes; SHA256: `abbb028656ba48d3cd76c260c90292d02e19dc0ef49a07a78796cef19c76e586`.

<!-- SOURCE_BEGIN .clinerules/04-coding-standards.md -->
```markdown

# CODING STANDARDS — QUANT BACKTEST SYSTEM

## 1. General Coding Principles

Write clean, readable, maintainable Python code.

Prefer:
- Simple functions.
- Clear module boundaries.
- Explicit inputs and outputs.
- Descriptive variable names.
- Type hints.
- Small, independently testable components.

Avoid:
- Unnecessary abstraction.
- Excessive inheritance.
- Hidden global state.
- Circular imports.
- Duplicate logic.
- Unexplained magic numbers.
- Broad exception suppression.

Correctness is more important than clever code.

## 2. Python Environment

Target Python version: 3.11 or newer.

Use a project-specific virtual environment.

Manage dependencies using pyproject.toml.

Prefer established libraries when justified.

Potential libraries include:
- pandas
- numpy
- scipy
- PyYAML
- pytest
- matplotlib
- pyarrow

Install only what the current implementation needs.

Do not introduce a major backtesting framework
without explaining the architectural implications.

## 3. Formatting and Naming

Follow PEP 8 conventions.

Use:
- snake_case for functions and variables.
- PascalCase for classes.
- UPPER_CASE for constants.
- Descriptive Python module names.

Prefer explicit names such as:
- entry_price
- exit_price
- position_size
- spread_cost
- realized_pnl

Avoid ambiguous names unless the meaning
is obvious from the local context.

## 4. Function Design

Each function should have one clear purpose.

Prefer pure functions when possible.

Functions should:
- Validate important assumptions.
- Use consistent units.
- Return predictable data types.
- Avoid unnecessary side effects.
- Handle edge cases explicitly.

Do not silently mutate input DataFrames.

Use copies only when needed; document intentional
in-place operations.

## 5. Type Hints and Documentation

Use Python type hints for public interfaces.

Write concise docstrings for:
- Public functions.
- Public classes.
- Complex calculations.
- Non-obvious algorithms.

For financial calculations, document:
- Input units.
- Output units.
- Formula conventions.
- Relevant assumptions.
- Exceptional conditions.

## 6. Shared Indicator Implementations

Before implementing an indicator:

1. Search indicators/ for an existing implementation.
2. Reuse existing code if correct and compatible.
3. Check parameter definitions.
4. Confirm warm-up behavior.
5. Verify timestamp alignment.
6. Add unit tests.

Never create separate versions of the same
indicator without a justified reason.

If variants are required, name and document
them explicitly.

## 7. DataFrame and Array Handling

Preserve chronological order.

Avoid chained assignment.

Avoid unintended index resets.

Document whether a function expects:
- A pandas Series.
- A pandas DataFrame.
- A NumPy array.

Check input and output lengths.

Avoid converting timestamp-indexed data into
unlabeled arrays when alignment matters.

Do not fill indicator warm-up NaNs with arbitrary
values merely to force signal generation.

## 8. Error Handling

Use clear, actionable error messages.

Raise appropriate exceptions for:
- Missing required columns.
- Invalid configurations.
- Unsupported symbols.
- Invalid timestamps.
- Invalid numeric inputs.
- Unsupported order types.
- Missing instrument specifications.

Do not use bare except clauses.

Do not suppress exceptions without an explicit,
documented reason.

Do not continue with invalid financial calculations.

## 9. Configuration Management

Load experimental parameters from configs/.

Validate configuration values before execution.

Avoid hardcoding:
- Strategy parameters.
- Initial capital.
- Commission rates.
- Spread assumptions.
- Slippage assumptions.
- Symbol specifications.
- Dataset paths.

When defaults are used, make them explicit.

Never change defaults silently.

## 10. Testing Standards

Use pytest for automated testing.

Add tests for new important calculation logic.

Tests should include:
- Normal cases.
- Boundary cases.
- Invalid inputs.
- Timestamp alignment.
- Numeric correctness.
- Regression cases.

Use small synthetic datasets with manually
verifiable expected results.

Prefer deterministic tests.

Do not rely exclusively on comparing two
implementations that may share the same bug.

## 11. Regression Protection

Before modifying existing behavior:

1. Inspect the current implementation.
2. Identify relevant tests.
3. Understand affected interfaces.
4. Implement the smallest safe change.
5. Run relevant tests.
6. Report behavior changes.

Do not rewrite an entire working module to
fix a small isolated issue.

## 12. Performance Optimization

First implement correct and testable logic.

Optimize only after identifying bottlenecks.

Prefer vectorized calculations for indicators
when they preserve temporal correctness.

Event-driven simulation is acceptable for
order execution and portfolio state changes.

Never use vectorization that leaks future data.

Benchmark meaningful optimizations.

Do not claim performance improvements without
measurements.

## 13. Logging

Use Python logging for operational diagnostics.

Prefer structured, informative log messages.

Log important events such as:
- Dataset loading.
- Validation failures.
- Configuration selection.
- Simulation start and finish.
- Execution assumptions.
- Run identifiers.
- Unexpected conditions.

Avoid excessive per-candle logging by default.

Never log API keys or credentials.

## 14. File and Data Safety

Do not overwrite data/raw/ files.

Do not delete research reports without explicit
user authorization.

Do not overwrite earlier run results by default.

Use .gitignore for:
- Virtual environments.
- Python caches.
- Temporary files.
- Secrets.
- Large generated datasets when appropriate.

Never commit credentials or API keys.

Do not store secrets in .clinerules/ or README.md.

## 15. AI Coding Workflow

For each coding request:

1. Read relevant existing code.
2. Identify reusable components.
3. Check applicable project rules.
4. Make a concise implementation plan.
5. Modify only necessary files.
6. Add or update relevant tests.
7. Execute tests when the environment permits.
8. Summarize the result in Vietnamese.

Do not repeatedly read unrelated large datasets
unless the task requires it.

Use small data samples for development and tests.

Do not perform expensive full-history backtests
unless requested or needed for validation.

## 16. Dependency and Security Rules

Do not execute arbitrary external scripts
without reviewing their purpose.

Avoid unnecessary network access.

Never send secrets or full private datasets
to external services without authorization.

Do not modify API configuration or credentials
unless specifically requested.

Do not print secret environment variables.

## 17. Change Management

For substantial changes, explain:
- Files to be modified.
- Expected behavior changes.
- Compatibility implications.
- Required tests.

For minor tasks, avoid unnecessary overhead.

Preserve backward compatibility where practical.

When breaking changes are necessary,
document them explicitly.

## 18. Final Verification

Before declaring a coding task complete:

- Check syntax and imports.
- Run relevant available tests.
- Check affected interfaces.
- Review time alignment where relevant.
- Confirm no raw data was modified.
- Confirm no secrets were exposed.
- Report unresolved warnings.

Never claim a test passed unless it was run.

If a test cannot be executed, state why.

## 19. Response Language

All user-facing explanations must be in Vietnamese.

Keep source code identifiers in English.

When reporting results, clearly distinguish:
- Implemented and tested.
- Implemented but not tested.
- Not implemented.
- Known limitations.
```
<!-- SOURCE_END .clinerules/04-coding-standards.md -->
