# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2024 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Typer CLI application entry point for lftools-uv.

This module exposes the main Typer application instance that serves as
the new CLI interface. It's designed to run in parallel with the existing
Click-based CLI during the migration phase.

To use the Typer-based CLI, set the environment variable:
    LFTOOLS_CLI_V2=1

The application is structured to maintain compatibility with the existing
state management and configuration systems while providing a more modern
CLI experience through Typer.
"""

from lftools_uv.typer_apps.root import get_app

# Expose the main Typer app instance
app = get_app()

# This allows the app to be used directly with typer.run() if needed
if __name__ == "__main__":
    app()
