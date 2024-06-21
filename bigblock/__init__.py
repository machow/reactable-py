from .models import Props
from .widgets import BigblockWidget


def bigblock(props: Props):

    return BigblockWidget(props=props.to_props())
