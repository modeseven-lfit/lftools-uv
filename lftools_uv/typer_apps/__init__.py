# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2024 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Typer-based CLI applications for lftools-uv.

This package contains the new Typer-based CLI implementation that will
gradually replace the existing Click-based CLI. During the migration phase,
both implementations will coexist.

The package is structured as follows:
- root.py: Main Typer app and global callback
- utils.py: Utility commands (starting with passgen pilot)
- Additional domain modules will be added incrementally
"""
