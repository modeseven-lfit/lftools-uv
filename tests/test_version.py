# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2017 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Unit tests for the version command."""

import filecmp
import os

import pytest

from lftools_uv import cli

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "fixtures",
)


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "version_bump"),
    keep_top_dir=True,
)
def test_version_bump(cli_runner, datafiles, monkeypatch):
    """Test version bump command."""
    # Use monkeypatch.chdir() which automatically restores the original
    # working directory after the test, even if the test fails
    monkeypatch.chdir(datafiles / "version_bump")
    cli_runner.invoke(cli.cli, ["version", "bump", "TestRelease"], obj={})

    for _file in (datafiles / "version_bump").iterdir():
        if not _file.is_dir():
            continue
        pom = _file / "pom.xml"
        expected_pom = _file / "pom.xml.expected"
        if pom.exists() and expected_pom.exists():
            assert filecmp.cmp(pom, expected_pom), f"Mismatch in {_file.name}/pom.xml"


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "version_release"),
    keep_top_dir=True,
)
def test_version_release(cli_runner, datafiles, monkeypatch):
    """Test version release command."""
    # Use monkeypatch.chdir() which automatically restores the original
    # working directory after the test, even if the test fails
    monkeypatch.chdir(datafiles / "version_release")
    cli_runner.invoke(cli.cli, ["version", "release", "TestRelease"], obj={})

    for _file in (datafiles / "version_release").iterdir():
        if not _file.is_dir():
            continue
        pom = _file / "pom.xml"
        expected_pom = _file / "pom.xml.expected"
        if pom.exists() and expected_pom.exists():
            assert filecmp.cmp(pom, expected_pom), f"Mismatch in {_file.name}/pom.xml"


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "version_bump", "release"),
    keep_top_dir=True,
)
def test_patch(cli_runner, datafiles, monkeypatch):
    """Test patch command."""
    # Use monkeypatch.chdir() which automatically restores the original
    # working directory after the test, even if the test fails
    monkeypatch.chdir(datafiles / "release")
    result = cli_runner.invoke(
        cli.cli,
        ["version", "patch", "TestRelease", str(datafiles / "release" / "README")],
        obj={},
    )
    assert result.exit_code == 404
