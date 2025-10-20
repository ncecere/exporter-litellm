# Changelog

All notable changes to the LiteLLM Prometheus Exporter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-10

### Added

- First stable release
- Published Docker container to GitHub Container Registry (GHCR)
- Container available at ghcr.io/ncecere/exporter-litellm:v1.0.0

## [0.4.1] - 2024-12-07

### Fixed

- Added __main__.py to make package directly executable
- Updated Dockerfile to properly handle Python package structure
- Fixed Docker container execution by correcting module path

## [0.4.0] - 2024-12-07

### Changed

- Restructured project into a proper Python package under src/litellm_exporter/
- Split monolithic exporter into modular components:
  - config/: Configuration management
  - database/: Database connection handling
  - metrics/: Prometheus metrics and collector
  - queries/: SQL query definitions
- Updated Dockerfile to use new package structure

### Fixed

- Fixed budget metrics query to properly use correct tables with budget_id relationships:
  - Now using LiteLLM_EndUserTable for user budgets
  - Now using LiteLLM_TeamMembership for team budgets
  - Now using LiteLLM_OrganizationMembership for organization budgets

### Removed

- Removed root litellm_exporter.py in favor of proper package structure

## [0.3.3] - 2024-01-09

### Fixed

- Fixed rate limits query to properly handle blocked status from different tables
- Updated blocked status handling for users and teams
- Improved error handling for database queries

## [0.3.2] - 2024-01-09

### Added

- ENV_VARS.md with comprehensive documentation of all environment variables
- Best practices for environment variable configuration
- Example configurations for different deployment scenarios

## [0.3.1] - 2024-01-09

### Fixed

- Fixed time window parameter not being passed correctly to spend metrics query

## [0.3.0] - 2024-01-09

### Added

- Repository configuration files:
  - .gitignore for Python projects
  - .gitattributes for line ending handling
  - .editorconfig for consistent coding styles
  - pyproject.toml for Python tools configuration
  - .pre-commit-config.yaml for code quality checks
- POSTGRES_SETUP.md with detailed instructions for creating read-only database users
- Security best practices documentation
- Development environment configuration

### Changed

- Simplified docker-compose.yml to use existing LiteLLM database
- Updated README.md with database security recommendations
- Improved deployment documentation

## [0.2.0] - 2024-01-09

### Added

- Configurable metrics update interval via `METRICS_UPDATE_INTERVAL` environment variable
- Docker Compose support for easier deployment
- GLWT License
- This CHANGELOG file

### Changed

- Updated documentation with new configuration options
- Reorganized Dockerfile environment variables for better clarity

## [0.1.0] - 2024-01-08

### Added

- Initial release of LiteLLM Prometheus Exporter
- Basic metric collection for LiteLLM usage
- Support for spend, token, request, rate limit, cache, budget, error, entity, API key, and model metrics
- Configurable time windows for different metric types
- Docker support
- Comprehensive documentation
- Database connection pooling
- Health checks
- Prometheus and Grafana integration examples
