"""Finite-sample prefix checks for indicator and feature builders."""

from collections.abc import Callable, Iterable

import pandas as pd


def check_prefix_invariance(
    builder: Callable[[pd.DataFrame], pd.Series | pd.DataFrame],
    data: pd.DataFrame,
    *,
    cutoffs: Iterable[int] | None = None,
) -> None:
    """Raise ValueError when a feature revises past output after seeing future rows.

    The builder must be deterministic and pure. Recompute features from raw
    inputs, rather than slicing already computed feature columns. Passing this
    check is evidence on supplied samples, not a proof for arbitrary inputs.
    By default every nonempty proper prefix is checked; use small fixtures.
    """
    def calculate(frame):
        result = builder(frame.copy(deep=True))
        if not isinstance(result, (pd.Series, pd.DataFrame)) or not result.index.equals(frame.index):
            raise ValueError("Feature builder must preserve its input index.")
        return result

    complete = calculate(data)
    for cutoff in range(1, len(data)) if cutoffs is None else cutoffs:
        if isinstance(cutoff, bool) or not isinstance(cutoff, int) or not 1 <= cutoff < len(data):
            raise ValueError("Causality cutoffs must be integers inside the sample.")
        prefix = calculate(data.iloc[:cutoff])
        try:
            if isinstance(complete, pd.DataFrame) and isinstance(prefix, pd.DataFrame):
                pd.testing.assert_frame_equal(complete.iloc[:cutoff], prefix)
            elif isinstance(complete, pd.Series) and isinstance(prefix, pd.Series):
                pd.testing.assert_series_equal(complete.iloc[:cutoff], prefix)
            else:
                raise ValueError("Feature builder changed output type.")
        except AssertionError as exc:
            raise ValueError(f"Future-dependent feature detected at prefix length {cutoff}.") from exc