from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class JsCellInfo:
    # This tracks what I know fo the JS class CellInfo
    row: dict[str, Any]
    value: Any


@dataclass
class JsColInfo:
    """Column information."""


@dataclass
class JsFilterValue:
    """Column filter values"""

    id: str
    value: Any


@dataclass
class JsRowInfo:
    """Row information"""

    # each row dict maps column name -> value
    rows: list[dict[str, Any]]


@dataclass
class JsColumn:
    id: str
    """column ID"""

    name: str
    """Column display name"""

    filterValue: Any
    """column filter value"""

    setFilter: Callable[[Any], str | None]
    """function to set the column filter value (set to undefined to clear the filter)"""


class JsTableState:
    """Not clear what this does, but is 2nd input for cell renderers."""

    sorted: list[JsColInfo]
    """columns being sorted in the table."""

    page: int
    """page index (zero-based)."""

    pageSize: int
    """page size"""

    pages: int
    """number of pages"""

    filters: list[JsFilterValue]
    """column filter values"""

    searchValue: str

    selected: list[int]
    """selected row indices (zero-based)"""

    pageRows: JsRowInfo
    """current row data on the page"""

    sortedData: JsRowInfo
    """current row data in the table (after sorting, filtering, grouping)"""

    data: JsRowInfo
    """original row data in the table"""

    meta: dict[str, Any]
    """custom table metadata (from python client)"""

    hiddenColumns: list[str]
    """columns being hidden in the table"""
