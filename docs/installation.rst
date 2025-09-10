.. SPDX-FileCopyrightText: 2025 The Linux Foundation
..
.. SPDX-License-Identifier: EPL-1.0

############
Installation
############

.. note::

    LFtools-uv requires Python 3.8+ and virtual environment isolation.
    https://virtualenv.pypa.io/en/stable/
    Not using proper isolation can have serious negative side effects!

Overview
========

LFtools-uv is available on PyPI and supports different installation methods depending on your use case:

- **uvx**: For CI/CD and one-off executions (recommended for automation)
- **uv pip**: For development and persistent installations (recommended for development)
- **pip**: For traditional Python package management

Using uvx (Recommended for CI/CD)
=================================

`uvx <https://docs.astral.sh/uv/guides/tools/>`_ is the best choice for CI/CD environments and automated workflows where you need isolated execution without affecting the system Python environment.

Prerequisites
-------------

First, install uv (which includes uvx):

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh

Basic Usage
-----------

Run lftools-uv commands without installation:

.. code-block:: bash

   # Execute any lftools-uv command
   uvx lftools-uv version
   uvx lftools-uv --help

   # Deploy artifacts
   uvx lftools-uv deploy nexus-zip --nexus-url https://nexus.example.com artifacts/

Optional Dependencies
---------------------

When using features that require optional dependencies, specify the extras in quotes:

.. code-block:: bash

   # LDAP functionality
   uvx "lftools-uv[ldap]" ldap csv project-committers

   # OpenStack functionality
   uvx "lftools-uv[openstack]" openstack server list

   # Combined extras
   uvx "lftools-uv[ldap,openstack]" --help

   # All functionality
   uvx "lftools-uv[all]" --help

Alternative Syntax
------------------

You can also use the ``--from`` flag for clarity:

.. code-block:: bash

   uvx --from "lftools-uv[ldap]" lftools-uv ldap --help

CI/CD Benefits
--------------

- **Isolation**: No interference with existing Python packages
- **Caching**: Automatic environment caching for faster future runs
- **Consistency**: Same tool version across pipeline stages
- **No Setup**: No virtual environment management required
- **Clean**: Environments automatically cleaned up after execution

Using uv pip (Recommended for Development)
==========================================

For development work or when you need persistent installations, use ``uv pip``:

.. code-block:: bash

   # Install uv first
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create and activate a virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install lftools-uv
   uv pip install lftools-uv

   # Or with all extras for development
   uv pip install "lftools-uv[all]"

Specific Extras
---------------

.. code-block:: bash

   # LDAP support
   uv pip install "lftools-uv[ldap]"

   # OpenStack support
   uv pip install "lftools-uv[openstack]"

   # Development tools
   uv pip install "lftools-uv[dev]"

   # Testing tools
   uv pip install "lftools-uv[test]"

   # Documentation tools
   uv pip install "lftools-uv[docs]"

Using pip (Traditional Method)
==============================

For environments where uv is not available:

.. code-block:: bash

   # Create virtual environment
   python3 -m venv lftools-env
   source lftools-env/bin/activate  # On Windows: lftools-env\Scripts\activate

   # Install lftools-uv
   pip install lftools-uv

   # Or with extras
   pip install "lftools-uv[all]"

System Dependencies
===================

Ubuntu/Debian
-------------

For LDAP functionality on Ubuntu/Debian systems:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install build-essential python3-dev libldap2-dev libsasl2-dev libssl-dev

RHEL/CentOS/Fedora
------------------

For LDAP functionality on RHEL-based systems:

.. code-block:: bash

   sudo yum install gcc python3-devel openldap-devel cyrus-sasl-devel openssl-devel
   # Or on newer systems:
   sudo dnf install gcc python3-devel openldap-devel cyrus-sasl-devel openssl-devel

For Development
===============

When developing lftools-uv itself, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/lfit/lftools-uv.git
   cd lftools-uv

   # Using uv (recommended)
   uv sync --extra dev --extra test --extra docs --extra ldap --extra openstack

   # Or using traditional pip
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[all]"

Verification
============

Verify your installation works:

.. code-block:: bash

   # Check version
   lftools-uv version
   # Alternative method
   uvx lftools-uv version

   # List available commands
   lftools-uv --help

   # Test optional dependencies
   lftools-uv ldap --help  # Shows commands when [ldap] extra installed
   lftools-uv openstack --help  # Shows commands when [openstack] extra installed

Troubleshooting
===============

Common Issues
-------------

**Command not found after installation:**
  Activate your virtual environment or use the full path to the executable.

**LDAP/OpenStack commands show "To activate this interface" message:**
  Install the appropriate extras: ``uv pip install "lftools-uv[ldap]"`` or ``uvx "lftools-uv[ldap]" ...``

**Permission errors:**
  Always use virtual environments. Never install with ``sudo pip``.

**Import errors for optional dependencies:**
  Make sure you installed the correct extras and they're available in your environment.
