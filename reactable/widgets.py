from __future__ import annotations

import ipyreact

from importlib_resources import files
from pathlib import Path
from typing import TYPE_CHECKING

STATIC_FILES = files("reactable.static")

if TYPE_CHECKING:
    from .models import Props


def embed_css():
    # https://github.com/widgetti/ipyreact/issues/39
    from IPython.display import HTML, display
    from pathlib import Path

    p_css = Path(STATIC_FILES / "reactable-py.esm.css")

    display(
        HTML(
            f"""
    <style>
    {p_css.read_text()}
    </style>
    """
        )
    )


class BigblockWidget(ipyreact.Widget):
    _esm = Path(str(STATIC_FILES / "reactable-py.esm.js"))

    def tagify(self) -> str:
        # to appease htmltools
        return str(self)

    # def to_tag(self):
    #    return htmltool.Tag("Reactable", )


def bigblock(props: Props):

    return BigblockWidget(props=props.to_props())


class RT:
    props: Props
    widget: "None | BigblockWidget"

    def __init__(self, props: Props):
        self.props = Props
        self._widget = None

    def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None:
        # TODO: note that this means updates to props won't affect widget
        if self._widget is not None:
            return self._widget._repr_mimebundle_(**kwargs)

        self._widget = BigblockWidget(props=self.props.to_props())
        return self._widget._repr_mimebundle_(**kwargs)
