# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Typer CLI interface for DCO checking."""

__author__ = "DW Talton"


import typer

from lftools_uv.shell import dco as dco_checker

dco_app = typer.Typer(name="dco", help="Check repository for commits missing DCO.")


@dco_app.callback()
def dco_callback():
    """DCO subsystem callback."""
    pass


@dco_app.command(name="check")
def check(
    repo_path: str | None = typer.Argument(None, help="Path to git repository (defaults to current directory)"),
    signoffs: str = typer.Option(
        "dco_signoffs", "--signoffs", help="Specify a directory to check for DCO signoff text files"
    ),
):
    """Check repository for commits missing DCO.

    This check will exclude merge commits and empty commits.
    It operates in your current working directory which has to
    be a git repository.  Alternatively, you can opt to pass in the
    path to a git repo.

    By default, this will also check for DCO signoff files in a directory
    named "dco_signoffs".  To check in a different directory, use the
    --signoffs option.  To ignore signoff files, an empty string can be passed.

    Refer to https://developercertificate.org/
    """
    if not repo_path:
        repo_path = "."
    status = dco_checker.check(repo_path, signoffs)
    raise typer.Exit(status)


@dco_app.command(name="match")
def match(
    repo_path: str | None = typer.Argument(None, help="Path to git repository (defaults to current directory)"),
    signoffs: str = typer.Option(
        "dco_signoffs", "--signoffs", help="Specify a directory to check for DCO signoff text files"
    ),
):
    """Check for commits whose DCO does not match the commit author's email.

    This check will exclude merge commits and empty commits.
    It operates in your current working directory which has to
    be a git repository.  Alternatively, you can opt to pass in the
    path to a git repo.

    By default, this will also check for DCO signoff files in a directory
    named "dco_signoffs".  To check in a different directory, use the
    --signoffs option.  To ignore signoff files, an empty string can be passed.

    Refer to https://developercertificate.org/
    """
    if not repo_path:
        repo_path = "."
    status = dco_checker.match(repo_path, signoffs)
    raise typer.Exit(status)
