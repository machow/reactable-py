from __future__ import annotations

from .models import Props
from .widgets import BigblockWidget, embed_css
from .options import options

__all__ = [
    "bigblock",
    "options",
    "Props",
]


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
