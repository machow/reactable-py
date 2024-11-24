from __future__ import annotations

import htmltools as html

from great_tables import GT
from great_tables._tbl_data import n_rows
from great_tables._helpers import random_id
from great_tables._text import _process_text
from great_tables._gt_data import ColInfoTypeEnum
from typing import TYPE_CHECKING, Any

from .models import Column, Language, Theme, ColGroup
from . import Reactable
from ._tbl_data import subset_frame, to_dict

if TYPE_CHECKING:
    from great_tables._gt_data import Locale, Spanners, Heading, Footnotes, SourceNotes, Options


class OptWrapper:
    _d: Options

    def __init__(self, d: Options):
        self._d = d

    def __getitem__(self, k: str) -> Any:
        return getattr(self._d, k).value


def dict_to_css(dict_: dict[str, str]) -> str:
    return "; ".join([f"{k}: {v}" for k, v in dict_.items()])


def locale_to_lang(locale: Locale | None) -> Language:
    if locale is None or locale._locale is None or locale._locale == "en":
        return Language()

    # TODO: fetch locale data, translate to Language
    raise NotImplementedError()


def create_col_groups(spanners: Spanners) -> list[ColGroup]:
    col_groups = []
    for spanner in spanners:
        if spanner.spanner_level > 0:
            raise NotImplementedError("Column groups with more than 1 level are not supported")

        col_groups.append(
            ColGroup(
                name=_process_text(spanner.spanner_label),
                columns=spanner.vars,
            )
        )

    return col_groups


def _is_empty(heading: Heading):
    # TODO: this should be moved into great tables
    self = heading
    return self.title is None and self.subtitle is None and self.preheader is None


def create_heading(heading: Heading, use_search: bool) -> html.Tag | None:
    if _is_empty(heading):
        return None

    el = html.div(
        html.div(
            html.HTML(_process_text(heading.title)),
            class_="gt_heading gt_title gt_font_normal",
            style="text-size: bigger;",
        ),
        html.div(
            html.HTML(_process_text(heading.subtitle)),
            class_="gt_heading gt_subtitle" + ("gt_bottom_border" if use_search else ""),
        ),
        style=dict_to_css(
            {
                # "font-family":
                "border-top-style": "solid",
                "border-top-width": "2px",
                "border-top-color": "#D3D3D3",
                "padding-bottom": "8px" if use_search else None,
            }
        ),
    )

    return el


def create_footer(
    footnotes: Footnotes, source_notes: SourceNotes, n_columns, multiline, sep="<br>"
) -> html.Tag | None:
    if not footnotes and not source_notes:
        return None

    # TODO: source note styles
    # TODO: footnotes not yet implemented in Great Tables

    def create_tr(note: html.Tag) -> html.Tag:
        el = html.tags.tr(
            html.tags.td(
                note,
                class_="gt_sourcenote",
                # style = ...,
                colspan=n_columns,
            )
        )

        return el

    if multiline:
        trs = []
        for note in source_notes:
            trs.append(create_tr(html.HTML(note)))
        res = html.tags.tfoot(trs, class_="gt_sourcenotes")

        return res

    text = list(map(_process_text, source_notes))
    combined_notes = html.div(html.HTML(sep.join(text)), style="padding-bottom: 2px;")

    return html.tags.tfoot(create_tr(combined_notes), class_="gt_sourcenotes")


def extract_cells(
    self: GT, columns: str | list[str], rows: int | list[int] | None = None, output: str = "html"
) -> list[str]:
    from great_tables._tbl_data import (
        cast_frame_to_string,
        replace_null_frame,
    )

    if rows is not None:
        raise NotImplementedError()

    # format ----
    new_gt = self._build_data(output)

    # TODO: are these actions done in GT render_body_h, is this a general activity?
    _str_orig_data = cast_frame_to_string(new_gt._tbl_data)
    df_stringified = replace_null_frame(new_gt._body.body, _str_orig_data)

    # extract specific columns ----
    if isinstance(columns, str):
        columns = [columns]

    # TODO: get_cell gets individual cell, need one that gets columns
    df_subset = subset_frame(df_stringified, cols=columns)
    return to_dict(df_subset)


def _render(self: GT):
    # TODO: final sorting
    # data = self._build_data(context="html")

    # add_css_styles()

    table_id = OptWrapper(self._options)["table_id"] or random_id()
    locale = self._locale

    # generate Language -------------------------------------------------------
    lang_defs = locale_to_lang(locale)

    # column info -------------------------------------------------------------
    _stub = self._boxhead._get_stub_column()
    _group = self._boxhead._get_row_group_column()
    _defaults = self._boxhead._get_default_columns()

    groupname_col = _group.var if _group else None

    col_info = _defaults
    if _group:
        col_info = [_group, *col_info]
    if _stub:
        col_info = [_stub, *col_info]

    visible_col_names = [col.var for col in col_info]

    # handle hidden columns ---------------------------------------------------
    data = subset_frame(self._tbl_data, cols=visible_col_names)
    data_n_rows = n_rows(data)

    # define a bunch of variables for options ----

    # TODO: note that gt calls this once per column, but that triggers
    # all formatting activity per column, so we call only once.
    formatted_cols = extract_cells(self, columns=visible_col_names, output="html")

    # Generate body styles ----------------------------------------------------
    # gt uses a default Column(style = JS(...))
    body_style_info = (style for style in self._styles if style.locname == "data")
    body_styles: dict[str, list[str]] = {k: [None] * data_n_rows for k in visible_col_names}

    for info in body_style_info:
        for style in info.styles:
            # TODO: Great Tables code currently filters styles for every cell (should refactor)
            crnt_style = body_styles[info.colname][info.rownum]
            new_style = as_react_style(style._to_html_style())
            if crnt_style is None:
                body_styles[info.colname][info.rownum] = new_style
            else:
                body_styles[info.colname][info.rownum] = {**crnt_style, **new_style}

    # create Column definitions (including rownames) --------------

    columns = []

    for col in col_info:
        # formatted column

        if col.type == ColInfoTypeEnum.stub:
            # TODO: rowname col should also have a righthand border?
            col_def = Column(
                id=col.var,
                cell=lambda ci: formatted_cols[ci.column_name][ci.row_index],
                name=_process_text(self._stubhead or ""),
                header_style={"font-weight": "normal"},
                width=col.column_width,
                sortable=False,
                filterable=False,
                html=True,
            )

        else:
            col_def = Column(
                id=col.var,
                cell=lambda ci: formatted_cols[ci.column_name][ci.row_index],
                name=_process_text(col.column_label),
                align=col.column_align,
                header_style={"font-weight": "normal"},
                width=col.column_width,
                # TODO: html shouldn't always be true?
                html=True,
                style=body_styles[col.var],
            )

        columns.append(col_def)

    # Column spanners (using ColGroups) ----
    col_groups = create_col_groups(self._spanners)

    # Generate table header and footer elements ----
    # TODO: implement option
    # use_search = opts["ihtml_use_search"]
    el_header = create_heading(self._heading, use_search=True)
    # TODO: implement multiline
    el_footer = create_footer(
        self._footnotes,
        self._source_notes,
        n_columns=len(visible_col_names),
        multiline=False,
    )

    # Generate theme ----------------------------------------------------------
    opts = OptWrapper(self._options)
    theme = Theme(
        color=opts["table_font_color"],
        background_color=opts["table_background_color"],
        border_color=None,
        border_width=None,
        # stripedColor=opts["row_striping_background_color"],
        highlight_color=None,
        cell_padding=None,
        # style = {"font-family": font_family_str},
        table_style=None,
        header_style=dict(
            borderTopStyle=opts["column_labels_border_top_style"],
            borderTopWidth=opts["column_labels_border_top_width"],
            borderTopColor=opts["column_labels_border_top_color"],
            borderBottomStyle=opts["column_labels_border_bottom_style"],
            borderBottomWidth=opts["column_labels_border_bottom_width"],
            borderBottomColor=opts["column_labels_border_bottom_color"],
        ),
    )

    itable = Reactable(
        data=data,
        columns=columns,
        column_groups=col_groups,
        default_expanded=True,
        rownames=None,
        # TODO: reactable always puts groupBy cols first, even before rowname cols
        group_by=groupname_col,
        # TODO: no ihtml options
        # sortable=opts["ihtml_use_sorting"],
        # resizable=opts["ihtml_use_resizing"],
        # filterable=opts["ihtml_use_filters"],
        # searchable=opts["ihtml_use_search"],
        # TODO: searchMethod not yet implemented
        # searchMethod=None,
        # pagination=opts["ihtml_use_pagination"],
        # defaultPageSize=opts["ihtml_page_size_default"],
        # showPageSizeOptions=opts["ihtml_use_page_size_select"],
        # pageSizeOptions=opts["ihtml_page_size_values"],
        # paginationType=opts["ihtml_pagination_type"],
        show_pagination=True,
        # showPageInfo=opts["ihtml_use_pagination_info"],
        min_rows=1,
        paginate_sub_rows=False,
        details=None,
        selection=None,
        # TODO: selectionId not implemented
        # selectionId=None,
        # defaultSelected=None,
        on_click=None,
        # highlight=opts["ihtml_use_highlighting"],
        outlined=False,
        bordered=False,
        borderless=False,
        # striped=opts["row_striping_include_table_body"],
        # compact=opts["ihtml_use_compact_mode"],
        # text_wrapping=opts["ihtml_use_text_wrapping"],
        # showSortIcon=True,
        # showSortable=True,
        class_=None,
        style=None,
        row_class=None,
        row_style=None,
        full_width=True,
        width=opts["table_width"],
        height="auto",
        theme=theme,
        language=lang_defs,
        element_id=table_id,
        static=False,
        #  use_page_size_select <- opt_val(data = data, option = "ihtml_use_page_size_select")
        #  page_size_default <- opt_val(data = data, option = "ihtml_page_size_default")
        #  page_size_values <- opt_val(data = data, option = "ihtml_page_size_values")
        #  pagination_type <- opt_val(data = data, option = "ihtml_pagination_type")
        #
        #  use_row_striping <- opt_val(data = data, option = "row_striping_include_table_body")
    )

    return el_header, itable, el_footer
