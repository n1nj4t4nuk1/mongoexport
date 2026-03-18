
.PHONY: install
install:
	python3 -m venv venv && \
	. venv/bin/activate && \
	python3 -m pip install --upgrade pip && \
	python3 -m pip install -e .

.PHONY: build
build:
	python3 -m pip install -U build twine && \
	python3 -m build

.PHONY: test
test:
	python3 -m pytest -v
