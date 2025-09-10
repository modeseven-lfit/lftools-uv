<!--
SPDX-License-Identifier: EPL-1.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# LF Tools UV

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/modeseven-lfit/lftools-uv/badge)](https://scorecard.dev/viewer/?uri=github.com/modeseven-lfit/lftools-uv)
[![License: EPL-1.0](https://img.shields.io/badge/License-EPL--1.0-blue.svg)](https://www.eclipse.org/legal/epl-v10.html)
[![PyPI](https://img.shields.io/pypi/v/lftools-uv.svg?label=PyPi)](https://pypi.org/project/lftools-uv/)
[![TestPyPI](https://img.shields.io/pypi/v/lftools-uv.svg?label=TestPyPi&pypiBaseUrl=https://test.pypi.org)](https://test.pypi.org/project/lftools-uv/)
[![CodeQL](https://github.com/modeseven-lfit/lftools-uv/actions/workflows/codeql.yml/badge.svg)](https://github.com/modeseven-lfit/lftools-uv/actions/workflows/codeql.yml)

This project's documentation is available on ReadTheDocs (RTD) and GitHub Pages:

- **Official Documentation**: <https://lftools-uv.readthedocs.io>
- **GitHub Pages**: <https://modeseven-lfit.github.io/lftools-uv/>

LF Tools UV is a collection of scripts and utilities that are useful to Linux
Foundation projects' CI and Releng related activities. We try to create
these tools to be as generic as possible such that they are reusable in other
CI environments.

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

### Using uvx (Recommended for CI/CD)

[uvx](https://docs.astral.sh/uv/guides/tools/) is ideal for CI/CD environments
and one-off executions where you want to run lftools-uv without affecting the
existing Python environment. It creates an isolated virtual environment for
each execution, preventing dependency conflicts with other tools in your pipeline.

#### Basic Usage

Run lftools-uv commands directly without installation:

```bash
# Basic command execution
uvx lftools-uv version

# Run with help
uvx lftools-uv --help
```

#### Using Optional Dependencies

When using features that require optional dependencies (like LDAP or
OpenStack), you need to specify the extras:

```bash
# For LDAP functionality - note the quotes to prevent shell expansion
uvx "lftools-uv[ldap]" ldap --help

# For OpenStack functionality
uvx "lftools-uv[openstack]" openstack --help

# Combined extras
uvx "lftools-uv[ldap,openstack]" --help

# All extras for full functionality
uvx "lftools-uv[all]" --help
```

#### Alternative uvx Syntax

You can also use the `--from` flag for clarity:

```bash
# Same as the above
uvx --from "lftools-uv[ldap]" lftools-uv ldap csv mygroup
uvx --from "lftools-uv[openstack]" lftools-uv openstack --help
```

#### CI/CD Pipeline Examples

**GitHub Actions:**

```yaml
- name: Deploy artifacts with lftools-uv
  run: |
    uvx lftools-uv deploy nexus-zip \
      --nexus-url ${{ secrets.NEXUS_URL }} \
      --nexus-repo releases \
      ./artifacts/*.zip
```

**GitLab CI:**

```yaml
deploy:
  script:
    - uvx "lftools-uv[all]" deploy logs --help
    - uvx lftools-uv sign sigul ./artifacts/
```

**Jenkins Pipeline:**

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sh 'uvx lftools-uv version'
                sh 'uvx "lftools-uv[ldap]" ldap csv project-committers'
            }
        }
    }
}
```

#### Benefits of uvx in CI/CD

- **Isolation**: No interference with existing Python packages in the CI environment
- **Speed**: Automatic caching of environments between runs
- **Consistency**: Same tool version across different pipeline stages
- **No Setup**: No need to manage virtual environments or installations
- **Clean**: Environments are automatically cleaned up after execution

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
