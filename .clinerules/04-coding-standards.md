
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
