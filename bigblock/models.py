from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Callable
from typing_extensions import TypeAlias

from dataclasses import asdict, dataclass, field, fields, replace, InitVar

from polars import DataFrame as PlDataFrame
from bigblock.data import SimpleFrame


# Utils ----
def rename(d: dict[str, Any], **to_from: str) -> dict[str, Any]:
    from_to = {v: k for v, k in to_from.items()}

    return {from_to.get(k, k): v for k, v in d.items()}


def filter_none(d: dict[str, Any]):
    return {k: v for k, v in d.items() if v is not None}


def process_data(d: PlDataFrame | SimpleFrame) -> dict[str, list[Any]]:
    if isinstance(d, PlDataFrame):
        return d.to_dict(as_series=False)
    elif isinstance(d, SimpleFrame):
        return d.to_dict()

    raise TypeError(f"Unsupported type: {type(d)}")


def get_column_names(d: PlDataFrame | SimpleFrame | dict[str, Any]) -> list[str]:
    if isinstance(d, PlDataFrame):
        names = [col.name for col in d]
    elif isinstance(d, SimpleFrame):
        names = list(d.columns)
    else:
        names = list(d)

    return names


def default_columns(d: PlDataFrame | SimpleFrame | dict[str, Any]) -> list[Column]:
    if isinstance(d, dict):
        return [Column(name=k, id=k) for k in d]

    names = get_column_names(d)

    out = []
    for name in names:
        col = Column(
            name=name,
            id=name,
        )
        out.append(col)
    return out


def as_props(data):
    res = {}
    for field in fields(data):
        attr = getattr(data, field.name)
        if hasattr(attr, "to_props"):
            res[field.name] = attr.to_props()
        else:
            res[field.name] = attr

    return res


@dataclass
class JS:
    code: str

    def to_props(self):
        return self.code


# Misc field types ----
HTML: TypeAlias = str
CssRules: TypeAlias = dict[str, "CssStyles"]
CssStyles: TypeAlias = dict[str, str]
CellRenderer: TypeAlias = Callable[["CellInfo"], str]
StrIsoCurrency: TypeAlias = str


JsFunction: TypeAlias = JS
JsFunctionCell: TypeAlias = JS
"""A javascript function that takes cell info, and table state."""

JsFunctionCol: TypeAlias = JS
"""A javascript function that takes column info, and table state."""

JsFunctionRow: TypeAlias = JS
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
    searchable: bool | None = None
    resizable: bool | None = None
    theme: Theme | None = None
    language: str | None = None
    dataKey: str | None = None

    # ...rest ----
    bordered: bool = False
    highlight: bool = False
    minRows: int | None = None
    defaultPageSize: int | None = None
    showPageSizeOptions: bool | None = None
    pageSizeOptions: list[int] = field(default_factory=lambda: [10, 25, 50, 100])
    paginationType: Literal["numbers", "jump", "simple"] = "numbers"
    showPageInfo: bool | None = None
    showPagination: bool | None = None
    pagination: bool | None = None
    height: int | None = None
    groupBy: str | list[str] | None = None

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
        if isinstance(self.data, (PlDataFrame, SimpleFrame)):
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
        self.groupBy = [self.groupBy] if isinstance(self.groupBy, str) else self.groupBy

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
        names = set(get_column_names(self.data))
        for col in self.columns:
            if col.id not in names:
                raise ValueError(f"Column id '{col.id}' is not a column name in the data.")

    def validate_groupBy(self):
        if self.groupBy is None:
            return

        col_map = {col.id: col for col in self.columns}
        missing = [col for col in self.groupBy if col not in col_map]
        if missing:
            raise ValueError(f"groupBy column names not in data: {missing}")

        details = [col for col in self.groupBy if getattr(col_map[col], "details", None)]
        if details:
            raise ValueError(
                "groupBy columns cannot have `details` set.\n\n" f"Affected columns: {details}"
            )

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

        renamed = rename(as_props(self), **{"class": "class_"})
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
