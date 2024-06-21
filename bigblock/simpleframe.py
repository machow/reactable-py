from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Any, Generic, overload
from typing_extensions import TypeAlias, TypeVar, Self
from pathlib import Path

T = TypeVar("T")

RowValIndex: TypeAlias = int
RowSliceIndex: TypeAlias = "list[int] | slice"
ColValIndex: TypeAlias = str
ColSliceIndex: TypeAlias = "list[str] | slice"

RowIndex: TypeAlias = "RowValIndex | RowSliceIndex"
ColIndex: TypeAlias = "ColValIndex | ColSliceIndex"


def _maybe_getitem(x, ii, default):
    try:
        return x[ii]
    except IndexError:
        return default


def _multi_getitem(x, indx: list[Any] | slice):
    if isinstance(x, dict):
        # slice dictionary keys as the new index
        if isinstance(indx, slice):
            indx = list(x)[indx]

        return {k: x[k] for k in indx}
    elif isinstance(x, list):
        if isinstance(indx, slice):
            return x[indx]

        return [x[k] for k in indx]
    else:
        raise TypeError(f"Unsupported type: {type(x)}")


@dataclass
class SimpleColumn(Generic[T]):
    values: list[T]

    @overload
    def __get_item__(self, indx: RowValIndex) -> T: ...

    @overload
    def __get_item__(self, indx: RowSliceIndex) -> Self[T]: ...

    def __getitem__(self, indx: RowIndex) -> Self:
        if isinstance(indx, int):
            return self.values[indx]

        elif isinstance(indx, list):
            return self.__class__([self.values[ii] for ii in indx])

        elif isinstance(indx, slice):
            return self.__class__(self.values[indx])

        raise TypeError(f"Unsupported type: {type(indx)}")

    def __len__(self):
        return len(self.values)

    def _repr(self, n: int | None = None, include_name=True):
        if n is not None and len(self.values) <= n:
            repr_vals = repr(self.values)
        else:
            repr_vals = repr(list(self.values[:5]) + ["..."])

        if include_name:
            return f"{self.__class__.__name__}({repr_vals})"

        return repr_vals

    def __repr__(self):
        return self._repr(n=5)

    def to_list(self):
        return self.values


@dataclass
class SimpleFrame:
    columns: dict[str, SimpleColumn | list[Any]]

    def __post_init__(self):
        if not all(isinstance(x, SimpleColumn) for x in self.columns.values()):
            self.columns: dict[str, SimpleColumn] = self.from_dict(self.columns).columns

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.columns)})"

    def _repr_pretty_(self, p, cycle):
        name = self.__class__.__name__
        if cycle:
            p.text(f"{name}(...)")

        p.text(f"{name}(\n")
        col_reps = [
            f'"{k}": {col._repr(n=5, include_name=False)}' for k, col in self.columns.items()
        ]
        if len(col_reps):
            str_col_reps = "    " + ",\n    ".join(col_reps)
        else:
            str_col_reps = ""

        p.text("\n".join([f"{name}({{", str_col_reps, "}})"]))

    def equals(self, other: Any) -> bool:
        """Check if frame is equal to another frame.

        * Column names must be in the same order.
        * Simple list equality is used for checking columns.
        """
        if not isinstance(other, type(self)):
            return False

        src_names, dst_names = list(self.columns), list(other.columns)

        for ii, (src_name, other_name) in enumerate(zip(src_names, dst_names)):
            if src_name != other_name:
                return False

        src_data, dst_data = list(self.columns.values()), list(other.columns.values())

        for ii, (src_col, dst_col) in enumerate(zip(src_data, dst_data)):
            if src_col != dst_col:
                return False

        return True

    @classmethod
    def from_dict(cls, columns: dict[str, list[Any]]) -> Self:

        res = {}

        crnt_len = None
        for col_name, col in columns.items():
            new_len = len(col)

            if crnt_len is not None and crnt_len != new_len:
                raise ValueError(
                    f"Columns are length {crnt_len}, but `{col_name}` is length {new_len}"
                )

            crnt_len = new_len

            res[col_name] = SimpleColumn(col) if not isinstance(col, SimpleColumn) else col

        return cls(res)

    def __getitem__(self, indx: RowIndex | ColIndex):
        if isinstance(indx, tuple):
            ii: RowIndex = indx[0]
            k: ColIndex = indx[1]
        # fetch single value ----
        if isinstance(ii, int) and isinstance(k, str):
            return self._get_value(ii, k)

        # fetch columns only ----
        elif isinstance(ii, str) or (
            isinstance(ii, list) and isinstance(_maybe_getitem(ii, 0, None), str)
        ):
            return self._get_frame(slice(None), ii)

        # fetch rows and columns ----
        else:
            return self._get_frame(ii, k)

    def _get_value(self, ii: RowValIndex, k: ColValIndex) -> Any:
        return self.columns[k][ii]

    def _get_frame(self, ii: RowIndex = slice(None), k: ColIndex = slice(None)) -> Self:
        if isinstance(k, str):
            k = [k]
        if isinstance(ii, int):
            ii = [ii]

        new_cols = _multi_getitem(self.columns, k)
        subsetted = {name: col[ii] for name, col in new_cols.items()}

        return self.__class__(subsetted)

    def to_dict(self):
        return {k: v.to_list() for k, v in self.columns.items()}

    def to_pandas(self):
        import pandas as pd

        return pd.DataFrame(self.to_dict())

    def to_polars(self):
        import polars as pl

        return pl.DataFrame(self.to_dict())

    @classmethod
    def read_csv(cls, fname: str | Path):
        with open(fname) as f:
            reader = csv.reader(f)
            try:
                fieldnames = next(reader)
            except StopIteration:
                return SimpleFrame({})

            cols = zip(*reader)
            data = dict(zip(fieldnames, cols))

            return cls.from_dict(data)
