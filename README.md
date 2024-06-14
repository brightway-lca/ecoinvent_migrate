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

`ecoinvent_migrate` makes the change report Excel files from ecoinvent usable.

These files are designed to allow for relinking against new versions of ecoinvent, **not** for updating an existing ecoinvent installation.

This library requires a valid ecoinvent license for all functionality.

## Installation

You can install _ecoinvent_migrate_ via [pip] from [PyPI]:

```console
$ pip install ecoinvent_migrate
```

## Usage

Migration are from one release to the next, e.g. from 3.5 to 3.6. There are separate files, and separate functions, for technosphere and biosphere edges. The files produced are serialized to JSON and software agnostic, but play well with the Brightway ecosystem.

### Technosphere

```python
from ecoinvent_migrate import *
filepath = generate_technosphere_mapping("3.7.1", "3.8")
```

This produces a file which has allows foreground inventory datasets which linked to 3.7.1 to find suitable replacement datasets in 3.8. The produced file looks like this:

```json
{
  "name": "ecoinvent-3.7.1-cutoff-ecoinvent-3.8-cutoff",
  "licenses": [
    {
      "name": "CC BY 4.0",
      "path": "https://creativecommons.org/licenses/by/4.0/",
      "title": "Creative Commons Attribution 4.0 International"
    }
  ],
  "version": "1.0.0",
  "description": "Data migration file from ecoinvent-3.7.1-cutoff to ecoinvent-3.8-cutoff generated with `ecoinvent_migrate` version 0.1.0 at 2024-06-14T12:17:38.900471+00:00",
  "homepage": "https://github.com/brightway-lca/ecoinvent_migrate",
  "created": "2024-06-14T12:17:38.900471+00:00",
  "contributors": [
    {
      "title": "ecoinvent association",
      "path": "https://ecoinvent.org/",
      "role": "author"
    },
    {
      "title": "Chris Mutel",
      "path": "https://chris.mutel.org/",
      "role": "wrangler"
    }
  ],
  "replace": [
    {
      "source": {
        "name": "assembly of generator and motor, auxilliaries and energy use, heat and power co-generation unit, 160kW electrical",
        "location": "RoW",
        "reference product": "assembly of generator and motor, auxilliaries and energy use, for heat and power co-generation unit, 160 KW electrical",
        "unit": "unit"
      },
      "target": {
        "name": "assembly of generator and motor, auxilliaries and energy use, heat and power co-generation unit, 160kW electrical",
        "location": "RoW",
        "reference product": "assembly of generator and motor, auxilliaries and energy use, heat and power co-generation unit, 160kW electrical",
        "unit": "unit"
      }
    }
  ],
  "disaggregate": [
    {
      "source": {
        "name": "application of plant protection product, by field sprayer",
        "location": "RoW",
        "reference product": "application of plant protection product, by field sprayer",
        "unit": "ha"
      },
      "targets": [
        {
          "name": "application of plant protection product, by field sprayer",
          "location": "Canada without Quebec",
          "reference product": "application of plant protection product, by field sprayer",
          "unit": "ha",
          "allocation": 0.025737164985667214
        },
        {
          "name": "application of plant protection product, by field sprayer",
          "location": "RoW",
          "reference product": "application of plant protection product, by field sprayer",
          "unit": "ha",
          "allocation": 0.9742628350143328
        }
      ]
    }
  ]
}
```

To use this file, you will need to take different actions for the two verbs. For `replace`, edges in your foreground which link to an ecoinvent dataset with the same attributes as in the `source` section can be replaced one-to-one with an edge to an ecoinvent process from the later release whose attributes match those in the `target` section. For the `disaggregate` verb, you will need to split the initial foreground edge into two or more edges, and scale the original amount and uncertainty information by the `allocation` value.

If you are using Brightway, there are convenience functions in `bw_migrations` and cached migration files which will be used for you automatically.

Migrations are designed and only tested for forward progress, i.e. from one release to the next subsequent release. Going in the opposite direction is not recommended.

You can't skip across multiple releases - attempting to do so will raise a `VersionJump` error:

```python
>>> generate_technosphere_mapping("3.7.1", "3.9.1")
---------------------------------------------------------------------------
VersionJump:
Source (3.7.1) and target (3.9.1) don't have a change report.
Usually this is the case when one jumps across multiple releases, but not always.
For example, the change report for 3.7.1 is from 3.6, not 3.7.
The change report we have available is:
Change Report Annex v3.9 - v3.9.1.xlsx
```

Technosphere mapping files are system model specific, and the default system model is `cutoff`. You can specify a different system model following the `ecoinvent_interface` [function specification](https://github.com/brightway-lca/ecoinvent_interface?tab=readme-ov-file#database-releases) with the `system_model` parameters, e.g. `generate_technosphere_mapping(..., system_model='apos')`.

### Biosphere

The same procedure applies for biosphere edges:

```python
from ecoinvent_migrate import *
filepath = generate_biosphere_mapping("3.9.1", "3.10")
```

This produces a data file like:

```json
{
  "name": "ecoinvent-3.9.1-biosphere-ecoinvent-3.10-biosphere",
  "licenses": [
    {
      "name": "CC BY 4.0",
      "path": "https://creativecommons.org/licenses/by/4.0/",
      "title": "Creative Commons Attribution 4.0 International"
    }
  ],
  "version": "1.0.0",
  "description": "Data migration file from ecoinvent-3.9.1-biosphere to ecoinvent-3.10-biosphere generated with `ecoinvent_migrate` version 0.1.0 at 2024-06-14T10:26:46.339261+00:00",
  "homepage": "https://github.com/brightway-lca/ecoinvent_migrate",
  "created": "2024-06-14T10:26:46.339261+00:00",
  "contributors": [
    {
      "title": "ecoinvent association",
      "path": "https://ecoinvent.org/",
      "role": "author"
    },
    {
      "title": "Chris Mutel",
      "path": "https://chris.mutel.org/",
      "role": "wrangler"
    }
  ],
  "replace": [
    {
      "source": {
        "uuid": "4f777e05-70f9-4a18-a406-d8232325073f",
        "name": "2,4-D amines"
      },
      "target": {
        "uuid": "b6b4201e-0561-5992-912f-e729fbf04e41",
        "name": "2,4-D dimethylamine salt"
      }
    }
  ],
  "delete": [
    {
      "source": {
        "uuid": "91861063-1826-4860-9957-7c5bde5817a6",
        "name": "Salt water (obsolete)"
      },
      "comment": "There is no salt water flow in ecoinvent."
    }
  ]
}
```

By default, the `delete` verb is skipped, as this is a more cautious approach to existing data. To have the `delete` section included, call `generate_biosphere_mapping(..., keep_deletions=True)`.

### Common input arguments

Both `generate_technosphere_mapping` and `generate_biosphere_mapping` accept the following input arguments:

* source_version (str): String representation of an ecoinvent version, e.g. "3.8"
* target_version (str): String representation of an ecoinvent version, e.g. "3.8"
* ecoinvent_username (str, optional): Ecoinvent account username
* ecoinvent_password (str, optional): Ecoinvent account password
* write_logs (bool, default `True`): Create detailed and high-level logs during mapping file creation
* output_directory (`pathlib.Path`, default is `platformlibs.user_data_dir`): Directory for the result files

Note that we **strongly recommend** [permanently setting your ecoinvent user credentials](https://github.com/brightway-lca/ecoinvent_interface?tab=readme-ov-file#authentication-via-settings-object).

The following input parameters should normally be left to their default values:

* project_name (str): The Brightway project name into which we install ecoinvent releases to check change report data validity.
* output_version (str, default is "1.0.0"): [Datapackage version number](https://specs.frictionlessdata.io/data-package/#version)
* licenses (list, default is CC-BY): Licenses following the [frictionless data datapackage standard](https://specs.frictionlessdata.io/data-package/#licenses)
* description (str, default is auto-generated): Description of generated datapackage.

### How does this library work?

We start by using [ecoinvent_interface](https://github.com/brightway-lca/ecoinvent_interface) to download the change report Excel file, and the two ecoinvent releases (source and target). We need to download the ecoinvent data because the change report is for the unlinked and unallocated "master" data; there are some changes needed for the specific system models.

For biosphere mapping, we read the Excel file, search around for the correct worksheet and column names, and map the data to "replace" and "delete" sections. This is pretty simple.

For technosphere mapping, we need to check if the indicated datasets are actually in `GLO` or in `RoW` (and analogously in `RER` / `RoE`.) We do this by finding the corresponding datasets in the actual database releases. We also need to use the actual data to look up the allocation factors when a single dataset is split into multiple datasets.

Not every line in the change report Excel file can be used, either because of the specifics of the system model, or some other unknown discrepancy. These exceptions are logged to both the log files and `sys.stderr`:

```console
2024-06-14 14:17:38.641 | WARNING  | ecoinvent_migrate.wrangling:resolve_glo_row_rer_roe:219 -
    Target process given in change report but missing in ecoinvent-3.8-cutoff lookup:
    {'name': 'rutile production, synthetic, 95% titanium dioxide, Benelite process',
     'location': 'GLO',
     'reference product': 'rutile, 95% titanium dioxide', 'unit': 'kg'}
```

Once the given change data is segregated and cleaned, it is serialized to JSON.

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
