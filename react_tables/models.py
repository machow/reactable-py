from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Callable
from typing_extensions import TypeAlias

from dataclasses import asdict, dataclass, field, fields, replace, InitVar

from polars import DataFrame as PlDataFrame
from .data import SimpleFrame
from ._tbl_data import col_type
from .tags import to_hydrate_format

if TYPE_CHECKING:
    from .options import Options


def get_options() -> Options:
    # to avoid circular imports
    from .options import options

    return options


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


def cols_dict_to_list(cols: dict[str, Column] | list[Column]) -> list[Column]:
    if isinstance(cols, list):
        return cols

    # validate that id isn't set on any column
    col_ids = set(cols.keys())
    for k, col in cols.items():
        if not isinstance(k, str):
            raise ValueError(
                "When specifying columns with a dictionary, keys should be strings. "
                f'Column entry for "{k}" has key of type "{type(k)}".'
            )
        if col.id is not None:
            raise ValueError(
                f"When specifying columns with a dictionary, id should not be set. "
                f'Column entry for "{k}" has id set to "{col.id}".'
            )

    # set id attribute using dict keys
    return [replace(col, id=k) for k, col in cols.items()]


def default_columns(
    d: PlDataFrame | SimpleFrame | dict[str, Any], default: Column | None = None
) -> list[Column]:
    if default is None:
        default = Column()
    if isinstance(d, dict):
        return [Column(name=k, id=k).infer_type(v).merge(default) for k, v in d.items()]

    names = get_column_names(d)

    out = []
    for name in names:
        col = (
            Column(
                name=name,
                id=name,
            )
            .infer_type(d[name])
            .merge(default)
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


def str_to_list(x: str | list[str]) -> list[str]:
    if isinstance(x, str):
        return [x]
    return x


@dataclass
class JS:
    code: str

    def to_props(self):
        return asdict(self)


# Misc field types ----
HTML: TypeAlias = str
CssRules: TypeAlias = "dict[str, 'CssStyles'] | str"
CssStyles: TypeAlias = "dict[str, str] | str"
CellRenderer: TypeAlias = Callable[["CellInfo"], str]
StrIsoCurrency: TypeAlias = str
ColEl: TypeAlias = Any
"""An element in a column"""

RowIndx: TypeAlias = int
"""The index of the current row"""


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
    class_: InitVar[str | list[str] | None] = None
    filterable: bool | None = None
    searchable: bool | None = None
    resizable: bool | None = None
    theme: Theme | None = None
    language: str | None = None
    meta: dict[str, Any] | None = None
    elementId: str | None = None
    dataKey: str | None = None

    # ...rest ----
    bordered: bool = False
    borderless: bool = False
    striped: bool = False
    compact: bool = True
    wrap: InitVar[bool] = True
    highlight: bool = False
    outlined: bool | None = None
    minRows: int | None = None
    paginateSubRows: bool | None = None
    details: InitVar[JS | Column | None] = field(default=None)
    defaultExpanded: bool | None = None
    selection: Literal["multiple", "single"] | None = None
    defaultPageSize: int | None = None
    showPageSizeOptions: bool | None = None
    pageSizeOptions: list[int] = field(default_factory=lambda: [10, 25, 50, 100])
    paginationType: Literal["numbers", "jump", "simple"] = "numbers"
    showPageInfo: bool | None = None
    showPagination: bool | None = None
    pagination: bool | None = None
    onClick: Literal["expand", "select"] | JsFunction | None = None
    fullWidth: InitVar[bool] = True
    width: int | None = None
    height: int | None = None
    groupBy: str | list[str] | None = None
    style: CssRules | None = None
    rowStyle: CssRules | Callable[RowIndx, dict[str, str]] | None = None
    rowClass: InitVar[list[str] | Callable[RowIndx, list[str]] | None] = None
    rownames: InitVar[bool] = False
    static: bool | None = None

    # derived props ----
    defaultSortDesc: bool = field(init=False)
    inline: bool = field(init=False)
    rowClassName: list[str] | None = field(init=False)
    nowrap: bool = field(init=False)
    className: list[str] | None = field(init=False)
    # groupBy: list[str] | None = None
    # defaults: Defaults

    def __post_init__(
        self,
        defaultColDef,
        defaultSortOrder: Literal["asc", "desc"],
        class_: str | list[str] | None,
        wrap: bool,
        details,
        fullWidth: bool | None,
        rowClass: list[str] | Callable[RowIndx, list[str]] | None,
        rownames: bool,
    ):
        # columns ----
        _simple_cols = default_columns(self.data, defaultColDef)
        if self.columns is None:
            # TODO: does not apply defaultColDef
            self.columns = _simple_cols
        else:
            self.columns = cols_dict_to_list(self.columns)
            self.columns = self.complete_columns(_simple_cols, defaultColDef, self.columns)

        self.validate_columns()

        # data ----
        if isinstance(self.data, (PlDataFrame, SimpleFrame)):
            self.data = process_data(self.data)

        self.defaultSorted = self.derive_default_sorted(defaultSortOrder)
        self.groupBy = [self.groupBy] if isinstance(self.groupBy, str) else self.groupBy

        # TODO: would be nice to put at top of function
        # but needs to be after data processing for now
        # TODO: will fail for data with no columns
        n_rows = len(list(self.data.values())[0])

        # derived ----
        self.defaultSortDesc = defaultSortOrder == "desc"
        self.inline = not fullWidth
        self.nowrap = not wrap
        self.className = class_

        # details ----
        if details is not None:
            # TODO: validate key not already in data
            details_default = Column(
                id=".details",
                name="",
                sortable=False,
                filterable=False,
                searchable=False,
                resizable=False,
                width=45,
                align="center",
            )

            if isinstance(details, Column):
                col_details = details.merge(details_default)
            elif callable(details):
                col_details = replace(details_default, details=details)
            else:
                col_details = replace(details_default, details=details)
        else:
            col_details = None

        # selection ----
        if self.selection is not None:
            _sel_key = ".selection"
            # TODO: avoid mutation
            col_select = Column(id=_sel_key, name="", resizable=False, width=45, _selectable=True)

            _existing_col = next((col for col in self.columns if col.id == _sel_key), None)
            if _existing_col:
                raise NotImplementedError("Column named .selection not currently supported")
        else:
            col_select = None

        # rownames ----
        if rownames:
            # TODO: validate key not already in data
            col_rownames = Column(
                id=".rownames",
                name="",
                sortable=False,
                filterable=False,
            )

            self.data = {".rownames": list(range(n_rows)), **self.data}
        else:
            col_rownames = None

        # include rownames, details, and selection columns ----
        if col_rownames:
            self.columns = [col_rownames, *self.columns]

        if col_details:
            self.columns = [col_details, *self.columns]

        if col_select:
            self.columns = [col_select, *self.columns]

        # initialize columns ----
        self.columns = [col.init_data(self.data) for col in self.columns]

        # row classes ----
        if callable(rowClass):
            self.rowClassName = [to_hydrate_format(rowClass(ii)) for ii in range(n_rows)]
        else:
            self.rowClassName = rowClass

        # row style ----
        if callable(self.rowStyle):
            self.rowStyle = [to_hydrate_format(self.rowStyle(ii)) for ii in range(n_rows)]
        elif isinstance(self.rowStyle, str):
            raise NotImplementedError()

        # apply global options ----
        if self.theme is None:
            self.theme = replace(get_options().theme)

        if self.language is None:
            self.language = replace(get_options().language)

    @staticmethod
    def complete_columns(
        simple_cols: list[Column], default: Column | None, columns: list[Column]
    ) -> list[Column]:
        if default is None:
            default = Column()
        crnt_cols = []
        col_def_map = {col.id: col for col in columns}
        for simple_col in simple_cols:
            col_name = simple_col.id
            if col_name in col_def_map:
                col_cnfg = replace(col_def_map[col_name], type=simple_col.type)
                crnt_cols.append(col_cnfg.merge(default))
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
        props_list = ["columns", "columnGroups"]
        out = {}
        for field in fields(self):
            attr = getattr(self, field.name)
            f_props = getattr(attr, "to_props", None)
            res = f_props() if f_props is not None else attr

            if field.name in props_list and res is not None:
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
    separators: bool | None = None
    percent: bool | None = None
    currency: StrIsoCurrency | None = None
    datetime: bool | None = None
    date: bool | None = None
    time: bool | None = None
    hour12: bool | None = None
    locales: bool | None = None

    def to_props(self):
        return filter_none(asdict(self))


@dataclass
class ColFormatGroupBy:
    cell: ColFormat | None = None
    aggregated: ColFormat | None = None

    def to_props(self):
        return filter_none(as_props(self))


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
    format: ColFormat | ColFormatGroupBy | None = None
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
    style: CssRules | Callable[[ColEl], dict[str, str]] | None = None
    headerClass: list[str] | None = None
    headerStyle: CssStyles | None = None
    footerClass: list[str] | None = None
    footerStyle: CssRules | None = None

    # internal ----
    # TODO: ideally this cannot be specified in the constructor
    # it's just passed to the widget
    type: str | None = None
    _selectable: bool = False

    def __post_init__(self):
        if self.name is None:
            self.name = self.id

        # TODO: currently ColFormat is never passed in directly,
        # but always converted to specify cell and aggregate formatting
        if isinstance(self.format, ColFormat):
            self.format = ColFormatGroupBy(
                cell=self.format.to_props(),
                aggregated=self.format.to_props(),
            )

    def _apply_transform(self, col_data: list[Any], transform: callable):
        return [
            to_hydrate_format(transform(CellInfo(val, ii, self.id)))
            for ii, val in enumerate(col_data)
        ]

    def init_data(self, data: dict[str, list[Any]]) -> Column:
        # TODO: what can we expect set at this stage? name? etc..?
        # TODO: this is a hack to handle cols like .details
        n_rows = len(list(data.values())[0])
        col_data = data[self.id] if not self.id.startswith(".") else [None] * n_rows

        new_col = replace(self)

        # merge column config ----

        # cell is function: transform content ----
        if isinstance(self.cell, JS):
            pass
        if callable(self.cell):
            new_col.cell = self._apply_transform(col_data, self.cell)

        # header: transform or set string as react tag ----

        # footer: transform or set string as react tag ----
        if callable(self.footer):
            # TODO: validate result is a string (e.g. int will raise on js side)
            new_col.footer = to_hydrate_format(self.footer(ColInfo(col_data, new_col.name)))
        elif isinstance(self.footer, JS):
            pass

        # details: transform ----
        if callable(self.details):
            new_col.details = list(
                map(to_hydrate_format, [self.details(ii) for ii in range(len(col_data))])
            )

        # filterInput: transform or set string as react tag ----

        # className: transform ----

        # style: transform ----
        # overall style
        if callable(self.style):
            new_col.style = [self.style(x) for x in col_data]

        # columnGroups (spanners) ----
        # call header func if exists (or add as react tag)
        return new_col

    def infer_type(self, series):
        return replace(self, type=col_type(series))

    def merge(self, other: Column):
        field_attrs = {field.name: getattr(self, field.name) for field in fields(self)}
        return replace(other, **filter_none(field_attrs))

    def to_props(self) -> dict[str, Any]:

        renamed = rename(as_props(self), **{"class": "class_", "selectable": "_selectable"})
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

    def __post_init__(self):
        # TODO: reactable does manual validation, but we could harness
        # the power of annotations to do this automatically
        # validate styles

        # validate width and padding

        # all other values should be strings
        pass

    def to_props(self) -> dict[str, Any]:
        renamed = rename(
            asdict(self),
            # tableBorderColor="borderColor",
            # tableBorderWidth="borderWidth",
            # headerBorderColor="borderColor",
            # headerBorderWidth="borderWidth",
            # groupHeaderBorderColor="borderColor",
            # groupHeaderBorderWidth="borderWidth",
            # cellBorderColor="borderColor",
            # cellBorderWidth="borderWidth",
            # footerBorderColor="borderColor",
            # footerBorderWidth="borderWidth",
        )

        return filter_none(renamed)


@dataclass
class Language:
    # Sorting
    sortLabel: str = "Sort {name}"

    # Filters
    filterPlaceholder: str = ""
    filterLabel: str = "Filter {name}"

    # Search
    searchPlaceholder: str = "Search"
    searchLabel: str = "Search"

    # Tables
    noData: str = "No rows found"

    # Pagination
    pageNext: str = "Next"
    pagePrevious: str = "Previous"
    pageNumbers: str = "{page} of {pages}"
    pageInfo: str = "{rowStart}\u2013{rowEnd} of {rows} rows"
    pageSizeOptions: str = "Show {rows}"
    pageNextLabel: str = "Next page"
    pagePreviousLabel: str = "Previous page"
    pageNumberLabel: str = "Page {page}"
    pageJumpLabel: str = "Go to page"
    pageSizeOptionsLabel: str = "Rows per page"

    # Row grouping
    groupExpandLabel: str = "Toggle group"

    # Row details
    detailsExpandLabel: str = "Toggle details"

    # Selection
    selectAllRowsLabel: str = "Select all rows"
    selectAllSubRowsLabel: str = "Select all rows in group"
    selectRowLabel: str = "Select row"

    def to_props(self):
        return asdict(self)
