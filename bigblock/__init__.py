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
