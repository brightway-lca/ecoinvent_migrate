# `ecoinvent_migrate` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
