.PHONY: style check test

check_dirs := . 

style: 
	ruff $(check_dirs) --fix
check: 
	ruff $(check_dirs) 
	mypy $(check_dirs)
test: 
	pytest