import pandas as pd
import polars as pl
import polars.testing
import pytest

from reactable._tbl_data import subset_frame, SimpleFrame, SimpleColumn

params_frames = [pytest.param(pd.DataFrame, id="pandas"), pytest.param(pl.DataFrame, id="polars")]
params_series = [pytest.param(pd.Series, id="pandas"), pytest.param(pl.Series, id="polars")]


@pytest.fixture(params=params_frames, scope="function")
def df(request) -> pd.DataFrame:
    return request.param({"col1": [1, 2, 3], "col2": ["a", "b", "c"], "col3": [4.0, 5.0, 6.0]})


@pytest.fixture(params=params_series, scope="function")
def ser(request):
    return request.param([1.0, 2.0, None])


def assert_frame_equal(src, target, include_index=True):
    if isinstance(src, pd.DataFrame):
        if not include_index:
            src = src.reset_index(drop=True)
            target = target.reset_index(drop=True)
        pd.testing.assert_frame_equal(src, target)
    elif isinstance(src, pl.DataFrame):
        pl.testing.assert_frame_equal(src, target)
    else:
        raise NotImplementedError(f"Unsupported data type: {type(src)}")


def test_subset_frame(df):
    res = subset_frame(df, rows=[0, 2], cols=["col1", "col3"])
    assert_frame_equal(
        res,
        df.__class__({"col1": [1, 3], "col3": [4.0, 6.0]}),
        include_index=False,
    )
