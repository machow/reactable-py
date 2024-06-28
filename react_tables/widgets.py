import ipyreact

from importlib_resources import files
from pathlib import Path

STATIC_FILES = files("react_tables.static")


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
