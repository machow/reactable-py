import pandas as pd
import polars as pl
import pytest

from reactable import Reactable
from reactable.simpleframe import SimpleFrame

params_frames = [
    pytest.param(pd.DataFrame, id="pandas"),
    pytest.param(pl.DataFrame, id="polars"),
    pytest.param(SimpleFrame, id="simpleframe"),
]


@pytest.fixture(params=params_frames)
def df(request):
    return request.param({"a": [1, 2], "b": ["3", "4"]})


def test_frame(df):
    d = Reactable(df)
    assert isinstance(d.data, dict)
    assert d.data["a"] == [1, 2]
    assert d.data["b"] == ["3", "4"]
