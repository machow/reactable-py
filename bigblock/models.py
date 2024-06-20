from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Callable
from typing_extensions import TypeAlias

from dataclasses import asdict, dataclass, field, fields, replace, InitVar

from polars import DataFrame as PlDataFrame


# Utils ----
def rename(d: dict[str, Any], **to_from: str) -> dict[str, Any]:
    from_to = {v: k for v, k in to_from.items()}

    return {from_to.get(k, k): v for k, v in d.items()}


def filter_none(d: dict[str, Any]):
    return {k: v for k, v in d.items() if v is not None}


def process_data(d: PlDataFrame) -> dict[str, list[Any]]:
    return d.to_dict(as_series=False)


def default_columns(d: PlDataFrame | dict[str, Any]) -> list[Column]:
    if isinstance(d, dict):
        return [Column(name=k, id=k) for k in d]

    out = []
    for ser in d:
        col = Column(
            name=ser.name,
            id=ser.name,
        )
        out.append(col.to_props())
    return out


# Misc field types ----
HTML: TypeAlias = str
CssRules: TypeAlias = dict[str, "CssStyles"]
CssStyles: TypeAlias = dict[str, str]
CellRenderer: TypeAlias = Callable[["CellInfo"], str]
StrIsoCurrency: TypeAlias = str


JsFunction: TypeAlias = str
JsFunctionCell: TypeAlias = str
"""A javascript function that takes cell info, and table state."""

JsFunctionCol: TypeAlias = str
"""A javascript function that takes column info, and table state."""

JsFunctionRow: TypeAlias = str
"""A javascript function that takes row info, and table state."""


# Misc data classes ----


@dataclass
class TableInfo:
    """TODO"""


@dataclass
class HeaderCellInfo:
    value: Any
    name: str | None = None


@dataclass
class CellInfo:
    value: Any
    row_index: Any
    column_name: Any


@dataclass
class RowInfo:
    row_index: int
    column_name: str


@dataclass
class ColInfo:
    values: list[Any]
    name: str


# Props ----


@dataclass
class Props:
    data: dict[str, list[Any]] | PlDataFrame
    columns: list[Column] | None = None
    columnGroups: list[ColGroup] | None = None
    sortable: bool = True
    defaultColDef: InitVar[Column | None] = None
    defaultSortOrder: InitVar[Literal["asc", "desc"]] = "asc"
    defaultSorted: list[str] | None = None
    showSortIcon: bool | None = None
    showSortable: bool | None = None
    filterable: bool | None = None
    resizable: bool | None = None
    theme: Theme | None = None
    language: str | None = None
    dataKey: str | None = None

    # ...rest ----
    bordered: bool = False
    highlight: bool = False
    minRows: int | None = None
    defaultPageSize: int | None = None

    # derived props ----
    defaultSortDesc: bool = field(init=False)
    # groupBy: list[str] | None = None
    # rownames: bool = True
    # defaults: Defaults

    def __post_init__(
        self,
        defaultColDef,
        defaultSortOrder: Literal["asc", "desc"],
    ):
        # data ----
        if isinstance(self.data, PlDataFrame):
            self.data = process_data(self.data)

        # columns ----

        if self.columns is None:
            # TODO: for names in data, but not in columns,
            # make the default
            self.columns = default_columns(self.data)
        else:
            self.columns = self.complete_columns(self.data, defaultColDef, self.columns)

        self.validate_columns()

        self.defaultSorted = self.derive_default_sorted(defaultSortOrder)

        # derived ----
        self.defaultSortDesc = defaultSortOrder == "desc"

    @staticmethod
    def complete_columns(
        data: dict[str, Any], default: Column | None, columns: list[Column]
    ) -> list[Column]:
        if default is None:
            default = Column()
        crnt_cols = []
        col_def_map = {col.id: col for col in columns}
        for col_name in data:
            if col_name in col_def_map:
                crnt_cols.append(col_def_map[col_name])
            else:
                crnt_cols.append(replace(default, id=col_name))

        return crnt_cols

    def derive_default_sorted(self, defaultSortOrder: Literal["asc", "desc"]):
        if self.defaultSorted is None:
            return

        out = []
        for col in self.columns:
            if col.id in self.defaultSorted:
                out.append(
                    dict(
                        id=col.id,
                        desc=(col.defaultSortOrder or defaultSortOrder) == "desc",
                    )
                )

        return out

    def validate_columns(self):
        for col in self.columns:
            if col.id not in self.data:
                raise ValueError(f"Column id '{col.id}' is not a column name in the data.")

    def to_props(self):
        props_list = ["columns"]
        out = {}
        for field in fields(self):
            attr = getattr(self, field.name)
            f_props = getattr(attr, "to_props", None)
            res = f_props() if f_props is not None else attr

            if field.name in props_list:
                res = [x.to_props() for x in res]

            out[field.name] = res

        return filter_none(out)


class Defaults:
    colDef: None = None
    colGroup: None = None
    sortOrder: None = None
    sorted: None = None
    pageSize: None = None
    expanded: None = None
    selected: None = None

    def to_props(self):
        return filter_none(asdict(self))


@dataclass
class ColFormat:
    prefix: str | None = None
    suffix: str | None = None
    digits: int | None = None
    separators: bool | None = False
    percent: bool | None = False
    currency: StrIsoCurrency | None = None
    datetime: bool | None = False
    date: bool | None = False
    time: bool | None = False
    hour12: bool | None = None
    locales: bool | None = None

    def to_props(self):
        return filter_none(asdict(self))


@dataclass
class Column:
    id: str | None = None
    name: str | None = None
    aggregate: (
        Literal["mean", "sum", "max", "min", "median", "count", "unique", "frequency"]
        | JsFunction
        | None
    ) = None
    sortable: bool | None = None
    resizable: bool | None = None
    filterable: bool | None = None
    searchable: bool | None = None
    filterMethod: JsFunction | None = None
    show: bool | None = None
    defaultSortOrder: Literal["asc", "desc"] | None = None
    sortNALast: bool | None = None
    format: ColFormat | None = None
    cell: JsFunctionCell | CellRenderer | None = None
    grouped: JsFunctionCell | None = None
    aggregated: JsFunctionCell | None = None
    header: JsFunctionCol | Callable[[HeaderCellInfo], HTML] | None = None
    footer: JsFunctionCol | Callable[[ColInfo], HTML] | None = None
    details: JsFunctionRow | Callable[[RowInfo], HTML] | None = None
    # filterInput
    html: bool | None = None
    na: str | None = None
    rowHeader: bool | None = None
    minWidth: int | None = None
    maxWidth: int | None = None
    width: int | None = None
    align: Literal["left", "right", "center"] | None = None
    vAlign: Literal["top", "center", "bottom"] | None = None
    headerVAlign: Literal["top", "center", "bottom"] | None = None
    sticky: Literal["left", "right"] | None = None
    class_: list[str] | Callable[[CellInfo], list[str]] | JsFunctionCell | None = None
    style: CssRules | None = None
    headerClass: list[str] | None = None
    headerStyle: CssStyles | None = None
    footerClass: list[str] | None = None
    footerStyle: CssRules | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.id

    def to_props(self) -> dict[str, Any]:
        renamed = rename(asdict(self), **{"class": "class_"})
        return filter_none(renamed)


@dataclass
class ColGroup:
    name: str | None = None
    columns: list[str] | None = None
    header: Callable[[HeaderCellInfo], HTML] | JsFunction | None = None
    html: bool | None = None
    align: Literal["left", "right", "center"] | None = None
    headerVAlign: Literal["top", "center", "bottom"] | None = None
    sticky: Literal["left", "right"] | None = None
    headerClass: list[str] | None = None
    headerStyle: CssStyles | None = None

    def to_props(self):
        return filter_none(asdict(self))


@dataclass
class Theme:
    color: str | None = None
    backgroundColor: str | None = None
    borderColor: str | None = None
    borderWidth: int | None = None
    stripedColor: str | None = None
    highlightColor: str | None = None
    cellPadding: str | None = None
    style: CssRules | None = None

    borderColor: str | None = None
    borderWidth: str | None = None
    tableStyle: CssRules | None = None

    headerStyle: CssRules | None = None
    groupHeaderStyle: CssRules | None = None
    tableBodyStyle: CssRules | None = None
    rowGroupStyle: CssRules | None = None
    rowStyle: CssRules | None = None
    rowStripedStyle: CssRules | None = None
    rowHighlightStyle: CssRules | None = None
    rowSelectedStyle: CssRules | None = None
    cellStyle: CssRules | None = None
    footerStyle: CssRules | None = None
    inputStyle: CssRules | None = None
    filterInputStyle: CssRules | None = None
    searchInputStyle: CssRules | None = None
    selectStyle: CssRules | None = None

    paginationStyle: CssRules | None = None
    pageButtonStyle: CssRules | None = None
    pageButtonHoverStyle: CssRules | None = None
    pageButtonActiveStyle: CssRules | None = None
    pageButtonCurrentStyle: CssRules | None = None

    def to_props(self) -> dict[str, Any]:
        renamed = rename(
            asdict(self),
            tableBorderColor="borderColor",
            tableBorderWidth="borderWidth",
            headerBorderColor="borderColor",
            headerBorderWidth="borderWidth",
            groupHeaderBorderColor="borderColor",
            groupHeaderBorderWidth="borderWidth",
            cellBorderColor="borderColor",
            cellBorderWidth="borderWidth",
            footerBorderColor="borderColor",
            footerBorderWidth="borderWidth",
        )

        return filter_none(renamed)
