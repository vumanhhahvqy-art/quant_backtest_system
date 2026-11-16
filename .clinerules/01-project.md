
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
