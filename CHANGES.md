# `ecoinvent_migrate` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

* Technosphere migrations which change unit are skipped, as the change report has no conversion factors. Removes e.g. kg of electric arc furnace dust becoming hectares of land use change (3.9.1 → 3.10), kg of liquid packaging board becoming units of beverage cartons (3.9.1 → 3.10), and kWh of compressor station electricity becoming MJ of natural gas burned (3.8 → 3.9). If any target of a disaggregation changes unit, the whole disaggregation is skipped
* Biosphere flow changes found by comparing release data are skipped when the unit changes, except for `m3` → `Sm3`. Removes Manganese-55 in kBq becoming Manganese in kg (3.9.1 → 3.10)

## [0.7] - 2026-11-05

### Added

* Support ecoinvent 3.12 → 3.13 technosphere migrations, including patches for co-products missing from the change report ([#22](https://github.com/brightway-lca/ecoinvent_migrate/pull/22))
* Patches can list the system models they apply to with `system_models`; patches without it still apply to all system models. The 3.10.1 → 3.11 replacement patches that were only correct for some system models are now restricted ([#28](https://github.com/brightway-lca/ecoinvent_migrate/pull/28))
* Warning when a replacement patch gives a dataset which isn't in the release ([#28](https://github.com/brightway-lca/ecoinvent_migrate/pull/28))
* `log_level` argument for `generate_technosphere_mapping`, `generate_biosphere_mapping` and `configure_logs` to set the console log level ([#27](https://github.com/brightway-lca/ecoinvent_migrate/pull/27))

### Changed

* Technosphere migrations whose source dataset isn't in the source system model are skipped instead of written ([#22](https://github.com/brightway-lca/ecoinvent_migrate/pull/22))

### Fixed

* Equal-allocation disaggregation repeated the last target ([#21](https://github.com/brightway-lca/ecoinvent_migrate/pull/21))
* 3.10.1 → 3.11 replacement patches broke valid migrations in consequential and EN15804, and for source patches the migration was then removed entirely ([#28](https://github.com/brightway-lca/ecoinvent_migrate/pull/28))
* 3.9.1 → 3.10 missing-data patches used the wrong field labels ([#24](https://github.com/brightway-lca/ecoinvent_migrate/pull/24))
* Whitespace in change report values, e.g. trailing non-breaking spaces, gave migration targets which don't exist ([#26](https://github.com/brightway-lca/ecoinvent_migrate/pull/26))
* Errors raised while applying technosphere patches were silently ignored ([#28](https://github.com/brightway-lca/ecoinvent_migrate/pull/28))
* Handle biosphere change reports with missing or mislabelled elementary flow UUIDs ([#23](https://github.com/brightway-lca/ecoinvent_migrate/pull/23))
* Biosphere change report comments are stripped safely ([#11](https://github.com/brightway-lca/ecoinvent_migrate/pull/11))

### [0.6.2] - 2025-03-25

* Fix biosphere mapping creation compatibility problem with new `randonneur` versions

### [0.6.1] - 2025-03-25

* Add missing `pandas` dependency

## [0.6] - 2025-03-25

* Examine technosphere changes in release data to autogenerate more changes and log cases where manual fixes are necessary
* Remove dependency on any Brightway libraries
* Compatibility with ecoinvent 3.11 change report file format
* Support multiple manual patch file formats
* Move to `src` layout
* Fix compatibility problem with new `randonneur` versions

## [0.5] - 2024-09-25

* Don't assume `delete` section present in biosphere mappings

## [0.4.1] - 2024-09-05

* Use `conversion_factor` instead of `allocation` for `replace` transformations

## [0.4.0] - 2024-08-30

* Add biosphere changes not listed in change report
* Add additional patches for technosphere

## [0.3.0] - 2024-08-13

* Patch missing ecoinvent migrations

## [0.2.0] - 2024-06-14

* Skip empty technosphere transformations
* Improve README
* Add common output files

## [0.1.0] - 2024-06-14

First release
