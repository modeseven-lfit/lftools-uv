# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Test generic REST client."""

import json

import responses

import lftools_uv.api.client as client

creds = {"authtype": "token", "endpoint": "", "token": "xyz"}
c = client.RestApi(creds=creds)


@responses.activate
def test_get():
    responses.add(responses.GET, "https://fakeurl/", json={"success": "get"}, status=200, match_querystring=True)
    resp = c.get("https://fakeurl/")
    assert resp[1] == {"success": "get"}


@responses.activate
def test_patch():
    responses.add(
        responses.PATCH, url="https://fakeurl/", json={"success": "patch"}, status=200, match_querystring=True
    )
    resp = c.patch("https://fakeurl/")
    assert resp[1] == {"success": "patch"}


@responses.activate
def test_post():
    responses.add(responses.POST, "https://fakeurl/", json={"success": "post"}, status=201, match_querystring=True)
    resp = c.post("https://fakeurl/")
    assert resp[1] == {"success": "post"}


@responses.activate
def test_put():
    responses.add(responses.PUT, "https://fakeurl/", json={"success": "put"}, status=200, match_querystring=True)
    resp = c.put("https://fakeurl/")
    assert resp[1] == {"success": "put"}


@responses.activate
def test_delete():
    responses.add(responses.DELETE, "https://fakeurl/", json={"success": "delete"}, status=200, match_querystring=True)
    resp = c.delete("https://fakeurl/")
    assert resp[1] == {"success": "delete"}


@responses.activate
def test_post_with_unicode_string_data():
    """Test that Unicode characters in string data are properly encoded as UTF-8."""

    # Create a callback to inspect the actual request body
    def request_callback(request):
        # Verify the body is bytes and properly UTF-8 encoded
        assert isinstance(request.body, bytes), "Request body should be bytes"

        # Decode and verify the Unicode characters are preserved
        body_str = request.body.decode("utf-8")
        assert "Aniś" in body_str or "Bełur" in body_str, "Unicode characters should be preserved"

        return (200, {}, json.dumps({"success": "unicode"}))

    responses.add_callback(
        responses.POST, "https://fakeurl/unicode", callback=request_callback, content_type="application/json"
    )

    # Test with Unicode characters that would fail with latin-1 encoding
    unicode_data = '{"user": "Aniś Bełur", "group": "tëam-ñame"}'
    resp = c.post("https://fakeurl/unicode", data=unicode_data)
    assert resp[1] == {"success": "unicode"}


@responses.activate
def test_post_with_various_unicode_characters():
    """Test various Unicode characters from different languages."""
    unicode_test_cases = [
        '{"name": "Señor García"}',  # Spanish
        '{"name": "Müller"}',  # German
        '{"name": "Dvořák"}',  # Czech
        '{"name": "日本語"}',  # Japanese
        '{"name": "Владимир"}',  # Russian
        '{"name": "François"}',  # French
        '{"name": "Björk"}',  # Icelandic
        '{"name": "Łukasz"}',  # Polish
        '{"user": "māori", "char": "ā"}',  # Maori
    ]

    for test_data in unicode_test_cases:

        def request_callback(request):
            # Verify proper UTF-8 encoding
            assert isinstance(request.body, bytes)
            decoded = request.body.decode("utf-8")
            return (200, {}, json.dumps({"received": decoded}))

        responses.add_callback(
            responses.POST, "https://fakeurl/unicode-test", callback=request_callback, content_type="application/json"
        )

        # Should not raise UnicodeEncodeError
        resp = c.post("https://fakeurl/unicode-test", data=test_data)
        assert resp[0].status_code == 200


@responses.activate
def test_post_with_bytes_data():
    """Test that bytes data is passed through unchanged."""

    def request_callback(request):
        # Verify the body is still bytes
        assert isinstance(request.body, bytes)
        assert request.body == b'{"already": "bytes"}'
        return (200, {}, json.dumps({"success": "bytes"}))

    responses.add_callback(
        responses.POST, "https://fakeurl/bytes", callback=request_callback, content_type="application/json"
    )

    # Pass bytes directly - should not be re-encoded
    bytes_data = b'{"already": "bytes"}'
    resp = c.post("https://fakeurl/bytes", data=bytes_data)
    assert resp[1] == {"success": "bytes"}


@responses.activate
def test_put_with_unicode_data():
    """Test PUT requests with Unicode data."""

    def request_callback(request):
        assert isinstance(request.body, bytes)
        decoded = request.body.decode("utf-8")
        assert "ñ" in decoded
        return (200, {}, json.dumps({"success": "put-unicode"}))

    responses.add_callback(
        responses.PUT, "https://fakeurl/unicode-put", callback=request_callback, content_type="application/json"
    )

    unicode_data = '{"description": "Project with español characters: ñáéíóú"}'
    resp = c.put("https://fakeurl/unicode-put", data=unicode_data)
    assert resp[1] == {"success": "put-unicode"}


@responses.activate
def test_patch_with_unicode_data():
    """Test PATCH requests with Unicode data."""

    def request_callback(request):
        assert isinstance(request.body, bytes)
        decoded = request.body.decode("utf-8")
        # Test the specific character that caused the original bug
        # Check for uppercase Š (U+0160) in "Šmit"
        assert "Š" in decoded, f"Expected 'Š' in decoded string, got: {decoded}"
        return (200, {}, json.dumps({"success": "patch-unicode"}))

    responses.add_callback(
        responses.PATCH, "https://fakeurl/unicode-patch", callback=request_callback, content_type="application/json"
    )

    # Use the character that caused the original 'latin-1' codec error
    unicode_data = '{"user": "Jože Šmit"}'  # Contains \u0160
    resp = c.patch("https://fakeurl/unicode-patch", data=unicode_data)
    assert resp[1] == {"success": "patch-unicode"}
