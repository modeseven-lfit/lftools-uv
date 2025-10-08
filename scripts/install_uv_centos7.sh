#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation
#
# Install UV Python package manager on CentOS 7 systems
#
# This script handles the challenges of installing UV on CentOS 7:
# 1. CentOS 7 is EOL and mirrors are unavailable - we fix repos to use vault.centos.org
# 2. The system glibc is too old - UV installer automatically uses musl-static version
# 3. Installs system-wide for all users

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root for system-wide installation"
        exit 1
    fi
}

# Check if this is CentOS 7
check_centos7() {
    if [[ ! -f /etc/centos-release ]]; then
        log_error "This script is designed for CentOS 7 only"
        exit 1
    fi

    local version
    version=$(cat /etc/centos-release | grep -oE '[0-9]+' | head -1)
    if [[ "$version" != "7" ]]; then
        log_error "This script is designed for CentOS 7 only. Detected version: $version"
        exit 1
    fi

    log_info "Detected CentOS 7 - proceeding with installation"
}

# Fix CentOS 7 repositories to use vault.centos.org
fix_centos7_repos() {
    log_info "Fixing CentOS 7 repositories to use vault.centos.org..."

    # Backup original repo files
    if [[ ! -d /etc/yum.repos.d.backup ]]; then
        cp -r /etc/yum.repos.d /etc/yum.repos.d.backup
        log_info "Backed up original repository configuration to /etc/yum.repos.d.backup"
    fi

    # Update repository URLs to use vault.centos.org
    sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo

    # Clean yum cache and rebuild
    yum clean all >/dev/null 2>&1
    yum makecache >/dev/null 2>&1

    log_success "Repository configuration updated successfully"
}

# Install required dependencies
install_dependencies() {
    log_info "Installing required dependencies..."

    local packages=("curl" "wget" "which")

    for package in "${packages[@]}"; do
        if ! rpm -q "$package" >/dev/null 2>&1; then
            log_info "Installing $package..."
            yum install -y "$package" >/dev/null 2>&1
        else
            log_info "$package is already installed"
        fi
    done

    log_success "All dependencies installed"
}

# Install UV using the official installer
install_uv() {
    log_info "Installing UV using the official installer..."

    # Create temporary directory for installation
    local temp_dir
    temp_dir=$(mktemp -d)

    # Download and run UV installer
    if curl -LsSf https://astral.sh/uv/install.sh | bash -s -- --dir "$temp_dir"; then
        log_success "UV installer completed successfully"

        # Copy binaries to system location
        if [[ -f "$temp_dir/bin/uv" ]]; then
            cp "$temp_dir/bin/uv" /usr/local/bin/
            cp "$temp_dir/bin/uvx" /usr/local/bin/
            chmod +x /usr/local/bin/uv /usr/local/bin/uvx
            log_success "UV binaries installed to /usr/local/bin/"
        else
            log_error "UV binary not found in expected location"
            return 1
        fi
    else
        log_error "UV installation failed"
        return 1
    fi

    # Clean up temporary directory
    rm -rf "$temp_dir"
}

# Verify UV installation
verify_installation() {
    log_info "Verifying UV installation..."

    if command -v uv >/dev/null 2>&1; then
        local version
        version=$(uv --version)
        log_success "UV is installed and working: $version"

        # Test basic functionality
        log_info "Testing basic UV functionality..."
        if uv --help >/dev/null 2>&1; then
            log_success "UV help command works correctly"
        else
            log_warn "UV help command failed - there may be issues"
        fi

        return 0
    else
        log_error "UV installation verification failed"
        return 1
    fi
}

# Create system-wide configuration
create_system_config() {
    log_info "Creating system-wide UV configuration..."

    # Create profile script to add UV to PATH
    cat > /etc/profile.d/uv.sh << 'EOF'
# UV Python package manager
export PATH="/usr/local/bin:$PATH"
EOF

    chmod +x /etc/profile.d/uv.sh
    log_success "System-wide PATH configuration created"
}

# Show installation summary
show_summary() {
    echo
    log_success "UV installation completed successfully!"
    echo
    echo "Installation Summary:"
    echo "===================="
    echo "• UV version: $(uv --version 2>/dev/null || echo 'Unknown')"
    echo "• Installation location: /usr/local/bin/"
    echo "• Configuration: /etc/profile.d/uv.sh"
    echo "• Repository backup: /etc/yum.repos.d.backup"
    echo
    echo "Usage:"
    echo "======="
    echo "• Create new project: uv init my-project"
    echo "• Add dependencies: uv add requests"
    echo "• Run scripts: uv run script.py"
    echo "• Install packages: uv pip install package"
    echo "• Show help: uv --help"
    echo
    echo "Note: You may need to start a new shell session or run 'source /etc/profile.d/uv.sh' to use uv immediately."
}

# Main installation function
main() {
    echo "CentOS 7 UV Installation Script"
    echo "==============================="
    echo

    check_root
    check_centos7

    # Check if UV is already installed
    if command -v uv >/dev/null 2>&1; then
        local current_version
        current_version=$(uv --version)
        log_warn "UV is already installed: $current_version"
        read -p "Do you want to reinstall? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 0
        fi
    fi

    fix_centos7_repos
    install_dependencies
    install_uv

    if verify_installation; then
        create_system_config
        show_summary
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
