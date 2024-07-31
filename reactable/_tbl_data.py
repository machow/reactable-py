from __future__ import annotations

import polars as pl

from datetime import datetime, date, time
from functools import singledispatch
from typing import Union, Literal
from typing_extensions import TypeAlias

from .simpleframe import SimpleColumn
from polars import Series as PlSeries

ColumnLike: TypeAlias = Union[PlSeries, SimpleColumn]

WidgetColTypes: TypeAlias = 'None | Literal["numeric", "Date", "character", "factor", "logical"]'


@singledispatch
def col_type(x: ColumnLike) -> WidgetColTypes:
    raise TypeError(f"Unsupported type: {type(x)}")


@col_type.register(PlSeries)
def _(x: PlSeries) -> WidgetColTypes:
    dtype = x.dtype
    if dtype.is_numeric():
        return "numeric"
    elif dtype.is_temporal():
        # TODO: this might be wrong for durations, etc..
        return "Date"
    elif dtype.is_(pl.String):
        return "character"
    elif dtype.is_(pl.Boolean):
        return "logical"
    elif dtype.is_(pl.Categorical):
        return "factor"

    return "UNKNOWN"


@col_type.register(list)
@col_type.register(SimpleColumn)
def _(x: SimpleColumn | list) -> WidgetColTypes:
    # TODO: this column is just a wrapper around lists, so need to infer type from that
    dtype = _peek_type(x)

    if dtype is int or dtype is float:
        return "numeric"
    elif dtype is str:
        return "character"
    elif dtype is bool:
        return "logical"
    elif dtype in {datetime, date, time}:
        return "Date"
    else:
        return "UNKNOWN"


def _peek_type(col: SimpleColumn | list):
    types = {type(x) for x in col[:5] if x is not None}

    if not types:
        types = {type(x) for x in col[5:] if x is not None}

    if len(types) == 1:
        return list(types)[0]

    return None
