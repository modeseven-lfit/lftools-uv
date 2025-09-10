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

import click
import pytest
from click.testing import CliRunner

from lftools_uv.cli.errors import error_handler, handle_errors
from lftools_uv.cli.state import AppState

# ---------------------------------------------------------------------------
# Tests for AppState
# ---------------------------------------------------------------------------


def test_app_state_basic():
    state = AppState()
    assert state.debug is False
    assert state.username is None
    state.update_credentials("alice", "secret")
    assert state.username == "alice"
    assert state.password == "secret"

    # Register dummy clients
    class Dummy: ...

    d1 = Dummy()
    state.set_client("jenkins", d1)
    assert state.get_client("jenkins") is d1

    asdict = state.as_dict()
    assert asdict["username"] == "alice"
    # Redacted password
    assert asdict["password"] == "********"

    desc = state.describe()
    assert "alice" in desc
    assert "jenkins=yes" in desc


def test_app_state_extra():
    state = AppState()
    state.put_extra("token", "abc123")
    assert state.get_extra("token") == "abc123"
    assert "token" in state.as_dict()["extra_keys"]


# ---------------------------------------------------------------------------
# Helper commands for error handling tests
# ---------------------------------------------------------------------------


@click.command()
@error_handler
def cmd_raises_value_error():
    raise ValueError("bad value")


@click.command()
@handle_errors(exit_codes={"ValueError": 42})
def cmd_custom_exit_code():
    raise ValueError("mapped value error")


@click.command()
@error_handler
@click.pass_context
def cmd_runtime_error(ctx):
    raise RuntimeError("boom runtime")


@click.command()
@handle_errors(reraise=True)
def cmd_reraise():
    raise RuntimeError("should bubble")


def test_error_handler_default_exit_code():
    runner = CliRunner()
    result = runner.invoke(cmd_raises_value_error)
    # ValueError not mapped in DEFAULT_EXIT_CODES so exit code 1
    assert result.exit_code == 1


def test_error_handler_custom_exit_code():
    runner = CliRunner()
    result = runner.invoke(cmd_custom_exit_code)
    assert result.exit_code == 42


def test_error_handler_debug_traceback(caplog):
    runner = CliRunner()
    # Provide context with debug state -> triggers traceback logging
    caplog.set_level(logging.ERROR)
    state = AppState(debug=True)
    result = runner.invoke(cmd_runtime_error, obj={"state": state})
    assert result.exit_code == 1
    # Should log the exception class
    assert any("RuntimeError: boom runtime" in r.message for r in caplog.records)
    # Traceback presence
    assert any("Traceback" in r.message for r in caplog.records)


def test_error_handler_without_debug_no_traceback(caplog):
    runner = CliRunner()
    caplog.set_level(logging.ERROR)
    state = AppState(debug=False)
    result = runner.invoke(cmd_runtime_error, obj={"state": state})
    assert result.exit_code == 1
    assert any("RuntimeError: boom runtime" in r.message for r in caplog.records)
    assert not any("Traceback" in r.message for r in caplog.records)


def test_error_handler_reraise():
    runner = CliRunner()
    result = runner.invoke(cmd_reraise)
    # Click treats unhandled exception as exit code 1 (non-zero)
    assert result.exit_code != 0


# Additional scenario: ensure SystemExit is not swallowed
@click.command()
@error_handler
def cmd_system_exit():
    raise SystemExit(5)


def test_error_handler_preserves_system_exit():
    runner = CliRunner()
    result = runner.invoke(cmd_system_exit)
    # The exact exit code should propagate
    assert result.exit_code == 5


# Ensure decorator include / exclude behavior
class CustomOne(Exception): ...


class CustomTwo(Exception): ...


@click.command()
@handle_errors(include=(CustomOne,))
def cmd_include_only():
    raise CustomTwo("not included so should propagate")


def test_handle_errors_include_only():
    runner = CliRunner()
    result = runner.invoke(cmd_include_only)
    # Unhandled exception -> non-zero, Click prints stack
    assert result.exit_code != 0


if __name__ == "__main__":  # pragma: no cover
    # Allow ad-hoc execution for debugging
    sys.exit(pytest.main([__file__]))
