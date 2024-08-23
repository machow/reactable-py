from __future__ import annotations

from .simpleframe import SimpleFrame, SimpleColumn

from datetime import datetime, date, time
from functools import singledispatch
from typing import TYPE_CHECKING, Any, Union, Literal, Optional
from typing_extensions import TypeAlias

from abc import ABC


if TYPE_CHECKING:
    from polars import DataFrame as PlDataFrame, Series as PlSeries
    from pandas import DataFrame as PdDataFrame, Series as PdSeries

else:
    from databackend import AbstractBackend

    class PlDataFrame(AbstractBackend):
        _backends = [("polars", "DataFrame")]

    class PdDataFrame(AbstractBackend):
        _backends = [("pandas", "DataFrame")]

    class PlSeries(AbstractBackend):
        _backends = [("polars", "Series")]

    class PdSeries(AbstractBackend):
        _backends = [("pandas", "Series")]

    class DataFrameLike(ABC):
        """Represent a DataFrame"""

    class ColumnLike(ABC):
        """Represent a Column"""

    DataFrameLike.register(PlDataFrame)
    DataFrameLike.register(PdDataFrame)
    DataFrameLike.register(SimpleFrame)

    ColumnLike.register(PlSeries)
    ColumnLike.register(PdSeries)
    ColumnLike.register(SimpleColumn)


# col_type -------------------------------------------------------------

WidgetColTypes: TypeAlias = 'None | Literal["numeric", "Date", "character", "factor", "logical"]'


@singledispatch
def col_type(x: ColumnLike) -> WidgetColTypes:
    raise TypeError(f"Unsupported type: {type(x)}")


@col_type.register(PlSeries)
def _(x: PlSeries) -> WidgetColTypes:
    import polars as pl

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


@col_type.register(PdSeries)
def _(x: PdSeries) -> WidgetColTypes:
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


# to_dict -------------------------------------------------------------


@singledispatch
def to_dict(data: DataFrameLike) -> "dict[str, list[Any]]":
    raise TypeError(f"Unsupported type: {type(data)}")


@to_dict.register
def _(data: PlDataFrame) -> "dict[str, list[Any]]":
    return data.to_dict(as_series=False)


@to_dict.register
def _(data: PdDataFrame) -> "dict[str, list[Any]]":
    return data.to_dict(orient="list")


@to_dict.register
def _(data: SimpleFrame) -> "dict[str, list[Any]]":
    return data.to_dict()


# column_names ---------------------------------------------------------


@singledispatch
def column_names(data: DataFrameLike) -> "list[str]":
    raise TypeError(f"Unsupported type: {type(data)}")


@column_names.register
def _(data: PlDataFrame) -> "list[str]":
    return data.columns


@column_names.register
def _(data: PdDataFrame) -> "list[str]":
    # note that column names don't have to be strings in pandas
    names = list(data.columns)
    for name in names:
        if not isinstance(name, str):
            raise TypeError(
                "Column names must be strings, received:\n"
                f"\n  * type: {type(name)}"
                f"\n  * value: {name}"
            )

    return names


@column_names.register
def _(data: SimpleFrame) -> "list[str]":
    return list(data.columns)


# subset_frame --------------------------------------------------------
@singledispatch
def subset_frame(
    data: DataFrameLike, row: Optional[list[int]], column: Optional[list[str]]
) -> DataFrameLike:
    raise TypeError(f"Unsupported type: {type(data)}")


@subset_frame.register
def _(
    data: PdDataFrame, rows: Optional[list[int]] = None, cols: Optional[list[str]] = None
) -> PdDataFrame:

    cols_indx = slice(None) if cols is None else data.columns.get_indexer_for(cols)
    rows_indx = slice(None) if rows is None else rows

    return data.iloc[rows_indx, cols_indx]


@subset_frame.register
def _(
    data: PlDataFrame, rows: Optional[list[int]] = None, cols: Optional[list[str]] = None
) -> PlDataFrame:

    cols_indx = slice(None) if cols is None else cols
    rows_indx = slice(None) if rows is None else rows

    return data[rows_indx, cols_indx]
