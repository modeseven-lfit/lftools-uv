<!--
SPDX-License-Identifier: EPL-1.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# LF Tools UV

This project's documentation is available on ReadTheDocs (RTD) and GitHub Pages:

- **Official Documentation**: <https://lf-releng-tools.readthedocs.io>
- **GitHub Pages**: <https://modeseven-lfit.github.io/lftools-uv/>

LF Tools UV is a collection of scripts and utilities that are useful to Linux
Foundation projects' CI and Releng related activities. We try to create
these tools to be as generic as possible such that they are reusable in other
CI environments.

## CLI Interface

**lftools-uv** uses Typer as the CLI library. For CI/CD environments that
require the previous Click-based output format, use `LEGACY_CLI=1`.

## Installation

### Using uv (Recommended)

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

1. Install uv:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install lftools-uv:

   ```bash
   uv pip install lftools-uv
   ```

3. Or install with all extras for development:

   ```bash
   uv pip install "lftools-uv[all]"
   ```

### Using pip

```bash
pip install lftools-uv
```

## Development Setup

### Prerequisites

- Python 3.8+
- uv (recommended) or pip

### Quick Start with uv

1. Clone the repository:

   ```bash
   git clone https://github.com/lfit/lftools-uv.git
   cd lftools-uv
   ```

2. Install development dependencies:

   ```bash
   make install-dev
   # or manually:
   uv sync --extra dev --extra test --extra docs --extra ldap --extra openstack
   ```

3. Run tests:

   ```bash
   make test
   # or manually:
   uv run pytest
   ```

4. Format and lint code:

   ```bash
   make format
   make lint
   ```

### Available Make Targets

- `make help` - Show all available targets
- `make install` - Install project dependencies
- `make install-dev` - Install with all development dependencies
- `make test` - Run tests
- `make lint` - Run linting
- `make format` - Format code
- `make build` - Build package
- `make docs` - Build documentation
- `make clean` - Clean build artifacts
- `make all` - Run full development pipeline

### Ubuntu Dependencies

For development on Ubuntu, you may need:

- build-essential
- python3-dev
- libldap2-dev
- libsasl2-dev
- libssl-dev

## Repository Information

### Development Repository

For development and testing, we maintain this project at:

- **Development**: `https://github.com/modeseven-lfit/lftools-uv.git`

### Production Repository

Once tested and approved, we publish releases from:

- **Production**: `https://github.com/lfit/lftools-uv.git`

### Local Git Setup

Configure your local git remote for the development repository:

```bash
git remote -v
# origin  https://github.com/modeseven-lfit/lftools-uv.git (fetch)
# origin  https://github.com/modeseven-lfit/lftools-uv.git (push)
```
