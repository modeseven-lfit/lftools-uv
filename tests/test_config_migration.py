# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""Tests for config directory migration from xdg to platformdirs."""

import os
from pathlib import Path
from unittest.mock import patch

from lftools_uv.config import get_lftools_config_dir, get_lftools_config_file


class TestConfigMigration:
    """Test config directory migration from xdg to platformdirs."""

    def test_get_lftools_config_dir_new_installation(self, tmp_path):
        """Test config directory creation for new installation."""
        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(tmp_path / "new_config")
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_dir = get_lftools_config_dir()

                assert config_dir == Path(tmp_path / "new_config")
                assert config_dir.exists()
                mock_platformdirs.assert_called_once_with("lftools")

    def test_get_lftools_config_dir_migration_from_old_location(self, tmp_path):
        """Test migration from old xdg-based location to new platformdirs location."""
        # Set up old config directory with a config file
        old_config_dir = tmp_path / ".config" / "lftools"
        old_config_dir.mkdir(parents=True)
        old_config_file = old_config_dir / "lftools.ini"
        old_config_file.write_text("[settings]\nkey=value\n")

        # Set up paths
        new_config_dir = tmp_path / "new_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_dir = get_lftools_config_dir()

                # Should return new location
                assert config_dir == new_config_dir
                assert config_dir.exists()

                # Should have migrated the config file
                migrated_config = new_config_dir / "lftools.ini"
                assert migrated_config.exists()
                assert migrated_config.read_text() == "[settings]\nkey=value\n"

    def test_get_lftools_config_dir_migration_preserves_directory_structure(self, tmp_path):
        """Test that migration preserves entire directory structure."""
        # Set up old config directory with subdirectories and files
        old_config_dir = tmp_path / ".config" / "lftools"
        old_config_dir.mkdir(parents=True)

        # Create config file
        (old_config_dir / "lftools.ini").write_text("[main]\ntest=true\n")

        # Create subdirectory with file
        subdir = old_config_dir / "profiles"
        subdir.mkdir()
        (subdir / "profile.ini").write_text("[profile1]\nname=test\n")

        # Set up new location
        new_config_dir = tmp_path / "new_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_dir = get_lftools_config_dir()

                # Verify structure was preserved
                assert (config_dir / "lftools.ini").exists()
                assert (config_dir / "profiles" / "profile.ini").exists()
                assert (config_dir / "lftools.ini").read_text() == "[main]\ntest=true\n"
                assert (config_dir / "profiles" / "profile.ini").read_text() == "[profile1]\nname=test\n"

    def test_get_lftools_config_dir_no_migration_when_new_exists(self, tmp_path):
        """Test that no migration occurs when new location already exists."""
        # Set up both old and new config directories
        old_config_dir = tmp_path / ".config" / "lftools"
        old_config_dir.mkdir(parents=True)
        (old_config_dir / "old.ini").write_text("[old]\ndata=old\n")

        new_config_dir = tmp_path / "new_config"
        new_config_dir.mkdir(parents=True)
        (new_config_dir / "new.ini").write_text("[new]\ndata=new\n")

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_dir = get_lftools_config_dir()

                # Should use existing new location
                assert config_dir == new_config_dir

                # Should not have migrated old file
                assert not (new_config_dir / "old.ini").exists()
                assert (new_config_dir / "new.ini").exists()
                assert (new_config_dir / "new.ini").read_text() == "[new]\ndata=new\n"

    def test_get_lftools_config_dir_migration_failure_fallback(self, tmp_path, caplog):
        """Test fallback to old location when migration fails."""
        # Set up old config directory
        old_config_dir = tmp_path / ".config" / "lftools"
        old_config_dir.mkdir(parents=True)
        (old_config_dir / "lftools.ini").write_text("[test]\nvalue=1\n")

        # Set up new location that will cause permission error
        new_config_dir = tmp_path / "new_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path
                with patch("shutil.copytree") as mock_copytree:
                    mock_copytree.side_effect = PermissionError("Permission denied")

                    config_dir = get_lftools_config_dir()

                    # Should fall back to old location
                    assert config_dir == old_config_dir

                    # Should log the error
                    assert "Failed to migrate config directory" in caplog.text
                    assert "Continuing to use legacy location" in caplog.text

    def test_get_lftools_config_file_integration(self, tmp_path):
        """Test that get_lftools_config_file returns correct path."""
        new_config_dir = tmp_path / "lftools_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_file = get_lftools_config_file()

                expected_path = str(new_config_dir / "lftools.ini")
                assert config_file == expected_path

    def test_migration_logs_success(self, tmp_path, caplog):
        """Test that successful migration is logged."""
        # Set up old config directory
        old_config_dir = tmp_path / ".config" / "lftools"
        old_config_dir.mkdir(parents=True)
        (old_config_dir / "lftools.ini").write_text("[test]\nkey=value\n")

        new_config_dir = tmp_path / "new_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                get_lftools_config_dir()

                # Should log migration messages
                assert "Migrating lftools config from" in caplog.text
                assert "Successfully migrated config to" in caplog.text

    def test_cross_platform_path_handling(self, tmp_path):
        """Test that paths work correctly across platforms."""
        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            # Test with different platform-style paths
            if os.name == "nt":
                # Windows-style path
                mock_platformdirs.return_value = str(tmp_path / "AppData" / "Local" / "lftools")
            else:
                # Unix-style path
                mock_platformdirs.return_value = str(tmp_path / ".config" / "lftools")

            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_dir = get_lftools_config_dir()
                config_file = get_lftools_config_file()

                # Should handle paths correctly regardless of platform
                assert isinstance(config_dir, Path)
                assert config_dir.exists()
                assert config_file.endswith("lftools.ini")
                assert os.path.exists(os.path.dirname(config_file))

    def test_migration_with_empty_old_directory(self, tmp_path):
        """Test migration behavior with empty old config directory."""
        # Set up empty old config directory
        old_config_dir = tmp_path / ".config" / "lftools"
        old_config_dir.mkdir(parents=True)

        new_config_dir = tmp_path / "new_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                config_dir = get_lftools_config_dir()

                # Should create new directory and migrate empty structure
                assert config_dir == new_config_dir
                assert config_dir.exists()
                assert config_dir.is_dir()

    def test_concurrent_access_safety(self, tmp_path):
        """Test that concurrent access doesn't cause issues."""
        new_config_dir = tmp_path / "concurrent_config"

        with patch("platformdirs.user_config_dir") as mock_platformdirs:
            mock_platformdirs.return_value = str(new_config_dir)
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = tmp_path

                # Multiple calls should be safe
                config_dir1 = get_lftools_config_dir()
                config_dir2 = get_lftools_config_dir()

                assert config_dir1 == config_dir2
                assert config_dir1.exists()
