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


CAMEL_OVERRIDES: dict[str, str] = {
    "sort_na_last": "sortNALast",
}


def to_camel_case(s: str) -> str:
    if s in CAMEL_OVERRIDES:
        return CAMEL_OVERRIDES[s]

    full_camel = "".join(x.capitalize() for x in s.lower().split("_"))
    return full_camel[0].lower() + full_camel[1:]


def to_camel_dict(d: dict) -> dict:
    return {to_camel_case(k): v for k, v in d.items()}


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
    column_groups: list[ColGroup] | None = None
    rownames: InitVar[bool] = False
    group_by: str | list[str] | None = None

    sortable: bool = True
    resizable: bool | None = None
    filterable: bool | None = None
    searchable: bool | None = None
    pagination: bool | None = None
    default_col_def: InitVar[Column | None] = None
    default_sort_order: InitVar[Literal["asc", "desc"]] = "asc"
    default_sorted: list[str] | None = None
    default_page_size: int | None = None
    show_page_size_options: bool | None = None
    page_size_options: list[int] = field(default_factory=lambda: [10, 25, 50, 100])
    pagination_type: Literal["numbers", "jump", "simple"] = "numbers"
    show_pagination: bool | None = None
    show_page_info: bool | None = None
    min_rows: int | None = None
    paginate_sub_rows: bool | None = None

    details: InitVar[JS | Column | None] = field(default=None)
    default_expanded: bool | None = None

    selection: Literal["multiple", "single"] | None = None
    # TODO: default_selected
    on_click: Literal["expand", "select"] | JsFunction | None = None
    highlight: bool = False

    outlined: bool | None = None
    bordered: bool = False
    borderless: bool = False
    striped: bool = False
    compact: bool = True

    wrap: InitVar[bool] = True

    show_sort_icon: bool | None = None
    show_sortable: bool | None = None

    class_: InitVar[str | list[str] | None] = None
    style: CssRules | None = None
    row_class: InitVar[list[str] | Callable[RowIndx, list[str]] | None] = None
    row_style: CssRules | Callable[RowIndx, dict[str, str]] | None = None

    full_width: InitVar[bool] = True
    width: int | None = None
    height: int | None = None

    theme: Theme | None = None
    language: str | None = None
    meta: dict[str, Any] | None = None
    element_id: str | None = None
    static: bool | None = None
    dataKey: str | None = None

    # derived props ----
    default_sort_desc: bool = field(init=False)
    inline: bool = field(init=False)
    row_class_name: list[str] | None = field(init=False)
    nowrap: bool = field(init=False)
    class_name: list[str] | None = field(init=False)
    # groupBy: list[str] | None = None
    # defaults: Defaults

    def __post_init__(
        self,
        rownames: bool,
        default_col_def,
        default_sort_order: Literal["asc", "desc"],
        details,
        wrap: bool,
        class_: str | list[str] | None,
        row_class: list[str] | Callable[RowIndx, list[str]] | None,
        full_width: bool | None,
    ):
        # columns ----
        _simple_cols = default_columns(self.data, default_col_def)
        if self.columns is None:
            # TODO: does not apply defaultColDef
            self.columns = _simple_cols
        else:
            self.columns = cols_dict_to_list(self.columns)
            self.columns = self.complete_columns(_simple_cols, default_col_def, self.columns)

        self.validate_columns()

        # data ----
        if isinstance(self.data, (PlDataFrame, SimpleFrame)):
            self.data = process_data(self.data)

        self.default_sorted = self.derive_default_sorted(default_sort_order)
        self.group_by = [self.group_by] if isinstance(self.group_by, str) else self.group_by

        # TODO: would be nice to put at top of function
        # but needs to be after data processing for now
        # TODO: will fail for data with no columns
        n_rows = len(list(self.data.values())[0])

        # simple derived properties ----
        self.default_sort_desc = default_sort_order == "desc"
        self.inline = not full_width
        self.nowrap = not wrap
        self.class_name = class_

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
        if callable(row_class):
            self.row_class_name = [to_hydrate_format(row_class(ii)) for ii in range(n_rows)]
        else:
            self.row_class_name = row_class

        # row style ----
        if callable(self.row_style):
            self.row_style = [to_hydrate_format(self.row_style(ii)) for ii in range(n_rows)]
        elif isinstance(self.row_style, str):
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

    def derive_default_sorted(self, default_sort_order: Literal["asc", "desc"]):
        if self.default_sorted is None:
            return

        out = []
        for col in self.columns:
            if col.id in self.default_sorted:
                out.append(
                    dict(
                        id=col.id,
                        desc=(col.default_sort_order or default_sort_order) == "desc",
                    )
                )

        return out

    def validate_columns(self):
        names = set(get_column_names(self.data))
        for col in self.columns:
            if col.id not in names:
                raise ValueError(f"Column id '{col.id}' is not a column name in the data.")

    def validate_groupBy(self):
        if self.group_by is None:
            return

        col_map = {col.id: col for col in self.columns}
        missing = [col for col in self.group_by if col not in col_map]
        if missing:
            raise ValueError(f"groupBy column names not in data: {missing}")

        details = [col for col in self.group_by if getattr(col_map[col], "details", None)]
        if details:
            raise ValueError(
                "groupBy columns cannot have `details` set.\n\n" f"Affected columns: {details}"
            )

    def to_props(self):
        props_list = ["columns", "column_groups"]
        out = {}
        for field in fields(self):
            attr = getattr(self, field.name)
            f_props = getattr(attr, "to_props", None)
            res = f_props() if f_props is not None else attr

            if field.name in props_list and res is not None:
                res = [x.to_props() for x in res]

            out[field.name] = res

        return to_camel_dict(filter_none(out))


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
    filter_method: JsFunction | None = None
    show: bool | None = None
    default_sort_order: Literal["asc", "desc"] | None = None
    sort_na_last: bool | None = None
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
    row_header: bool | None = None
    min_width: int | None = None
    max_width: int | None = None
    width: int | None = None
    align: Literal["left", "right", "center"] | None = None
    v_align: Literal["top", "center", "bottom"] | None = None
    header_v_align: Literal["top", "center", "bottom"] | None = None
    sticky: Literal["left", "right"] | None = None
    class_: list[str] | Callable[[CellInfo], list[str]] | JsFunctionCell | None = None
    style: CssRules | Callable[[ColEl], dict[str, str]] | None = None
    header_class: list[str] | None = None
    header_style: CssStyles | None = None
    footer_class: list[str] | None = None
    footer_style: CssRules | None = None

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

        # class to apply to cells ----
        if callable(self.class_):
            new_col.class_ = self._apply_transform(col_data, self.class_)

        # header: transform or set string as react tag ----
        if callable(self.header):
            # TODO: confusing that the column data name is called id, and label is called name?
            new_col.header = to_hydrate_format(self.header(HeaderCellInfo(self.name, self.id)))

        # footer: transform or set string as react tag ----
        if callable(self.footer):
            # TODO: validate result is a string (e.g. int will raise on js side)
            new_col.footer = to_hydrate_format(self.footer(ColInfo(col_data, new_col.name)))
        elif isinstance(self.footer, JS):
            pass
        else:
            new_col.footer = to_hydrate_format(self.footer)

        # details: transform ----
        if callable(self.details):
            new_col.details = list(
                map(
                    to_hydrate_format,
                    [self.details(RowInfo(ii, self.name)) for ii in range(len(col_data))],
                )
            )

        # filterInput: transform or set string as react tag ----

        # className: transform ----

        # style: transform ----
        # overall style
        if callable(self.style):
            new_col.style = self._apply_transform(col_data, self.style)
        elif isinstance(self.style, list):
            if len(self.style) != n_rows:
                raise ValueError(
                    f"Style list must be same length as data. Data has {n_rows}, list has {len(self.style)}"
                )

            new_col.style = self.style

        # _golumnGroups (spanners) ----
        # call header func if exists (or add as react tag)
        return new_col

    def infer_type(self, series):
        return replace(self, type=col_type(series))

    def merge(self, other: Column):
        field_attrs = {field.name: getattr(self, field.name) for field in fields(self)}
        return replace(other, **filter_none(field_attrs))

    def to_props(self) -> dict[str, Any]:

        renamed = rename(
            as_props(self),
            **{
                "class_": "class_name",
                "selectable": "_selectable",
                "header_class": "header_class_name",
            },
        )
        return to_camel_dict(filter_none(renamed))


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


"""R documentation for reactable function

data
A data frame or matrix.

Can also be a crosstalk::SharedData object that wraps a data frame.

columns
Named list of column definitions. See colDef().

columnGroups
List of column group definitions. See colGroup().

rownames
Show row names? Defaults to TRUE if the data has row names.

To customize the row names column, add a column definition using ".rownames" as the column name.

Cells in the row names column are automatically marked up as row headers for assistive technologies.

groupBy
Character vector of column names to group by.

To aggregate data when rows are grouped, use the aggregate argument in colDef().

sortable
Enable sorting? Defaults to TRUE.

resizable
Enable column resizing?

filterable
Enable column filtering?

searchable
Enable global table searching?

searchMethod
Custom search method to use for global table searching. A JS() function that takes an array of row objects, an array of column IDs, and the search value as arguments, and returns the filtered array of row objects.

defaultColDef
Default column definition used by every column. See colDef().

defaultColGroup
Default column group definition used by every column group. See colGroup().

defaultSortOrder
Default sort order. Either "asc" for ascending order or "desc" for descending order. Defaults to "asc".

defaultSorted
Character vector of column names to sort by default. Or to customize sort order, a named list with values of "asc" or "desc".

pagination
Enable pagination? Defaults to TRUE.

defaultPageSize
Default page size for the table. Defaults to 10.

showPageSizeOptions
Show page size options?

pageSizeOptions
Page size options for the table. Defaults to 10, 25, 50, 100.

paginationType
Pagination control to use. Either "numbers" for page number buttons (the default), "jump" for a page jump, or "simple" to show 'Previous' and 'Next' buttons only.

showPagination
Show pagination? Defaults to TRUE if the table has more than one page.

showPageInfo
Show page info? Defaults to TRUE.

minRows
Minimum number of rows to show per page. Defaults to 1.

paginateSubRows
When rows are grouped, paginate sub rows? Defaults to FALSE.

details
Additional content to display when expanding a row. An R function that takes the row index and column name as arguments, or a JS() function that takes a row info object as an argument. Can also be a colDef() to customize the details expander column.

defaultExpanded
Expand all rows by default?

selection
Enable row selection? Either "multiple" or "single" for multiple or single row selection.

To get the selected rows in Shiny, use getReactableState().

To customize the selection column, use ".selection" as the column name.

defaultSelected
A numeric vector of default selected row indices.

onClick
Action to take when clicking a cell. Either "expand" to expand the row, "select" to select the row, or a JS() function that takes a row info object, column object, and table state object as arguments.

highlight
Highlight table rows on hover?

outlined
Add borders around the table?

bordered
Add borders around the table and every cell?

borderless
Remove inner borders from table?

striped
Add zebra-striping to table rows?

compact
Make tables more compact?

wrap
Enable text wrapping? If TRUE (the default), long text will be wrapped to multiple lines. If FALSE, text will be truncated to fit on one line.

showSortIcon
Show a sort icon when sorting columns?

showSortable
Show an indicator on sortable columns?

class
Additional CSS classes to apply to the table.

style
Inline styles to apply to the table. A named list or character string.

Note that if style is a named list, property names should be camelCased.

rowClass
Additional CSS classes to apply to table rows. A character string, a JS() function that takes a row info object and table state object as arguments, or an R function that takes a row index argument.

rowStyle
Inline styles to apply to table rows. A named list, character string, JS() function that takes a row info object and table state object as arguments, or an R function that takes a row index argument.

Note that if rowStyle is a named list, property names should be camelCased. If rowStyle is a JS() function, it should return a JavaScript object with camelCased property names.

fullWidth
Stretch the table to fill the full width of its container? Defaults to TRUE.

width
Width of the table in pixels. Defaults to "auto" for automatic sizing.

To set the width of a column, see colDef().

height
Height of the table in pixels. Defaults to "auto" for automatic sizing.
"""


@dataclass
class Reactable(Props):
    """A reactive table.

    Parameters
    ----------
    data:
        The data.
    columns:
        Named list of column definitions.
    column_groups:
        List of column group definitions.
    sortable:
        Whether to enable sorting. Defaults to `True`.
    resizable:
        Whether to enable column resizing.
    filterable:
        Whether to enable column filtering.
    searchable:
        Whether to enable global table searching.
    pagination:
        Whether to enable pagination.
    default_col_def:
        Default column definition used by every column.
    default_sort_order:
        Default sort order. Either "asc" for ascending order or "desc" for
        descending order. Defaults to "asc".
    default_sorted:
        List of column names to sort by default. Or to customize sort order,
        a dictionary mapping column names to "asc" or "desc".
    default_page_size:
        Default page size for the table. Defaults to 10.
    show_page_size_options:
        Whether to show page size options.
    pagination_type:
        Pagination control to use. Either "numbers" for page number buttons (the default),
        "jump" for a page jump, or "simple" to show 'Previous' and 'Next' buttons only.
    show_pagination:
        Whether to show pagination.
    show_page_info:
        Whether to show page info.
    min_rows:
        Minimum number of rows to show per page. Defaults to 1.
    paginate_sub_rows:
        When rows are grouped, paginate sub rows. Defaults to `False`.
    details:
        Additional content to display when expanding a row.
    default_expanded:
        Whether to expand all rows by default.
    selection:
        Enable row selection. Either "multiple" or "single" for multiple or single row selection.
        To customize the selection column, use `".selection"` as the column name.
    on_click:
        Action to take when clicking a cell. Either "expand" to expand the row, "select" to
        select the row, or a JS function that takes a row info object as an argument.
    highlight:
        Whether to highlight table rows on hover.
    outlined:
        Whether to add borders around the table.
    bordered:
        Whether to add borders around the table and every cell.
    borderless:
        Whether to remove inner borders from table.
    striped:
        Whether to add zebra-striping to table rows.
    compact:
        Whether to make tables more compact.
    wrap:
        Whether to enable text wrapping. If `True` (the default), long text will be wrapped to
        multiple lines. If `False`, text will be truncated to fit on one line.
    show_sort_icon:
        Whether to show a sort icon when sorting columns.
    show_sortable:
        Whether to show an indicator on sortable columns.
    class_:
        Additional CSS classes to apply to the table.
    style:
        Inline styles to apply to the table.
    row_class:
        Additional CSS classes to apply to table rows.
    row_style:
        Inline styles to apply to table rows.
    full_width:
        Whether to stretch the table to fill the full width of its container. Defaults to `True`.
    width:
        Width of the table in pixels. Defaults to "auto" for automatic sizing.
    height:
        Height of the table in pixels. Defaults to "auto" for automatic sizing.
    theme:
        Theme options for the table, specified by `Theme()`. Defaults to the global
        `reactable.theme` option.
    language:
        Language options for the table, specified by `Language()`. Defaults to the global
        `reactable.language` option.
    meta:
        Custom metadata to pass to JavaScript render functions or style functions.
    element_id:
        Element ID for the widget




    """

    def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None:
        from .widgets import BigblockWidget

        return BigblockWidget(props=self.to_props())._repr_mimebundle_()
