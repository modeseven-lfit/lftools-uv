#!/usr/bin/env python3
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2017, 2023 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Python wrapper for gerrit_create shell script."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Execute the gerrit_create shell script with all arguments passed through."""
    # Find the shell script relative to this module
    current_dir = Path(__file__).parent.parent.parent
    shell_script = current_dir / "shell" / "gerrit_create"

    if not shell_script.exists():
        print(f"Error: Shell script not found at {shell_script}", file=sys.stderr)
        sys.exit(1)

    # Execute the shell script with all command line arguments
    cmd = [str(shell_script)] + sys.argv[1:]
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print(f"Error: Could not execute shell script at {shell_script}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
