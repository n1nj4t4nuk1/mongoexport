# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small Python CLI/library (`mongoexport` on PyPI) that streams a MongoDB collection to a JSON file
using `_id`-based pagination, per-batch delays, and retries. Not related to MongoDB's own
`mongoexport` binary despite the identical name — be careful when searching for docs or when
testing the installed console script on a machine that also has MongoDB Database Tools.

## Commands

```bash
make install     # python3 -m venv venv + pip install -e .
make build       # pip install -U build twine && python3 -m build  (used by CI on release)
make test        # python3 -m pytest -v
python -m mongoexport --uri ... --db ... --collection ...   # same entry point as the `mongoexport` script
```

There are currently **no tests and no test dependencies declared** — `make test` and the README's
`pip install -e ".[dev]"` both refer to things that don't exist yet (`pyproject.toml` has no
`[project.optional-dependencies]`). If you add tests, add the extra and install pytest explicitly;
a single test then runs as `python3 -m pytest -v tests/test_exporter.py::test_name`.

There is also **no linter, formatter, or type-checker configured** anywhere — no `[tool.ruff]`,
`[tool.black]`, `[tool.mypy]`, or `[tool.pytest]` in `pyproject.toml`, and no `setup.cfg`, `tox.ini`,
or pre-commit config. Existing lines run to ~106 characters, so don't assume an 88-column formatter
and reflow files. And nothing runs tests or lints in CI: `publish.yml` fires only on a published
release, and the sole push-triggered workflow is the Codeberg mirror (a build-and-test job was
removed deliberately in `460ac33`).

## Architecture

Four modules, one data path: `cli.parse_arguments()` → `argparse.Namespace` → `exporter.export_data(args)`.

- **`cli.py`** owns every tunable. `export_data` reads them off the namespace (`args.batch_size`,
  `args.retry_delay`, …), so the public API is coupled to CLI flag names. Adding an option means
  adding the `add_argument` here *and* consuming `args.<name>` in the exporter; library callers must
  construct a Namespace with the full set of attributes (see the docstring in `__init__.py`).
- **`exporter.py`** is the whole implementation. Two things to preserve when editing:
  - **Keyset pagination, not skip/limit.** Each page queries `{"_id": {"$gt": last_id}}` sorted by
    `_id` ascending, carrying `last_id` from the previous batch's final document. This assumes `_id`
    values are mutually comparable; a collection with mixed `_id` BSON types will page in BSON type
    order, and a custom non-monotonic `_id` scheme can silently skip documents. Each page is a fresh
    `find()` rather than one long-lived cursor, so the `--delay` sleeps between batches carry no
    cursor-timeout exposure — a refactor to a single streaming cursor would reintroduce that.
  - **Hand-rolled streaming JSON array.** The output file is opened once; `"["` is written up front,
    each batch is serialized with `bson.json_util.dumps` and then written as `json_str[1:-1]` to strip
    the array brackets, with a `,` inserted between batches via the `first_batch` flag, and `"]"` at
    the end. This keeps memory bounded to one batch. Any change to serialization must keep the
    bracket/comma bookkeeping intact or the file stops being valid JSON.
  - Retries live in `_fetch_batch_with_retries` and only cover `PyMongoError` from building/draining
    the cursor. Exhausting retries re-raises, but `export_data` wraps everything in
    `except Exception: logger.error(...)` — it never re-raises and the CLI always exits 0. A failure
    mid-export therefore leaves a **truncated file with no closing `]`**. Treat both the swallowed
    exception and the missing exit code as known gaps, not as intentional design to preserve.
- **`logging_config.py`** is called only from `cli.main()`. Library modules use
  `logging.getLogger(__name__)` and never configure handlers, so importing `export_data` directly
  produces no output until the caller sets up logging.

## Constraints to respect when editing

- **`requires-python = ">=3.8"`.** Annotations use `typing.Optional/Dict/List` throughout and there
  is currently zero PEP 604 (`X | None`) or PEP 585 (`list[...]`) syntax — keep it that way, since
  both break on 3.8. Likewise the floor is `pymongo>=3.12`, so pymongo-4-only APIs are off limits.
- **Packages are listed explicitly**, not auto-discovered: `[tool.setuptools] packages = ["mongoexport"]`.
  A new subpackage (say `mongoexport/formats/`) will import fine from a `-e` install but silently
  ship missing from the wheel until it's added to that list. `setup.py` is only a bare `setup()`
  compatibility shim — it configures nothing.

## Release flow

`pyproject.toml` version and `mongoexport/__init__.py`'s `__version__` are separate strings and are
**currently out of sync** (0.1.3 vs 0.1.0). Bump both when releasing.

Publishing is triggered by a published GitHub Release (`.github/workflows/publish.yml`): `make build`
→ `twine check dist/*` → `pypa/gh-action-pypi-publish` via PyPI trusted publishing (OIDC,
`id-token: write`, no API token). Every push also mirrors the repo to Codeberg via
`.github/workflows/mirror-codeberg.yml`.
