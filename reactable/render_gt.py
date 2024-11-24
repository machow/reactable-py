from __future__ import annotations

import ipywidgets
import ipyreact
import htmltools as html

from .tags import as_react_style, to_widget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from great_tables import GT


def render(self: GT) -> ipyreact.Widget:
    from great_tables._scss import compile_scss
    from ._render_gt import _render

    # get table elements ----
    el_header, itable, el_footer = _render(self)

    # compile table specific css ----
    css = compile_scss(self, id=itable.element_id)

    style = to_widget(html.tags.style(css))

    # return widget ----
    res = [itable.to_widget()]

    if el_header:
        res = [ipywidgets.HTML(str(el_header))] + res
    if el_footer:
        res = res + [ipywidgets.HTML(str(el_footer))]

    res = [style] + res
    return ipyreact.Widget(_type="div", props={"id": itable.element_id}, children=res)
