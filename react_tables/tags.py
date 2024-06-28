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
        "attribs": process_attrs(el.attrs),
        "children": [to_hydrate_format(child) for child in el.children],
    }


def process_attrs(attrs: dict):
    res = {k: v if k != "style" else as_react_style(v) for k, v in attrs.items()}

    return res


def as_react_style(style: str | dict) -> dict:
    if not isinstance(style, str):
        return style

    pairs = [pair.split(":") for pair in style.split(";") if pair]
    props = {}
    for pair in pairs:
        if len(pair) == 2:
            name, value = pair
            props[name.strip()] = value.strip()
        else:
            raise ValueError(f"Invalid style pair: {pair}\n\nIn style: {style}")
    return props


# R CODE
# asReactStyle <- function(style) {
#   if (!is.character(style)) {
#     return(style)
#   }
#   pairs <- strsplit(unlist(strsplit(style, ";")), ":")
#   if (length(pairs) > 0) {
#     pairs <- Reduce(function(props, pair) {
#       if (length(pair) == 2) {
#         name <- trimws(pair[[1]])
#         value <- trimws(pair[[2]])
#         props[[name]] <- value
#       }
#       props
#     }, pairs, list())
#   }
#   pairs
# }
#
# # Backport for R 3.1
# trimws <- function(x) {
#   x <- sub("[ \t\r\n]+$", "", x, perl = TRUE)
#   sub("^[ \t\r\n]+", "", x, perl = TRUE)
# }
#
