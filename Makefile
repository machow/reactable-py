LIBRARY_DIR=$(PWD)/reactable
REACTABLE_DIR=tmp/reactable

all: reactable/static/reactable-py.esm.js

setup:
	mkdir -p tmp/reactable
	git clone https://github.com/machow/reactable.git tmp/reactable

docs-build:
	cd docs && quarto render

docs-reference:
	quartodoc build --config docs/_quarto.yml

reactable/static/reactable-py.esm.%: 
	cd tmp/reactable
	npx esbuild \
      $(REACTABLE_DIR)/srcjs/index2.js \
	  --bundle --outfile=$(LIBRARY_DIR)/static/reactable-py.esm.js --format=esm \
	  --target=esnext \
	  --loader:.js=jsx 
	  #--banner:js='import * as requireReact from "react"; import * as requireReactDom from "react-dom"; function require(m) { if (m === "react") return requireReact; if (m === "react-dom") return requireReactDom; throw new Error("Unknown module" + m); }'
