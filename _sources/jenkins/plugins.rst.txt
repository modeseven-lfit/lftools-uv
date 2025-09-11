.. SPDX-FileCopyrightText: 2025 The Linux Foundation
..
.. SPDX-License-Identifier: EPL-1.0

*******
plugins
*******

The jenkins plugins command provides functionality for managing Jenkins plugins.

.. code-block:: text

   Usage: lftools-uv jenkins plugins [OPTIONS] COMMAND [ARGS]...

   Jenkins plugins management commands.

   Options:
     --help  Show this message and exit.

   Commands:
     list     Show installed Jenkins plugins
     install  Add Jenkins plugins
     remove   Delete Jenkins plugins

.. note::
   This command requires proper Jenkins configuration setup.
   See the installation documentation for configuration details.
