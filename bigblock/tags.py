from __future__ import annotations

import htmltools


# the react app expects html data to be in this dict
# format, so it can manually create the html elements
# in react
def to_hydrate_format(el: htmltools.Tag | str):
    if not isinstance(el, htmltools.Tag):
        return el

    return {
        "name": el.name,
        "attribs": el.attrs,
        "children": [to_hydrate_format(child) for child in el.children],
    }
