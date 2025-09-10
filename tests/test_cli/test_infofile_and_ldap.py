# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2024 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from click.testing import CliRunner

from lftools_uv.cli.infofile import infofile as info_mod

if TYPE_CHECKING:
    from lftools_uv.cli.ldap_cli import ldap_cli as ldap_mod
else:
    try:
        from lftools_uv.cli.ldap_cli import ldap_cli as ldap_mod
    except ModuleNotFoundError:
        ldap_mod = None  # python-ldap not installed; LDAP-related tests will be skipped


@pytest.fixture(autouse=True)
def _configure_logging():
    """
    Ensure logging output (INFO+) is captured by Click's CliRunner output.

    We set up a root handler only once; further tests reuse it.
    """
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(stream=sys.stderr)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        root.addHandler(handler)
    root.setLevel(logging.INFO)
    yield


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# Helpers for creating temporary YAML files
# ---------------------------------------------------------------------------

INFO_FILE_TEMPLATE = """---
project: 'proj_name'
project_creation_date: '2024-01-01'
project_category: ''
lifecycle_state: 'Incubation'
project_lead: &umbrella_proj_name_ptl
    name: 'Lead Name'
    email: 'lead@example.org'
    id: 'leadid'
    company: 'ExampleCo'
    timezone: 'UTC'
primary_contact: *umbrella_proj_name_ptl
repositories:
    - proj/repository
committers:
    - name: 'Alice'
      email: 'alice@example.org'
      company: 'ExampleCo'
      id: 'aliceid'
      timezone: 'UTC'
    - name: 'Bob'
      email: 'bob@example.org'
      company: 'ExampleCo'
      id: 'bobid'
      timezone: 'UTC'
"""

LDAP_FILE_TEMPLATE = """---
committers:
    - name: 'Carol'
      email: 'carol@example.org'
      company: 'ExampleCo'
      id: 'carolid'
      timezone: 'UTC'
    - name: 'Bob'
      email: 'bob@example.org'
      company: 'ExampleCo'
      id: 'bobid'
      timezone: 'UTC'
"""


# ---------------------------------------------------------------------------
# Tests for infofile create-info-file
# ---------------------------------------------------------------------------


def test_create_info_file_empty_mode(runner: CliRunner, caplog):
    """
    create-info-file with --empty should avoid network calls and produce
    YAML-like scaffolding via logging.
    """
    result = runner.invoke(
        info_mod,
        [
            "create-info-file",
            "gerrit.example.org",
            "umbrella/proj-name",
            "--empty",
        ],
    )
    assert result.exit_code == 0, f"Command failed. Output: {result.output}, Exception: {result.exception}"
    # The YAML content is logged, so check the captured log output
    log_output = caplog.text
    assert "project:" in log_output
    assert "repositories:" in log_output
    assert "committers:" in log_output
    assert "umbrella_proj-name_ptl" in log_output or "umbrella_proj_name_ptl" in log_output


# ---------------------------------------------------------------------------
# Tests for infofile get-committers
# ---------------------------------------------------------------------------


def test_get_committers_full_output(runner: CliRunner, tmp_path: Path, caplog):
    info_path = tmp_path / "INFO.yaml"
    info_path.write_text(INFO_FILE_TEMPLATE)
    result = runner.invoke(
        info_mod,
        [
            "get-committers",
            str(info_path),
            "--full",
        ],
    )
    assert result.exit_code == 0, result.output
    # The committer info is logged, so check the captured log output
    log_output = caplog.text
    assert "aliceid" in log_output
    assert "bobid" in log_output
    # Full mode includes name/email lines
    assert "alice@example.org" in log_output
    assert "bob@example.org" in log_output


# ---------------------------------------------------------------------------
# Tests for infofile sync-committers
# ---------------------------------------------------------------------------


def test_sync_committers_adds_new_committer(runner: CliRunner, tmp_path: Path):
    info_path = tmp_path / "INFO.yaml"
    ldap_path = tmp_path / "LDAP.yaml"

    info_path.write_text(INFO_FILE_TEMPLATE)
    ldap_path.write_text(LDAP_FILE_TEMPLATE)

    # Add Carol (carolid) from LDAP file into INFO; specify repo replacement
    result = runner.invoke(
        info_mod,
        [
            "sync-committers",
            str(info_path),
            str(ldap_path),
            "carolid",
            "--repo",
            "new/repo",
        ],
    )
    assert result.exit_code == 0, result.output
    updated = info_path.read_text()
    assert "carolid" in updated
    assert "new/repo" in updated


def test_sync_committers_existing_committer_no_duplicate(runner: CliRunner, tmp_path: Path):
    info_path = tmp_path / "INFO.yaml"
    ldap_path = tmp_path / "LDAP.yaml"
    info_path.write_text(INFO_FILE_TEMPLATE)
    ldap_path.write_text(LDAP_FILE_TEMPLATE)

    # Attempt to re-sync existing 'bobid' should exit cleanly (code 0)
    result = runner.invoke(
        info_mod,
        [
            "sync-committers",
            str(info_path),
            str(ldap_path),
            "bobid",
            "--repo",
            "proj/repository",
        ],
    )
    assert result.exit_code == 0
    # Ensure not duplicated
    content = info_path.read_text()
    assert content.count("bobid") == 1


# ---------------------------------------------------------------------------
# Tests for infofile check-votes (simplified)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("voters, expected_exit_code", [(["aliceid"], 0), ([], 1)])
def test_check_votes_simple_mock(runner: CliRunner, tmp_path: Path, monkeypatch, voters, expected_exit_code):
    """
    We mock GerritRestAPI so that it returns a static list of reviewers.
    The command uses either Gerrit or GitHub; we test the Gerrit path.
    """
    info_path = tmp_path / "INFO.yaml"
    info_path.write_text(INFO_FILE_TEMPLATE)

    class DummyGerrit:
        def __init__(self, *a, **kw):
            pass

        def get(self, endpoint: str):
            # emulate /reviewers response structure
            return [
                {
                    "username": v,
                    "approvals": {"Code-Review": "+1"},
                }
                for v in voters
            ]

    import sys

    infofile_module = sys.modules["lftools_uv.cli.infofile"]
    monkeypatch.setattr(infofile_module, "GerritRestAPI", DummyGerrit)

    result = runner.invoke(
        info_mod,
        [
            "check-votes",
            str(info_path),
            "https://gerrit.example.org/",
            "12345",
        ],
    )
    assert result.exit_code == expected_exit_code


# ---------------------------------------------------------------------------
# LDAP csv command tests (simulate ldap module interactions)
# ---------------------------------------------------------------------------


class FakeLDAPObject:
    """
    Minimal simulation of an LDAP object required by csv command logic.
    """

    def __init__(self):
        self.protocol_version = None
        self._search_calls: list[tuple[str, str, str, Any]] = []
        self._result_queue: list[tuple[int, list]] = []
        # Preload results for group search (id=1) and user search (id=2)
        # Structure: list of tuples (dn, {attr: [values]})
        group_dn = "cn=mygroup,ou=Groups,dc=example,dc=org"
        user_base = "ou=Users,dc=example,dc=org"
        user_dn = f"uid=uid123,{user_base}"
        self._group_result = [(group_dn, {"member": [user_dn.encode()]})]
        self._user_result = [(user_dn, {"uid": [b"uid123"], "cn": [b"Common Name"], "mail": [b"cn@example.org"]})]
        self._next_search_id = 1

    # LDAP API simulation
    def simple_bind_s(self):
        return

    def unbind_s(self):
        return

    def search(self, dn, scope, search_filter, attrs):
        # Record call
        sid = self._next_search_id
        self._next_search_id += 1
        self._search_calls.append((dn, scope, search_filter, tuple(attrs)))
        # Enqueue appropriate results
        if "Groups" in dn:
            self._result_queue.append((100, self._group_result))
            self._result_queue.append((100, []))  # terminator
        else:
            # user search
            self._result_queue.append((100, self._user_result))
            self._result_queue.append((100, []))
        return sid

    def result(self, search_id, all):
        if not self._result_queue:
            return (101, [])
        return self._result_queue.pop(0)


@pytest.fixture
def patched_ldap(monkeypatch):
    """
    Patch ldap.initialize to return a FakeLDAPObject.
    """
    if ldap_mod is None:
        pytest.skip("python-ldap not installed")

    import sys

    ldap_cli_module = sys.modules["lftools_uv.cli.ldap_cli"]

    def fake_initialize(server):
        return FakeLDAPObject()

    monkeypatch.setattr(ldap_cli_module.ldap, "initialize", fake_initialize)
    return ldap_mod


@pytest.mark.skipif(ldap_mod is None, reason="python-ldap not installed")
def test_ldap_csv_command(runner: CliRunner, patched_ldap, caplog):
    """
    Validate that the ldap csv command logs expected CSV lines via logging.
    """
    result = runner.invoke(
        ldap_mod,
        [
            "csv",
            "--ldap-server",
            "ldaps://dummy",
            "--ldap-user-base",
            "ou=Users,dc=example,dc=org",
            "--ldap-group-base",
            "ou=Groups,dc=example,dc=org",
            "mygroup",
        ],
    )
    assert result.exit_code == 0, result.output
    # The CSV line is logged, so check the captured log output
    log_output = caplog.text
    assert "uid123,Common Name,cn@example.org" in log_output
