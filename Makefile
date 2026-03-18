
.PHONY: deps
deps:
	python3 -m venv venv && \
	. venv/bin/activate && \
	python3 -m pip install --upgrade pip && \
	python3 -m pip install -e .

.PHONY: test
test:
	. venv/bin/activate && python3 -m pytest -v
