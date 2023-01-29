# Welcome to Python Project Template

This is a template for Python projects. It is intended to be a starting point for new projects, and provides a structure that can be used consistently across projects.

## Getting Started

Fork the repository and clone it to your local machine. Then, run the following commands to rename all folders, files and variable from `myproject` to the name of your project:
  
```bash
newproject="mynewproject"
# rename and delete the project folder
mv  myproject/ mynewproject/
# rename the project in the pyproject.toml file
sed -i "" "s/myproject/mynewproject/g" pyproject.toml
```

Adjust documentation in `docs/index.md` and `README.md` to your needs.


## Scipts

The following scripts are available:
- `make style`: run the ruff fix
- `make check`: run the ruff check
- `make test`: run the tests

## Features

- [x] Python version: 3.8
- [x] project structure: `pyproject.toml` and `src/`
- [x] Building system: [Hatch](https://hatch.pypa.io/latest/)
- [x] lint, format, sorting with [ruff](https://github.com/charliermarsh/ruff)
- [x] testing with [pytest](https://docs.pytest.org/en/stable/)
- [x] cli suppored with `cli.py` file and installed automatically
- [x] type checking with [mypy](https://mypy.readthedocs.io/en/stable/) -> remove `mypy` from `pyproject.toml` and `makefile` if not needed
- [x] documentation with [mkdocs](https://www.mkdocs.org/) with automatic deployment to github pages through and support for docstrings using (https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html). More extension here: https://chrieke.medium.com/the-best-mkdocs-plugins-and-customizations-fc820eb19759


## Acknowledgements

This project was insipred by the structure of [fastapi](https://github.com/tiangolo/fastapi/blob/master/pyproject.toml) and created with [Hatch](https://hatch.pypa.io/latest/).

## Code

Link to a function in the code:
[`Object 1`][myproject.utils.fancy_function]