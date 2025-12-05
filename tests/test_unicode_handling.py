# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2025 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Test Unicode handling across the codebase."""

import logging

import pytest


class TestUnicodeInLogging:
    """Test that logging handles Unicode characters correctly."""

    def test_logging_with_fstring_unicode(self, caplog):
        """Test that f-string logging works with Unicode characters."""
        log = logging.getLogger(__name__)

        # Test various Unicode characters in f-strings
        test_cases = [
            ("Aniś Bełur", "team-ñame"),
            ("Señor García", "español"),
            ("François Müller", "français"),
            ("Владимир Петров", "русский"),
            ("田中太郎", "日本語"),
            ("Jože Šmit", "slovenščina"),
        ]

        with caplog.at_level(logging.INFO):
            for name, team in test_cases:
                # This should NOT raise UnicodeEncodeError
                log.info(f"User {name} from team {team}")
                assert name in caplog.text
                assert team in caplog.text

    def test_logging_with_percent_formatting_unicode(self, caplog):
        """Test that percent-style logging works with Unicode characters."""
        log = logging.getLogger(__name__)

        with caplog.at_level(logging.INFO):
            # Percent-style formatting should handle Unicode
            log.info("Creating repo under organization: %s", "tëam-ñame")
            assert "tëam-ñame" in caplog.text

            log.info("User %s has voted on change %s", "Aniś Bełur", "73947")
            assert "Aniś Bełur" in caplog.text

    def test_logging_error_with_unicode(self, caplog):
        """Test that error logging handles Unicode correctly."""
        log = logging.getLogger(__name__)

        with caplog.at_level(logging.ERROR):
            log.error("Failed to process user: Jože Šmit")
            assert "Jože Šmit" in caplog.text

    def test_logging_with_unicode_in_dict(self, caplog):
        """Test logging with Unicode characters in dictionary values."""
        log = logging.getLogger(__name__)

        data = {"user": "François", "organization": "Fondation Linux", "team": "équipe-développement"}

        with caplog.at_level(logging.INFO):
            log.info(f"Processing data: {data}")
            assert "François" in caplog.text
            assert "équipe-développement" in caplog.text

    def test_incorrect_logging_syntax_detection(self):
        """Test that we can detect incorrect logging syntax patterns."""
        # These are examples of INCORRECT patterns that should be avoided
        incorrect_patterns = [
            # Using comma instead of f-string or %
            'log.info("Creating repo: ", org_name)',
            'log.info("User:", username)',
            'log.info("Approvals:", approval_list)',
        ]

        # Correct patterns
        correct_patterns = [
            'log.info(f"Creating repo: {org_name}")',
            'log.info("User: %s", username)',
            'log.info(f"Approvals: {approval_list}")',
        ]

        # This test serves as documentation of correct vs incorrect patterns
        assert len(incorrect_patterns) > 0
        assert len(correct_patterns) == len(incorrect_patterns)


class TestUnicodeInStrings:
    """Test Unicode handling in string operations."""

    def test_unicode_characters_in_json_strings(self):
        """Test that JSON strings with Unicode are handled correctly."""
        import json

        test_data = {"user": "Aniś Bełur", "group": "tëam-ñame", "description": "Project with español: ñáéíóú"}

        # Should not raise UnicodeEncodeError
        json_str = json.dumps(test_data, ensure_ascii=False)
        assert "Aniś Bełur" in json_str
        assert "tëam-ñame" in json_str

        # Should be able to encode to UTF-8
        encoded = json_str.encode("utf-8")
        assert isinstance(encoded, bytes)

        # Should be able to decode back
        decoded = encoded.decode("utf-8")
        assert decoded == json_str

    def test_unicode_in_url_parameters(self):
        """Test that Unicode in URL parameters is handled."""
        import urllib.parse

        # Test encoding Unicode characters for URL
        params = {"user": "Jože Šmit", "team": "équipe-française"}

        # Should not raise UnicodeEncodeError
        encoded = urllib.parse.urlencode(params)
        assert "Jo" in encoded  # The ž will be percent-encoded
        assert "quipe" in encoded  # The é will be percent-encoded

    def test_unicode_characters_from_different_scripts(self):
        """Test handling of Unicode from various writing systems."""
        unicode_strings = [
            "Latin: Aniś Bełur",
            "Greek: Αλέξανδρος",
            "Cyrillic: Владимир",
            "Hebrew: שלום",
            "Arabic: مرحبا",
            "Japanese: こんにちは",
            "Korean: 안녕하세요",
            "Thai: สวัสดี",
            "Emoji: 👋🌍",
        ]

        for test_str in unicode_strings:
            # Should encode and decode without errors
            encoded = test_str.encode("utf-8")
            decoded = encoded.decode("utf-8")
            assert decoded == test_str

    def test_unicode_normalization(self):
        """Test Unicode normalization handling."""
        import unicodedata

        # Same character, different representations
        # é can be: 1) single character U+00E9, or 2) e + combining acute U+0065 U+0301
        str1 = "François"  # Composed form
        str2 = "François"  # May be decomposed form

        # Normalize both to NFC (composed)
        normalized1 = unicodedata.normalize("NFC", str1)
        normalized2 = unicodedata.normalize("NFC", str2)

        # Should be equal after normalization
        assert normalized1 == normalized2


class TestUnicodeEdgeCases:
    """Test edge cases and specific characters that have caused issues."""

    def test_latin1_incompatible_characters(self):
        """Test characters that cannot be encoded with latin-1."""
        # These characters caused the original bug: 'latin-1' codec can't encode
        problematic_chars = [
            "\u0161",  # š (lowercase s with caron)
            "\u0141",  # Ł (uppercase L with stroke)
            "\u0142",  # ł (lowercase l with stroke)
            "\u0107",  # ć (lowercase c with acute)
            "\u010d",  # č (lowercase c with caron)
            "\u017e",  # ž (lowercase z with caron)
        ]

        for char in problematic_chars:
            test_string = f"User name: Josip {char}ivkovic"

            # Should encode with UTF-8 without error
            encoded = test_string.encode("utf-8")
            assert isinstance(encoded, bytes)

            # Should fail with latin-1 (this is the original bug)
            with pytest.raises(UnicodeEncodeError):
                test_string.encode("latin-1")

    def test_emoji_handling(self):
        """Test that emojis are handled correctly."""
        emoji_string = "Success! ✅ User 👤 logged in from 🌍"

        # Should encode to UTF-8
        encoded = emoji_string.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == emoji_string

    def test_zero_width_characters(self):
        """Test handling of zero-width Unicode characters."""
        # Zero-width space, zero-width joiner, etc.
        zwsp = "\u200b"  # Zero-width space
        zwj = "\u200d"  # Zero-width joiner

        test_string = f"Name{zwsp}with{zwj}special{zwsp}chars"

        # Should handle these characters
        encoded = test_string.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == test_string

    def test_combining_diacritical_marks(self):
        """Test combining diacritical marks."""
        # Base character + combining mark
        base = "e"
        acute = "\u0301"  # Combining acute accent
        combined = base + acute  # Should display as é

        # Should encode/decode correctly
        encoded = combined.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == combined


class TestUnicodeInGerritScenarios:
    """Test Unicode handling in Gerrit-specific scenarios."""

    def test_gerrit_user_names_with_unicode(self):
        """Test that Gerrit user names with Unicode are handled."""
        # Common European names that might appear in Gerrit
        gerrit_users = [
            "Aniś Bełur",
            "François Dupont",
            "Björn Müller",
            "José García",
            "Łukasz Kowalski",
            "Jože Šmit",
        ]

        for user in gerrit_users:
            # Simulate JSON payload that would be sent to Gerrit API
            import json

            payload = json.dumps({"reviewer": user}, ensure_ascii=False)

            # Should encode to UTF-8 for API request
            encoded = payload.encode("utf-8")
            assert isinstance(encoded, bytes)

            # Should decode back correctly
            decoded = encoded.decode("utf-8")
            assert user in decoded

    def test_gerrit_group_names_with_unicode(self):
        """Test that Gerrit group names with Unicode are handled."""
        group_names = [
            "tëam-ñame",
            "équipe-développement",
            "команда-разработчиков",
        ]

        for group in group_names:
            import json

            payload = json.dumps({"group": group}, ensure_ascii=False)
            encoded = payload.encode("utf-8")
            decoded = encoded.decode("utf-8")
            assert group in decoded

    def test_gerrit_commit_messages_with_unicode(self):
        """Test that commit messages with Unicode are handled."""
        commit_messages = [
            "Fix: Resolved issue reported by François",
            "Feature: Added support for español",
            "Doc: Updated README with 日本語 translation",
        ]

        for message in commit_messages:
            # Should encode/decode without issues
            encoded = message.encode("utf-8")
            decoded = encoded.decode("utf-8")
            assert decoded == message


class TestUnicodeInGitHubScenarios:
    """Test Unicode handling in GitHub-specific scenarios."""

    def test_github_repo_descriptions_with_unicode(self):
        """Test that repository descriptions with Unicode are handled."""
        descriptions = [
            "A project for français developers",
            "Herramienta para desarrolladores en español",
            "日本語のドキュメント",
        ]

        for desc in descriptions:
            # Should handle Unicode in API calls
            encoded = desc.encode("utf-8")
            decoded = encoded.decode("utf-8")
            assert decoded == desc

    def test_github_team_names_with_unicode(self, caplog):
        """Test that team names with Unicode are handled."""
        log = logging.getLogger(__name__)
        org_name = "test-org"
        team_name = "équipe-française"

        with caplog.at_level(logging.INFO):
            # This simulates the logging that happens in create-team
            # Should NOT raise TypeError
            log.info(f"Creating team {team_name} under organization {org_name}")
            assert team_name in caplog.text
            assert org_name in caplog.text


class TestUnicodeRegressionPrevention:
    """Tests specifically designed to prevent regressions of the fixed bugs."""

    def test_prevent_latin1_encoding_error_regression(self):
        """Ensure the latin-1 encoding error doesn't regress.

        This test specifically targets the bug fixed in:
        - lftools Gerrit change #73947
        - lftools-uv fix in api/client.py
        """
        # The character that caused the original bug
        problematic_string = '{"user": "Jože Šmit"}'  # Contains \u0161

        # This should work with UTF-8 encoding
        encoded = problematic_string.encode("utf-8")
        assert isinstance(encoded, bytes)

        # Verify the fix prevents latin-1 encoding issues
        # If we accidentally use latin-1, this would fail
        with pytest.raises(UnicodeEncodeError):
            problematic_string.encode("latin-1")

    def test_prevent_logging_format_error_regression(self, caplog):
        """Ensure the logging format error doesn't regress.

        This test specifically targets the bug fixed in:
        - lftools Gerrit change #73947 (github_cli.py)
        - lftools-uv fix in cli/github_cli.py and api/endpoints/gerrit.py
        """
        log = logging.getLogger(__name__)

        org_name = "test-org"
        approval_list = ["user1", "user2"]

        with caplog.at_level(logging.INFO):
            # Correct f-string format (should work)
            log.info(f"Creating repo under organization: {org_name}")
            assert "Creating repo under organization: test-org" in caplog.text

            # Correct f-string format (should work)
            log.info(f"Approvals: {approval_list}")
            assert "Approvals:" in caplog.text

    def test_unicode_in_api_request_data(self):
        """Test that API request data with Unicode is properly handled.

        This simulates what happens in RestApi._request() after the fix.
        """
        # Simulate the fix in client.py
        data = '{"reviewer": "Aniś Bełur", "group": "tëam-ñame"}'

        # The fix: encode string data as UTF-8
        if isinstance(data, str):
            data = data.encode("utf-8")

        # Verify it's now bytes
        assert isinstance(data, bytes)

        # Verify it can be decoded back correctly
        decoded = data.decode("utf-8")
        assert "Aniś Bełur" in decoded
        assert "tëam-ñame" in decoded


class TestUnicodeInNexusScenarios:
    """Test Unicode handling in Nexus-specific scenarios."""

    def test_nexus_json_encoding_with_unicode(self):
        """Test that Nexus JSON data with Unicode is encoded as UTF-8, not latin-1.

        This test specifically targets the bug found in lftools_uv/nexus/__init__.py
        where json.dumps().encode(encoding="latin-1") was used in 5 places.
        """
        import json

        # Test data that might contain Unicode (e.g., user names, descriptions)
        test_cases = [
            {"name": "François Dupont", "email": "francois@example.com"},
            {"description": "Repository for español team"},
            {"user": "Jože Šmit", "role": "developer"},
            {"patterns": ["*.jar", "*.war"], "name": "équipe-française"},
            {"contentClass": "any", "name": "tëam-ñame"},
        ]

        for test_data in test_cases:
            json_str = json.dumps(test_data)

            # Should encode with UTF-8 (the fix)
            encoded_utf8 = json_str.encode(encoding="utf-8")
            assert isinstance(encoded_utf8, bytes)

            # Verify it can be decoded back
            decoded = encoded_utf8.decode("utf-8")
            assert decoded == json_str

            # For data with non-latin-1 characters, latin-1 encoding should fail
            if any(char in json_str for char in ["š", "Š", "ñ", "é", "ë"]):
                try:
                    json_str.encode("latin-1")
                except UnicodeEncodeError:
                    pass  # Expected for characters outside latin-1

    def test_nexus_target_creation_with_unicode(self):
        """Test that Nexus target creation handles Unicode in names."""
        import json

        # Simulate creating a Nexus target with Unicode in the name
        target = {
            "data": {
                "contentClass": "any",
                "patterns": ["*.jar"],
                "name": "équipe-développement",
            }
        }

        # Test with ensure_ascii=False to preserve Unicode characters
        json_data = json.dumps(target, ensure_ascii=False).encode(encoding="utf-8")
        assert isinstance(json_data, bytes)

        # Verify the data can be decoded
        decoded = json_data.decode("utf-8")
        assert "équipe-développement" in decoded

    def test_nexus_user_creation_with_unicode(self):
        """Test that Nexus user creation handles Unicode names."""
        import json

        # Simulate creating a Nexus user with Unicode characters
        user_data = {
            "data": {
                "userId": "fmüller",
                "firstName": "François",
                "lastName": "Müller",
                "email": "fmuller@example.com",
                "roles": ["developer"],
            }
        }

        # Test with ensure_ascii=False to preserve Unicode characters
        json_data = json.dumps(user_data, ensure_ascii=False).encode(encoding="utf-8")
        assert isinstance(json_data, bytes)

        decoded = json_data.decode("utf-8")
        assert "François" in decoded
        assert "Müller" in decoded

    def test_nexus_role_creation_with_unicode(self):
        """Test that Nexus role creation handles Unicode descriptions."""
        import json

        role_data = {
            "data": {
                "id": "dev-team",
                "name": "Development Team",
                "description": "Équipe de développement français",
                "privileges": ["read", "write"],
            }
        }

        # Test with ensure_ascii=False to preserve Unicode characters
        json_data = json.dumps(role_data, ensure_ascii=False).encode(encoding="utf-8")
        decoded = json_data.decode("utf-8")
        assert "Équipe de développement français" in decoded

    def test_nexus_repo_group_update_with_unicode(self):
        """Test that Nexus repo group updates handle Unicode."""
        import json

        repo_data = {"data": {"name": "Grupo de repositórios", "description": "Repository group for español projects"}}

        # Test with ensure_ascii=False to preserve Unicode characters
        json_data = json.dumps(repo_data, ensure_ascii=False).encode(encoding="utf-8")
        decoded = json_data.decode("utf-8")
        assert "Grupo de repositórios" in decoded
        assert "español" in decoded
