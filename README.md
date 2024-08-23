# reactable-py

reactable generates interactive tables in Python.
It's a port of the R package [reactable](https://github.com/glin/reactable) by [@glin](https://github.com/glin).

See these handy documentation pages:

- [📚 User guide](https://machow.github.io/reactable-py/get-started)
- [🧩 Examples](https://machow.github.io/reactable-py/demos/)

## Features

- **controls**: sorting, filtering, and pagination.
- **structure**: grouping, aggregating, expanding rows.
- **format**: represent numbers, dates, currencies.
- **style**: conditional styling for headers, cell values, and more.

## Installing

```bash
pip install reactable
```

## Basic use

Use with jupyter notebooks or quarto documents (.qmd) to display tables.

```python
from reactable import Reactable, embed_css
from reactable.data import sleep

embed_css()

Reactable(sleep)
```

![reactable example table using the sleep dataset](https://machow.github.io/reactable-py/assets/sleep-table.png)

## Learn more

**Essentials**

- [Code basics](https://machow.github.io/reactable-py/get-started/code-structure.html)
- [Displaying tables](https://machow.github.io/reactable-py/get-started/display-export.html)

**Controls**

- [Sorting](https://machow.github.io/reactable-py/get-started/controls-sorting.html)
- [Filtering](https://machow.github.io/reactable-py/get-started/controls-filtering.html)
- [Searching](https://machow.github.io/reactable-py/get-started/controls-searching.html)
- [Pagination](https://machow.github.io/reactable-py/get-started/controls-pagination.html)
- [Column resizing](https://machow.github.io/reactable-py/get-started/controls-resizing.html)
- [Cell click actions](https://machow.github.io/reactable-py/get-started/controls-click-actions.html)

**Structure**

- [Column headers](https://machow.github.io/reactable-py/get-started/structure-headers.html)
- [Row groups and aggregation](https://machow.github.io/reactable-py/get-started/structure-grouping.html)
- [Expandable details](https://machow.github.io/reactable-py/get-started/structure-details.html)
- [Footers](https://machow.github.io/reactable-py/get-started/structure-footers.html)
- [Rownames](https://machow.github.io/reactable-py/get-started/structure-rownames.html)

**Format**

- [Column formatting](https://machow.github.io/reactable-py/get-started/format-columns.html)
- [Column aggregated cells](https://machow.github.io/reactable-py/get-started/format-aggregated.html)
- [Rendering cells](https://machow.github.io/reactable-py/get-started/format-cell.html)
- [Rendering header and footer](https://machow.github.io/reactable-py/get-started/format-header-footer.html)
- [Rendering details](https://machow.github.io/reactable-py/get-started/format-details.html)

**Style**

- [Table styling](https://machow.github.io/reactable-py/get-started/style-table.html)
- [Conditional styling (python)](https://machow.github.io/reactable-py/get-started/style-conditional.html)
- [Custom sort indicators](https://machow.github.io/reactable-py/get-started/style-custom-sort-indicators.html)
- [Theming](https://machow.github.io/reactable-py/get-started/style-theming.html)

**Extra**

- [Javascript formatters](https://machow.github.io/reactable-py/get-started/format-custom-rendering.html)
- [Javascript styling](https://machow.github.io/reactable-py/get-started/style-conditional-js.html)
- [Javascript filters](https://machow.github.io/reactable-py/get-started/extra-advanced-filters.html)
- [Using reactable with htmltools](https://machow.github.io/reactable-py/get-started/extra-htmltools.html)
