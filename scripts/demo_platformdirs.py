#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""
Demonstration script showing platformdirs cross-platform config directory behavior.

This script shows how the migration from xdg to platformdirs provides better
cross-platform support and follows OS-specific conventions.
"""

import platform
from pathlib import Path

import platformdirs

from lftools_uv.config import get_lftools_config_dir, get_lftools_config_file


def main():
    """Demonstrate platformdirs cross-platform behavior."""
    print("🔧 lftools-uv platformdirs Migration Demo")
    print("=" * 50)

    # System information
    print(f"Operating System: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print()

    # Show old vs new approach
    print("📁 Directory Locations")
    print("-" * 30)

    # Old xdg-based approach (Linux-centric)
    old_config_dir = Path.home() / ".config" / "lftools"
    print(f"Old (xdg):        {old_config_dir}")

    # New platformdirs approach (cross-platform)
    new_config_dir = get_lftools_config_dir()
    config_file = get_lftools_config_file()
    print(f"New (platformdirs): {new_config_dir}")
    print(f"Config file:        {config_file}")
    print()

    # Show platform-specific behavior
    print("🌍 Platform-Specific Directories")
    print("-" * 35)
    print(f"User Config:  {platformdirs.user_config_dir('lftools')}")
    print(f"User Cache:   {platformdirs.user_cache_dir('lftools')}")
    print(f"User Data:    {platformdirs.user_data_dir('lftools')}")
    print(f"User Logs:    {platformdirs.user_log_dir('lftools')}")
    print()

    # Platform-specific explanations
    system = platform.system()
    print("📋 Platform Conventions")
    print("-" * 25)

    if system == "Darwin":  # macOS
        print("✅ macOS: Using native ~/Library/ structure")
        print("  • Config: ~/Library/Application Support/")
        print("  • Cache:  ~/Library/Caches/")
        print("  • Logs:   ~/Library/Logs/")

    elif system == "Windows":
        print("✅ Windows: Using native %APPDATA% structure")
        print("  • Config: %APPDATA%\\lftools\\")
        print("  • Cache:  %LOCALAPPDATA%\\lftools\\")
        print("  • Logs:   %LOCALAPPDATA%\\lftools\\Logs\\")

    elif system == "Linux":
        print("✅ Linux: Using XDG Base Directory Specification")
        print("  • Config: ~/.config/lftools/")
        print("  • Cache:  ~/.cache/lftools/")
        print("  • Logs:   ~/.local/state/lftools/")

    else:
        print(f"✅ {system}: Using appropriate conventions for this platform")

    print()

    # Migration status
    print("🔄 Migration Status")
    print("-" * 20)

    old_exists = old_config_dir.exists()
    new_exists = new_config_dir.exists()

    if old_exists and not new_exists:
        print("⚠️  Old config directory found - will be migrated on first use")
        print(f"   From: {old_config_dir}")
        print(f"   To:   {new_config_dir}")

    elif old_exists and new_exists:
        print("✅ Config migrated successfully")
        print("   Both old and new directories exist")

    elif new_exists:
        print("✅ Using new platformdirs location")
        print("   No migration needed")

    else:
        print("📝 New installation - will create platform-appropriate directories")

    print()

    # Benefits summary
    print("🎯 Benefits of platformdirs Migration")
    print("-" * 40)
    print("✅ Cross-platform compatibility")
    print("✅ Native OS conventions")
    print("✅ Better enterprise environment support")
    print("✅ Cleaner separation of config/cache/logs")
    print("✅ Follows Python ecosystem standards")
    print("✅ Backward compatibility with existing configs")
    print()

    # Developer information
    print("👩‍💻 For Developers")
    print("-" * 17)
    print("Migration is automatic and transparent:")
    print("• Existing configs are preserved")
    print("• No user action required")
    print("• Fallback to old location if migration fails")
    print("• Cross-platform path handling")
    print()

    print("🚀 Migration completed successfully!")


if __name__ == "__main__":
    main()
