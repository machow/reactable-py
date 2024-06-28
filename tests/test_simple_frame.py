import pytest
from react_tables.simpleframe import SimpleFrame, SimpleColumn

data = SimpleFrame({"x": [1, 2], "y": ["a", "b"]})


@pytest.mark.parametrize(
    "ii, k, dst",
    [
        (0, "x", 1),
        (0, slice(None), SimpleFrame({"x": [1], "y": ["a"]})),
        (0, ["x", "y"], SimpleFrame({"x": [1], "y": ["a"]})),
        ([0], ["x", "y"], SimpleFrame({"x": [1], "y": ["a"]})),
        (slice(None), ["x"], SimpleFrame({"x": [1, 2]})),
        ([0, 1], ["x"], SimpleFrame({"x": [1, 2]})),
    ],
)
def test_getitem(ii, k, dst):
    res = data[ii, k]
    if isinstance(dst, SimpleFrame):
        assert isinstance(res, SimpleFrame)

        assert res.equals(dst)
