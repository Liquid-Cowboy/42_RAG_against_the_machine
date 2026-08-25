LINT_FLAGS := --warn-return-any
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs
--check-untyped-defs

install:

run:

debug:

clean:

lint:

lint-strict:
	flake8 .
	mypy . --strict