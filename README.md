# ecoinvent_migrate

[![PyPI](https://img.shields.io/pypi/v/ecoinvent_migrate.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/ecoinvent_migrate.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/ecoinvent_migrate)][pypi status]
[![License](https://img.shields.io/pypi/l/ecoinvent_migrate)][license]

[![Read the documentation at https://ecoinvent_migrate.readthedocs.io/](https://img.shields.io/readthedocs/ecoinvent_migrate/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/ecoinvent_migrate/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/ecoinvent_migrate/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/ecoinvent_migrate/
[read the docs]: https://ecoinvent_migrate.readthedocs.io/
[tests]: https://github.com/brightway-lca/ecoinvent_migrate/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/ecoinvent_migrate
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

`ecoinvent_migrate` downloads the change report annex Excel files from ecoinvent, and turns them
into something usable - [Randonneur migration files](https://github.com/brightway-lca/randonneur).

## Installation

You can install _ecoinvent_migrate_ via [pip] from [PyPI]:

```console
$ pip install ecoinvent_migrate
```

## Usage

Migration are from one release to the next, e.g. from 3.5 to 3.6. There are separate files, and
separate functions, for technosphere and biosphere edges.

```python
from ecoinvent_migrate import *
filepath = generate_technosphere_mapping("3.7.1", "3.8")
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [BSD 3 Clause license][License],
_ecoinvent_migrate_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.

<!-- github-only -->

[command-line reference]: https://ecoinvent_migrate.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/ecoinvent_migrate/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/ecoinvent_migrate/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/ecoinvent_migrate/issues

## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_ecoinvent_migrate
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
