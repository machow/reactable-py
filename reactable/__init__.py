from __future__ import annotations

from .models import (
    Reactable,
    Column,
    ColGroup,
    ColFormat,
    ColFormatGroupBy,
    CellInfo,
    ColInfo,
    HeaderCellInfo,
    RowInfo,
    Theme,
    Language,
    JS,
)
from .widgets import BigblockWidget, embed_css, bigblock, RT
from .options import options
from .render_gt import render

reactable = bigblock

__all__ = [
    # table classes ----
    "Reactable",
    "Column",
    "ColGroup",
    "ColFormat",
    "ColFormatGroupBy",
    "Theme",
    "Language",
    # renderer data classes ----
    "CellInfo",
    "ColInfo",
    "HeaderCellInfo",
    "RowInfo",
    "JS",
    # global options ----
    "options",
    # TODO: remove ----
    "reactable",
]
