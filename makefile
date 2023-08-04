.PHONY: style check test docs copy-docs docs-deploy

check_dirs := . 

style: 
	ruff $(check_dirs) --fix
check: 
	ruff $(check_dirs) 
test: 
	pytest


copy-docs:
	cp -r notebooks/* docs/examples/

docs:
	$(MAKE) copy-docs
	mkdocs serve

docs-build:
	$(MAKE) copy-docs
	mkdocs build

docs-deploy:
	$(MAKE) copy-docs
	mkdocs gh-deploy --force