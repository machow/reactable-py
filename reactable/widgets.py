from __future__ import annotations

import ipyreact

from importlib_resources import files
from pathlib import Path
from typing import TYPE_CHECKING

STATIC_FILES = files("reactable.static")

if TYPE_CHECKING:
    from .models import Props


# This ensures that the javascript is only loaded once, rather
# than included in every widget instance. Note that
ipyreact.define_module("reactable", Path(str(STATIC_FILES / "reactable-py.esm.js")))


def embed_css():
    # https://github.com/widgetti/ipyreact/issues/39
    from IPython.display import HTML, display
    from pathlib import Path

    p_css = Path(STATIC_FILES / "reactable-py.esm.css")

    # TODO: the link tag exists, because reactable expects it as part
    # of its theme css loading process
    # see https://github.com/glin/reactable/blob/363068caab2fa708b247a4ab0f73cdc694223587/srcjs/theme.js#L239
    display(
        HTML(
            f"""
    <div>
    <style>
    {p_css.read_text()}
    </style>
    <link href="/reactable.css" rel="stylesheet">
    </div>
    """
        )
    )


class ReactableWidget(ipyreact.Widget):
    # _esm = Path(str(STATIC_FILES / "reactable-py.esm.js"))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, _module="reactable", _type="default")

    def tagify(self) -> str:
        # to appease htmltools
        return str(self)

    def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None:
        # import os
        # from reactable import options
        #
        # if options.path_js is not None:
        #     self._esm = options.path_js
        # elif os.environ.get("REACTABLE_PATH_JS"):
        #     self._esm = os.environ["REACTABLE_PATH_JS"]
        return super()._repr_mimebundle_(**kwargs)

    # def to_tag(self):
    #    return htmltool.Tag("Reactable", )


def bigblock(props: Props):

    return ReactableWidget(props=props.to_props())
