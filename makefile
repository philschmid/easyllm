.PHONY: quality style unit-test integ-test

check_dirs := src 

# run tests

unit-test:
	python3 -m pytest -s -v ./tests/unit

integ-test:
	python3 -m pytest -s -v ./tests/integ/

# Check that source code meets quality standards

quality:
	black --check --line-length 119 --target-version py36 $(check_dirs)
	isort --check-only $(check_dirs)
	flake8 src

# Format source code automatically

style:
	black --line-length 119 --target-version py36 $(check_dirs)
	isort $(check_dirs)